import argparse
from datetime import datetime
import html
import json
import os
from pathlib import Path
import random
import re
import sys
import time
from urllib.parse import urljoin, urlparse

# Ensure local .venv site-packages is loaded even when invoked via system python on Windows
VENV_SITE = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
  sys.path.insert(0, str(VENV_SITE))

from bs4 import BeautifulSoup
import requests

MARGINALIA_API_URL = "https://api2.marginalia-search.com/search"
WIBY_API_URL = "https://wiby.me/json/"

USER_AGENT = (
    "DeepestInternetScout/0.3 (+https://github.com/abilbao1/deepest-internet)"
)

# --- Parámetros de Filtrado (Fase 2) ---
MIN_CHAR_LENGTH = 3000
MIN_LONG_PARAGRAPHS = 5
LONG_PARAGRAPH_CHARS = 140
MIN_PROSE_RATIO = 0.50
MAX_LINK_DENSITY = 0.35

BLOCKED_DOMAINS = {
    "amazon.com",
    "amzn.to",
    "youtube.com",
    "youtu.be",
    "wikipedia.org",
    "reddit.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "pinterest.com",
    "ebay.com",
    "goodreads.com",
    "google.com",
    "apple.com",
    "linkedin.com",
    "github.com",
    "cloudflare.com",
    "stripe.com",
}

COMMERCIAL_PHRASES = [
    "add to cart",
    "shopping cart",
    "buy now",
    "purchase copies",
    "go the amazon site",
    "go to the amazon site",
    "affiliate disclosure",
    "checkout now",
]

BLOCK_TAGS = {
    "p",
    "div",
    "blockquote",
    "article",
    "section",
    "li",
    "td",
    "tr",
    "dt",
    "dd",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "pre",
}


def slugify(value: str, max_len: int = 70) -> str:
  value = value.lower().strip()
  value = re.sub(r"[^a-z0-9]+", "-", value)
  value = value.strip("-")
  return (value[:max_len].rstrip("-")) or "untitled"


def load_random_seeds(seeds_path: Path, n: int = 1) -> list[str]:
  with open(seeds_path, "r", encoding="utf-8") as f:
    data = json.load(f)
  all_seeds = [seed for category in data.values() for seed in category]
  return random.sample(all_seeds, min(n, len(all_seeds)))


def search_small_web(query: str, count: int = 6) -> tuple[str, list[dict]]:
  """Usa Marginalia API v2 si MARGINALIA_API_KEY está configurada; si no, usa Wiby JSON API."""
  api_key = os.environ.get("MARGINALIA_API_KEY", "").strip()
  if api_key:
    try:
      response = requests.get(
          MARGINALIA_API_URL,
          params={"query": query, "count": count},
          headers={"User-Agent": USER_AGENT, "API-Key": api_key},
          timeout=8,
      )
      if response.ok:
        results = response.json().get("results", [])
        if results:
          return "Marginalia Search API", results
    except requests.RequestException as exc:
      print(f"[!] Error en Marginalia API ({exc}). Saltando a Wiby...")

  last_exc = None
  for attempt in range(2):
    try:
      response = requests.get(
          WIBY_API_URL,
          params={"q": query},
          headers={"User-Agent": USER_AGENT},
          timeout=12,
      )
      response.raise_for_status()
      raw_results = response.json()
      normalized = [
          {
              "url": item.get("URL", ""),
              "title": html.unescape(item.get("Title", "Sin título")),
              "description": html.unescape(item.get("Snippet", "")),
          }
          for item in raw_results[:count]
      ]
      return "Wiby Old-Web JSON API", normalized
    except requests.RequestException as exc:
      last_exc = exc
      time.sleep(1.5)

  print(f"[!] No se pudo consultar Wiby para '{query}': {last_exc}")
  return "Wiby Old-Web JSON API (Error)", []


def get_domain(url: str) -> str:
  host = urlparse(url).netloc.lower()
  return host[4:] if host.startswith("www.") else host


def is_blocked_domain(url: str) -> bool:
  host = get_domain(url)
  return any(
      host == dom or host.endswith("." + dom) for dom in BLOCKED_DOMAINS
  )


def extract_outbound_links(soup: BeautifulSoup, base_url: str) -> list[dict]:
  """Extrae enlaces salientes (hacia otros dominios independientes) para seguir tirando del hilo."""
  source_domain = get_domain(base_url)
  seen_urls = set()
  outbound = []

  for a in soup.find_all("a", href=True):
    raw_href = a["href"].strip()
    if not raw_href or raw_href.startswith(
        ("#", "mailto:", "javascript:", "tel:")
    ):
      continue

    full_url = urljoin(base_url, raw_href)
    parsed = urlparse(full_url)
    if parsed.scheme not in ("http", "https"):
      continue

    target_domain = get_domain(full_url)
    if not target_domain or target_domain == source_domain:
      continue
    if is_blocked_domain(full_url):
      continue
    if full_url in seen_urls:
      continue

    seen_urls.add(full_url)
    anchor_text = re.sub(r"\s+", " ", a.get_text(strip=True))
    if not anchor_text or len(anchor_text) < 2:
      anchor_text = target_domain

    outbound.append({
        "title": anchor_text[:120],
        "url": full_url,
        "domain": target_domain,
    })

  return outbound


def extract_paragraphs(main_node: BeautifulSoup) -> list[str]:
  """Extrae párrafos reales respetando etiquetas inline (<i>, <em>, <a>) y hard-wraps de los años 90."""
  for br in main_node.find_all("br"):
    br.replace_with("\n\n")

  for tag in main_node.find_all(BLOCK_TAGS):
    tag.insert_before("\n\n")
    tag.insert_after("\n\n")

  raw_text = main_node.get_text(separator=" ")
  blocks = re.split(r"\n\s*\n+", raw_text)

  paragraphs = []
  for block in blocks:
    cleaned = re.sub(r"\s+", " ", block).strip()
    if cleaned:
      paragraphs.append(cleaned)
  return paragraphs


def fetch_and_analyze(url: str, seed: str = "") -> dict:
  """Descarga la página, extrae texto limpio, enlaces salientes y métricas de calidad."""
  if is_blocked_domain(url):
    return {
        "accepted": False,
        "reason": "Dominio comercial/mainstream bloqueado",
    }

  try:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=12,
    )
    response.raise_for_status()
  except requests.RequestException as exc:
    return {"accepted": False, "reason": f"Página caída o inaccesible ({exc})"}

  content_type = response.headers.get("Content-Type", "").lower()
  if content_type and "html" not in content_type and "text" not in content_type:
    return {
        "accepted": False,
        "reason": f"Contenido no es HTML/texto ({content_type})",
    }

  if not response.encoding or response.encoding.lower() == "iso-8859-1":
    response.encoding = response.apparent_encoding

  soup = BeautifulSoup(response.text, "html.parser")

  # Extraer enlaces externos de toda la página antes de limpiar tags (para capturar blogrolls en sidebars)
  outbound_links = extract_outbound_links(soup, url)

  for tag in soup(
      ["script", "style", "nav", "footer", "header", "noscript", "aside"]
  ):
    tag.decompose()

  main_node = soup.find("article") or soup.find("main") or soup.body or soup

  # Calcular texto en enlaces antes de modificar el DOM
  link_chars = sum(
      len(re.sub(r"\s+", " ", a.get_text(strip=True)))
      for a in main_node.find_all("a")
  )

  paragraphs = extract_paragraphs(main_node)
  full_text = "\n\n".join(paragraphs)
  total_chars = sum(len(p) for p in paragraphs)

  if total_chars < MIN_CHAR_LENGTH:
    return {
        "accepted": False,
        "reason": (
            f"Texto demasiado corto ({total_chars} chars < {MIN_CHAR_LENGTH})"
        ),
    }

  # Evaluar densidad de enlaces (para descartar índices, menús y directorios de links)
  link_density = min(link_chars / max(total_chars, 1), 1.0)
  if link_density > MAX_LINK_DENSITY:
    return {
        "accepted": False,
        "reason": (
            "Página índice/navegación (densidad de links:"
            f" {link_density:.0%} > {MAX_LINK_DENSITY:.0%})"
        ),
    }

  # Evaluar densidad de prosa (párrafos reales vs líneas sueltas)
  long_paragraphs = [p for p in paragraphs if len(p) >= LONG_PARAGRAPH_CHARS]
  prose_chars = sum(len(p) for p in long_paragraphs)
  prose_ratio = prose_chars / max(total_chars, 1)

  if (
      len(long_paragraphs) < MIN_LONG_PARAGRAPHS
      or prose_ratio < MIN_PROSE_RATIO
  ):
    return {
        "accepted": False,
        "reason": (
            f"Poca estructura de ensayo ({len(long_paragraphs)} párrafos"
            f" largos, {prose_ratio:.0%} prosa)"
        ),
    }

  # Evaluar frases comerciales/tiendas
  lower_text = full_text.lower()
  for phrase in COMMERCIAL_PHRASES:
    if phrase in lower_text:
      return {
          "accepted": False,
          "reason": f"Detectado contenido comercial ('{phrase}')",
      }

  # Evaluar relevancia temática respecto a la semilla (al menos 2 menciones de términos de la semilla)
  if seed:
    tokens = [t.lower() for t in re.split(r"\W+", seed) if len(t) >= 3]
    if tokens:
      mentions = sum(lower_text.count(token) for token in tokens)
      if mentions < 2:
        return {
            "accepted": False,
            "reason": (
                f"Mención tangencial de la semilla '{seed}' ({mentions}"
                " aparición en el cuerpo)"
            ),
        }

  return {
      "accepted": True,
      "text": full_text,
      "total_chars": total_chars,
      "long_paragraphs": len(long_paragraphs),
      "prose_ratio": prose_ratio,
      "link_density": link_density,
      "outbound_links": outbound_links,
  }


def save_reading_markdown(
    readings_root: Path,
    seed: str,
    title: str,
    url: str,
    engine: str,
    analysis: dict,
) -> Path:
  """Guarda el ensayo rescatado en readings/<semilla>/<titulo>.md con sus links salientes."""
  seed_folder = readings_root / slugify(seed, max_len=50)
  seed_folder.mkdir(parents=True, exist_ok=True)

  file_slug = slugify(title, max_len=65)
  md_path = seed_folder / f"{file_slug}.md"

  domain = get_domain(url)
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
  outbound = analysis.get("outbound_links", [])

  lines = [
      f"# {title}",
      "",
      f"- **URL Original:** {url}",
      f"- **Dominio:** `{domain}`",
      f"- **Semilla de descubrimiento:** `{seed}`",
      f"- **Motor:** {engine}",
      f"- **Fecha de rescate:** {timestamp}",
      (
          f"- **Métricas:** {analysis['total_chars']} caracteres |"
          f" {analysis['long_paragraphs']} párrafos largos | Prosa:"
          f" {analysis['prose_ratio']:.0%} | Densidad de links:"
          f" {analysis['link_density']:.0%}"
      ),
      "",
      "---",
      "",
      "## Texto Rescatado",
      "",
      analysis["text"],
      "",
      "---",
      "",
      f"## Enlaces Salientes para Tirar del Hilo ({len(outbound)})",
      "",
  ]

  if outbound:
    for link in outbound:
      lines.append(f"- [{link['title']}]({link['url']}) (`{link['domain']}`)")
  else:
    lines.append("*No se detectaron enlaces externos independientes.*")

  lines.append("")
  md_path.write_text("\n".join(lines), encoding="utf-8")
  return md_path


def save_seed_trail(
    readings_root: Path, seed: str, all_outbound: list[dict]
) -> Path | None:
  """Guarda un archivo resumen _links_para_explorar.md dentro de la carpeta de la semilla."""
  if not all_outbound:
    return None

  seed_folder = readings_root / slugify(seed, max_len=50)
  seed_folder.mkdir(parents=True, exist_ok=True)
  trail_path = seed_folder / "_links_para_explorar.md"

  seen = set()
  unique_links = []
  for item in all_outbound:
    if item["url"] not in seen:
      seen.add(item["url"])
      unique_links.append(item)

  lines = [
      f"# Hilos Salientes Descubiertos desde `{seed}`",
      "",
      (
          "Enlaces externos encontrados en los ensayos y blogrolls de esta"
          " semilla:"
      ),
      "",
  ]
  for link in unique_links:
    lines.append(
        f"- **[{link['title']}]({link['url']})** — `{link['domain']}` *(visto"
        f" en: {link['source_title']})*"
    )

  lines.append("")
  trail_path.write_text("\n".join(lines), encoding="utf-8")
  return trail_path


def process_seed(seed: str, readings_root: Path, count: int = 6) -> None:
  print(f"\n============================================================")
  print(f"=== [FASE 3] Explorando semilla: '{seed}' ===")
  print(f"============================================================")

  engine, results = search_small_web(seed, count=count)
  print(f"Motor: {engine} | Candidatos iniciales: {len(results)}\n")

  accepted_count = 0
  rejected_count = 0
  seed_outbound: list[dict] = []

  for item in results:
    url = item.get("url", "")
    title = item.get("title", "Sin título").strip()
    analysis = fetch_and_analyze(url, seed=seed)

    if analysis["accepted"]:
      accepted_count += 1
      md_path = save_reading_markdown(
          readings_root=readings_root,
          seed=seed,
          title=title,
          url=url,
          engine=engine,
          analysis=analysis,
      )
      outbound = analysis["outbound_links"]
      for link in outbound:
        seed_outbound.append({**link, "source_title": title})

      rel_path = md_path.relative_to(readings_root.parent)
      print(f"  [GUARDADO #{accepted_count}] {title}")
      print(f"    Archivo: {rel_path}")
      print(f"    URL: {url}")
      print(
          f"    Métricas: {analysis['total_chars']} chars | "
          f"{analysis['long_paragraphs']} párrafos | "
          f"Links salientes rescatados: {len(outbound)}\n"
      )
    else:
      rejected_count += 1
      print(f"  [DESCARTADO] {title} ({url})")
      print(f"    Motivo: {analysis['reason']}\n")

  trail_path = save_seed_trail(readings_root, seed, seed_outbound)
  print(
      f"--> Resumen '{seed}': {accepted_count} ensayos guardados |"
      f" {rejected_count} descartados."
  )
  if trail_path:
    print(
        "    Mapa de enlaces salientes:"
        f" {trail_path.relative_to(readings_root.parent)}\n"
    )


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
      description=(
          "Explorador de ensayos filosóficos y anomalías de la old-web (Fase 3)"
      )
  )
  parser.add_argument(
      "seeds",
      nargs="*",
      help=(
          "Una o varias semillas a buscar (ej. python scout.py 'gnosticism'"
          " 'David Lynch' 'Borges')"
      ),
  )
  parser.add_argument(
      "-r",
      "--random",
      type=int,
      default=1,
      help=(
          "Número de semillas aleatorias de seeds.json a explorar si no se"
          " pasan por argumento (default: 1)"
      ),
  )
  parser.add_argument(
      "-c",
      "--count",
      type=int,
      default=6,
      help="Cantidad máxima de candidatos a analizar por semilla (default: 6)",
  )
  return parser.parse_args()


def main() -> None:
  base_dir = Path(__file__).resolve().parent
  seeds_file = base_dir / "seeds.json"
  readings_root = base_dir / "readings"

  args = parse_args()
  if args.seeds:
    seeds = args.seeds
  else:
    seeds = load_random_seeds(seeds_file, n=args.random)

  print(f"Semillas seleccionadas ({len(seeds)}): {seeds}")
  for seed in seeds:
    process_seed(seed, readings_root=readings_root, count=args.count)


if __name__ == "__main__":
  main()

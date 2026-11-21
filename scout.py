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
WAYBACK_AVAILABLE_URL = "https://archive.org/wayback/available"

USER_AGENT = (
    "DeepestInternetScout/0.4 (+https://github.com/abilbao1/deepest-internet)"
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
    "archive.org",
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
  for _ in range(2):
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
  if ":" in host:
    host = host.split(":", 1)[0]
  return host[4:] if host.startswith("www.") else host


def is_blocked_domain(url: str) -> bool:
  host = get_domain(url)
  return any(
      host == dom or host.endswith("." + dom) for dom in BLOCKED_DOMAINS
  )


def resolve_wayback_snapshot(url: str) -> tuple[str, str, str] | None:
  """Consulta la API de Wayback Machine para rescatar una URL caída.

  Devuelve (public_url, raw_id_url, timestamp) o None si no hay captura.
  """
  try:
    resp = requests.get(
        WAYBACK_AVAILABLE_URL,
        params={"url": url},
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    if not resp.ok:
      return None
    closest = resp.json().get("archived_snapshots", {}).get("closest", {})
    if not closest or not closest.get("available"):
      return None

    timestamp = closest.get("timestamp", "")
    if not timestamp:
      return None

    public_url = f"https://web.archive.org/web/{timestamp}/{url}"
    raw_id_url = f"https://web.archive.org/web/{timestamp}id_/{url}"
    return public_url, raw_id_url, timestamp
  except requests.RequestException:
    return None


def extract_outbound_links(
    soup: BeautifulSoup, original_base_url: str
) -> list[dict]:
  """Extrae enlaces salientes (hacia otros dominios independientes) para seguir tirando del hilo."""
  source_domain = get_domain(original_base_url)
  seen_urls = set()
  outbound = []

  for a in soup.find_all("a", href=True):
    raw_href = a["href"].strip()
    if not raw_href or raw_href.startswith(
        ("#", "mailto:", "javascript:", "tel:")
    ):
      continue

    # Si el enlace viene de un HTML archivado en web.archive.org, limpiar el prefijo
    wb_match = re.match(
        r"^https?://web\.archive\.org/web/\d+(?:id_)?/(https?://.+)$", raw_href
    )
    if wb_match:
      full_url = wb_match.group(1)
    else:
      full_url = urljoin(original_base_url, raw_href)

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


def fetch_html_with_wayback_fallback(url: str) -> dict:
  """Intenta descargar la URL viva; si falla, la rescata automáticamente de Wayback Machine."""
  try:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=8,
    )
    response.raise_for_status()
    return {
        "ok": True,
        "response": response,
        "via_wayback": False,
        "resolved_url": url,
        "wayback_timestamp": None,
    }
  except requests.RequestException as live_exc:
    snapshot = resolve_wayback_snapshot(url)
    if not snapshot:
      return {
          "ok": False,
          "reason": (
              "Página caída y sin copia en Wayback Machine"
              f" ({type(live_exc).__name__})"
          ),
      }

    public_url, raw_id_url, timestamp = snapshot
    try:
      wb_response = requests.get(
          raw_id_url,
          headers={"User-Agent": USER_AGENT},
          timeout=15,
      )
      wb_response.raise_for_status()
      return {
          "ok": True,
          "response": wb_response,
          "via_wayback": True,
          "resolved_url": public_url,
          "wayback_timestamp": timestamp,
      }
    except requests.RequestException as wb_exc:
      return {
          "ok": False,
          "reason": (
              "Página caída y fallo al descargar copia de Wayback"
              f" ({type(wb_exc).__name__})"
          ),
      }


def fetch_and_analyze(
    url: str, seed: str = "", is_chained: bool = False
) -> dict:
  """Descarga la página (viva o desde Wayback Machine), extrae texto limpio, enlaces y métricas."""
  if is_blocked_domain(url):
    return {
        "accepted": False,
        "reason": "Dominio comercial/mainstream bloqueado",
    }

  fetch_res = fetch_html_with_wayback_fallback(url)
  if not fetch_res["ok"]:
    return {"accepted": False, "reason": fetch_res["reason"]}

  response = fetch_res["response"]
  content_type = response.headers.get("Content-Type", "").lower()
  if content_type and "html" not in content_type and "text" not in content_type:
    return {
        "accepted": False,
        "reason": f"Contenido no es HTML/texto ({content_type})",
    }

  if not response.encoding or response.encoding.lower() == "iso-8859-1":
    response.encoding = response.apparent_encoding

  soup = BeautifulSoup(response.text, "html.parser")

  # Soportar <frameset><frame src="..."></frameset> típico de dominios de los años 90 (Tripod, Geocities)
  frame_tag = soup.find("frame", src=True)
  if frame_tag and len(soup.get_text(strip=True)) < 500:
    raw_frame_src = frame_tag["src"].strip()
    wb_frame_m = re.match(
        r"^https?://web\.archive\.org/web/\d+(?:id_)?/(https?://.+)$",
        raw_frame_src,
    )
    frame_url = (
        wb_frame_m.group(1) if wb_frame_m else urljoin(url, raw_frame_src)
    )
    frame_res = fetch_html_with_wayback_fallback(frame_url)
    if frame_res["ok"]:
      fetch_res = frame_res
      response = fetch_res["response"]
      if not response.encoding or response.encoding.lower() == "iso-8859-1":
        response.encoding = response.apparent_encoding
      soup = BeautifulSoup(response.text, "html.parser")

  # Si la página no traía un título real (p. ej. enlace encadenado con anchor genérico), usar <title>
  html_title = ""
  if soup.title and soup.title.string:
    html_title = re.sub(
        r"\s+", " ", html.unescape(soup.title.string)
    ).strip()

  outbound_links = extract_outbound_links(soup, url)

  for tag in soup(
      ["script", "style", "nav", "footer", "header", "noscript", "aside"]
  ):
    tag.decompose()

  main_node = soup.find("article") or soup.find("main") or soup.body or soup

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

  link_density = min(link_chars / max(total_chars, 1), 1.0)
  if link_density > MAX_LINK_DENSITY:
    return {
        "accepted": False,
        "reason": (
            "Página índice/navegación (densidad de links:"
            f" {link_density:.0%} > {MAX_LINK_DENSITY:.0%})"
        ),
    }

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

  lower_text = full_text.lower()
  for phrase in COMMERCIAL_PHRASES:
    if phrase in lower_text:
      return {
          "accepted": False,
          "reason": f"Detectado contenido comercial ('{phrase}')",
      }

  # En búsqueda directa de semilla exigimos al menos 2 menciones; en enlaces encadenados permitimos ramificar
  if seed and not is_chained:
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
      "html_title": html_title,
      "text": full_text,
      "total_chars": total_chars,
      "long_paragraphs": len(long_paragraphs),
      "prose_ratio": prose_ratio,
      "link_density": link_density,
      "outbound_links": outbound_links,
      "via_wayback": fetch_res["via_wayback"],
      "resolved_url": fetch_res["resolved_url"],
      "wayback_timestamp": fetch_res["wayback_timestamp"],
  }


def save_reading_markdown(
    readings_root: Path,
    seed: str,
    title: str,
    original_url: str,
    engine: str,
    analysis: dict,
) -> Path:
  """Guarda el ensayo rescatado en readings/<semilla>/<titulo>.md con sus links salientes."""
  seed_folder = readings_root / slugify(seed, max_len=50)
  seed_folder.mkdir(parents=True, exist_ok=True)

  effective_title = analysis.get("html_title") or title
  file_slug = slugify(effective_title, max_len=65)
  md_path = seed_folder / f"{file_slug}.md"

  domain = get_domain(original_url)
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
  outbound = analysis.get("outbound_links", [])
  via_wayback = analysis.get("via_wayback", False)
  resolved_url = analysis.get("resolved_url", original_url)

  lines = [
      f"# {effective_title}",
      "",
      f"- **URL Funcional:** {resolved_url}",
  ]
  if via_wayback:
    wb_date = (analysis.get("wayback_timestamp") or "")[:8]
    lines.append(
        f"- **URL Original (Caída):** {original_url} *(Rescatada de Wayback"
        f" Machine — captura `{wb_date}`)*"
    )
  lines.extend([
      f"- **Dominio:** `{domain}`",
      f"- **Semilla de descubrimiento:** `{seed}`",
      f"- **Origen:** {engine}",
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
  ])

  if outbound:
    for link in outbound:
      lines.append(f"- [{link['title']}]({link['url']}) (`{link['domain']}`)")
  else:
    lines.append("*No se detectaron enlaces externos independientes.*")

  lines.append("")
  md_path.write_text("\n".join(lines), encoding="utf-8")
  return md_path


def load_seed_state(seed_folder: Path) -> tuple[set[str], list[dict]]:
  """Carga las URLs ya visitadas y la cola de enlaces salientes de una semilla."""
  visited_file = seed_folder / "_visited.json"
  trail_file = seed_folder / "_links_para_explorar.md"

  visited: set[str] = set()
  if visited_file.exists():
    try:
      visited = set(json.loads(visited_file.read_text(encoding="utf-8")))
    except Exception:
      visited = set()
  else:
    # Poblar visited con las URLs originales de los .md ya existentes en la carpeta
    for md_file in seed_folder.glob("*.md"):
      if md_file.name.startswith("_"):
        continue
      content = md_file.read_text(encoding="utf-8", errors="ignore")
      for match in re.findall(
          r"-\s+\*\*URL (?:Original|Funcional).*?:\*\*\s+(https?://\S+)",
          content,
      ):
        visited.add(match.strip())

  queue: list[dict] = []
  seen_in_queue: set[str] = set()
  if trail_file.exists():
    content = trail_file.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"-\s+(?:\[([^\]]+)\]\s+)?\*\*\[([^\]]+)\]\((https?://[^)]+)\)\*\*\s+—\s+`([^`]+)`(?:\s+\*\(visto en:\s+([^)]+)\)\*)?"
    )
    for m in pattern.finditer(content):
      badge, title, url, domain, source_title = (
          m.group(1) or "",
          m.group(2),
          m.group(3),
          m.group(4),
          m.group(5) or "semilla",
      )
      wb_m = re.match(
          r"^https?://web\.archive\.org/web/\d+/(https?://.+)$", url
      )
      orig_url = wb_m.group(1) if wb_m else url
      if orig_url not in seen_in_queue:
        seen_in_queue.add(orig_url)
        queue.append({
            "badge": badge,
            "title": title,
            "url": orig_url,
            "resolved_url": url,
            "domain": domain,
            "source_title": source_title,
        })

  return visited, queue


def save_seed_state(
    seed_folder: Path,
    seed: str,
    visited: set[str],
    queue: list[dict],
    status_map: dict[str, str],
) -> Path | None:
  """Actualiza _visited.json y _links_para_explorar.md con el estado de cada enlace y nuevos hallazgos."""
  seed_folder.mkdir(parents=True, exist_ok=True)
  visited_file = seed_folder / "_visited.json"
  visited_file.write_text(
      json.dumps(sorted(visited), indent=2, ensure_ascii=False),
      encoding="utf-8",
  )

  if not queue:
    return None

  trail_path = seed_folder / "_links_para_explorar.md"
  lines = [
      f"# Hilos Salientes Descubiertos desde `{seed}`",
      "",
      (
          "Enlaces externos encontrados en los ensayos y blogrolls de esta"
          " semilla (se exploran automáticamente al volver a correr la"
          " semilla):"
      ),
      "",
  ]
  for link in queue:
    orig_url = link["url"]
    display_url = link.get("resolved_url") or orig_url
    badge = status_map.get(orig_url) or link.get("badge", "")
    prefix = f"[{badge}] " if badge else ""
    source_title = link.get("source_title", "semilla")
    lines.append(
        f"- {prefix}**[{link['title']}]({display_url})** — `{link['domain']}`"
        f" *(visto en: {source_title})*"
    )

  lines.append("")
  trail_path.write_text("\n".join(lines), encoding="utf-8")
  return trail_path


def process_seed(seed: str, readings_root: Path, count: int = 6) -> None:
  seed_folder = readings_root / slugify(seed, max_len=50)
  visited, queue = load_seed_state(seed_folder)
  pending_links = [item for item in queue if item["url"] not in visited]

  is_chained_mode = seed_folder.exists() and len(pending_links) > 0

  print(f"\n============================================================")
  if is_chained_mode:
    print(
        f"=== [FASE 4] Semilla '{seed}' ya explorada -> TIRANDO DEL HILO ==="
    )
    print(f"============================================================")
    candidates = pending_links[:count]
    engine = "Hilo Encadenado (Links Salientes + Wayback Machine)"
    print(
        f"Enlaces salientes pendientes en cola: {len(pending_links)}"
        f" | Procesando ahora: {len(candidates)}\n"
    )
  else:
    print(
        f"=== [FASE 4] Explorando semilla nueva en buscador: '{seed}' ==="
    )
    print(f"============================================================")
    engine, raw_results = search_small_web(seed, count=count)
    candidates = [item for item in raw_results if item.get("url") not in visited]
    print(f"Motor: {engine} | Candidatos nuevos: {len(candidates)}\n")

  accepted_count = 0
  rejected_count = 0
  wayback_rescues = 0
  status_map: dict[str, str] = {}
  existing_queue_urls = {item["url"] for item in queue}

  for item in candidates:
    url = item.get("url", "")
    title = item.get("title", "Sin título").strip()
    visited.add(url)

    analysis = fetch_and_analyze(
        url, seed=seed, is_chained=is_chained_mode
    )

    if analysis["accepted"]:
      accepted_count += 1
      via_wb = analysis.get("via_wayback", False)
      if via_wb:
        wayback_rescues += 1

      effective_title = analysis.get("html_title") or title
      source_label = (
          f"{engine} [Rescatado de Archive.org]" if via_wb else engine
      )
      md_path = save_reading_markdown(
          readings_root=readings_root,
          seed=seed,
          title=effective_title,
          original_url=url,
          engine=source_label,
          analysis=analysis,
      )

      # Actualizar URL resuelta (p. ej. link funcional de Wayback Machine) en la cola
      for q_item in queue:
        if q_item["url"] == url:
          q_item["resolved_url"] = analysis.get("resolved_url", url)
          q_item["title"] = effective_title
      status_map[url] = (
          "RESCATADO EN ARCHIVE.ORG" if via_wb else "ENSAYO GUARDADO"
      )

      outbound = analysis["outbound_links"]
      new_outbound_added = 0
      for link in outbound:
        if (
            link["url"] not in existing_queue_urls
            and link["url"] not in visited
        ):
          existing_queue_urls.add(link["url"])
          queue.append({
              **link,
              "resolved_url": link["url"],
              "source_title": effective_title,
          })
          new_outbound_added += 1

      rel_path = md_path.relative_to(readings_root.parent)
      wb_tag = " [WAYBACK MACHINE]" if via_wb else ""
      print(f"  [GUARDADO #{accepted_count}]{wb_tag} {effective_title}")
      print(f"    Archivo: {rel_path}")
      print(f"    URL Funcional: {analysis.get('resolved_url', url)}")
      if via_wb:
        print(f"    URL Original (Caída): {url}")
      print(
          f"    Métricas: {analysis['total_chars']} chars | "
          f"{analysis['long_paragraphs']} párrafos | "
          f"Nuevos hilos añadidos: {new_outbound_added}\n"
      )
    else:
      rejected_count += 1
      status_map[url] = "DESCARTADO"
      print(f"  [DESCARTADO] {title} ({url})")
      print(f"    Motivo: {analysis['reason']}\n")

  trail_path = save_seed_state(
      seed_folder, seed, visited, queue, status_map
  )
  remaining = len([item for item in queue if item["url"] not in visited])
  print(
      f"--> Resumen '{seed}': {accepted_count} ensayos guardados"
      f" ({wayback_rescues} rescatados de Archive.org) | {rejected_count}"
      f" descartados | {remaining} hilos pendientes en cola."
  )
  if trail_path:
    print(
        "    Mapa de enlaces actualizado:"
        f" {trail_path.relative_to(readings_root.parent)}\n"
    )


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
      description=(
          "Explorador de ensayos filosóficos y anomalías de la old-web (Fase 4)"
      )
  )
  parser.add_argument(
      "seeds",
      nargs="*",
      help=(
          "Una o varias semillas a buscar o continuar explorando (ej. python"
          " scout.py 'gnosticism')"
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
      help="Cantidad máxima de candidatos o enlaces salientes a analizar por semilla (default: 6)",
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

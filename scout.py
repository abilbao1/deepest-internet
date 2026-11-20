import json
import os
from pathlib import Path
import random
import re
import sys
from urllib.parse import urlparse

# Ensure local .venv site-packages is loaded even when invoked via system python on Windows
VENV_SITE = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
  sys.path.insert(0, str(VENV_SITE))

from bs4 import BeautifulSoup
import requests

MARGINALIA_API_URL = "https://api2.marginalia-search.com/search"
WIBY_API_URL = "https://wiby.me/json/"

USER_AGENT = (
    "DeepestInternetScout/0.2 (+https://github.com/abilbao1/deepest-internet)"
)

# --- Parámetros de Filtrado (Fase 2) ---
MIN_CHAR_LENGTH = 3000
MIN_LONG_PARAGRAPHS = 5
LONG_PARAGRAPH_CHARS = 140
MIN_PROSE_RATIO = 0.50
MAX_LINK_DENSITY = 0.35

BLOCKED_DOMAINS = {
    "amazon.com",
    "youtube.com",
    "wikipedia.org",
    "reddit.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "pinterest.com",
    "ebay.com",
    "goodreads.com",
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


def load_random_seed(seeds_path: Path) -> str:
  with open(seeds_path, "r", encoding="utf-8") as f:
    data = json.load(f)
  all_seeds = [seed for category in data.values() for seed in category]
  return random.choice(all_seeds)


def search_small_web(query: str, count: int = 8) -> tuple[str, list[dict]]:
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

  response = requests.get(
      WIBY_API_URL,
      params={"q": query},
      headers={"User-Agent": USER_AGENT},
      timeout=10,
  )
  response.raise_for_status()
  raw_results = response.json()
  normalized = [
      {
          "url": item.get("URL", ""),
          "title": item.get("Title", "Sin título"),
          "description": item.get("Snippet", ""),
      }
      for item in raw_results[:count]
  ]
  return "Wiby Old-Web JSON API", normalized


def is_blocked_domain(url: str) -> bool:
  host = urlparse(url).netloc.lower()
  return any(
      host == dom or host.endswith("." + dom) for dom in BLOCKED_DOMAINS
  )


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


def fetch_and_analyze(url: str) -> dict:
  """Descarga la página, extrae el texto limpio y calcula métricas de calidad para el filtro."""
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
  link_density = link_chars / max(total_chars, 1)
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

  return {
      "accepted": True,
      "text": full_text,
      "total_chars": total_chars,
      "long_paragraphs": len(long_paragraphs),
      "prose_ratio": prose_ratio,
      "link_density": link_density,
  }


def process_seed(seed: str, count: int = 6) -> None:
  print(f"\n============================================================")
  print(f"=== [FASE 2] Explorando y filtrando semilla: '{seed}' ===")
  print(f"============================================================")

  engine, results = search_small_web(seed, count=count)
  print(f"Motor: {engine} | Candidatos iniciales: {len(results)}\n")

  accepted_count = 0
  rejected_count = 0

  for item in results:
    url = item.get("url", "")
    title = item.get("title", "Sin título").strip()
    analysis = fetch_and_analyze(url)

    if analysis["accepted"]:
      accepted_count += 1
      preview = analysis["text"][:320].replace("\n", " ")
      print(f"  [ACEPTADO #{accepted_count}] {title}")
      print(f"    URL: {url}")
      print(
          f"    Métricas: {analysis['total_chars']} chars | "
          f"{analysis['long_paragraphs']} párrafos | "
          f"Prosa: {analysis['prose_ratio']:.0%} | "
          f"Links: {analysis['link_density']:.0%}"
      )
      print(f"    Extracto: {preview}...\n")
    else:
      rejected_count += 1
      print(f"  [DESCARTADO] {title} ({url})")
      print(f"    Motivo: {analysis['reason']}\n")

  print(
      f"--> Resumen '{seed}': {accepted_count} ensayos aceptados |"
      f" {rejected_count} descartados.\n"
  )


def main() -> None:
  base_dir = Path(__file__).resolve().parent
  seeds_file = base_dir / "seeds.json"

  if len(sys.argv) > 1:
    seeds = sys.argv[1:]
  else:
    seeds = [load_random_seed(seeds_file)]

  for seed in seeds:
    process_seed(seed)


if __name__ == "__main__":
  main()

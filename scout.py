import json
import os
from pathlib import Path
import random
import sys

# Ensure local .venv site-packages is loaded even when invoked via system python on Windows
VENV_SITE = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
  sys.path.insert(0, str(VENV_SITE))

from bs4 import BeautifulSoup
import requests

MARGINALIA_API_URL = "https://api2.marginalia-search.com/search"
WIBY_API_URL = "https://wiby.me/json/"

HEADERS = {
    "User-Agent": "DeepestInternetScout/0.1 (+https://github.com/abilbao1/deepest-internet)",
    "API-Key": os.environ.get("MARGINALIA_API_KEY", "public"),
}


def load_random_seed(seeds_path: Path) -> str:
  with open(seeds_path, "r", encoding="utf-8") as f:
    data = json.load(f)
  all_seeds = [seed for category in data.values() for seed in category]
  return random.choice(all_seeds)


def search_small_web(query: str, count: int = 5) -> tuple[str, list[dict]]:
  """Queries Marginalia API v2 first; falls back to Wiby JSON API if public key rate-limits/times out."""
  try:
    response = requests.get(
        MARGINALIA_API_URL,
        params={"query": query, "count": count},
        headers=HEADERS,
        timeout=8,
    )
    if response.ok:
      payload = response.json()
      results = payload.get("results", [])
      if results:
        return "Marginalia Search API", results
  except requests.RequestException as exc:
    print(
        f"[!] Marginalia API public endpoint no disponible ({exc}). Usando"
        " Wiby JSON API como respaldo..."
    )

  response = requests.get(
      WIBY_API_URL,
      params={"q": query},
      headers={"User-Agent": HEADERS["User-Agent"]},
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


def extract_clean_text(url: str) -> str:
  response = requests.get(
      url,
      headers={"User-Agent": HEADERS["User-Agent"]},
      timeout=12,
  )
  response.raise_for_status()
  soup = BeautifulSoup(response.text, "html.parser")

  for tag in soup(
      ["script", "style", "nav", "footer", "header", "noscript", "aside"]
  ):
    tag.decompose()

  main_node = soup.find("article") or soup.find("main") or soup.body or soup
  lines = [
      line.strip() for line in main_node.get_text(separator="\n").splitlines()
  ]
  clean_lines = [line for line in lines if line]
  return "\n".join(clean_lines)


def main() -> None:
  base_dir = Path(__file__).resolve().parent
  seeds_file = base_dir / "seeds.json"

  if len(sys.argv) > 1:
    seed = " ".join(sys.argv[1:])
  else:
    seed = load_random_seed(seeds_file)

  print(f"=== [FASE 1] Explorando semilla: '{seed}' ===")
  engine, results = search_small_web(seed, count=5)
  print(f"Motor utilizado: {engine}")
  print(f"Resultados obtenidos: {len(results)}\n")

  for idx, item in enumerate(results, start=1):
    url = item.get("url", "")
    title = item.get("title", "Sin título")
    description = item.get("description", "")
    print(f"[{idx}] {title}")
    print(f"    URL: {url}")
    if description:
      print(f"    Resumen: {description[:160]}...")

    try:
      text = extract_clean_text(url)
      preview = text[:450].replace("\n", " ")
      print(f"    Longitud extraída: {len(text)} caracteres")
      print(f"    Extracto: {preview}...\n")
    except Exception as exc:
      print(f"    [!] Error al extraer texto de {url}: {exc}\n")


if __name__ == "__main__":
  main()

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
from deep_translator import MyMemoryTranslator
import requests

MARGINALIA_API_URL = "https://api2.marginalia-search.com/search"
WIBY_API_URL = "https://wiby.me/json/"
WAYBACK_AVAILABLE_URL = "https://archive.org/wayback/available"
GTX_TRANSLATE_URL = "https://clients5.google.com/translate_a/t"

USER_AGENT = (
    "DeepestInternetScout/0.5 (+https://github.com/abilbao1/deepest-internet)"
)

# --- Parámetros de Filtrado (Fase 2) ---
MIN_CHAR_LENGTH = 3000
MIN_LONG_PARAGRAPHS = 5
LONG_PARAGRAPH_CHARS = 140
MIN_PROSE_RATIO = 0.50
MAX_LINK_DENSITY = 0.35
TRANSLATE_CHUNK_MAX_CHARS = 3800

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


def load_glossary(glossary_path: Path) -> list[tuple[re.Pattern, str]]:
  """Carga glossary.json ordenado de términos más largos a más cortos."""
  if not glossary_path.exists():
    return []
  with open(glossary_path, "r", encoding="utf-8") as f:
    raw_map: dict[str, str] = json.load(f)
  compiled = []
  for term, replacement in sorted(raw_map.items(), key=lambda x: -len(x[0])):
    pattern = re.compile(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)
    compiled.append((pattern, replacement))
  return compiled


def apply_glossary(text: str, glossary: list[tuple[re.Pattern, str]]) -> str:
  for pattern, replacement in glossary:
    text = pattern.sub(replacement, text)
  return text


def translate_chunk(
    chunk: str, glossary: list[tuple[re.Pattern, str]]
) -> str:
  """Traduce un bloque de texto de inglés a español aplicando primero el glosario filosófico."""
  prepared = apply_glossary(chunk, glossary)
  try:
    resp = requests.post(
        GTX_TRANSLATE_URL,
        params={"client": "dict-chrome-ex", "sl": "en", "tl": "es"},
        data={"q": prepared},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=12,
    )
    if resp.ok:
      data = resp.json()
      if isinstance(data, list) and data:
        return str(data[0]).strip()
  except Exception:
    pass

  # Fallback a MyMemoryTranslator de deep-translator (límite 500 chars por llamada)
  try:
    translator = MyMemoryTranslator(source="en-GB", target="es-ES")
    if len(prepared) <= 490:
      return translator.translate(prepared)
  except Exception:
    pass

  return prepared


def translate_essay(
    full_text: str, glossary: list[tuple[re.Pattern, str]]
) -> str:
  """Divide el ensayo en bloques de párrafos y los traduce al español preservando el formato."""
  paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
  chunks: list[str] = []
  current_batch: list[str] = []
  current_len = 0

  for p in paragraphs:
    if current_len + len(p) + 2 > TRANSLATE_CHUNK_MAX_CHARS and current_batch:
      chunks.append("\n\n".join(current_batch))
      current_batch = [p]
      current_len = len(p)
    else:
      current_batch.append(p)
      current_len += len(p) + 2

  if current_batch:
    chunks.append("\n\n".join(current_batch))

  translated_chunks: list[str] = []
  for chunk in chunks:
    translated_chunks.append(translate_chunk(chunk, glossary))
    if len(chunks) > 1:
      time.sleep(0.25)

  return "\n\n".join(translated_chunks)


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
  """Consulta la API de Wayback Machine para rescatar una URL caída."""
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

  if seed and not is_chained:
    tokens = [t.lower() for t in re.split(r"\W+", seed) if len(t) >= 3]
    if tokens:
      missing = [t for t in tokens if lower_text.count(t) == 0]
      mentions = sum(lower_text.count(token) for token in tokens)
      if missing or mentions < 2:
        return {
            "accepted": False,
            "reason": (
                f"Mención insuficiente de la semilla '{seed}' (faltan:"
                f" {missing}, total menciones: {mentions})"
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
    glossary: list[tuple[re.Pattern, str]],
) -> Path:
  """Guarda el ensayo rescatado y traducido al español en readings/<semilla>/<titulo>.md."""
  seed_folder = readings_root / slugify(seed, max_len=50)
  seed_folder.mkdir(parents=True, exist_ok=True)

  effective_title = analysis.get("html_title") or title
  file_slug = slugify(effective_title, max_len=65)
  md_path = seed_folder / f"{file_slug}.md"

  translated_title = translate_chunk(effective_title, glossary)
  translated_body = translate_essay(analysis["text"], glossary)

  domain = get_domain(original_url)
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
  outbound = analysis.get("outbound_links", [])
  via_wayback = analysis.get("via_wayback", False)
  resolved_url = analysis.get("resolved_url", original_url)

  lines = [
      f"# {translated_title}",
      f"*(Título original: {effective_title})*",
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
      "## Texto en Español (Traducción con Glosario Filosófico)",
      "",
      translated_body,
      "",
      "---",
      "",
      "<details>",
      "<summary>Ver texto original en inglés</summary>",
      "",
      analysis["text"],
      "",
      "</details>",
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


def translate_existing_markdown_file(
    md_path: Path, glossary: list[tuple[re.Pattern, str]]
) -> bool:
  """Traduce al español un archivo .md rescatado en fases previas si aún no está traducido."""
  content = md_path.read_text(encoding="utf-8")
  if "## Texto en Español" in content:
    return False

  marker = "## Texto Rescatado\n\n"
  end_marker = "\n\n---\n\n## Enlaces Salientes"
  if marker not in content or end_marker not in content:
    return False

  header_part, rest = content.split(marker, 1)
  english_body, footer_part = rest.split(end_marker, 1)

  # Traducir también el título # ...
  header_lines = header_part.splitlines()
  if header_lines and header_lines[0].startswith("# "):
    orig_title = header_lines[0][2:].strip()
    es_title = translate_chunk(orig_title, glossary)
    header_lines[0] = f"# {es_title}\n*(Título original: {orig_title})*"
    header_part = "\n".join(header_lines) + "\n\n"

  es_body = translate_essay(english_body, glossary)

  new_content = (
      f"{header_part}## Texto en Español (Traducción con Glosario Filosófico)\n\n"
      f"{es_body}\n\n---\n\n"
      f"<details>\n<summary>Ver texto original en inglés</summary>\n\n"
      f"{english_body}\n\n</details>"
      f"{end_marker}{footer_part}"
  )
  md_path.write_text(new_content, encoding="utf-8")
  return True


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


def process_seed(
    seed: str,
    readings_root: Path,
    glossary: list[tuple[re.Pattern, str]],
    count: int = 6,
) -> None:
  seed_folder = readings_root / slugify(seed, max_len=50)
  visited, queue = load_seed_state(seed_folder)
  pending_links = [item for item in queue if item["url"] not in visited]

  is_chained_mode = seed_folder.exists() and len(pending_links) > 0

  print(f"\n============================================================")
  if is_chained_mode:
    print(
        f"=== [FASE 5] Semilla '{seed}' ya explorada -> TIRANDO DEL HILO + TRADUCCIÓN ==="
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
        f"=== [FASE 5] Explorando y traduciendo semilla: '{seed}' ==="
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
      print(f"  [TRADUCIENDO CON GLOSARIO] {effective_title}...")
      md_path = save_reading_markdown(
          readings_root=readings_root,
          seed=seed,
          title=effective_title,
          original_url=url,
          engine=source_label,
          analysis=analysis,
          glossary=glossary,
      )

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
      print(f"  [GUARDADO EN ESPAÑOL #{accepted_count}]{wb_tag} {effective_title}")
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
      f"--> Resumen '{seed}': {accepted_count} ensayos traducidos y guardados"
      f" ({wayback_rescues} de Archive.org) | {rejected_count} descartados |"
      f" {remaining} hilos pendientes en cola."
  )
  if trail_path:
    print(
        "    Mapa de enlaces actualizado:"
        f" {trail_path.relative_to(readings_root.parent)}\n"
    )


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
      description=(
          "Explorador y traductor filosófico de anomalías de la old-web (Fase 5)"
      )
  )
  parser.add_argument(
      "seeds",
      nargs="*",
      help="Una o varias semillas a buscar o continuar explorando",
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
      default=5,
      help=(
          "Cantidad máxima de candidatos o enlaces salientes a analizar por"
          " semilla (default: 5)"
      ),
  )
  parser.add_argument(
      "--translate-existing",
      action="store_true",
      help=(
          "Traduce al español los archivos .md de readings/ que fueron"
          " rescatados en fases previas"
      ),
  )
  parser.add_argument(
      "--collide",
      action="store_true",
      help=(
          "Choca automáticamente 2 semillas de categorías distintas de"
          " seeds.json en una misma búsqueda"
      ),
  )
  return parser.parse_args()


def pick_colliding_seeds(seeds_path: Path, max_attempts: int = 12) -> str:
  """Elige 2 semillas de categorías distintas que tengan intersección real en el buscador."""
  with open(seeds_path, "r", encoding="utf-8") as f:
    data: dict[str, list[str]] = json.load(f)
  categories = list(data.keys())

  for _ in range(max_attempts):
    cat1, cat2 = random.sample(categories, 2)
    s1 = random.choice(data[cat1]).split()[-1]
    s2 = random.choice(data[cat2]).split()[-1]
    combo = f"{s1} {s2}"
    _, results = search_small_web(combo, count=3)
    if results:
      return combo
  return "Wittgenstein Zen"


def main() -> None:
  base_dir = Path(__file__).resolve().parent
  seeds_file = base_dir / "seeds.json"
  glossary_file = base_dir / "glossary.json"
  readings_root = base_dir / "readings"

  glossary = load_glossary(glossary_file)
  args = parse_args()

  if args.translate_existing and readings_root.exists():
    print("=== Traduciendo ensayos existentes en readings/ ===")
    for md_file in sorted(readings_root.rglob("*.md")):
      if md_file.name.startswith("_"):
        continue
      if translate_existing_markdown_file(md_file, glossary):
        print(f"  [TRADUCIDO] {md_file.relative_to(base_dir)}")
    if not args.seeds:
      return

  if args.seeds:
    seeds = args.seeds
  elif args.collide:
    seeds = [pick_colliding_seeds(seeds_file)]
  else:
    seeds = load_random_seeds(seeds_file, n=args.random)

  print(f"Semillas seleccionadas ({len(seeds)}): {seeds}")
  for seed in seeds:
    process_seed(
        seed, readings_root=readings_root, glossary=glossary, count=args.count
    )


if __name__ == "__main__":
  main()

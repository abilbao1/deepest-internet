from pathlib import Path
import re
import sys

# Ensure local .venv site-packages is loaded
VENV_SITE = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
  sys.path.insert(0, str(VENV_SITE))

import typst


def escape_typst(text: str) -> str:
  """Escapa caracteres especiales de Typst y convierte *cursivas* de Markdown a _cursivas_ de Typst."""
  for ch in ["\\", "#", "$", "@", "<", ">", "_"]:
    text = text.replace(ch, "\\" + ch)
  # Convertir *cursiva* de Markdown en _cursiva_ de Typst
  text = re.sub(r"\*([^*\n]+)\*", r"_\1_", text)
  text = text.replace("*", "\\*")
  return text


def parse_markdown_essay(md_path: Path) -> dict:
  content = md_path.read_text(encoding="utf-8")

  title = md_path.stem
  orig_title = ""
  lines = content.splitlines()
  if lines and lines[0].startswith("# "):
    title = lines[0][2:].strip()
  if len(lines) > 1 and lines[1].startswith("*(Título original:"):
    orig_title = lines[1].replace("*(Título original:", "").rstrip(")*").strip()

  def find_meta(label: str) -> str:
    m = re.search(rf"-\s+\*\*{label}:\*\*\s+(.+)", content)
    return m.group(1).strip() if m else ""

  url = find_meta("URL Funcional") or find_meta("URL Original")
  domain = find_meta("Dominio").strip("`")
  seed = find_meta("Semilla de descubrimiento").strip("`")
  license_note = find_meta("Estado Editorial / Licencia")

  marker = "## Texto en Español"
  if marker in content:
    after = content.split(marker, 1)[1]
    # Saltar el resto de la línea del encabezado
    after = after.split("\n", 1)[1] if "\n" in after else after
    body = after.split("\n---\n", 1)[0].strip()
  elif "## Texto Rescatado" in content:
    after = content.split("## Texto Rescatado", 1)[1]
    after = after.split("\n", 1)[1] if "\n" in after else after
    body = after.split("\n---\n", 1)[0].strip()
  else:
    body = content

  return {
      "title": title,
      "orig_title": orig_title,
      "url": url,
      "domain": domain,
      "seed": seed,
      "license_note": license_note,
      "body": body,
  }


def build_typst_source(meta: dict) -> str:
  title = escape_typst(meta["title"])
  orig_title = escape_typst(meta["orig_title"])
  domain = escape_typst(meta["domain"])
  seed = escape_typst(meta["seed"])
  url = escape_typst(meta["url"])
  license_note = escape_typst(meta["license_note"])

  raw_blocks = [b.strip() for b in re.split(r"\n\s*\n+", meta["body"]) if b.strip()]
  body_typst_blocks: list[str] = []
  first_prose_done = False

  for block in raw_blocks:
    if block.startswith("### "):
      heading_txt = escape_typst(block[4:].strip())
      body_typst_blocks.append(
          f"#v(1.2em)\n#align(center)[#text(fill: rgb(\"#7a2821\"), size: 12pt,"
          f" weight: \"bold\", tracking: 0.08em)[— {heading_txt} —]]\n#v(0.5em)"
      )
    elif block.startswith("> "):
      quote_txt = escape_typst(block[2:].strip())
      body_typst_blocks.append(
          f"#pad(left: 1.5em, right: 1em)[#text(style: \"italic\", fill:"
          f" rgb(\"#3d3833\"))[{quote_txt}]]"
      )
    else:
      escaped_p = escape_typst(block)
      if not first_prose_done and len(escaped_p) > 80:
        first_prose_done = True
        body_typst_blocks.append(
            f'#dropcap(height: 3, gap: 6pt, weight: "bold")[{escaped_p}]'
        )
      else:
        body_typst_blocks.append(escaped_p)

  joined_body = "\n\n".join(body_typst_blocks)

  return f"""#import "@preview/droplet:0.3.1": dropcap

#set page(
  paper: "a5",
  fill: rgb("#fbf8f1"),
  margin: (top: 2.2cm, bottom: 2.2cm, left: 2cm, right: 2cm),
  header: context {{
    if counter(page).get().first() > 1 [
      #set text(font: "Georgia", size: 8pt, fill: rgb("#7d756c"), style: "italic")
      #smallcaps[{domain}] #h(1fr) Semilla: {seed}
      #v(2pt)
      #line(length: 100%, stroke: 0.4pt + rgb("#dcd4c6"))
    ]
  }},
  footer: context [
    #set text(font: "Georgia", size: 8.5pt, fill: rgb("#7d756c"))
    #align(center)[— #counter(page).display("1") —]
  ]
)

#set text(
  font: "Georgia",
  size: 10.2pt,
  fill: rgb("#1d1b18"),
  lang: "es",
)

#set par(
  justify: true,
  leading: 0.78em,
  spacing: 1.35em,
)

// --- Cabecera Editorial ---
#align(center)[
  #set par(justify: false)
  #set text(hyphenate: false)
  #text(size: 8.5pt, fill: rgb("#7a2821"), tracking: 0.18em, weight: "bold")[
    ARCHIVO DEEPEST INTERNET · SEMILLA: #upper[{seed}]
  ]
  #v(0.6em)
  #text(size: 18pt, weight: "bold", fill: rgb("#161412"))[{title}]
  #v(0.3em)
  #if "{orig_title}" != "" [
    #text(size: 10pt, style: "italic", fill: rgb("#635c54"))[({orig_title})]
  ]
  #v(0.8em)
  #line(length: 45%, stroke: 0.8pt + rgb("#7a2821"))
  #v(0.4em)
  #text(size: 8pt, fill: rgb("#635c54"))[
    Fuente original: #raw("{url}")
  ]
  #if "{license_note}" != "" [
    #linebreak()
    #text(size: 7.5pt, fill: rgb("#7a2821"), style: "italic")[{license_note}]
  ]
  #v(1.2em)
]

{joined_body}

#v(2em)
#align(center)[
  #line(length: 30%, stroke: 0.5pt + rgb("#7a2821"))
  #v(0.5em)
  #text(size: 8pt, style: "italic", fill: rgb("#635c54"))[
    Rescatado, traducido y curado en Deepest Internet
  ]
]
"""


def main() -> None:
  if len(sys.argv) < 2:
    print("Uso: python publish.py <ruta-al-archivo.md>")
    sys.exit(1)

  base_dir = Path(__file__).resolve().parent
  md_path = Path(sys.argv[1]).resolve()
  if not md_path.exists():
    print(f"[!] No existe el archivo: {md_path}")
    sys.exit(1)

  out_dir = base_dir / "published"
  out_dir.mkdir(parents=True, exist_ok=True)

  meta = parse_markdown_essay(md_path)
  typst_src = build_typst_source(meta)

  typ_path = out_dir / f"{md_path.stem}.typ"
  pdf_path = out_dir / f"{md_path.stem}.pdf"

  typ_path.write_text(typst_src, encoding="utf-8")
  pdf_bytes = typst.compile(str(typ_path))
  pdf_path.write_bytes(pdf_bytes)

  print(f"=== [MAQUETACIÓN TYPST COMPLETADA] ===")
  print(f"  Título: {meta['title']}")
  print(f"  Fuente Typst: {typ_path.relative_to(base_dir)}")
  print(f"  PDF Editorial: {pdf_path.relative_to(base_dir)} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
  main()

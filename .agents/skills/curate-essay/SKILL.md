---
name: curate-essay
description: >-
  Revisa, corrige y maqueta en PDF editorial (con Typst Universe) un ensayo filosófico
  rescatado en la carpeta readings/. Activa esta skill cuando el usuario pida revisar,
  curar, pulir la traducción, limpiar erratas de scraping o preparar para publicar/Twitter
  un ensayo de readings/.
---

# Skill: Curaduría Filológica y Edición en Typst (`curate-essay`)

Esta skill guía al agente para actuar como **editor filológico y maquetador** sobre un ensayo rescatado por `scout.py` en la carpeta `readings/`.

## Procedimiento Paso a Paso

### Paso 1: Lectura Bilingüe y Glosario
1. Lee el archivo `.md` indicado por el usuario dentro de `readings/<semilla>/<ensayo>.md`.
2. Lee `glossary.json` en la raíz del proyecto para tener presentes los términos filosóficos y esotéricos protegidos.
3. Examina en paralelo la sección `## Texto en Español (Traducción con Glosario Filosófico)` y el bloque `<details><summary>Ver texto original en inglés</summary>`.

### Paso 2: Limpieza de Erratas de Scraping y Revisión de Traducción
Edita la sección `## Texto en Español` del archivo `.md` aplicando estrictamente estas reglas:
1. **Eliminar basura de scraping:** Borra menús de navegación residuales al inicio o final (ej. `"Archivo de Gnosis | Biblioteca | Librería | Índice..."`), cabeceras de sitio repetidas, contadores de visitas o enlaces rotos sueltos.
2. **Estructura de secciones:** Si el ensayo tiene subtítulos internos que quedaron como líneas sueltas de texto (ej. `El cosmos`, `La deidad`, `La humanidad`, o secciones numeradas `1.`, `2.`), conviértelos en subtítulos Markdown (`### Subtítulo`) para que el maquetador Typst los formatee como secciones editoriales.
3. **Pulido sintáctico y conceptual (Prohibido resumir):**
   - Coteja con el original en inglés para corregir calcos sintácticos, preposiciones mal traducidas o frases robóticas del traductor automático.
   - Respeta rigurosamente los términos de `glossary.json` (*Lo Uno*, *Hipóstasis*, *Demiurgo*, *Arcontes*, *Gnosis*, *Pléroma*, *goce [jouissance]*, *Dasein*, *hauntología*, etc.).
   - **REGLA ESTRICTA:** Jamás resumas, acortes ni elimines párrafos del ensayo original.

### Paso 3: Evaluación Legal para Publicación (Twitter/X)
Añade en la cabecera de metadatos del `.md` una línea `- **Estado Editorial / Licencia:**` clasificando el texto en uno de estos tres casos:
- **Dominio Público:** Autor clásico y traducción inglesa anterior a 1930 (ej. Plotino trad. MacKenna) -> *Apto para publicar completo*.
- **Licencia Abierta / Copyleft:** El texto incluye nota explícita permitiendo su copia/redistribución con atribución -> *Apto para publicar completo citando fuente*.
- **Copyright Estándar (Derecho de Cita):** Artículo contemporáneo sin licencia abierta -> *Para Twitter/X se recomienda publicar selección de fragmentos/citas comentadas con enlace al original*.

### Paso 4: Compilación Editorial a PDF con Typst Universe (`publish.py`)
Una vez guardado el `.md` revisado, ejecuta el compilador editorial:

```powershell
C:\Python314\python.exe publish.py "<ruta-al-archivo.md>"
```

Esto generará en la carpeta `published/`:
- `published/<slug>.typ` (Código fuente Typst importando `@preview/droplet:0.3.1` de Typst Universe).
- `published/<slug>.pdf` (Cuaderno filosófico en PDF listo para leer o capturar láminas para Twitter).

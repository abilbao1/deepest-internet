# Instrucciones y Filosofía de Desarrollo

## 1. Reglas de Oro del Proyecto
- **Desarrollo Vertical (Vertical Slicing):** Cada fase debe entregar un flujo completo de punta a punta que funcione y devuelva resultados reales. Nada de construir capas abstractas "por si acaso".
- **Tests y Validaciones Mínimas:** Durante el desarrollo de una fase, solo se hacen las comprobaciones mínimas necesarias para verificar que el código corre y cumple el objetivo de la fase. Cero sobre-ingeniería.
- **Auditoría de Fin de Fase:** Al terminar el desarrollo de una fase, se frena y se audita: revisar el código escrito, limpiar basura/código muerto, verificar los textos obtenidos y confirmar que cumple el objetivo.
- **Flujo Git (`main`):** Se trabaja directamente sobre la rama `main`. Una vez superada la auditoría de cada fase, se hace `git commit` y `git push` antes de pasar a la siguiente.

---

## 2. Stack Tecnológico (Python vs Java)
Se elige **Python** por encima de Java por pragmatismo puro:
- Levantar el repositorio de *MarginaliaSearch* en Java implica correr un motor de búsqueda completo (índices Lucene, contenedores pesados y mucha RAM).
- Con **Python**, consultamos directamente a Marginalia / Wiby a partir de nuestras semillas/queries, descargamos los enlaces con `requests`, extraemos párrafos y enlaces con `BeautifulSoup`, rescatamos enlaces caídos con la API de *Wayback Machine (Archive.org)* y traducimos textos con glosario filosófico protegido.

---

## 3. Hoja de Ruta (Fases Verticales)

### Fase 1: Conexión con Marginalia/Wiby y Extracción Cruda (Vertical Slice Mínimo) [COMPLETADA]
- **Objetivo:** Dado un término o semilla, consultar el buscador de la old-web, obtener URLs, descargar el texto limpio del artículo y mostrarlo en local.
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 2: Lógica de Filtrado Básico [COMPLETADA]
- **Objetivo:** Descartar ruido evidente (páginas sin texto, listados de links vacíos, textos demasiado cortos que no son ensayos/posts, o dominios comerciales).
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 3: Salida Legible por Carpetas y Extracción de Blogrolls [COMPLETADA]
- **Objetivo:** Guardar los textos rescatados en carpetas `readings/<semilla>/<titulo>.md` y extraer enlaces salientes en `_links_para_explorar.md`.
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 4: Exploración Encadenada y Rescate en Wayback Machine [COMPLETADA]
- **Objetivo:** Si se selecciona una semilla que ya fue examinada (ya existe su carpeta y `_links_para_explorar.md`), partir de sus enlaces salientes pendientes en vez de buscar de cero. Si un enlace está caído en la web viva, rescatarlo automáticamente desde la API de *Wayback Machine (`archive.org`)* y registrar la URL histórica viva.
- **Validación:** Re-ejecutar `"gnosticism"` para que explore sus enlaces salientes (incluyendo los caídos) y verifique el rescate desde Archive.org.
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 5: Traducción Automática al Español con Glosario Filosófico [COMPLETADA]
- **Objetivo:** Traducir los ensayos rescatados al español usando `deep-translator` combinado con un glosario filosófico (`glossary.json`) que proteja y preserve conceptos técnicos complejos (continentales, gnósticos, esotéricos).
- **Validación:** Traducir ensayos rescatados y auditar la fidelidad conceptual y legibilidad en español.
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 6: Curaduría Filológica con Skill del Proyecto y Edición PDF en Typst Universe [COMPLETADA]
- **Objetivo:** Disponer de una Skill propia del proyecto (`.agents/skills/curate-essay/SKILL.md`) para que el agente revise la traducción, limpie erratas de scraping, clasifique la licencia legal para Twitter/X y compile el ensayo en un cuaderno PDF editorial (`publish.py`) usando `@preview/droplet:0.3.1` de *Typst Universe*. Incluye además el modo `--collide` en `scout.py` para chocar 2 semillas de categorías distintas.
- **Validación:** Curar y compilar a PDF el ensayo *La cosmovisión gnóstica* y validar una colisión de dos semillas dispares (`"Wittgenstein Zen"`).
- **Cierre:** Auditoría -> Commit & Push a `main`.

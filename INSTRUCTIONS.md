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
- Con **Python**, consultamos directamente a Marginalia (vía su API/búsqueda web) a partir de nuestras semillas/queries (ej. *k-punk*, Mark Fisher, teoría cultural, blogs cyberpunk), descargamos los enlaces con `httpx`/`requests` y extraemos el texto limpio de los artículos con `trafilatura` en pocas líneas de código.

---

## 3. Hoja de Ruta (Fases Verticales)

### Fase 1: Conexión con Marginalia y Extracción Cruda (Vertical Slice Mínimo)
- **Objetivo:** Dado un término o semilla (ej. `"k-punk"`, `"Mark Fisher"`, `"hauntology"`), consultar Marginalia, obtener un puñado de URLs, descargar el texto limpio del artículo y guardarlo/mostrarlo en local.
- **Validación:** Ejecutar el script con 1 query y verificar que descarga textos legibles.
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 2: Lógica de Filtrado Básico
- **Objetivo:** Descartar ruido evidente (páginas sin texto, listados de links vacíos, textos demasiado cortos que no son ensayos/posts, o dominios que no nos interesan).
- **Validación:** Comparar la salida antes y después del filtro con 2-3 semillas culturales/filosóficas.
- **Cierre:** Auditoría -> Commit & Push a `main`.

### Fase 3: Salida Legible y Exploración de Blogrolls (Iteración)
- **Objetivo:** Guardar los textos rescatados en archivos Markdown limpios (con su URL original y título) listos para leer, y extraer enlaces salientes interesantes para realimentar futuras búsquedas.
- **Validación:** Revisar la carpeta de salida con los primeros textos rescatados.
- **Cierre:** Auditoría -> Commit & Push a `main`.

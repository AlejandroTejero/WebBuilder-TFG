# Mejoras propuestas para WebBuilder
## Guía práctica de implementación para los próximos días

Este documento recoge las mejoras más importantes detectadas en el proyecto **WebBuilder**, con foco en la calidad de generación, obediencia al prompt del usuario, coherencia visual, robustez técnica y facilidad de refinamiento.

La idea es que te sirva como **hoja de ruta realista** para ir implementando cambios poco a poco, sin perderte y sin tocar todo a la vez.

---

# 1. Objetivo general

Ahora mismo el sistema ya genera webs funcionales, pero todavía falla en varios puntos típicos:

- a veces **entiende el prompt**, pero no lo ejecuta con precisión
- mezcla demasiado los **defaults internos** con la estética que pide el usuario
- puede producir **HTML/Tailwind válido a medias**
- trata todos los datasets y todas las imágenes casi igual
- le cuesta reutilizar patrones visuales de manera consistente
- en refinamiento, puede arreglar una cosa pero romper otra

Por eso, las mejoras deben ir orientadas a cinco metas:

1. **Obedecer mejor el prompt del usuario**
2. **Reducir errores técnicos de generación**
3. **Reutilizar patrones consistentes**
4. **Aprovechar mejor la semántica de los datos**
5. **Hacer el refinamiento más preciso y menos destructivo**

---

# 2. Orden recomendado de implementación

Para no tocar demasiadas cosas a la vez, este sería un orden sensato:

## Fase 1 — mejoras de impacto inmediato
1. Sistema base de diseño y tema
2. Priorización explícita del prompt del usuario
3. Validación automática post-generación

## Fase 2 — mejoras de calidad estructural
4. Librería de componentes de ejemplo
5. Mapeo semántico de campos
6. Skills modulares por tarea

## Fase 3 — mejoras de sofisticación visual
7. Estrategias de tratamiento de imagen
8. Patrones por tipo de sitio
9. Refinamiento incremental

## Fase 4 — mejora de trazabilidad
10. Snapshots y versionado de generaciones

---

# 3. Mejora 1 — Sistema base de diseño y tema

## Qué problema resuelve

Ahora mismo el LLM genera muchas decisiones visuales directamente en el HTML, por ejemplo clases Tailwind con colores hex, variantes de cards, bordes, sombras y tipografía.

Eso provoca varios problemas:

- clases inválidas como `bg-#111111`
- inconsistencia entre páginas
- repetición de decisiones visuales
- dificultad para refinar solo el tema sin rehacer toda la UI

## Idea principal

Crear una **base de diseño centralizada**, con tokens o clases semánticas, para que el LLM reutilice una estructura estable en vez de inventar estilos cada vez.

## Qué debería incluir

### Colores
- fondo principal
- superficie
- borde
- texto principal
- texto secundario
- color de acento
- success
- danger
- muted

### Tipografía
- fuente de títulos
- fuente de cuerpo
- tamaños base
- pesos frecuentes

### Layout
- anchos de contenedor
- paddings base
- spacing vertical
- radios
- sombras

### Componentes base
- cards
- badges
- botones
- paneles
- tablas de detalle
- inputs
- paginación

## Enfoque recomendado

En lugar de obligar al modelo a escribir siempre clases Tailwind con hex arbitrarios, conviene darle clases más semánticas, por ejemplo:

- `bg-site`
- `bg-surface`
- `text-site`
- `text-muted`
- `border-site`
- `accent-link`
- `card-base`
- `badge-success`
- `badge-danger`

Luego esas clases se resuelven en tu CSS/Tailwind base.

## Cómo implementarlo

### Opción A — clases CSS propias
Crear un archivo base tipo `theme.css` con utilidades semánticas.

Ventaja:
- muy simple de controlar

### Opción B — tokens + Tailwind config
Definir el tema desde `tailwind.config.js` y exponer nombres estables.

Ventaja:
- más escalable
- más limpio si luego generas varias variantes de tema

## Resultado esperado

- menos errores de clases
- coherencia visual automática
- refinamientos más fáciles
- posibilidad de cambiar el tema sin reescribir toda la plantilla

---

# 4. Mejora 2 — Priorización explícita de instrucciones

## Qué problema resuelve

El sistema recibe varias fuentes de “verdad” al mismo tiempo:

- prompt del usuario
- reglas internas del generador
- sugerencias del dataset
- ejemplos visuales
- defaults del sistema

Si no se define una jerarquía clara, el LLM mezcla todo y aparecen casos como:

- el usuario pide estilo editorial
- el dataset tiene imagen
- los ejemplos empujan a grid visual
- el resultado termina siendo híbrido y poco fiel

## Idea principal

Formalizar una jerarquía explícita de prioridades.

## Jerarquía recomendada

1. **Prompt del usuario**
2. **Restricciones funcionales del proyecto**
3. **Requisitos estructurales de la página**
4. **Sugerencias semánticas del dataset**
5. **Defaults visuales**
6. **Detalles decorativos**

## Cómo reflejarlo en prompts

Incluir reglas como:

- “PRIORIDAD ABSOLUTA: la instrucción del usuario manda sobre cualquier convención visual por defecto.”
- “Las sugerencias del dataset nunca pueden contradecir el prompt.”
- “Las guías visuales son subordinadas a la estética pedida por el usuario.”

## Dónde aplicarlo

- generación del plan
- construcción del prompt final
- enriquecimiento con datos
- refinamiento posterior

## Resultado esperado

- el sistema deja de “pisar” al usuario
- más fidelidad estética
- menos resultados genéricos

---

# 5. Mejora 3 — Validación automática post-generación

## Qué problema resuelve

Aunque el LLM genere algo “bastante bien”, puede dejar errores concretos:

- clases Tailwind inválidas
- URLs Django incorrectas
- variables de template no existentes
- estructuras incoherentes con el prompt
- decisiones visuales que contradicen instrucciones

## Idea principal

Añadir una fase automática entre:

**generar → validar → corregir → empaquetar**

## Qué validar

### Validación técnica
- clases Tailwind mal formadas
- sintaxis HTML básica
- sintaxis Django template
- `{% url %}` con nombres existentes
- variables usadas en plantilla que no llegan en contexto

### Validación funcional
- si el usuario pidió “sin imágenes”, comprobar que no haya imágenes en listados
- si pidió “grid 4 columnas”, revisar que aparezca la estructura adecuada
- si pidió “sin precios”, revisar que no se haya metido price o CTA comercial

### Validación visual mínima
- comprobar presencia del color de acento
- comprobar densidad visual esperada
- detectar hero demasiado invasivo si pidió estilo sobrio

## Cómo implementarlo

### Nivel 1 — reglas simples con regex / parser
Muy útil para empezar:
- detectar `bg-#`
- detectar `text-#`
- detectar placeholders indeseados
- detectar strings prohibidos

### Nivel 2 — chequeo estructural
- analizar templates
- comprobar bloques
- revisar si ciertas secciones existen o no

### Nivel 3 — validación semántica por prompt
- extraer condiciones del prompt y compararlas con el HTML generado

## Resultado esperado

- menos errores “tontos”
- más robustez
- más confianza en el refinamiento

---

# 6. Mejora 4 — Librería de componentes de ejemplo

## Qué problema resuelve

Ahora el generador parece apoyarse demasiado en ficheros completos o en patrones globales.

Eso hace que:
- ciertas partes salgan bien y otras no
- repita soluciones pobres
- le cueste adaptar una misma página a estilos distintos

## Idea principal

Crear una **biblioteca modular de componentes reutilizables**, con ejemplos pequeños y bien etiquetados.

## Componentes que conviene cubrir

### Navegación
- navbar minimal
- navbar editorial
- navbar catálogo

### Apertura / hero
- hero sobrio
- hero editorial
- hero catálogo compacto

### Cards
- card visual con imagen
- card editorial sin imagen
- card técnica
- card de catálogo

### Metadatos
- badges
- etiquetas
- tabla de atributos
- ficha técnica

### Estructuras auxiliares
- paginación
- buscador
- empty state
- footer
- filtros

## Muy importante: añadir contexto de uso

Cada ejemplo debería decir:

- cuándo usarlo
- cuándo no usarlo
- qué variables espera
- qué tipo de prompt lo favorece

Ejemplo:

### `card_editorial.html`
Usar cuando:
- el usuario pide estilo editorial
- el listado debe ser denso o sobrio
- no conviene mostrar imágenes

Evitar cuando:
- el valor principal está en la imagen
- el tipo de sitio es catálogo visual

## Resultado esperado

- más consistencia
- mejor composición de páginas
- menos necesidad de improvisar estructuras desde cero

---

# 7. Mejora 5 — Mapeo semántico de campos

## Qué problema resuelve

No basta con detectar nombres de campos. Hace falta entender **qué rol cumple cada campo**.

Ejemplo:
- `name` puede ser título principal
- `image` puede ser hero, thumbnail o avatar
- `status` puede ser badge de color
- `created` puede ser fecha destacada
- `species` puede ser metadato o filtro

## Idea principal

Añadir una capa de clasificación semántica de campos.

## Roles útiles

- title
- subtitle
- description
- image
- status
- category
- date
- author
- location
- price
- score
- tag
- id
- metadata

## Cómo usarlo luego

### En listados
- `title` → nombre visible de la card
- `image` → imagen principal si procede
- `status` → badge
- `description` → extracto
- `date` → metadato secundario

### En detalle
- `title` → cabecera
- `image` → bloque principal
- `metadata` → tabla o panel
- `status` → énfasis visual

## Cómo implementarlo

### Regla básica
Mapeo por nombres frecuentes:
- `name`, `title`
- `image`, `img`, `photo`
- `description`, `summary`, `excerpt`
- `created_at`, `date`, `published`

### Regla intermedia
Mapeo por valores:
- si el campo tiene URLs de imagen → image
- si tiene fechas → date
- si tiene pocos valores repetidos → category/status
- si tiene texto largo → description

### Regla avanzada
LLM o heurística mixta para resolver ambigüedades.

## Resultado esperado

- listados más coherentes
- detalle mejor estructurado
- badges y metadatos más útiles

---

# 8. Mejora 6 — Sistema de skills modulares

## Qué problema resuelve

Un único bloque enorme de reglas acaba siendo difícil de mantener y poco específico.

## Idea principal

Separar “cómo actuar” en varios módulos especializados.

## Skills recomendadas

### Skill de interpretación del prompt
- extraer colores
- detectar tono visual
- detectar restricciones
- entender si el sitio es editorial, catálogo, dashboard, etc.

### Skill de diseño visual
- traducir el prompt a layout, densidad, tipografía y componentes

### Skill de templates Django
- uso correcto de `{% extends %}`, `{% block %}`, `{% url %}`, `{% for %}`, `{% empty %}`

### Skill de mapping de datos
- decidir qué campos mostrar y dónde

### Skill de refinamiento
- corregir sin reescribir de más
- mantener lo que ya funciona
- tocar solo zonas concretas

## Organización recomendada

Una carpeta tipo:

- `skills/prompt_interpretation.py`
- `skills/design_composition.py`
- `skills/django_templates.py`
- `skills/data_mapping.py`
- `skills/refinement.py`

## Resultado esperado

- reglas más claras
- mantenimiento más fácil
- menos contradicciones internas

---

# 9. Mejora 7 — Estrategias de tratamiento de imagen

## Qué problema resuelve

Ahora las imágenes tienden a mostrarse casi siempre igual.

Eso empobrece mucho el resultado porque no es lo mismo una imagen de:
- personaje
- producto
- artículo
- logo
- paisaje
- avatar

## Idea principal

Definir varios modos de uso visual de imágenes.

## Modos recomendados

- `square`
- `portrait`
- `landscape`
- `hero`
- `thumbnail`
- `contained`
- `background-cover`

## Ejemplos de uso

### Personajes / perfiles
- portrait o square

### Productos / catálogo
- square

### Noticias / artículos
- landscape

### Logos
- contained

### Destinos / lugares
- landscape o hero

## Qué debe decidir el sistema

- ratio
- crop o contain
- tamaño
- si la imagen va en card, hero o detalle
- si conviene usarla o no

## Resultado esperado

- webs mucho más visuales
- mejor adaptación al contenido
- menos sensación de plantilla repetida

---

# 10. Mejora 8 — Patrones por tipo de sitio

## Qué problema resuelve

Aunque dos datasets sean distintos, muchos sitios comparten una misma “familia” visual.

## Idea principal

Tener patrones de alto nivel por tipo de web.

## Tipos recomendados

- catálogo visual
- editorial / blog
- portfolio
- directorio
- dashboard simple
- ficha técnica
- landing informativa

## Qué puede definir cada patrón

- layout base
- cantidad de imagen
- estilo de cards
- jerarquía tipográfica
- densidad de información
- peso del hero
- estilo de detalle

## Resultado esperado

- menos improvisación
- más coherencia global
- mejor obediencia al tono general

---

# 11. Mejora 9 — Refinamiento incremental

## Qué problema resuelve

Si el refinamiento toca demasiado, puede romper partes que ya estaban bien.

## Idea principal

Permitir refinamientos parciales y acotados.

## Modos útiles

- refinar solo colores
- refinar solo tipografía
- refinar solo list page
- refinar solo detail page
- refinar solo navbar/footer
- refinar solo errores técnicos
- refinar solo fidelidad al prompt

## Qué debe hacer el refinador

- detectar qué conservar
- tocar solo archivos necesarios
- explicar internamente qué cambia y qué no
- evitar reescritura completa salvo necesidad

## Resultado esperado

- iteración más segura
- menos roturas
- refinamiento más controlable

---

# 12. Mejora 10 — Snapshots y versionado

## Qué problema resuelve

Sin historial claro, es difícil:
- comparar generaciones
- volver atrás
- justificar mejoras
- analizar por qué una versión fue mejor que otra

## Idea principal

Guardar versiones sucesivas del proceso.

## Qué conviene guardar

- prompt original
- plan generado
- plantilla inicial
- validaciones
- refinamientos sucesivos
- resultado final

## Utilidad

### Técnica
- comparar resultados
- detectar regresiones
- depurar mejor

### Académica
- explicar evolución del sistema
- enseñar mejora iterativa en el TFG

---

# 13. Propuesta de implementación realista por días

## Día 1
- revisar arquitectura actual
- definir jerarquía de prioridades
- localizar puntos donde el prompt se pierde o se pisa

## Día 2
- crear sistema base de tema
- centralizar colores y estilos comunes

## Día 3
- empezar librería de componentes
- navbar, footer, cards, badges

## Día 4
- añadir validaciones básicas post-generación
- clases Tailwind inválidas
- errores evidentes de template

## Día 5
- mapeo semántico de campos
- heurísticas básicas

## Día 6
- estrategias de imagen
- definir ratios y reglas

## Día 7
- skills modulares
- ordenar prompts y responsabilidades

## Día 8
- refinamiento incremental
- limitar alcance de cambios

## Día 9
- snapshots y trazabilidad

## Día 10
- pruebas reales con varios prompts
- comparar resultados
- documentar hallazgos

---

# 14. Prioridad final resumida

## Prioridad alta
1. sistema base de diseño
2. prioridad explícita del prompt
3. validación post-generación
4. librería de componentes
5. mapeo semántico de campos

## Prioridad media
6. skills modulares
7. tratamiento de imagen
8. patrones por tipo de sitio
9. refinamiento incremental

## Prioridad extra muy útil
10. snapshots y versionado

---

# 15. Conclusión

La dirección buena para mejorar WebBuilder no es añadir “más magia”, sino hacer el sistema más:

- **predecible**
- **modular**
- **validable**
- **obediente al usuario**
- **sensible al tipo de dato**
- **capaz de refinar sin romper**

Si implementas estas mejoras por fases, el proyecto puede pasar de ser un generador “prometedor pero irregular” a un sistema mucho más sólido y defendible como TFG.

La clave está en combinar tres cosas:

1. **buenos prompts**
2. **buenas estructuras reutilizables**
3. **buenas validaciones automáticas**

Ahí está el salto real de calidad.
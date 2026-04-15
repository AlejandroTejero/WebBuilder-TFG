# WebBuilder — Plan de mejoras + trabajo realizado

## Documento unificado de seguimiento

Este documento mezcla dos cosas:

1. **Qué queremos hacer** en WebBuilder a medio plazo.
2. **Qué hemos hecho ya**, especialmente en la sesión de hoy.

La idea es tener un único documento de referencia para no perder el hilo entre mejoras futuras, cambios ya implementados y siguientes pasos.

---

# 1. Objetivo general del sistema

WebBuilder ya genera webs funcionales a partir de datos y prompts en lenguaje natural, pero todavía tiene margen de mejora en varios puntos:

- a veces entiende el prompt, pero no lo ejecuta con suficiente precisión
- mezcla defaults internos con lo que pide el usuario
- puede generar HTML/Tailwind válido a medias
- no reutiliza todavía suficientes patrones consistentes
- trata muchos datasets e imágenes de manera demasiado uniforme
- en refinamiento puede arreglar una parte pero romper otra

Por eso, la evolución del sistema debe orientarse a cinco metas principales:

1. **Obedecer mejor el prompt del usuario**
2. **Reducir errores técnicos de generación**
3. **Reutilizar patrones consistentes**
4. **Aprovechar mejor la semántica de los datos**
5. **Hacer el refinamiento más preciso y menos destructivo**

---

# 2. Hoja de ruta general de mejoras

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

# 3. Qué se ha hecho ya

## 3.1. Arreglar el flujo del prompt del usuario
Se revisó el problema de que el LLM parecía “ignorar” el prompt del usuario y se detectó que el fallo no era solo visual, sino también de flujo.

### Qué pasaba
- el `user_prompt` no llegaba correctamente a la fase final de generación

### Qué se corrigió
- se ajustó el flujo para que el `user_prompt` viaje dentro del plan y llegue al generador final

### Impacto
- el sistema ya no trabaja “como si el usuario no hubiera escrito nada”
- mejora la fidelidad entre lo pedido y lo generado

---

## 3.2. Rebajar reglas visuales demasiado invasivas
Se revisaron los requisitos visuales del sistema para evitar que el LLM forzara siempre una estética tipo startup o landing genérica.

### Antes
Había demasiadas reglas visuales duras, por ejemplo:
- gradientes obligatorios
- hovers fuertes
- imágenes casi obligatorias en cards
- layouts demasiado visuales incluso cuando el usuario pedía algo sobrio

### Cambio realizado
Se sustituyó esa lógica por una estructura más limpia:
- **requisitos estructurales**
- **guía visual subordinada al prompt del usuario**

### Impacto
- el sistema deja de imponer por defecto una estética concreta
- mejora mucho la respuesta a prompts editoriales, sobrios o minimalistas

---

## 3.3. Priorización explícita de instrucciones en `generator_prompts.py`
Se reforzó `generator_prompts.py` para que la jerarquía de decisiones sea explícita y el usuario mande de verdad.

### Qué se añadió
- `_PRIORITY_RULES`
- `build_priority_rules_text()`

### Dónde se integró
- `prompt_pages_structure()`
- `prompt_views()`
- `prompt_base_template()`
- `prompt_template()`
- `prompt_load_data()`

### Jerarquía resultante
1. manda el usuario
2. luego restricciones funcionales
3. luego estructura de página
4. luego dataset
5. luego ejemplos y defaults

### Impacto
- menos contradicciones
- menos mezcla rara entre dataset, ejemplo y prompt
- más obediencia real al usuario

---

## 3.4. Mejora de `enrich_prompt.py`
Se revisó `enrich_prompt.py` para que el dataset complemente, pero no imponga.

### Qué se hizo
- se reforzó la idea de que el contexto del dataset es **ayuda**, no mandato
- se dejaron las sugerencias derivadas del dataset en tono opcional
- se evitaron formulaciones que pudieran pisar al usuario

### Impacto
- el dataset ya no empuja tanto hacia decisiones visuales o de contenido no pedidas
- mayor control del prompt original

---

## 3.5. Creación de una base visual común para el LLM
Se creó dentro de `WebBuilder/utils/llm/design/` un archivo nuevo:

- `theme_rules.py`

### Qué contiene
- reglas seguras de uso de color en Tailwind
- combinaciones base de layout y componentes
- variantes orientativas por estilo
- patrones base de componente
- helper `build_theme_rules_text()`

### Impacto
- el LLM tiene una base visual más estable
- se reduce la improvisación visual
- baja la probabilidad de clases Tailwind inventadas o mal formadas

---

## 3.6. Conexión de `theme_rules.py` con `generator_prompts.py`
Se conectó `theme_rules.py` con los prompts principales.

### Qué se hizo
Se importó:

```python
from .design.theme_rules import build_theme_rules_text
```

y se inyectó `theme_rules_text` dentro de:
- `prompt_base_template()`
- `prompt_template()`
- `prompt_views()`

### Impacto
- la base visual ya forma parte del contexto de generación
- mejora la coherencia general entre páginas
- se reduce la tendencia a inventar clases extrañas

---

## 3.7. Revisión de integración final de `generator_prompts.py`
Se revisó el archivo entero para comprobar:
- que el import estuviera correcto
- que `build_theme_rules_text()` se estuviera usando de verdad
- que el orden del prompt tuviera sentido
- que ejemplos y guías quedaran subordinados al usuario

### Resultado
`generator_prompts.py` quedó ya bien integrado respecto a:
- prioridad del usuario
- tema común
- requisitos por página
- ejemplos como apoyo secundario

---

## 3.8. Ampliación de `consistency_checker.py`
Se amplió `consistency_checker.py` para convertirlo en una base real de validación post-generación.

### Qué se añadió
- limpieza de templates generados
- chequeos de consistencia entre `models.py`, `views.py` y templates
- chequeos de sintaxis Django
- detección de clases Tailwind HEX inválidas
- validación de estructura mínima de templates
- detección de contradicciones simples con el prompt
- función unificada `run_all_checks(...)`

### Nuevas responsabilidades del checker
1. `fix_template`
2. `check_consistency`
3. `check_django_syntax`
4. `check_tailwind_validity`
5. `check_template_structure`
6. `check_prompt_contradictions`
7. `run_all_checks`

### Impacto
- el sistema ya no depende solo del LLM para “hacerlo bien”
- se añade una capa de validación automática bastante útil

---

## 3.9. Integración de la validación en `project_generator.py`
Se conectó la validación ampliada al flujo real de generación.

### Qué se cambió
- se importa `fix_template` y `run_all_checks`
- `fix_template()` se aplica a `base.html` y a los templates por página
- se reemplaza la validación anterior por `run_all_checks(...)`
- en regeneración se usan `sample_items` reales
- en los retries se limpia la salida de `views.py` y los templates

### Impacto
- la validación nueva ya no está “muerta”, sino conectada al generador
- los archivos generados pasan por una revisión más completa antes de quedar como finales

---

# 4. Estado actual del sistema tras la sesión

## Ya está razonablemente bien cubierto
- flujo del `user_prompt`
- jerarquía explícita de prioridad
- dataset como ayuda y no como imposición
- base visual común para el LLM
- validación post-generación inicial
- integración de esa validación en el flujo principal

## Lo que sigue pendiente o mejorable
- librería de componentes de ejemplo
- mapeo semántico de campos
- tratamiento de imagen según contexto
- patrones por tipo de sitio
- refinamiento incremental
- snapshots/versionado
- limpieza de algunos temas de seguridad o producto aparte

---

# 5. Ajuste pendiente importante detectado

Hay un ajuste concreto que conviene hacer cuanto antes.

## Problema
En `project_generator.py`, la validación final se está ejecutando contra el `enriched_prompt` en lugar de usar solo el `user_prompt` original.

### Por qué importa
`enriched_prompt` mezcla:
- el prompt real del usuario
- el contexto del dataset
- sugerencias auxiliares
- defaults suaves

Eso puede hacer que el validador detecte “contradicciones” contra texto que no era una petición explícita del usuario.

## Cambio recomendado
Cambiar:

```python
issues = run_all_checks(files, user_prompt=enriched_prompt)
```

por:

```python
issues = run_all_checks(files, user_prompt=user_prompt)
```

### Criterio correcto
- para **generar**, usar `enriched_prompt`
- para **validar contradicciones con el usuario**, usar `user_prompt`

---

# 6. Próximas mejoras recomendadas

## 6.1. Librería de componentes de ejemplo
Crear una biblioteca modular de piezas reutilizables.

### Componentes prioritarios
- navbar
- footer
- hero
- cards visuales
- cards editoriales
- badges
- tabla de detalle
- paginación
- buscador
- empty states

### Objetivo
- reducir improvisación
- subir coherencia
- adaptar mejor la estética según el prompt

---

## 6.2. Mapeo semántico de campos
Pasar de detectar nombres de campos a entender su función real.

### Roles útiles
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
- metadata

### Objetivo
- listados más inteligentes
- detalles mejor estructurados
- badges y metadatos con más sentido

---

## 6.3. Skills modulares
Separar reglas y ayudas por responsabilidad.

### Posibles módulos
- interpretación del prompt
- composición visual
- templates Django
- mapping de datos
- refinamiento

### Objetivo
- menos contradicciones internas
- mantenimiento más claro
- prompts más específicos por tarea

---

## 6.4. Estrategias de tratamiento de imagen
No mostrar siempre las imágenes igual.

### Modos recomendados
- square
- portrait
- landscape
- hero
- thumbnail
- contained
- background-cover

### Objetivo
- adaptar la imagen al tipo de contenido
- mejorar la calidad visual general

---

## 6.5. Patrones por tipo de sitio
Definir familias visuales de alto nivel.

### Tipos interesantes
- catálogo visual
- editorial / blog
- portfolio
- directorio
- dashboard simple
- ficha técnica
- landing informativa

### Objetivo
- menos improvisación
- más coherencia global
- mejor obediencia al tono general

---

## 6.6. Refinamiento incremental
Permitir refinamientos parciales en lugar de reescrituras grandes.

### Modos útiles
- solo colores
- solo tipografía
- solo list page
- solo detail page
- solo navbar/footer
- solo errores técnicos
- solo fidelidad al prompt

### Objetivo
- iterar con menos riesgo
- conservar lo que ya funciona

---

## 6.7. Snapshots y versionado
Guardar el historial del proceso generativo.

### Qué guardar
- prompt original
- plan generado
- primera generación
- validaciones
- refinamientos sucesivos
- resultado final

### Objetivo
- comparar versiones
- explicar la evolución del sistema
- justificar mejor decisiones en el TFG

---

# 7. Prioridad recomendada a partir de ahora

## Prioridad alta
1. corregir el uso de `user_prompt` en la validación
2. librería de componentes de ejemplo
3. mapeo semántico de campos
4. seguir reforzando validación post-generación

## Prioridad media
5. skills modulares
6. tratamiento de imagen
7. patrones por tipo de sitio
8. refinamiento incremental

## Prioridad extra muy útil
9. snapshots y versionado

---

# 8. Resumen de lo avanzado hoy

En una frase, hoy se han reforzado cuatro pilares clave del sistema:

1. **Obediencia al prompt**
2. **Jerarquía clara de instrucciones**
3. **Base visual común para generar mejor HTML/Tailwind**
4. **Validación post-generación real integrada en el flujo**

---

# 9. Conclusión

La línea buena de evolución para WebBuilder no es añadir “más magia”, sino hacer el sistema más:

- predecible
- modular
- validable
- obediente al usuario
- sensible al tipo de dato
- capaz de refinar sin romper

Lo más importante de esta sesión es que ya no solo se ha mejorado el prompting, sino también la arquitectura de apoyo al LLM:

- mejor flujo del prompt
- mejor jerarquía
- mejor base visual
- mejor validación

Eso hace que WebBuilder esté más cerca de dejar de ser un generador prometedor pero irregular y convertirse en un sistema mucho más sólido y defendible como TFG.

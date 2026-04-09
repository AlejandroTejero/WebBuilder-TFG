ASISTENTE — DECISIONES DE DISEÑO
=================================

LAYOUT GENERAL
- Sin sidebar NO. Mantener sidebar pero rediseñado: minimalista, sin emojis,
  solo muestra el stepper de progreso (pasos 1/2/3) y el bloque de análisis
  activo (URL + estado). Quitar el link de historial del sidebar o dejarlo
  muy discreto.
- Dos columnas: izquierda 55% (formulario), derecha 45% sticky (schema + preview).
- Sin sidebar se gana ancho, repartir bien entre las dos columnas.
- Público objetivo: mayoritariamente desktop.

SELECTOR DE LLM
- Botón en el formulario con el modelo predeterminado ya seleccionado.
- Al pulsar abre un modal centrado con animación, que ocupa la parte central
  de la pantalla y tiene peso visual.
- Dentro del modal: tres opciones en vertical:
    1. Predeterminado (opción recomendada, se vende como "se adapta a tu API")
    2. Elegir modelo (se despliega lista con cards verticales y especificaciones)
    3. Personalizado (no despliega nada, lleva a la página de configuración)
- En móvil: el modal se comporta como un bottom sheet / modal fullscreen.

WIZARD DE PROMPT
- Mantener los 3 modos: Libre / Ejemplos / Guiado.
- El modo Guiado rediseñarlo: más minimalista y profesional,
  quitarle el aspecto de selector infantil que tiene ahora.
- Sin emojis en ningún lado.

ESTILO GENERAL
- Alinear completamente al sistema visual del home:
    · Variables CSS: --wb-bg, --wb-t1, --wb-border, etc.
    · Tipografía: Geist / Geist Mono (quitar Outfit)
    · Border-radius pequeños: 5-8px (quitar los 16px actuales)
    · Sin azul #3b82f6, sin morados, sin gradientes de color
    · Monocromático como el home
- Sin emojis en ningún componente.

FASE ACTUAL
- Solo CSS (4 ficheros: base.css, form.css, schema.css, loading.css).
- HTML se toca en una segunda fase.
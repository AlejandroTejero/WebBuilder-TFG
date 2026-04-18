"""Catálogo de presets visuales para guiar la generación de templates con LLM.

Este módulo no genera HTML. Solo describe estilos consistentes y muy distintos
entre sí para que el LLM varíe tanto la paleta como la estructura y el lenguaje
visual de las páginas.

Reglas importantes:
- Las clases de ejemplo son clases Tailwind válidas para CDN.
- Los colores HEX usan siempre sintaxis arbitraria válida, por ejemplo
  ``bg-[#111111]`` o ``text-[#c8ff00]``.
- Los layouts se describen en texto para que el LLM los traduzca a HTML.
- Los layouts de list y detail deben poder adaptarse a catalog, blog,
  dashboard y portfolio sin asumir nombres de campos concretos.
"""

from __future__ import annotations

import copy
import random
import re
import unicodedata
from typing import Any


STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "neo_terminal": {
        "id": "neo_terminal",
        "name": "Neo terminal / lista densa horizontal",
        "keywords": [
            "neon",
            "neón",
            "cyberpunk",
            "terminal",
            "techno",
            "hacker",
            "dark ui",
            "dark",
            "futurista",
            "futuristic",
            "gaming",
            "saas oscura",
        ],
        "color": {
            "summary": "Fondo casi negro con contraste alto y acento neón ácido. La sensación debe ser técnica, nocturna y muy orientada a densidad de información.",
            "background": "Usar fondo principal bg-[#050505] o bg-[#0b0b0b] con texto base text-white y secundarios text-[#a3a3a3].",
            "surface": "Superficies ligeramente elevadas con bg-[#101010], border border-[#222222] y separaciones visibles pero sobrias.",
            "accent": "Acento principal verde neón o lima eléctrica con text-[#c8ff00], bg-[#c8ff00], border-[#c8ff00] y estados hover con brillo controlado.",
            "borders": "Bordes finos y definidos, normalmente border-[#222222] o border-[#2f2f2f], sin perder contraste sobre fondo oscuro.",
        },
        "layout": {
            "summary": "El layout debe sentirse como una interfaz editorial-técnica donde lo importante es escanear muchos elementos rápidamente.",
            "home": "Home con hero compacto, una banda superior con llamada a la acción y debajo una columna principal de bloques densos. Prioriza listados destacados en formato horizontal y módulos secundarios en una rejilla sobria de 2 columnas. Evita grandes vacíos verticales.",
            "list": "Listado siempre en pila vertical de filas densas. Cada ítem se presenta como una banda horizontal con imagen o miniatura cuadrada pequeña a la izquierda, bloque de metadatos y título a la derecha, y acciones o etiquetas alineadas al extremo derecho si hacen falta. Debe funcionar para catálogo, blog, dashboard y portfolio tratando cada elemento como una entrada escaneable.",
            "detail": "Detalle con estructura de dos zonas: cabecera compacta con título, metadatos y acciones; luego cuerpo en una o dos columnas donde el contenido principal domina y una columna secundaria muestra datos de apoyo, enlaces o bloques relacionados. La jerarquía debe parecer una ficha técnica legible en oscuro.",
        },
        "components": {
            "summary": "Componentes compactos, afilados y orientados a lectura rápida.",
            "cards": "Cards y filas con rounded-xl, border, bg-[#101010] y sombras muy suaves; prioridad a densidad antes que a espectacularidad. Las imágenes se recortan en formato cuadrado o casi cuadrado.",
            "badges": "Badges pequeños y técnicos con inline-flex items-center rounded-full border border-[#c8ff00] px-2.5 py-1 text-[11px] font-medium text-[#c8ff00].",
            "typography": "Tipografía sans, firme y compacta. Títulos con tracking-tight y pesos altos; metadatos pequeños en uppercase o tamaños reducidos para reforzar el aire terminal.",
            "separators": "Separadores frecuentes con border-t border-[#1f1f1f] o divide-y divide-[#1f1f1f] para reforzar el escaneo por filas.",
        },
    },
    "bento_pop": {
        "id": "bento_pop",
        "name": "Bento box asimétrico y cromático",
        "keywords": [
            "bento",
            "mosaico",
            "grid",
            "asymmetrical",
            "asimetrico",
            "asimétrico",
            "playful",
            "creativo",
            "startup",
            "colorido",
            "vibrante",
            "vibrant",
        ],
        "color": {
            "summary": "Paleta brillante y optimista, con celdas que pueden alternar fondos vivos sin perder legibilidad general.",
            "background": "Fondo general claro como bg-[#fff7ed] o bg-[#fafaf9] para dejar respirar las piezas cromáticas.",
            "surface": "Cada bloque puede usar una superficie distinta: bg-[#ffffff], bg-[#fef3c7], bg-[#dbeafe], bg-[#f5d0fe], bg-[#dcfce7]. Deben convivir con texto oscuro legible.",
            "accent": "Acentos vivos en naranja, azul, fucsia o verde. Los CTA pueden alternar entre bg-[#fb7185], bg-[#2563eb], bg-[#14b8a6] o bg-[#f59e0b] según el bloque.",
            "borders": "Bordes suaves y definidos, normalmente border border-black/10 o border border-[#1f2937]/10, nunca agresivos.",
        },
        "layout": {
            "summary": "La estructura debe parecer una composición bento: piezas de distintos tamaños, ritmos cambiantes y lectura dinámica.",
            "home": "Home construida como un mosaico asimétrico. Combina un hero grande que ocupe varias celdas con tarjetas secundarias de altura desigual y bloques que mezclen destacados, KPIs, entradas recientes o proyectos. La sensación debe ser modular y muy visual.",
            "list": "Los listados no deben ser una lista monótona. Usa grid responsivo con tarjetas de distintos tamaños: algunas celdas pueden ser anchas, otras compactas, y conviene intercalar elementos destacados cada cierto número de ítems. Debe seguir funcionando para catálogo, blog, dashboard y portfolio con una lógica de exploración visual.",
            "detail": "Detalle en composición modular: cabecera visual arriba y luego bloques temáticos repartidos en una grid de 12 columnas o equivalentes. El contenido principal puede ocupar un bloque grande mientras metadatos, enlaces, stats o piezas relacionadas viven en celdas complementarias.",
        },
        "components": {
            "summary": "Componentes amables, redondeados y muy visuales.",
            "cards": "Cards tipo panel con rounded-3xl, border border-black/10, sombras suaves y suficiente padding. Algunas tarjetas pueden tener más altura o anchura para romper la monotonía.",
            "badges": "Badges amigables y coloridos con rounded-full px-3 py-1 text-xs font-semibold; usar fondos suaves y texto oscuro o acentos sólidos cuando haga falta destacar.",
            "typography": "Tipografía sans contemporánea, con títulos grandes y expresivos. El texto debe ser directo, enérgico y fácil de escanear.",
            "separators": "Evitar demasiados separadores lineales. La propia rejilla, el color y el espaciado ya hacen el trabajo de segmentación.",
        },
    },
    "brutalist_poster": {
        "id": "brutalist_poster",
        "name": "Brutalista / cartel impreso",
        "keywords": [
            "brutalist",
            "brutalismo",
            "brutalista",
            "poster",
            "cartel",
            "raw",
            "experimental",
            "edgy",
            "industrial",
            "bold",
        ],
        "color": {
            "summary": "Colores planos de alto impacto, contraste duro y cero sutileza visual.",
            "background": "Fondo dominante amarillo ácido o crudo como bg-[#f5e71c] o bg-[#fff04a], combinado con texto negro absoluto text-black.",
            "surface": "Superficies planas en blanco, negro o amarillo, sin transparencias ni gradientes. Se puede alternar bg-white y bg-black con texto invertido.",
            "accent": "Acento rojo o negro muy contundente, por ejemplo bg-[#ff3b30], text-[#ff3b30] o bloques negros con texto amarillo.",
            "borders": "Bordes gruesos, siempre visibles, con border-2 o border-[3px] border-black. Nada de bordes sutiles.",
        },
        "layout": {
            "summary": "La página debe parecer un cartel o sistema editorial crudo, con bloques duros y composición deliberadamente rígida.",
            "home": "Home con hero muy grande, titulares dominantes, bloques apilados y bandas de contenido de alto contraste. Se aceptan asimetrías, pero siempre con rectángulos duros y jerarquía agresiva.",
            "list": "Listado como pila de bloques grandes o tabla visual de bandas. Cada elemento ocupa ancho completo o media página con título enorme, metadatos marcados y miniatura opcional tratada como bloque rígido. Debe servir tanto para entradas, productos, métricas o proyectos sin depender de campos concretos.",
            "detail": "Detalle estructurado en franjas: cabecera impactante, cuerpo principal amplio, módulos secundarios en bloques apilados o columnas rígidas. Nada de composiciones delicadas ni decorativas.",
        },
        "components": {
            "summary": "Componentes secos, geométricos y sin suavizado.",
            "cards": "Cards sin border radius: rounded-none border-2 border-black o rounded-none border-[3px] border-black. Evitar sombras suaves; si se usa sombra, que sea dura y corta.",
            "badges": "Badges rectangulares, compactos y duros, con rounded-none border-2 border-black px-2 py-1 text-xs font-black uppercase.",
            "typography": "Tipografía sans muy pesada, mayúsculas frecuentes, tracking estrecho y titulares enormes. El texto debe sentirse como impresión de cartel.",
            "separators": "Separadores gruesos con border-t-2 border-black o bloques de color sólido. La división entre secciones debe ser explícita.",
        },
    },
    "magazine_split": {
        "id": "magazine_split",
        "name": "Magazine / periódico contemporáneo",
        "keywords": [
            "magazine",
            "editorial magazine",
            "newspaper",
            "periodico",
            "periódico",
            "journal",
            "revista",
            "article",
            "news",
            "blog editorial",
        ],
        "color": {
            "summary": "Paleta contenida, inspirada en prensa: marfil, tinta, gris carbón y un acento sobrio.",
            "background": "Fondo principal bg-[#f7f3eb] o bg-[#faf7f0] con texto base text-[#111111].",
            "surface": "Superficies en crema, blanco roto o gris muy suave con bordes finos border-[#d6d3d1].",
            "accent": "Acento vino, azul noche o verde bosque muy medido, por ejemplo text-[#7f1d1d] o text-[#1f3a5f].",
            "borders": "Bordes editoriales finos y elegantes con border-[#d6d3d1] o border-[#bfb8aa].",
        },
        "layout": {
            "summary": "La estructura debe recordar a una revista o periódico contemporáneo, con protagonismo de imagen grande y textos en columnas limpias.",
            "home": "Home con un gran bloque principal dividido horizontalmente: imagen o visual dominante a la izquierda y texto de portada a la derecha. Debajo, bandas de historias, piezas destacadas o módulos de exploración en ritmo editorial, con columnas y jerarquía clásica.",
            "list": "Listado en filas horizontales amplias tipo portada de revista. Cada elemento muestra imagen generosa a la izquierda y contenido a la derecha: título, extracto, metadatos y CTA. Debe adaptarse a catálogo, blog, dashboard y portfolio tratando cada registro como una historia principal o una pieza destacada.",
            "detail": "Detalle con cabecera muy editorial, posible imagen protagonista ancha y luego cuerpo en una columna principal de lectura con una columna secundaria para notas, navegación contextual, datos o piezas relacionadas. Mantener una sensación de maquetación periodística.",
        },
        "components": {
            "summary": "Componentes sobrios, refinados y con jerarquía tipográfica fuerte.",
            "cards": "Las cards deben parecer módulos editoriales más que tarjetas de producto. Usar bordes finos, poco radio y padding generoso; evitar apariencia de app.",
            "badges": "Badges discretos y casi tipográficos, preferiblemente outline o texto en small caps visuales, sin exceso de color.",
            "typography": "Combina serif para titulares y sans o serif legible para texto corrido. Mucha atención al tamaño de títulos, interlineado y ancho de columna.",
            "separators": "Separadores finos, rules editoriales y líneas horizontales frecuentes para dividir secciones con elegancia.",
        },
    },
    "glass_orbit": {
        "id": "glass_orbit",
        "name": "Glassmorphism suave",
        "keywords": [
            "glass",
            "glassmorphism",
            "blur",
            "cristal",
            "frosted",
            "soft ui",
            "aurora",
            "gradient",
            "gradiente",
            "lavender",
            "lavanda",
        ],
        "color": {
            "summary": "Gradientes suaves, atmósfera luminosa e interfaces translúcidas con tonos índigo, lavanda y blanco lechoso.",
            "background": "Fondo con degradados suaves entre bg-[#eef2ff], bg-[#e0e7ff], bg-[#f5f3ff] y toques de bg-[#dbeafe].",
            "surface": "Superficies translúcidas usando bg-white/40 o bg-white/50, border border-white/40 y backdrop-blur-xl para crear efecto cristal.",
            "accent": "Acentos en índigo, violeta o azul eléctrico moderado, por ejemplo text-[#4f46e5], bg-[#6366f1], border-[#818cf8].",
            "borders": "Bordes semitransparentes y luminosos con border-white/40 o border-[#c7d2fe].",
        },
        "layout": {
            "summary": "La composición debe ser aireada y flotante, con paneles que parecen capas de cristal sobre un fondo difuminado.",
            "home": "Home con hero amplio, capas superpuestas y paneles flotantes. Debe haber espacios amplios, bloques destacados en una grid limpia y sensación de profundidad sin saturar el contenido.",
            "list": "Listado en grid o lista espaciosa de paneles translúcidos. Cada ítem debe tener respiración suficiente, miniatura opcional integrada con esquinas suaves y metadatos ligeros. Debe encajar tanto en catálogo como en blog, dashboard o portfolio mediante paneles elegantes y ligeros.",
            "detail": "Detalle con gran cabecera flotante y luego contenido distribuido en panel principal y paneles laterales translúcidos. La lectura debe sentirse premium, ligera y muy visual.",
        },
        "components": {
            "summary": "Componentes pulidos, suaves y con sensación de profundidad ligera.",
            "cards": "Cards con rounded-3xl, bg-white/40, border border-white/40, backdrop-blur-xl y shadow-xl. El contenido interno debe mantener contraste suficiente.",
            "badges": "Badges suaves con rounded-full bg-white/50 px-3 py-1 text-xs font-medium text-[#4338ca] border border-white/50.",
            "typography": "Tipografía sans moderna y limpia. Títulos grandes pero ligeros, con pesos medios o semibold y abundante espacio alrededor.",
            "separators": "Separadores mínimos; usar más el espaciado, el desenfoque y las diferencias de superficie que las líneas duras.",
        },
    },
    "quiet_editorial": {
        "id": "quiet_editorial",
        "name": "Editorial limpio y estrecho",
        "keywords": [
            "minimal",
            "minimalista",
            "clean",
            "limpio",
            "editorial",
            "serif",
            "luxury",
            "portfolio minimal",
            "elegante",
            "quiet",
            "simple",
        ],
        "color": {
            "summary": "Blanco roto, negro suave y un solo acento muy discreto. La paleta debe desaparecer para dejar que la estructura respire.",
            "background": "Fondo principal bg-[#fffdf8] o bg-white con texto base text-[#111111].",
            "surface": "Superficies casi idénticas al fondo, con diferencias mínimas como bg-[#faf7f2] y bordes muy tenues border-[#ece7df].",
            "accent": "Un acento único y elegante, por ejemplo text-[#6b7280] o text-[#7c3f00], usado solo en enlaces, detalles o estados activos.",
            "borders": "Bordes finísimos y discretos, nunca protagonistas. Priorizar silencio visual.",
        },
        "layout": {
            "summary": "La estructura debe ser estrecha, centrada y pausada, con mucho espacio en blanco y foco absoluto en la lectura.",
            "home": "Home en una columna central relativamente estrecha, con hero textual, bloques muy espaciados y pocas interrupciones visuales. El ritmo debe ser pausado y premium, casi como una página de ensayo o portafolio de autor.",
            "list": "Listado en columna vertical centrada y estrecha, sin imágenes en el listado salvo que el prompt las exija de forma muy clara. Cada elemento se resuelve con título, una línea descriptiva, metadatos discretos y una separación amplia respecto al siguiente. Debe funcionar para catálogo, blog, dashboard y portfolio mediante abstracción editorial y ausencia de ruido.",
            "detail": "Detalle en columna de lectura estrecha, con título, subtítulo o metadatos y luego cuerpo principal continuo. Los módulos auxiliares deben ser pocos y muy discretos, idealmente antes o después del contenido principal, no compitiendo con él.",
        },
        "components": {
            "summary": "Componentes casi invisibles, donde el peso visual recae en la tipografía y el espaciado.",
            "cards": "Evitar apariencia de card siempre que sea posible. Cuando un contenedor sea necesario, usar rounded-none o rounded-sm, border-b o border muy tenue y mucho margen vertical.",
            "badges": "Badges mínimos o incluso ausencia de badges. Si aparecen, que sean puramente tipográficos, pequeños y muy discretos.",
            "typography": "Usar serif elegante para titulares y texto principal si encaja. Jerarquía basada en tamaño, peso y espacio; nunca en color estridente. Mucho leading y columnas de lectura controladas.",
            "separators": "Separadores extremadamente sutiles, preferiblemente border-b border-[#ece7df] con grandes márgenes verticales.",
        },
    },
}


_PRESET_ORDER = tuple(STYLE_PRESETS.keys())


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def get_preset(user_prompt: str) -> dict[str, Any]:
    """Selecciona el preset más adecuado para el prompt del usuario.

    La detección usa coincidencias simples por palabras clave. Si no encuentra una
    intención clara, devuelve un preset aleatorio para forzar variedad real.
    """

    prompt = _normalize_text(user_prompt)
    if not prompt:
        return copy.deepcopy(random.choice(list(STYLE_PRESETS.values())))

    scored_presets: list[tuple[int, int, str]] = []

    for index, preset_key in enumerate(_PRESET_ORDER):
        preset = STYLE_PRESETS[preset_key]
        score = 0
        for keyword in preset.get("keywords", []):
            normalized_keyword = _normalize_text(keyword)
            if normalized_keyword and normalized_keyword in prompt:
                score += max(1, len(normalized_keyword.split()))
        scored_presets.append((score, -index, preset_key))

    best_score, _, best_key = max(scored_presets)
    if best_score <= 0:
        return copy.deepcopy(random.choice(list(STYLE_PRESETS.values())))

    return copy.deepcopy(STYLE_PRESETS[best_key])


def describe_preset(preset: dict[str, Any]) -> str:
    """Devuelve una descripción plana del preset lista para inyectar en un prompt."""

    color = preset.get("color", {})
    layout = preset.get("layout", {})
    components = preset.get("components", {})
    keywords = preset.get("keywords", [])

    lines = [
        f"PRESET VISUAL SELECCIONADO: {preset.get('name', 'Preset sin nombre')}",
    ]
    lines.extend(
        [
            "",
            "CAPA DE COLOR:",
            f"- Resumen: {color.get('summary', '')}",
            f"- Fondo: {color.get('background', '')}",
            f"- Superficie: {color.get('surface', '')}",
            f"- Acento: {color.get('accent', '')}",
            f"- Bordes: {color.get('borders', '')}",
            "",
            "CAPA DE LAYOUT:",
            f"- Resumen: {layout.get('summary', '')}",
            f"- Home: {layout.get('home', '')}",
            f"- List: {layout.get('list', '')}",
            f"- Detail: {layout.get('detail', '')}",
            "",
            "CAPA DE COMPONENTES:",
            f"- Resumen: {components.get('summary', '')}",
            f"- Cards: {components.get('cards', '')}",
            f"- Badges: {components.get('badges', '')}",
            f"- Tipografía: {components.get('typography', '')}",
            f"- Separadores: {components.get('separators', '')}",
            "",
            "Aplica este preset de forma coherente en todas las páginas generadas. No mezcles este lenguaje visual con otros presets y no inventes clases CSS fuera de Tailwind CDN.",
        ]
    )

    return "\n".join(lines)


__all__ = ["STYLE_PRESETS", "get_preset", "describe_preset"]
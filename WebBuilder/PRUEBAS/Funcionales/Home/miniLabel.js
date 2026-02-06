// static/js/mini-label-lines.js
(function () {
  // ====================== AJUSTES RÁPIDOS ======================
  const config = {
    selector: ".mini-label",
    orderByLabelNumber: true,      // Ordena por .label1, .label2, ... (si no, usa el orden del DOM)
    initialDelayMs: 80,            // Pausa antes de empezar la primera línea
    charStaggerMs: 22,             // Escalonado entre letras
    lineGapMs: 180,                // Pausa entre líneas (al terminar una, antes de empezar la siguiente)
    translateYPx: -8,              // Desde dónde “cae” cada letra
    durationMs: 420,               // Duración de cada letra
    easing: "cubic-bezier(.22,.61,.36,1)", // Suavizado
  };

  // ====================== UTIL: inyectar CSS ======================
  function injectStyle(cssText, id = "ml-letters-style") {
    if (document.getElementById(id)) return;
    const style = document.createElement("style");
    style.id = id;
    style.textContent = cssText;
    document.head.appendChild(style);
  }

  // CSS para las letras (autocontenido, sin tocar tu CSS)
  injectStyle(`
  /* Split de letras para .mini-label */
  .mini-label[data-ml-split="true"] { opacity: 1 !important; transform: none !important; animation: none !important; }
  .mini-label .ml-inner { display: inline; }
  .mini-label .ml-char {
    display: inline-block;
    will-change: transform, opacity;
    opacity: 0;
    transform: translateY(${config.translateYPx}px);
  }
  .mini-label.is-revealed .ml-char {
    opacity: 1;
    transform: translateY(0);
    transition:
      opacity ${config.durationMs}ms ${config.easing},
      transform ${config.durationMs}ms ${config.easing};
  }
  @media (prefers-reduced-motion: reduce) {
    .mini-label .ml-char { opacity: 1 !important; transform: none !important; transition: none !important; }
  }
  `);

  // ====================== Split por letras ======================
  function splitLabelIntoChars(el) {
    if (!el || el.dataset.mlSplit === "true") return el;

    // Desactiva la animación CSS previa de .mini-label para evitar conflicto
    el.style.animation = "none";
    el.style.opacity = "1";
    el.style.transform = "none";

    const original = el.textContent;
    el.setAttribute("aria-label", original);
    el.setAttribute("role", "text");

    // Contenedor visual
    const inner = document.createElement("span");
    inner.className = "ml-inner";
    inner.setAttribute("aria-hidden", "true");

    // Construye spans por carácter (mantiene espacios)
    const frag = document.createDocumentFragment();
    for (const ch of original) {
      const span = document.createElement("span");
      span.className = "ml-char";
      span.textContent = ch === " " ? "\u00A0" : ch;
      frag.appendChild(span);
    }
    inner.appendChild(frag);

    // Limpia y monta
    el.textContent = "";
    el.appendChild(inner);

    el.dataset.mlSplit = "true";
    return el;
  }

  // ====================== Helpers de tiempo ======================
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ====================== Orden de líneas ======================
  function sortMiniLabels(nodes) {
    const list = Array.from(nodes);
    if (!config.orderByLabelNumber) return list;

    return list.sort((a, b) => {
      const getNum = (el) => {
        const cls = el.className || "";
        const m = cls.match(/label(\d+)/);
        return m ? parseInt(m[1], 10) : Number.POSITIVE_INFINITY;
      };
      const na = getNum(a), nb = getNum(b);
      if (na === nb) return 0;
      return na - nb;
    });
  }

  // ====================== Reproducir animación secuencial ======================
  async function playSequential(labels) {
    // Accesibilidad/movimiento reducido
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      labels.forEach((el) => {
        if (!el.dataset.mlSplit) splitLabelIntoChars(el);
        el.classList.add("is-revealed");
      });
      return;
    }

    await sleep(config.initialDelayMs);

    for (const el of labels) {
      // Asegura split
      splitLabelIntoChars(el);

      // Aplica delays por letra
      const chars = el.querySelectorAll(".ml-char");
      chars.forEach((ch, i) => {
        ch.style.transitionDelay = `${i * config.charStaggerMs}ms`;
      });

      // Dispara línea
      el.classList.add("is-revealed");

      // Espera a que termine la línea antes de pasar a la siguiente
      const lineDuration =
        (chars.length - 1) * config.charStaggerMs + config.durationMs + config.lineGapMs;
      await sleep(lineDuration);
    }
  }

  // ====================== Init ======================
  function init() {
    const nodes = document.querySelectorAll(config.selector);
    if (!nodes.length) return;

    const ordered = sortMiniLabels(nodes);

    // Pre-split para que el layout no "salte"
    ordered.forEach(splitLabelIntoChars);

    // Lanza animación al entrar en la página
    playSequential(ordered);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

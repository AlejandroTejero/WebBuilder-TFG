/*!
 * minitext.js
 * Animación ligera para <p class="mini-text"> inspirada en miniLabel.js
 * - Stagger + desplazamiento inicial aleatorio
 * - Parallax suave con el ratón
 * - Respeta prefers-reduced-motion
 * - No rompe los <span> internos
 */
(function () {
  "use strict";

  // ===== Utilidades
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function clamp(n, min, max) { return Math.min(max, Math.max(min, n)); }

  // Inserta CSS una única vez
  const STYLE_ID = "mini-text-runtime-style";
  function injectStylesOnce() {
    if (document.getElementById(STYLE_ID)) return;
    const css = `
      .mini-text {
        --mt-parallax-x: 0;
        --mt-parallax-y: 0;
        --mt-stagger: 0ms;
      }
      .mini-text.mt-ready { display: inline-block; }
      .mini-text .mt-word {
        display: inline-block;
        will-change: transform, opacity;
        opacity: 0;
        transform:
          translate3d(var(--mt-dx, 0px), var(--mt-dy, 0px), 0)
          translate3d(var(--mt-parallax-x, 0px), var(--mt-parallax-y, 0px), 0);
        transition:
          transform var(--mt-dur, 600ms) cubic-bezier(.2,.8,.2,1) var(--mt-delay, 0ms),
          opacity   var(--mt-dur, 600ms) ease var(--mt-delay, 0ms);
      }
      .mini-text.mt-in .mt-word {
        opacity: 1;
        transform:
          translate3d(0,0,0)
          translate3d(var(--mt-parallax-x, 0px), var(--mt-parallax-y, 0px), 0);
      }
      /* Hover/Focus suave (si no hay reducción de movimiento) */
      @media (prefers-reduced-motion: no-preference) {
        .mini-text .mt-word:hover,
        .mini-text .mt-word:focus-visible {
          transform:
            translate3d(0,0,0)
            translate3d(var(--mt-parallax-x, 0px), var(--mt-parallax-y, 0px), 0)
            scale(1.03);
        }
      }
    `;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = css;
    document.head.appendChild(style);
  }

  // Envuelve solo nodos de texto en spans .mt-word; respeta elementos <span> ya presentes
  function wrapWordsPreservingSpans(rootEl) {
    const walker = document.createTreeWalker(rootEl, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => {
        // Ignora nodos vacíos/espacios
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        // No procesar texto dentro de un .mt-word ya existente
        if (node.parentElement && node.parentElement.classList.contains("mt-word")) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });

    const toProcess = [];
    while (walker.nextNode()) toProcess.push(walker.currentNode);

    toProcess.forEach(textNode => {
      const frag = document.createDocumentFragment();
      const parts = textNode.nodeValue.split(/(\s+)/); // conserva espacios
      parts.forEach(part => {
        if (part.trim().length === 0) {
          frag.appendChild(document.createTextNode(part));
        } else {
          const span = document.createElement("span");
          span.className = "mt-word";
          span.textContent = part;
          frag.appendChild(span);
        }
      });
      textNode.parentNode.replaceChild(frag, textNode);
    });
  }

  // Inicializa un bloque .mini-text
  function setupMiniText(el, opts = {}) {
    injectStylesOnce();

    // Opciones con valores por defecto
    const {
      maxOffset = 18,           // desplazamiento inicial
      baseDelay = 180,          // antes: 40/120 -> MUY lento (espaciado entre palabras)
      randomDelayJitter = 370,  // antes: 120/300 -> variación extra
      duration = 1800,          // antes: 600/1600 -> transiciones mucho más largas
      parallax = 6
    } = opts;



    // Si ya está inicializado, no repetir
    if (el.dataset.mtInit === "1") return;
    el.dataset.mtInit = "1";

    // Prepara estructura
    wrapWordsPreservingSpans(el);
    el.classList.add("mt-ready");

    // Configura offsets y delays
    const words = Array.from(el.querySelectorAll(".mt-word"));
    words.forEach((w, i) => {
      const dx = (Math.random() * 2 - 1) * maxOffset;
      const dy = (Math.random() * 2 - 1) * maxOffset;
      const jitter = Math.random() * randomDelayJitter;
      const delay = i * baseDelay + jitter;

      w.style.setProperty("--mt-dx", `${dx.toFixed(1)}px`);
      w.style.setProperty("--mt-dy", `${dy.toFixed(1)}px`);
      w.style.setProperty("--mt-delay", `${Math.round(delay)}ms`);
      w.style.setProperty("--mt-dur", `${duration}ms`);
    });

    // Entrada con IntersectionObserver (o inmediata si reduce)
    const enter = () => el.classList.add("mt-in");
    if (prefersReduced) {
      words.forEach(w => {
        w.style.setProperty("--mt-dx", "0px");
        w.style.setProperty("--mt-dy", "0px");
        w.style.setProperty("--mt-delay", "0ms");
        w.style.setProperty("--mt-dur", "0ms");
      });
      enter();
    } else {
      const io = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            enter();
            obs.disconnect();
          }
        });
      }, { threshold: 0.2 });
      io.observe(el);
    }

    // Parallax suave con el ratón (desactiva si reduce)
    if (!prefersReduced) {
      // Usa contenedor grande si existe para mejor efecto
      const container = el.closest(".scatter-grid") || el;
      let raf = null;

      function onMove(ev) {
        const rect = container.getBoundingClientRect();
        const x = clamp((ev.clientX - rect.left) / rect.width, 0, 1);
        const y = clamp((ev.clientY - rect.top) / rect.height, 0, 1);
        const px = (x - 0.5) * parallax * 2;
        const py = (y - 0.5) * parallax * 2;

        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          el.style.setProperty("--mt-parallax-x", `${px.toFixed(2)}px`);
          el.style.setProperty("--mt-parallax-y", `${py.toFixed(2)}px`);
        });
      }

      function resetParallax() {
        el.style.setProperty("--mt-parallax-x", "0px");
        el.style.setProperty("--mt-parallax-y", "0px");
      }

      container.addEventListener("mousemove", onMove);
      container.addEventListener("mouseleave", resetParallax);
    }
  }

  // API pública por si quieres reinicializar manualmente
  window.MiniText = {
    init(selector = ".mini-text", options) {
      document.querySelectorAll(selector).forEach(el => setupMiniText(el, options));
    }
  };

  // Auto-inicialización
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => window.MiniText.init());
  } else {
    window.MiniText.init();
  }
})();

// particles.js — Fondo de partículas NO bloqueante (copiar y pegar)
(function () {
  "use strict";

  // ====================== AJUSTES RÁPIDOS ======================
  const config = {
    particles: {
      number: 50,                     // Nº de partículas
      size: { min: 1, max: 3 },        // Tamaño (px)
      speed: 0.6,                      // Velocidad base
      color: "#0ea5e9",                // Color de puntos
      opacity: 0.7,                    // Opacidad (0–1)
    },
    links: {
      enable: true,                    // Unir puntos cercanos
      distance: 110,                   // Distancia máx. para unir
      width: 1,                        // Grosor de la línea
      color: "rgba(14,165,233,0.25)",  // Color de líneas
    },
    behavior: {
      parallaxOnMouse: false,          // Pequeño efecto con el ratón
      maxFPS: 60,                      // Límite FPS
    }
  };
  // =============================================================

  // ---------- Utilidades ----------
  const rand = (min, max) => Math.random() * (max - min) + min;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  // ---------- Setup Canvas ----------
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // Asegurar estilos para NO bloquear interacción ni tapar UI
  Object.assign(canvas.style, {
    position: "fixed",
    inset: "0",
    width: "100%",
    height: "100%",
    zIndex: "0",
    pointerEvents: "none"
  });

  let vw = 0, vh = 0, dpr = 1;
  function resize() {
    // Tamaño CSS
    const rect = canvas.getBoundingClientRect();
    vw = Math.max(1, Math.floor(rect.width));
    vh = Math.max(1, Math.floor(rect.height));
    // DPI
    dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(vw * dpr);
    canvas.height = Math.floor(vh * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener("resize", resize, { passive: true });

  // ---------- Partículas ----------
  const P = [];
  const COUNT = config.particles.number;

  function makeParticle() {
    const s = rand(config.particles.size.min, config.particles.size.max);
    const angle = rand(0, Math.PI * 2);
    const speed = config.particles.speed * (0.6 + Math.random() * 0.8);
    return {
      x: Math.random() * vw,
      y: Math.random() * vh,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: s,
    };
  }

  for (let i = 0; i < COUNT; i++) P.push(makeParticle());

  // ---------- Interacción opcional ----------
  const mouse = { x: vw / 2, y: vh / 2, active: false };
  if (config.behavior.parallaxOnMouse) {
    window.addEventListener("mousemove", (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    }, { passive: true });
    window.addEventListener("mouseleave", () => { mouse.active = false; }, { passive: true });
  }

  // ---------- Dibujo ----------
  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  function step(dt) {
    // Clear
    ctx.clearRect(0, 0, vw, vh);

    // Mover y rebotar en bordes (wrap-around suave)
    for (let i = 0; i < P.length; i++) {
      const p = P[i];
      p.x += p.vx;
      p.y += p.vy;

      // Parallax muy sutil si está activo
      if (config.behavior.parallaxOnMouse && mouse.active) {
        const dx = (mouse.x - vw * 0.5) / vw;
        const dy = (mouse.y - vh * 0.5) / vh;
        p.x += dx * 0.1;
        p.y += dy * 0.1;
      }

      // Wrap-around
      if (p.x < -10) p.x = vw + 10;
      else if (p.x > vw + 10) p.x = -10;
      if (p.y < -10) p.y = vh + 10;
      else if (p.y > vh + 10) p.y = -10;
    }

    // Líneas
    if (config.links.enable) {
      const distMax = config.links.distance;
      const distMax2 = distMax * distMax;
      ctx.lineWidth = config.links.width;
      ctx.strokeStyle = config.links.color;

      for (let i = 0; i < P.length; i++) {
        const a = P[i];
        for (let j = i + 1; j < P.length; j++) {
          const b = P[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 <= distMax2) {
            // Atenuar alfa según distancia
            const alpha = 1 - d2 / distMax2;
            ctx.globalAlpha = clamp(alpha, 0, 1) * parseFloat(config.particles.opacity);
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }
      ctx.globalAlpha = 1;
    }

    // Puntos
    ctx.fillStyle = config.particles.color;
    ctx.globalAlpha = clamp(config.particles.opacity, 0, 1);
    for (let i = 0; i < P.length; i++) {
      const p = P[i];
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  // ---------- Animación con rAF + throttle FPS ----------
  let lastTime = 0;
  const minFrameTime = 1000 / clamp(config.behavior.maxFPS || 60, 1, 240);
  let rafId = null;
  let running = true;

  function loop(ts) {
    if (!running) return;
    if (ts - lastTime >= minFrameTime) {
      const dt = ts - lastTime;
      lastTime = ts;
      step(dt);
    }
    rafId = requestAnimationFrame(loop);
  }

  // Pausar cuando la pestaña no esté visible (ahorro batería)
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      running = false;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;
    } else {
      running = true;
      lastTime = performance.now();
      rafId = requestAnimationFrame(loop);
    }
  });

  // Iniciar
  lastTime = performance.now();
  rafId = requestAnimationFrame(loop);
})();

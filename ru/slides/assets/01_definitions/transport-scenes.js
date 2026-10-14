/* A photon moves at constant distance per elapsed time along every flight.
   Drawings illustrate individual balance terms; they are not random samples. */
(() => {
  'use strict';
  const specs = {
    absorption: {
      points: [[80, 200], [350, 200], [620, 200]], initial: 0.38, disappears: true,
      describe: before => before ? 'До поглощения: фотон движется вдоль \\(\\hat{\\mathbf s}\\).' : 'Поглощение в \\(\\mathbf x\\): фотон перестаёт распространяться.'
    },
    'scatter-loss': {
      points: [[75, 220], [350, 220], [526, 74]], initial: 0.58,
      describe: before => before ? 'До рассеяния: фотон принадлежит выбранному \\(d\\Omega\\).' : 'После рассеяния: фотон продолжает движение вне \\(d\\Omega\\).'
    },
    'scatter-gain': {
      points: [[145, 340], [350, 200], [625, 200]], initial: 0.58,
      describe: before => before ? "До рассеяния: фотон движется вдоль \\(\\hat{\\mathbf s}'\\)." : 'После рассеяния: фотон движется вдоль \\(\\hat{\\mathbf s}\\) в выбранном \\(d\\Omega\\).'
    },

  };
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const controllers = [];
  const distance = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  const active = el => {
    const deck = window.Reveal;
    if (document.hidden || !el.isConnected || !deck?.isReady?.()) return false;
    if (deck.isOverview?.()) return false;
    if (deck.getCurrentSlide() !== el.closest('section.slide')) return false;
    for (let ancestor = el; ancestor && ancestor !== document.body; ancestor = ancestor.parentElement) {
      if (ancestor.hidden || ancestor.getAttribute('aria-hidden') === 'true') return false;
      const style = window.getComputedStyle(ancestor);
      if (style.display === 'none' || style.visibility === 'hidden') return false;
    }
    return true;
  };
  function create(el) {
    if (el.dataset.rteReady) return;
    const spec = specs[el.dataset.rteScene];
    if (!spec) return;
    el.dataset.rteReady = 'true';
    const photon = el.querySelector('[data-rte-photon]');
    const status = el.querySelector('[data-rte-status]');
    const segments = spec.points.slice(1).map((point, i) => distance(spec.points[i], point));
    const length = segments.reduce((a, b) => a + b, 0);
    const event = segments[0] / length;
    const duration = Number(el.dataset.duration) || 7000;
    let progress = spec.initial, frame = null, last = null, running = false;
    const pointAt = value => {
      let remaining = value * length;
      for (let i = 0; i < segments.length; i += 1) {
        if (remaining <= segments[i] || i === segments.length - 1) {
          const fraction = remaining / segments[i];
          return spec.points[i].map((a, axis) => a + fraction * (spec.points[i + 1][axis] - a));
        }
        remaining -= segments[i];
      }
      return spec.points.at(-1);
    };
    function draw() {
      const before = progress < event;
      const xy = pointAt(progress);
      photon.setAttribute('cx', xy[0].toFixed(2));
      photon.setAttribute('cy', xy[1].toFixed(2));
      photon.style.opacity = spec.disappears && !before ? '0' : '1';
      const message = spec.describe(before, xy);
      if (status.dataset.rteMessage !== message) {
        status.dataset.rteMessage = message;
        window.RteMath.setText(status, message);
      }
    }
    function stop() {
      running = false;
      el.dataset.rteAnimating = 'false';
      if (frame !== null) cancelAnimationFrame(frame);
      frame = null;
      last = null;
    }
    function tick(now) {
      if (!running) return;
      if (!active(el) || reduced.matches) { stop(); return; }
      if (last !== null) progress = (progress + (now - last) / duration) % 1;
      last = now;
      draw();
      frame = requestAnimationFrame(tick);
    }
    function sync() {
      if (!active(el)) { stop(); return; }
      if (reduced.matches) {
        stop();
        progress = spec.initial;
        draw();
        return;
      }
      if (running) return;
      progress = 0;
      last = null;
      running = true;
      el.dataset.rteAnimating = 'true';
      draw();
      frame = requestAnimationFrame(tick);
    }
    el.dataset.rteAnimating = 'false';
    draw();
    controllers.push({ sync });
  }
  const syncAll = () => controllers.forEach(controller => controller.sync());
  let hooked = false;
  function hookReveal() {
    if (hooked || !window.Reveal?.on) return;
    hooked = true;
    ['ready', 'slidechanged', 'overviewshown', 'overviewhidden'].forEach(event => {
      window.Reveal.on(event, syncAll);
    });
    syncAll();
  }
  function init() {
    document.querySelectorAll('[data-rte-scene]').forEach(create);
    hookReveal();
    document.addEventListener('visibilitychange', syncAll);
    document.addEventListener('tabby', syncAll);
    document.addEventListener('shown.bs.tab', syncAll);
    document.addEventListener('click', event => {
      if (event.target.closest('[role="tab"], .panel-tabset-tabby a, .nav-tabs a')) {
        requestAnimationFrame(syncAll);
      }
    });
    reduced.addEventListener('change', syncAll);
    window.addEventListener('load', () => { hookReveal(); syncAll(); }, { once: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();

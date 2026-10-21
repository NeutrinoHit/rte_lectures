/* Typeset LaTeX in SVG foreignObject labels and changing teaching controls. */
(() => {
  'use strict';
  const pending = new Map();
  let scheduled = false;
  let busy = false;
  function schedule(delay = 0) {
    if (scheduled || busy || !pending.size) return;
    scheduled = true;
    setTimeout(() => { scheduled = false; flush(); }, delay);
  }
  function enqueue(el, value, kind) {
    if (!el) return;
    const key = `${kind}:${value}`;
    if (el.dataset.rteMathValue === key && !pending.has(el)) return;
    pending.set(el, { value, kind, key });
    schedule();
  }
  function write(el, job) {
    el.textContent = job.kind === 'math' ? `\\(${job.value}\\)` : job.value;
    el.dataset.rteMathValue = job.key;
  }
  function done() {
    busy = false;
    document.dispatchEvent(new CustomEvent('rte:math-ready'));
    schedule();
  }
  // The shared footer switches MathJax 2 to its output renderer and typesets the deck
  // once. Work started before that goes through MathJax's default HTML-CSS output,
  // which is slow inside SVG labels and delays every formula of the lecture.
  const footer = document.querySelector('script[data-context-home]');
  function footerPending(engine) {
    return Boolean(footer && engine.Hub && !window.__neutrinohitMathJaxConfigured
      && performance.now() < 15000);
  }
  function flush() {
    if (busy || !pending.size) return;
    const engine = window.MathJax;
    if (!engine || (!engine.typesetPromise && !engine.Hub?.Queue) || footerPending(engine)) {
      schedule(100);
      return;
    }
    const jobs = [...pending].filter(([el]) => el.isConnected);
    pending.clear();
    if (!jobs.length) return;
    busy = true;
    if (engine.typesetPromise) {
      Promise.resolve(engine.startup?.promise).then(() => {
        const nodes = jobs.map(([el]) => el);
        engine.typesetClear?.(nodes);
        jobs.forEach(([el, job]) => write(el, job));
        return engine.typesetPromise(nodes);
      }).then(done, error => { console.error('RTE LaTeX labels:', error); done(); });
    } else {
      const commands = [];
      jobs.forEach(([el, job]) => {
        const jax = engine.Hub.getAllJax(el);
        el.dataset.rteMathValue = job.key;
        if (job.kind === 'math' && jax.length === 1) {
          commands.push(['Text', jax[0], job.value]);
        } else {
          jax.forEach(item => item.Remove());
          write(el, job);
          commands.push(['Typeset', engine.Hub, el]);
        }
      });
      engine.Hub.Queue(...commands, done);
    }
  }
  window.RteMath = {
    set: (el, tex) => enqueue(el, tex, 'math'),
    setText: (el, text) => enqueue(el, text, 'text'),
  };
  // The RevealJS math plugin typesets every label of the deck. Labels still holding
  // raw LaTeX after that are typeset here; the deck is not typeset a second time.
  function init() {
    document.querySelectorAll('.rte-svg-math, figcaption, .rte-scene-status, .rte-observable-controls label').forEach(el => {
      const text = el.textContent;
      if (/\\[([]/.test(text) && !pending.has(el)) enqueue(el, text, 'text');
    });
  }
  function afterDeckTypeset() {
    const engine = window.MathJax;
    if (engine?.typesetPromise) Promise.resolve(engine.startup?.promise).then(init);
    else if (engine?.Hub?.Queue && !footerPending(engine)) engine.Hub.Queue(init);
    else setTimeout(afterDeckTypeset, 100);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', afterDeckTypeset, { once: true });
  else afterDeckTypeset();
})();

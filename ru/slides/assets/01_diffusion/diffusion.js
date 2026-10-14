/* Analytic dimensionless diffusion kernels, sampled only to draw their graphs. */
(() => {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const H = (r, t, a = 0.01) => (4 * Math.PI * t / 3) ** -1.5 * Math.exp(-3 * r * r / (4 * t) - a * t);
  const Y = (r, a) => Math.exp(-r * Math.sqrt(3 * a)) / (4 * Math.PI * r);
  const P = (r, t) => 4 * Math.PI * r * r * H(r, t, 0);
  const number = (value, places = 2) => value.toFixed(places);
  const math = (el, tex) => {
    if (window.RteMath) window.RteMath.set(el, tex);
    else el.textContent = `\\(${tex}\\)`;
  };
  const mixed = (el, text) => {
    if (window.RteMath) window.RteMath.setText(el, text);
    else el.textContent = text;
  };
  const scale = (lo, hi, ymax) => ({
    x: r => 90 + 560 * (r - lo) / (hi - lo),
    y: value => 330 - 240 * value / ymax
  });
  function points(fn, lo, hi, s, count = 360) {
    return Array.from({length: count + 1}, (_, i) => {
      const r = lo + (hi - lo) * i / count;
      return `${s.x(r).toFixed(3)},${s.y(fn(r)).toFixed(3)}`;
    });
  }
  function drawCurve(el, fn, lo, hi, s) {
    el.querySelector('[data-rte-diffusion-curve]').setAttribute('d', `M${points(fn, lo, hi, s).join(' L')}`);
  }
  function flash(el) {
    const slider = el.querySelector('[data-rte-diffusion-time]');
    const s = scale(0, 18, H(0, 10));
    function draw() {
      const t = Number(slider.value);
      drawCurve(el, r => H(r, t), 0, 18, s);
      math(el.querySelector('[data-rte-diffusion-time-output]'), String.raw`T=${t}`);
      math(el.querySelector('[data-rte-diffusion-mass]'), String.raw`\frac{N(t)}{N}=e^{-aT}\simeq ${number(Math.exp(-0.01 * t))}`);
      math(el.querySelector('[data-rte-diffusion-rms]'), String.raw`\frac{r_{\mathrm{rms}}}{\ell_*}=\sqrt{2T}\simeq ${number(Math.sqrt(2 * t))}`);
      slider.setAttribute('aria-valuetext', `Безразмерное время ${t}`);
      el.querySelector('desc').textContent = `Диффузионное решение для точечной вспышки при безразмерном времени ${t}. Профиль расширяется при неизменной вертикальной шкале. Число фотонов составляет ${Math.exp(-0.01 * t).toFixed(2)} от начального; среднеквадратичный радиус равен ${Math.sqrt(2 * t).toFixed(2)} транспортных длин.`;
    }
    slider.addEventListener('input', draw);
    draw();
  }
  function stationary(el) {
    const slider = el.querySelector('[data-rte-diffusion-absorption]');
    const s = scale(3, 25, Y(3, 0));
    const marker = el.querySelector('[data-rte-diffusion-length-line]');
    function draw() {
      const a = Number(slider.value);
      const length = a > 0 ? 1 / Math.sqrt(3 * a) : Infinity;
      drawCurve(el, r => Y(r, a), 3, 25, s);
      marker.style.display = length >= 3 && length <= 25 ? '' : 'none';
      if (Number.isFinite(length)) marker.setAttribute('d', `M${s.x(length)} 80 V330`);
      const aTex = String.raw`a=${number(a, 3)}`;
      math(el.querySelector('[data-rte-diffusion-absorption-title]'), aTex);
      math(el.querySelector('[data-rte-diffusion-absorption-output]'), aTex);
      math(el.querySelector('[data-rte-diffusion-length]'), a > 0
        ? String.raw`\frac{L_D}{\ell_*}=\frac{1}{\sqrt{3a}}\simeq ${number(length)}`
        : String.raw`\frac{L_D}{\ell_*}\longrightarrow\infty`);
      slider.setAttribute('aria-valuetext', `Безразмерное поглощение ${a.toFixed(3)}`);
      mixed(el.querySelector('[data-rte-diffusion-status]'), a === 0
        ? String.raw`При \(a=0\): \(Y=1/(4\pi R)\), \(L_D\to\infty\). Начало координат исключено: точечный источник сингулярен при \(R=0\).`
        : length < 3
          ? String.raw`Длина затухания \(L_D/\ell_*<3\) находится левее показанного диапазона. Начало координат исключено: точечный источник сингулярен при \(R=0\).`
          : String.raw`Золотая линия отмечает \(R=L_D/\ell_*\). Начало координат исключено: точечный источник сингулярен при \(R=0\).`);
      el.querySelector('desc').textContent = a === 0
        ? 'Стационарный профиль без поглощения спадает обратно пропорционально расстоянию. Длина затухания бесконечна. Показаны расстояния от 3 до 25 транспортных длин.'
        : `Стационарный профиль при безразмерном поглощении ${a.toFixed(3)}. Длина затухания равна ${length.toFixed(2)} транспортных длин${length < 3 ? ' и лежит левее показанного диапазона' : ''}.`;
    }
    slider.addEventListener('input', draw);
    draw();
  }
  function svg(tag, attrs = {}) {
    const el = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, String(value)));
    return el;
  }
  function mathLabel(tex, x, y, width, height, tick = false) {
    const foreign = svg('foreignObject', {x, y, width, height});
    const div = document.createElementNS('http://www.w3.org/1999/xhtml', 'div');
    div.setAttribute('class', `rte-svg-math${tick ? ' rte-diffusion-tick' : ''}`);
    foreign.append(div);
    math(div, tex);
    return foreign;
  }
  function frontAxes(el, t, s, ymax) {
    const group = el.querySelector('[data-rte-diffusion-front-axes]');
    group.replaceChildren(svg('path', {class: 'rte-diffusion-axis', d: 'M90 80 V330 H655'}));
    const xticks = t === 1 ? [0, 1, 3, 5] : [0, 5, 15, 25];
    xticks.forEach(value => {
      group.append(svg('path', {class: 'rte-diffusion-axis', d: `M${s.x(value)} 330 V337`}), mathLabel(String(value), s.x(value) - 32, 337, 64, 43));
    });
    [0, ymax / 2, ymax].forEach(value => {
      group.append(svg('path', {class: 'rte-diffusion-axis', d: `M84 ${s.y(value)} H90`}), mathLabel(value === 0 ? '0' : number(value, t === 1 ? 2 : 3), 0, s.y(value) - 23, 78, 46, true));
    });
    group.append(mathLabel('R', 655, 314, 40, 42));
  }
  function front(el) {
    const selector = el.querySelector('[data-rte-diffusion-front-time]');
    const marker = el.querySelector('[data-rte-diffusion-front-line]');
    const label = el.querySelector('[data-rte-diffusion-front-label]').closest('foreignObject');
    const forbidden = el.querySelector('[data-rte-diffusion-forbidden]');
    function draw() {
      const t = Number(selector.value);
      const rmax = Math.max(5, t + 5), ymax = t === 1 ? 0.9 : 0.25;
      const s = scale(0, rmax, ymax), x = s.x(t);
      drawCurve(el, r => P(r, t), 0, rmax, s);
      el.querySelector('[data-rte-diffusion-tail]').setAttribute('d', `M${x},330 L${points(r => P(r, t), t, rmax, s, 240).join(' L')} L650,330 Z`);
      marker.setAttribute('d', `M${x} 80 V330`);
      label.setAttribute('x', String(x + 8));
      forbidden.setAttribute('x', String(x));
      forbidden.setAttribute('width', String(650 - x));
      math(el.querySelector('[data-rte-diffusion-front-title]'), String.raw`a=0,\qquad T=${t}`);
      frontAxes(el, t, s, ymax);
      el.querySelector('desc').textContent = `Радиальная диффузионная вероятность при безразмерном времени ${t}. Золотая линия отмечает причинный фронт на расстоянии ${t} транспортных длин. Справа от неё точное уравнение переноса даёт нулевую плотность, но диффузионное приближение сохраняет положительный хвост. Вертикальная шкала от нуля до ${ymax.toFixed(2)}.`;
    }
    selector.addEventListener('change', draw);
    draw();
  }
  function init() {
    document.querySelectorAll('[data-rte-diffusion]').forEach(el => {
      if (el.dataset.rteDiffusionReady) return;
      el.dataset.rteDiffusionReady = 'true';
      if (el.dataset.rteDiffusion === 'flash') flash(el);
      if (el.dataset.rteDiffusion === 'stationary') stationary(el);
      if (el.dataset.rteDiffusion === 'front') front(el);
      el.addEventListener('keydown', event => {
        if (event.target.matches('input, select')) event.stopPropagation();
      });
      el.querySelector('.rte-diffusion-controls').hidden = false;
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

/* Deterministic geometric response and exact bin integrals, not a photon simulation. */
(() => {
  'use strict';
  const svgNS = 'http://www.w3.org/2000/svg';
  const fmt = value => value.toFixed(2);
  const texNumber = value => value.toFixed(2);
  const setMath = (el, tex) => {
    if (window.RteMath) window.RteMath.set(el, tex);
    else el.textContent = `\\(${tex}\\)`;
  };
  const setText = (el, text) => {
    if (window.RteMath) window.RteMath.setText(el, text);
    else el.textContent = text;
  };
  const preventSlideKeys = el => el.addEventListener('keydown', event => {
    if (event.target.matches('input, select')) event.stopPropagation();
  });
  function detector(el) {
    const angle = el.querySelector('[data-rte-observable-angle]');
    const field = el.querySelector('[data-rte-observable-field]');
    const axis = el.querySelector('[data-rte-observable-axis]');
    const axisLabel = el.querySelector('[data-rte-observable-axis-label]').closest('foreignObject');
    const rate = el.querySelector('[data-rte-observable-rate]');
    const status = el.querySelector('[data-rte-observable-status]');
    function draw() {
      const alpha = Number(angle.value);
      const radians = alpha * Math.PI / 180;
      const c = Math.cos(radians);
      const acceptance = (1 + c) / 2;
      const isotropic = field.value === 'isotropic';
      const ox = -Math.cos(radians), oy = Math.sin(radians);
      axis.setAttribute('d', `M350 205 L${350 + 132 * ox} ${205 - 132 * oy}`);
      axisLabel.setAttribute('x', String(350 + 161 * ox + 28 * oy - 35));
      axisLabel.setAttribute('y', String(205 - 132 * oy + 28 * ox - 28));
      el.querySelector('[data-rte-observable-beam]').style.display = isotropic ? 'none' : '';
      el.querySelector('[data-rte-observable-isotropic]').style.display = isotropic ? '' : 'none';
      setMath(el.querySelector('[data-rte-observable-c]'), String.raw`c=-\hat{\mathbf s}\cdot\hat{\mathbf o}=${texNumber(c)}`);
      setMath(el.querySelector('[data-rte-observable-a]'), String.raw`a(c)=${texNumber(acceptance)}`);
      el.querySelector('[data-rte-observable-beam-values]').style.display = isotropic ? 'none' : '';
      el.querySelector('[data-rte-observable-isotropic-values]').style.display = isotropic ? '' : 'none';
      setMath(rate, String.raw`\frac{R}{A\eta F}=${texNumber(isotropic ? 0.5 : acceptance)}`);
      setMath(el.querySelector('[data-rte-observable-angle-output]'), String.raw`\alpha=${alpha}^{\circ}`);
      angle.setAttribute('aria-valuetext', `${alpha} градусов`);
      el.querySelector('desc').textContent = isotropic
        ? `Изотропное поле с фиксированной полной интенсивностью. Ось ОМ повёрнута на ${alpha} градусов; нормированный средний отклик равен половине при любом повороте, векторный поток равен нулю.`
        : `Луч движется вправо к ОМ. Ось лицевой стороны ОМ повёрнута на ${alpha} градусов относительно встречного направления. Косинус угла прихода равен ${fmt(c)}, нормированный отклик равен ${fmt(acceptance)}.`;
      setText(status, isotropic
        ? String.raw`Изотропное поле: \(\langle a\rangle_{\Omega}=\frac12\) при любом повороте ОМ. Векторный поток \(\mathbf J=0\), но отклик положителен.`
        : String.raw`\(A\) и \(\eta\) фиксированы. В обоих полях одинаковая полная интенсивность \(F\); поворот меняет отклик на луч.`);
    }
    angle.addEventListener('input', draw);
    field.addEventListener('change', draw);
    preventSlideKeys(el);
    el.querySelector('.rte-observable-controls').hidden = false;
    draw();
  }
  function timeBins(el) {
    const slider = el.querySelector('[data-rte-observable-window-end]');
    const bins = el.querySelector('[data-rte-observable-bins]');
    const shade = el.querySelector('[data-rte-observable-shade]');
    const endLine = el.querySelector('[data-rte-observable-end-line]');
    const total = 10, tau = 25, width = 10;
    const x = t => 90 + 560 * t / 150;
    const y = r => 330 - 600 * r;
    const rate = t => total / tau * Math.exp(-t / tau);
    const integral = (a, b) => total * (Math.exp(-a / tau) - Math.exp(-b / tau));
    function draw() {
      const end = Number(slider.value);
      const points = Array.from({length: end + 1}, (_, t) => `${x(t)},${y(rate(t))}`).join(' L');
      shade.setAttribute('d', `M${x(0)},330 L${points} L${x(end)},330 Z`);
      bins.replaceChildren();
      for (let a = 0; a < end; a += width) {
        const b = Math.min(a + width, end);
        const charge = integral(a, b), mean = charge / (b - a);
        const rect = document.createElementNS(svgNS, 'rect');
        rect.setAttribute('x', String(x(a)));
        rect.setAttribute('y', String(y(mean)));
        rect.setAttribute('width', String(x(b) - x(a)));
        rect.setAttribute('height', String(330 - y(mean)));
        rect.setAttribute('class', 'rte-observable-bin');
        const title = document.createElementNS(svgNS, 'title');
        title.textContent = `От ${a} до ${b} наносекунд: заряд ${fmt(charge)} фотоэлектрона; средняя скорость ${fmt(mean)} фотоэлектрона в наносекунду`;
        rect.append(title);
        bins.append(rect);
      }
      endLine.setAttribute('d', `M${x(end)} 80 V330`);
      setMath(el.querySelector('[data-rte-observable-window-output]'), String.raw`T=${end}\,\text{нс}`);
      setMath(el.querySelector('[data-rte-observable-charge]'), String.raw`Q_{[0,T]}=${texNumber(integral(0, end))}\,\text{ф.э.}`);
      slider.setAttribute('aria-valuetext', `${end} наносекунд`);
      el.querySelector('desc').textContent = `Учебный причинный профиль с полным зарядом 10 фотоэлектронов и временем 25 нс. Окно от нуля до ${end} наносекунд содержит ${fmt(integral(0, end))} фотоэлектрона. Высота прямоугольников шириной 10 наносекунд равна средней скорости прихода, а площадь — заряду бина. Хвост за окном сохраняется.`;
      setText(el.querySelector('[data-rte-observable-status]'), String.raw`Высота столбика — \(B/\Delta T\); его площадь — \(B\). При \(T=${end}\,\text{нс}\) окно содержит \(${texNumber(integral(0, end))}\) из \(10\) ф.э. Хвост за окном сохраняется.`);
    }
    slider.addEventListener('input', draw);
    preventSlideKeys(el);
    el.querySelector('.rte-observable-controls').hidden = false;
    draw();
  }
  function init() {
    document.querySelectorAll('[data-rte-observable]').forEach(el => {
      if (el.dataset.rteObservableReady) return;
      el.dataset.rteObservableReady = 'true';
      if (el.dataset.rteObservable === 'detector') detector(el);
      if (el.dataset.rteObservable === 'time-bins') timeBins(el);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

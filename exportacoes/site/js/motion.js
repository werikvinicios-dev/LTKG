// Movimento do livro: a logo que se monta (a mesma coreografia do trailer), as leis que se montam com a rolagem,
// a neve de Vhalessa e o congelamento do último carrasco. Só transform, opacity, clip-path e máscara.
export const reduzido = matchMedia("(prefers-reduced-motion: reduce)").matches;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const eo = x => 1 - Math.pow(1 - clamp(x), 3);
export const ei = x => Math.pow(clamp(x), 3);
export const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eob = (x, s = 1.9) => { x = clamp(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; };
const env = (t, a, b, c, d) => t < a || t > d ? 0 : t < b ? seg(t, a, b) : t < c ? 1 : 1 - seg(t, c, d);

// ------------------------------------------------------------------ a logo
const TP = { arco: .45, estandarte: .8, eixo: 1.32, balanca: 1.85, halo: 3.9 };
const PEROLAS = [2.1, 2.175, 2.25, 2.325, 2.4, 2.475, 2.55];
const LETRAS = [4.0, 4.8], FILETE = 4.75, SUB = 5.0, FIM = 5.9;

function peca(dados, base, tam) {
  const im = new Image();
  im.src = dados.src; im.alt = ""; im.decoding = "async"; im.draggable = false;
  im.style.left = dados.x / tam[0] * 100 + "%"; im.style.top = dados.y / tam[1] * 100 + "%";
  im.style.width = dados.w / tam[0] * 100 + "%";
  base.appendChild(im);
  return im;
}
const origem = (im, d, ox, oy) => { im.style.transformOrigin = `${(ox - d.x) / d.w * 100}% ${(oy - d.y) / d.h * 100}%`; };

export function montarLogo(caixaEmb, caixaLet, P, extra = {}) {
  const E = P.emblema, L = P.letreiro, T = [E.tam, E.tam];
  const ordem = ["halo", "arco_e", "arco_d", "estandarte", "travessao", "prato_e", "prato_d", "eixo", "coroa"];
  const im = {};
  for (const k of ordem) im[k] = peca(E[k], caixaEmb, T);
  im.perolas = E.perolas.map(d => peca(d, caixaEmb, T));
  origem(im.halo, E.halo, 512, 512); origem(im.arco_e, E.arco_e, 512, 512); origem(im.arco_d, E.arco_d, 512, 512);
  origem(im.travessao, E.travessao, E.pivo[0], E.pivo[1]); origem(im.eixo, E.eixo, E.ponta[0], E.ponta[1]); origem(im.coroa, E.coroa, 512, 110);
  E.ganchos.forEach((g, i) => origem(im[i ? "prato_d" : "prato_e"], E[i ? "prato_d" : "prato_e"], g[0], g[1]));
  im.perolas.forEach((p, i) => origem(p, E.perolas[i], E.perolas[i].x + E.perolas[i].w / 2, E.perolas[i].y + E.perolas[i].h / 2));
  const glifos = L.glifos.map(g => { const p = peca(g, caixaLet, L.tam); origem(p, g, g.cx, g.cy); return p; });
  const filete = peca(L.filete, caixaLet, L.tam), sub = peca(L.sub, caixaLet, L.tam);
  // brilhos dos encaixes, a onda de choque e as faíscas
  const brilho = (x, y, r) => { const b = document.createElement("div"); b.className = "brilho"; Object.assign(b.style, { left: (x - r) / 10.24 + "%", top: (y - r) / 10.24 + "%", width: r / 5.12 + "%", height: r / 5.12 + "%" }); caixaEmb.appendChild(b); return b; };
  const fl = { eixo: brilho(512, 990, 110), estandarte: brilho(512, 820, 80), arco: brilho(512, 140, 90), balanca: brilho(512, 268, 90), halo: brilho(512, 420, 260) };
  const flP = E.perolas.map(d => brilho(d.x + d.w / 2, d.y + d.h / 2, 46));
  const onda = document.createElement("div"); onda.className = "onda"; caixaEmb.appendChild(onda);
  const cv = document.createElement("canvas"); cv.className = "faisca"; caixaEmb.appendChild(cv);
  const ctx = cv.getContext("2d");
  const rng = (() => { let s = 31; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  const faiscas = Array.from({ length: 34 }, () => ({ a: -Math.PI * (.05 + rng() * .9), v: .3 + rng() * .6, vida: .25 + rng() * .5 }));

  const tr = (el, s) => { el.style.transform = s; };
  function quadro(t) {
    const R = caixaEmb.getBoundingClientRect().width / 1024;
    // halo
    let k = seg(t, TP.halo - .5, TP.halo), e = eob(k, 1.2);
    tr(im.halo, `rotate(${(1 - e) * 28}deg) scale(${lerp(1.7, 1, e)})`); im.halo.style.opacity = eo(k);
    // arco
    k = seg(t, TP.arco - .42, TP.arco); e = eob(k);
    for (const [n, lado] of [["arco_e", -1], ["arco_d", 1]]) { tr(im[n], `translateX(${lado * (1 - e) * 420 * R}px) rotate(${-lado * (1 - e) * 9}deg)`); im[n].style.opacity = eo(Math.min(1, k * 1.6)); }
    // estandarte desenrolando
    k = seg(t, TP.estandarte - .36, TP.estandarte);
    const corte = lerp(195, 875, eo(k)), d = E.estandarte;
    im.estandarte.style.clipPath = `inset(0 0 ${clamp((d.y + d.h - corte) / d.h) * 100}% 0)`; im.estandarte.style.opacity = k > 0 ? 1 : 0;
    // espada
    const te = TP.eixo; let dy = 0, tremor = 0;
    if (t < te) { k = seg(t, te - .34, te); dy = -(1 - k * k) * 1150; }
    else { const tau = t - te; dy = tau < .1 ? 16 * Math.sin(tau / .1 * Math.PI) : 0; tremor = 2.4 * Math.exp(-tau * 5.5) * Math.sin(2 * Math.PI * 8.5 * tau); }
    tr(im.eixo, `translateY(${dy * R}px) rotate(${-tremor}deg)`); im.eixo.style.opacity = t > te - .34 ? 1 : 0;
    im.eixo.style.filter = t < te && t > te - .34 ? `blur(${1 + 3 * seg(t, te - .34, te)}px)` : "none";
    // balança: desce, pousa na guarda e oscila
    const tb = TP.balanca; k = seg(t, tb - .3, tb);
    const queda = -(1 - k * k) * 240, tau = t - tb;
    const th = tau <= 0 ? 0 : 15 * Math.exp(-tau * 1.45) * Math.cos(2 * Math.PI * 1.05 * tau) * (1 - seg(tau, 1.6, 2.1));
    const a_ = Math.min(1, k * 2.5);
    tr(im.travessao, `translateY(${queda * R}px) rotate(${-th}deg)`); im.travessao.style.opacity = a_;
    E.ganchos.forEach(([gx, gy], i) => {
      const r = th * Math.PI / 180, P0 = E.pivo[0], P1 = E.pivo[1];
      const nx = P0 + (gx - P0) * Math.cos(r) + (gy - P1) * Math.sin(r), ny = P1 - (gx - P0) * Math.sin(r) + (gy - P1) * Math.cos(r);
      const el = im[i ? "prato_d" : "prato_e"];
      tr(el, `translate(${(nx - gx) * R}px, ${(ny - gy + queda) * R}px) rotate(${th * .35}deg)`); el.style.opacity = a_;
    });
    // coroa
    k = seg(t, TP.arco - .1, TP.arco + .25);
    tr(im.coroa, `scale(${lerp(.6, 1, eob(k))})`); im.coroa.style.opacity = Math.min(1, k * 2);
    // pérolas
    PEROLAS.forEach((tp, i) => {
      const kk = seg(t, tp - .12, tp);
      tr(im.perolas[i], `rotate(${-tremor}deg) scale(${Math.max(.01, eob(kk, 2.6))})`); im.perolas[i].style.opacity = Math.min(1, kk * 2);
      flP[i].style.opacity = .55 * env(t, tp, tp + .02, tp + .05, tp + .35);
    });
    for (const [n, b] of Object.entries(fl)) { const tp = TP[n] ?? TP.balanca; b.style.opacity = (n === "halo" || n === "eixo" ? 1 : .7) * env(t, tp, tp + .015, tp + .06, tp + (n === "halo" || n === "eixo" ? .9 : .45)); }
    // onda de choque do halo
    k = seg(t, TP.halo, TP.halo + .7); onda.style.opacity = k > 0 && k < 1 ? .9 * (1 - k) : 0; onda.style.transform = `translate(-50%,-50%) scale(${lerp(.3, 5.5, eo(k))})`;
    // tranco do impacto
    const ti = t - te, f = ti > 0 && ti < .45 ? Math.exp(-ti * 9) * 9 : 0;
    caixaEmb.style.transform = f ? `translate(${f * Math.sin(ti * 95)}px, ${f * 1.4 * Math.cos(ti * 71)}px)` : "";
    // faíscas da ponta
    const W = cv.width = caixaEmb.clientWidth * devicePixelRatio, H = cv.height = caixaEmb.clientHeight * devicePixelRatio;
    ctx.clearRect(0, 0, W, H);
    if (ti > 0 && ti < .9) {
      const px = W * .5, py = H * (990 / 1024), g = 3.2 * H;
      ctx.fillStyle = "rgba(255,190,110,1)";
      for (const s of faiscas) { if (ti > s.vida) continue; ctx.globalAlpha = 1 - ti / s.vida;
        const x = px + Math.cos(s.a) * s.v * H * ti, y = py + Math.sin(s.a) * s.v * H * ti + .5 * g * ti * ti;
        ctx.beginPath(); ctx.arc(x, y, 1.6 * devicePixelRatio, 0, 7); ctx.fill(); }
      ctx.globalAlpha = 1;
    }
    // letreiro: letras encaixando, filete crescendo, subtítulo
    glifos.forEach((g, i) => {
      const tp = lerp(LETRAS[0], LETRAS[1], i / Math.max(1, glifos.length - 1)), kk = seg(t, tp - .22, tp), ee = eob(kk, 2.2), lado = i % 2 ? -1 : 1;
      const Rl = caixaLet.getBoundingClientRect().width / 1024;
      tr(g, `translateY(${-(1 - ee) * 60 * Rl}px) rotate(${-lado * (1 - ee) * 14}deg) scale(${lerp(1.25, 1, ee)})`); g.style.opacity = Math.min(1, kk * 2.2);
    });
    k = eio(seg(t, FILETE, FILETE + .4)); const fd = L.filete;
    const esq = clamp((512 - k * 380 - fd.x) / fd.w), dir = clamp((fd.x + fd.w - (512 + k * 380)) / fd.w);
    filete.style.clipPath = `inset(0 ${dir * 100}% 0 ${esq * 100}%)`;
    k = eo(seg(t, SUB, SUB + .5)); tr(sub, `translateY(${(1 - k) * 8}px)`); sub.style.opacity = k;
    extra.aoQuadro?.(t);
  }
  let t0 = null, raf = 0;
  function passo(ts) { if (t0 === null) t0 = ts; const t = (ts - t0) / 1000; quadro(t); if (t < FIM + .9) raf = requestAnimationFrame(passo); }
  const tocar = () => { cancelAnimationFrame(raf); t0 = null; raf = requestAnimationFrame(passo); };
  if (reduzido) quadro(99); else tocar();
  return { tocar, quadro };
}

// ------------------------------------------------------------------ uma lei se montando (u: segundos desde o início da montagem)
export const MONTA = 1.4;
export function montarLei(fig, dados) {
  const [w, h] = dados.tam;
  fig.style.setProperty("--ar", (w / h).toFixed(4));
  const T = [w, h];
  const estr = peca(dados.estrutura, fig, T), eixo = peca(dados.eixo, fig, T);
  const pecas = dados.pecas.map(p => ({ d: p, el: peca(p, fig, T) }));
  const halo = document.createElement("div"); halo.className = "halo-lei"; fig.appendChild(halo);
  const de = dados.estrutura;
  const cx = (dados.cen[0] - de.x) / de.w * 100, cy = (dados.cen[1] - de.y) / de.h * 100;
  estr.style.transformOrigin = `${cx}% ${cy}%`;
  pecas.forEach(({ d, el }) => { el.style.transformOrigin = "50% 50%"; });
  return function (u) {
    const R = fig.clientHeight / h;
    // estrutura traçada como a compasso a partir do alto, dos dois lados
    const ke = seg(u, .28, 1.0), A = Math.min(180, eo(ke) * 1.08 * 180);
    const masc = ke >= 1 ? "none" : `conic-gradient(from 0deg at ${cx}% ${cy}%, #000 0deg ${A}deg, transparent ${A}deg ${360 - A}deg, #000 ${360 - A}deg)`;
    estr.style.maskImage = estr.style.webkitMaskImage = masc;
    estr.style.transform = `rotate(${-(1 - eob(seg(u, .28, 1.15), 1.4)) * 22}deg)`;
    estr.style.opacity = ke > 0 ? 1 : 0;
    // eixo crescendo do centro para as pontas
    const ext = eo(seg(u, 0, .45)) * h * .52, d = dados.eixo;
    const top = clamp((h / 2 - ext - d.y) / d.h), bot = clamp((d.y + d.h - (h / 2 + ext)) / d.h);
    eixo.style.clipPath = `inset(${top * 100}% 0 ${bot * 100}% 0)`; eixo.style.opacity = u > 0 ? 1 : 0;
    // pérolas descem pelo eixo e travam; a gema cresce do centro
    pecas.forEach(({ d, el }, j) => {
      const tj = .82 + j * .09, kp = seg(u, tj, tj + .3);
      el.style.opacity = Math.min(1, kp * 3);
      el.style.transform = d.tipo === "gema" ? `scale(${Math.max(.02, eob(kp, 2.6))})` : `translateY(${-(1 - eob(kp, 2.2)) * h * .28 * R}px)`;
    });
    halo.style.opacity = .9 * env(u, MONTA, MONTA + .03, MONTA + .08, MONTA + .6);
  };
}

// ------------------------------------------------------------------ neve de Vhalessa (três profundidades)
export function neve(canvas) {
  const ctx = canvas.getContext("2d");
  let W = 0, H = 0, flocos = [], ativo = true, parada = false, vento = .25;
  const criar = () => {
    W = canvas.width = innerWidth * devicePixelRatio; H = canvas.height = innerHeight * devicePixelRatio;
    const n = Math.round(Math.min(220, innerWidth * innerHeight / 7000));
    flocos = Array.from({ length: n }, () => { const z = Math.random(); return { x: Math.random() * W, y: Math.random() * H, z, r: (.6 + z * 2.4) * devicePixelRatio, f: Math.random() * 6.28 }; });
  };
  criar(); addEventListener("resize", criar);
  let ult = performance.now();
  function passo(ts) {
    const dt = Math.min(.05, (ts - ult) / 1000); ult = ts;
    if (ativo) {
      ctx.clearRect(0, 0, W, H);
      for (const p of flocos) {
        if (!parada) {
          p.f += dt * (.6 + p.z);
          p.y += (18 + 52 * p.z) * dt * devicePixelRatio;
          p.x += (Math.sin(p.f) * 8 + vento * 40 * p.z) * dt * devicePixelRatio;
          if (p.y > H + 5) { p.y = -5; p.x = Math.random() * W; }
          if (p.x > W + 5) p.x = -5;
        }
        ctx.globalAlpha = .18 + .5 * p.z;
        ctx.fillStyle = "#eef3fa";
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 7); ctx.fill();
      }
    }
    requestAnimationFrame(passo);
  }
  if (!reduzido) requestAnimationFrame(passo);
  return { mostrar(v) { ativo = v; canvas.style.display = v ? "" : "none"; }, parar(v) { parada = v; }, vento(v) { vento = v; } };
}

// ------------------------------------------------------------------ atos presos à rolagem
export function atos(raiz, aoAto) {
  const lista = [...raiz.querySelectorAll("[data-ato]")];
  function medir() {
    for (const el of lista) {
      const r = el.getBoundingClientRect(), total = el.offsetHeight - innerHeight;
      const p = total > 0 ? clamp(-r.top / total) : (r.top < innerHeight ? 1 : 0);
      const visivel = r.bottom > 0 && r.top < innerHeight;
      el.style.setProperty("--p", p.toFixed(4));
      aoAto(el.dataset.ato, p, visivel, el);
    }
  }
  let pendente = false;
  const pedir = () => { if (!pendente) { pendente = true; requestAnimationFrame(() => { pendente = false; medir(); }); } };
  addEventListener("scroll", pedir, { passive: true }); addEventListener("resize", pedir);
  medir();
  return () => { removeEventListener("scroll", pedir); removeEventListener("resize", pedir); };
}

// geada que cresce das bordas (cristais desenhados uma vez; a revelação segue g)
export function geada(canvas) {
  const ctx = canvas.getContext("2d");
  let linhas = [];
  const criar = () => {
    const W = canvas.width = canvas.clientWidth * devicePixelRatio, H = canvas.height = canvas.clientHeight * devicePixelRatio;
    let s = 17; const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
    linhas = [];
    for (let i = 0; i < 150; i++) {
      const lado = Math.floor(r() * 4);
      let x = lado < 2 ? r() * W : (lado === 2 ? 0 : W), y = lado < 2 ? (lado === 0 ? 0 : H) : r() * H;
      let a = [Math.PI / 2, -Math.PI / 2, 0, Math.PI][lado] + (r() - .5);
      const passos = 8 + Math.floor(r() * 24);
      for (let k = 0; k < passos; k++) {
        const nx = x + Math.cos(a) * 9 * devicePixelRatio, ny = y + Math.sin(a) * 9 * devicePixelRatio;
        linhas.push([x, y, nx, ny, k / 32]);
        if (r() < .35) { const aa = a + (r() < .5 ? -1 : 1), c = (4 + r() * 8) * devicePixelRatio; linhas.push([nx, ny, nx + Math.cos(aa) * c, ny + Math.sin(aa) * c, k / 32]); }
        x = nx; y = ny; a += (r() - .5) * .5;
      }
    }
  };
  addEventListener("resize", criar);
  let pronto = false;
  return function (g) {
    if (!pronto) { criar(); pronto = true; }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (g <= 0) return;
    ctx.strokeStyle = "rgba(232,242,252,.8)"; ctx.lineWidth = devicePixelRatio;
    ctx.beginPath();
    for (const [x, y, nx, ny, d] of linhas) if (d <= g) { ctx.moveTo(x, y); ctx.lineTo(nx, ny); }
    ctx.stroke();
  };
}

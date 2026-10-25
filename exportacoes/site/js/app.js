// Leis para Matar Deuses — o livro digital. Salas: Pórtico, Biblioteca, Leitor (#cap-NN), Registro, Atlas e Galeria.
// Progresso, marcadores e ajustes ficam só no navegador do leitor (localStorage).
import { montarLogo, montarLei, MONTA, neve, atos, geada, seg, eo, eio, reduzido } from "./motion.js";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const dois = n => String(n).padStart(2, "0");
const sem = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

// ------------------------------------------------------------------ estado do leitor
const CHAVE = "lmd:estado";
const PADRAO = { prog: {}, pos: null, marcadores: [], prefs: { tema: "noite", fonte: 1.18, entre: 1.7, largura: 36, volume: .5 }, revelar: false };
let estado = (() => { try { return Object.assign(structuredClone(PADRAO), JSON.parse(localStorage.getItem(CHAVE) || "{}")); } catch { return structuredClone(PADRAO); } })();
estado.prefs = Object.assign({}, PADRAO.prefs, estado.prefs);
let salvarT = 0;
const salvar = () => { clearTimeout(salvarT); salvarT = setTimeout(() => { try { localStorage.setItem(CHAVE, JSON.stringify(estado)); } catch { } }, 400); };
const alcancado = () => Math.max(0, ...Object.entries(estado.prog).filter(([, f]) => f >= .12).map(([n]) => +n));
const aberto = cap => estado.revelar || cap <= alcancado();

function aviso(txt) { const a = $("#aviso"); a.textContent = txt; a.classList.add("ver"); clearTimeout(a._t); a._t = setTimeout(() => a.classList.remove("ver"), 2600); }

// ------------------------------------------------------------------ dados
const D = {};
const capCache = {};
const json = u => fetch(u).then(r => { if (!r.ok) throw new Error(u); return r.json(); });
const capitulo = n => capCache[n] ||= json(`data/cap${dois(n)}.json`);

// ------------------------------------------------------------------ salas e rotas
const SALAS = ["portico", "biblioteca", "registro", "atlas", "galeria"];
let limpar = [];
let NEVE;
function rota() {
  const h = location.hash.slice(1);
  if (/^cap-\d\d$/.test(h)) return { sala: "cap", n: +h.slice(4) };
  return { sala: SALAS.includes(h) ? h : "portico" };
}
async function abrir(r = rota(), comVeu = true) {
  const veu = $("#veu");
  if (comVeu && !reduzido) { veu.classList.add("ativo"); await new Promise(f => setTimeout(f, 260)); }
  limpar.forEach(f => f()); limpar = [];
  fecharPaineis();
  const main = $("#conteudo");
  $$("[data-sala]").forEach(a => a.toggleAttribute("aria-current", a.dataset.sala === r.sala || (r.sala === "cap" && a.dataset.sala === "biblioteca")));
  $$("[data-sala][aria-current]").forEach(a => a.setAttribute("aria-current", "page"));
  NEVE?.mostrar(r.sala !== "cap"); NEVE?.parar(false);
  try {
    if (r.sala === "cap") await leitor(main, r.n);
    else { ({ portico, biblioteca, registro, atlas, galeria })[r.sala](main); scrollTo(0, 0); }
  } catch (e) { main.innerHTML = `<div class="sala-topo"><h1 class="titulo">Não foi possível abrir esta página</h1><p>${esc(e.message)}. Recarregue a página para tentar de novo.</p></div>`; }
  main.focus({ preventScroll: true });
  veu.classList.remove("ativo");
}
addEventListener("hashchange", () => abrir());

// barra que se recolhe ao descer e volta ao subir
let ultY = 0;
addEventListener("scroll", () => { const y = scrollY; $("#barra").dataset.oculta = y > 240 && y > ultY ? "true" : "false"; ultY = y; }, { passive: true });

// ------------------------------------------------------------------ Pórtico
function arte(nome) { return D.extras.galeria.find(g => g.img.src.includes(nome))?.img.src; }
function portico(main) {
  const c1 = D.obra.capitulos[0];
  const ilan = D.reg.elenco.find(e => e.nome.startsWith("Ilan"));
  const frase = (txt) => txt.split(" ").map(p => `<span class="pal fora">${p}</span>`).join(" ");
  const cont = estado.pos ? D.obra.capitulos[estado.pos.n - 1] : null;
  main.innerHTML = `
  <section class="ato abertura" aria-label="Leis para Matar Deuses">
    <div class="fundo" id="fundo-ab"></div>
    <div class="palco-logo">
      <div class="emblema" id="emb" role="img" aria-label="O emblema de Aresta: arco, espada, balança e sete pérolas"></div>
      <h1 class="so-leitor">Leis para Matar Deuses</h1>
      <div class="letreiro" id="let" aria-hidden="true"></div>
      <p class="credito">Uma saga de Werik Martins</p>
      <button class="repetir" type="button" id="b-repetir">Ver a logo se montar de novo</button>
    </div>
    <div class="rolar" aria-hidden="true"><span></span>Desça</div>
  </section>
  <section class="ato" data-ato="vhalessa" style="--rolagem:230vh">
    <div class="palco"><div class="quadro" style="background-image:url(${c1.abertura.src})"></div>
      <div class="frase"><p class="olho" style="margin-bottom:1rem">Vhalessa · véspera do Acendimento</p>
        <p>${frase("Em Aresta, a magia não cria poder.")} <em>${frase("Ela o move.")}</em></p>
        <p class="legenda-ato">Na cidade mais fria do Norte, quem aquece as casas é um deus. E tudo que se move deixa um preço.</p></div></div>
  </section>
  <section class="ato" data-ato="leis" style="--rolagem:950vh" aria-label="As Sete Leis">
    <div class="palco"><div class="leis-palco">
      <div class="leis-topo"><p class="olho">O que todo mago aprende primeiro</p><h2 class="titulo">As Sete Leis</h2></div>
      <div class="trilho" id="trilho">${D.reg.leis.map(l => `<div class="lei-c"><div class="lei-fig" data-lei="${l.id}"></div>
        <span class="lei-num">${l.num}</span><span class="lei-nome">${esc(l.nome)}</span><span class="lei-frase">${esc(l.frase)}</span></div>`).join("")}</div>
      <p class="leis-pe">Valem para mortais, deuses e dragões. Nenhum selo, nenhuma coroa e nenhuma prece muda uma vírgula delas.</p>
    </div></div>
  </section>
  <section class="ato" data-ato="carrasco" style="--rolagem:320vh" aria-label="O último carrasco">
    <div class="palco carrasco"><div class="quadro" id="q-carrasco" style="background-image:url(${arte("ponte_nevasca") || c1.abertura.src})"></div>
      <canvas class="cristais" id="cristais"></canvas><div class="geada" id="geada"></div>
      <img class="selo-ordem" id="selo" src="pecas/selo_ordem.webp" alt="O selo de cera da Ordem da Última Sentença">
      <div class="frase"><p class="olho">Ilan Varek</p><h2 class="titulo" id="t-carrasco">O Último Carrasco</h2><p>${esc(ilan?.x || "")}</p></div></div>
  </section>
  <section class="faixa"><div class="dentro">
    <div class="cabeca"><p class="olho">O Volume I em seis partes</p><h2 class="titulo">Cada parte, uma lei</h2>
      <p>${D.obra.capitulos.length} capítulos, ${Math.round(D.obra.capitulos.reduce((s, c) => s + c.palavras, 0) / 1000)} mil palavras e uma ilustração em cada abertura.</p></div>
    <div class="partes">${D.obra.partes.map(p => `<a class="parte" href="#biblioteca" data-parte="${p.num}"><img src="${p.img.src}" alt="" loading="lazy">
      <span class="olho">Parte ${p.num} · ${esc(p.lei)}</span><h3>${esc(p.titulo)}</h3><p>${esc(p.epigrafe)}</p><small>Capítulos ${p.de} a ${p.ate}</small></a>`).join("")}</div>
  </div></section>
  <section class="faixa"><div class="dentro">
    <div class="cabeca"><p class="olho">Trailer oficial</p><h2 class="titulo">Para derrubar um deus</h2></div>
    <div class="trailer" id="trailer" style="background-image:url(midia/trailer.webp)"><button type="button" aria-label="Assistir ao trailer"><span><svg viewBox="0 0 24 24"><path d="M6 4l14 8-14 8z"/></svg></span></button></div>
  </div></section>
  <section class="faixa"><div class="dentro convite">
    <p class="olho">${cont ? "Você parou aqui" : "A leitura começa numa rua gelada"}</p>
    <h2 class="titulo">${cont ? esc(cont.titulo) : "Onze páginas de contrato"}</h2>
    <div class="ornamento"><i></i></div>
    <div class="linha">
      <a class="botao cheio" href="#cap-${dois(cont ? cont.n : 1)}">${cont ? `Continuar <small>capítulo ${cont.n}</small>` : "Começar a leitura"}</a>
      <a class="botao" href="#biblioteca">Ver todos os capítulos</a></div>
  </div></section>
  <footer class="rodape">Leis para Matar Deuses · Volume I · © Werik Martins. Trilha e efeitos do trailer: bancos de som CC0.</footer>`;
  // a logo se monta (a mesma coreografia do trailer)
  const fundo = $("#fundo-ab");
  const logo = montarLogo($("#emb"), $("#let"), D.extras.pecas, { aoQuadro: t => { fundo.style.opacity = .7 + .3 * eo(seg(t, 3.9, 4.6)); } });
  $("#b-repetir").onclick = () => logo.tocar();
  // as leis se montando com a rolagem
  const figs = $$(".lei-fig").map(f => montarLei(f, D.extras.pecas.leis[f.dataset.lei]));
  const trilho = $("#trilho"), cartas = $$(".lei-c", trilho);
  const palavras = $$("[data-ato='vhalessa'] .pal");
  const qv = $("[data-ato='vhalessa'] .quadro"), qc = $("#q-carrasco"), ge = $("#geada"), selo = $("#selo"), tc = $("#t-carrasco");
  const cristais = geada($("#cristais"));
  const TL = 0.4 + 6 * 1.2 + MONTA + 1.6;
  limpar.push(atos(main, (ato, p, vis) => {
    if (ato === "vhalessa") {
      qv.style.transform = `scale(${1.16 - .12 * p}) translateY(${(p - .5) * -4}%)`;
      palavras.forEach((w, i) => w.classList.toggle("fora", p < .12 + i * .075));
    } else if (ato === "leis") {
      const T = p * TL;
      figs.forEach((f, i) => f(T - (0.4 + i * 1.2)));
      const cw = cartas[0].offsetWidth, vw = innerWidth;
      const fi = Math.max(0, Math.min(6, (T - .9) / 1.2));
      const k = eio(seg(T, TL - 2.2, TL - .4)), caber = Math.min(1, (vw - 32) / (cw * 7));
      const foco = (fi + .5) * cw, todo = cw * 3.5;
      const x = vw / 2 - (foco + (todo - foco) * k) * (1 + (caber - 1) * k);
      trilho.style.transform = `translateX(${x}px) scale(${1 + (caber - 1) * k})`;
      trilho.style.transformOrigin = "0 50%";
      cartas.forEach((c, i) => { c.style.opacity = .35 + .65 * Math.max(k, Math.min(1, Math.max(0, 1 - Math.abs(fi - i) * .55))); });
    } else if (ato === "carrasco") {
      const g = eio(seg(p, .3, .52));                       // o tempo para
      NEVE?.parar(vis && p > .3);
      qc.style.transform = `scale(${1.08 - .05 * Math.min(p, .3) / .3 + .03 * eo(seg(p, .3, .36))})`;
      qc.style.filter = `grayscale(${.75 * g}) brightness(${1 + .1 * g}) hue-rotate(${-8 * g}deg) contrast(${1 + .1 * g})`;
      ge.style.opacity = Math.min(1, .25 * Math.max(0, 1 - Math.abs(p - .31) * 40) + .8 * eo(seg(p, .32, .75)));
      cristais(eo(seg(p, .33, .8)));
      const k = seg(p, .46, .56);
      selo.style.opacity = Math.min(1, k * 3);
      selo.style.transform = k < 1 ? `scale(${1.6 - .6 * k * k}) rotate(${-14 + 8 * k}deg)` : "rotate(-6deg)";
      tc.style.opacity = .25 + .75 * eo(seg(p, .55, .7)); tc.style.letterSpacing = `${.03 + .12 * (1 - eo(seg(p, .55, .75)))}em`;
    }
  }));
  $$(".parte").forEach(a => a.onclick = () => { sessionStorage.setItem("lmd:parte", a.dataset.parte); });
  $("#trailer button").onclick = () => { $("#trailer").innerHTML = `<video src="midia/trailer.mp4" controls autoplay playsinline poster="midia/trailer.webp"></video>`; pausarSom(); };
}

// ------------------------------------------------------------------ Biblioteca
function biblioteca(main) {
  const caps = D.obra.capitulos;
  const total = caps.reduce((s, c) => s + c.palavras, 0);
  const lidas = caps.reduce((s, c) => s + c.palavras * Math.min(1, estado.prog[c.n] || 0), 0);
  const cont = estado.pos ? caps[estado.pos.n - 1] : caps[0];
  main.innerHTML = `<header class="sala-topo"><p class="olho">A Biblioteca</p><h1 class="titulo">O Volume I</h1>
    <p>Seis partes, cada uma aberta por uma das Leis. A leitura nunca fica bloqueada; o Registro e a Galeria abrem à medida que você avança.</p></header>
  <div class="sala-corpo">
    <div class="retomar"><div><p class="olho">${estado.pos ? "Continuar de onde parou" : "Comece por aqui"}</p><h3>Capítulo ${cont.n} · ${esc(cont.titulo)}</h3>
      <div class="prog-total" title="${Math.round(lidas / total * 100)}% do livro"><i style="width:${lidas / total * 100}%"></i></div></div>
      <a class="botao cheio" href="#cap-${dois(cont.n)}">${estado.pos ? "Continuar" : "Ler"}</a></div>
    ${D.obra.partes.map(p => `<section class="bloco-parte" id="parte-${p.num}">
      <div class="banda-parte"><img src="${p.img.src}" alt="" loading="lazy"><span class="olho">Parte ${p.num} · ${esc(p.lei)}</span><h2>${esc(p.titulo)}</h2><p>${esc(p.epigrafe)}</p></div>
      <ol class="caps">${caps.filter(c => c.parte === p.num).map(c => {
        const f = estado.prog[c.n] || 0, min = Math.max(1, Math.round(c.palavras / 230));
        return `<li><a class="cap-l" href="#cap-${dois(c.n)}"><span class="num">${c.n}</span><img class="mini" src="${c.abertura.src}" alt="" loading="lazy">
          <div><h3>${esc(c.titulo)}</h3><div class="meta">${esc(c.pov.split("(")[0].trim())} · ${min} min de leitura</div>${f > 0 ? `<div class="barra-cap"><i style="width:${Math.min(100, f * 100)}%"></i></div>` : ""}</div>
          ${f >= .9 ? `<button class="lembrar" type="button" data-lembrar="${c.n}">Relembrar</button>` : f > 0 ? `<span class="lido">${Math.round(f * 100)}%</span>` : "<span></span>"}</a>
          <p class="resumo" id="res-${c.n}" hidden></p></li>`;
      }).join("")}</ol></section>`).join("")}
  </div>`;
  $$("[data-lembrar]", main).forEach(b => b.onclick = async ev => {
    ev.preventDefault(); ev.stopPropagation();
    D.resumos ||= await json("data/resumos.json");
    const p = $(`#res-${b.dataset.lembrar}`); p.textContent = D.resumos[b.dataset.lembrar]; p.hidden = !p.hidden;
  });
  const alvo = sessionStorage.getItem("lmd:parte");
  if (alvo) { sessionStorage.removeItem("lmd:parte"); setTimeout(() => $(`#parte-${alvo}`)?.scrollIntoView({ behavior: reduzido ? "auto" : "smooth" }), 80); }
}

// ------------------------------------------------------------------ Leitor
function aplicarPrefs(el = $(".leitor")) {
  if (!el) return;
  const p = estado.prefs;
  el.dataset.tema = p.tema;
  el.style.setProperty("--fonte", p.fonte + "rem"); el.style.setProperty("--entre", p.entre); el.style.setProperty("--largura", p.largura + "rem");
  $$("#a-tema button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === p.tema));
  $("#a-fonte").value = p.fonte; $("#a-entre").value = p.entre; $("#a-largura").value = p.largura;
}
async function leitor(main, n) {
  const c = D.obra.capitulos[n - 1];
  if (!c) { location.hash = "biblioteca"; return; }
  const dados = await capitulo(n);
  const parte = D.obra.partes.find(p => p.num === c.parte);
  let iP = 0, depois = true;
  const corpo = dados.blocos.map(b => {
    if (b.t === "sep") { depois = true; return `<div class="sep" aria-hidden="true"><i></i><i></i><i></i></div>`; }
    if (b.t === "img") { depois = true; return `<figure><img src="${b.img.src}" alt="" loading="lazy" width="${b.img.w}" height="${b.img.h}"></figure>`; }
    if (b.t === "doc") return `<aside class="doc"><span class="olho">${esc(b.tipo)}</span>${b.x}</aside>`;
    if (b.t === "h") { depois = true; return `<h2 data-b="${iP++}">${b.x}</h2>`; }
    const cls = iP === 0 ? "capitular sem" : depois ? "sem" : "";
    depois = false;
    return `<p data-b="${iP++}" class="${cls}">${b.x}</p>`;
  }).join("");
  let li = 0;
  const letras = c.titulo.split(" ").map(pal => `<span style="white-space:nowrap">${[...pal].map(ch => `<span class="l" style="animation-delay:${.25 + li++ * .025}s">${esc(ch)}</span>`).join("")}</span>`).join(" ");
  const prox = D.obra.capitulos[n];
  main.innerHTML = `<div class="leitura-prog" id="lprog"></div>
  <article class="leitor" data-tema="${estado.prefs.tema}">
    <header class="cap-abre"><div class="arte" id="arte" style="background-image:url(${c.abertura.src})"></div>
      <p class="olho">Parte ${c.parte} · ${esc(parte.titulo)} · ${c.rotulo} ${c.n}</p><h1>${letras}</h1>
      ${c.epigrafe ? `<p class="epi">${c.epigrafe}</p>` : ""}</header>
    <div class="coluna" id="coluna">${corpo}</div>
    <div class="fim-cap" id="fim-cap"><img class="selo" src="pecas/selo_ordem.webp" alt="">
      <p class="olho">Fim do capítulo ${c.n}</p>${c.respiro ? `<p class="respiro">“${c.respiro}”</p>` : ""}</div>
    ${c.finais.length ? `<div class="finais">${c.finais.map(f => `<img src="${f.src}" alt="" loading="lazy" width="${f.w}" height="${f.h}">`).join("")}</div>` : ""}
    ${prox ? `<a class="proximo" href="#cap-${dois(prox.n)}"><img src="${prox.abertura.src}" alt="" loading="lazy"><span class="olho">Próximo · Capítulo ${prox.n}</span><h3>${esc(prox.titulo)}</h3></a>`
           : `<a class="proximo" href="#registro"><img src="${parte.img.src}" alt=""><span class="olho">Fim do Volume I</span><h3>Abra o Registro completo</h3></a>`}
    <div style="height:4rem"></div>
  </article>
  <div class="ferramentas">
    <button class="ib" type="button" id="f-sumario" aria-label="Sumário e marcadores"><svg><use href="#i-sumario"/></svg></button>
    <button class="ib" type="button" id="f-marcar" aria-label="Marcar este trecho"><svg><use href="#i-marcador"/></svg></button>
    <button class="ib" type="button" id="f-ajustes" aria-label="Ajustes de leitura"><svg><use href="#i-texto"/></svg></button>
  </div>`;
  aplicarPrefs();
  const col = $("#coluna"), barra = $("#lprog"), arteEl = $("#arte"), fim = $("#fim-cap");
  const blocos = $$("[data-b]", col);
  // volta ao ponto de leitura
  const alvo = sessionStorage.getItem("lmd:bloco");
  sessionStorage.removeItem("lmd:bloco");
  const ir = alvo != null ? +alvo : (estado.pos?.n === n ? estado.pos.b : null);
  if (ir != null && blocos[ir]) { blocos[ir].scrollIntoView({ block: "center" }); if (alvo != null) blocos[ir].classList.add("realce"); }
  else scrollTo(0, 0);
  let pend = false;
  const medir = () => {
    pend = false;
    const r = col.getBoundingClientRect(), f = Math.max(0, Math.min(1, -r.top / Math.max(1, r.height - innerHeight * .6)));
    barra.style.width = f * 100 + "%";
    if (!reduzido) arteEl.style.transform = `translateY(${Math.min(scrollY, innerHeight) * .25}px) scale(1.04)`;
    if (f > (estado.prog[n] || 0)) estado.prog[n] = +f.toFixed(3);
    const topo = blocos.find(b => b.getBoundingClientRect().bottom > innerHeight * .22);
    estado.pos = { n, b: topo ? +topo.dataset.b : 0 };
    salvar();
  };
  const rolar = () => { if (!pend) { pend = true; requestAnimationFrame(medir); } };
  addEventListener("scroll", rolar, { passive: true }); limpar.push(() => removeEventListener("scroll", rolar));
  medir();
  // fim do capítulo: o selo é carimbado e o Registro avisa o que abriu
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const antes = alcancado();
    fim.classList.add("carimbado"); estado.prog[n] = 1; salvar();
    if (prox && antes < prox.n) {
      const novos = [...D.reg.lugares, ...D.reg.elenco, ...D.reg.glossario].filter(v => v.cap === n).length;
      if (novos) aviso(`${novos} ${novos > 1 ? "verbetes novos" : "verbete novo"} no Registro`);
    }
    io.disconnect();
  }), { threshold: .6 });
  io.observe(fim); limpar.push(() => io.disconnect());
  // assentar figuras ao entrar
  const io2 = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("assenta"); io2.unobserve(e.target); } }), { rootMargin: "0px 0px -10% 0px" });
  $$("figure, .doc, .sep", col).forEach(el => io2.observe(el)); limpar.push(() => io2.disconnect());
  // ferramentas
  $("#f-ajustes").onclick = () => abrirPainel("p-ajustes");
  $("#f-sumario").onclick = () => { montarSumario(n); abrirPainel("p-sumario"); };
  $("#f-marcar").onclick = () => {
    const b = blocos[estado.pos?.b ?? 0];
    const trecho = (b?.textContent || "").slice(0, 110).trim();
    estado.marcadores.unshift({ n, b: estado.pos?.b ?? 0, trecho, quando: Date.now() }); estado.marcadores = estado.marcadores.slice(0, 60); salvar();
    aviso("Marcador salvo");
  };
  const tecla = ev => {
    if (ev.target.closest("input, textarea") || ev.altKey || ev.ctrlKey || ev.metaKey) return;
    if (ev.key === "ArrowRight" && prox) location.hash = `cap-${dois(prox.n)}`;
    if (ev.key === "ArrowLeft" && n > 1) location.hash = `cap-${dois(n - 1)}`;
  };
  addEventListener("keydown", tecla); limpar.push(() => removeEventListener("keydown", tecla));
}
function montarSumario(atual) {
  $("#sumario").innerHTML = D.obra.partes.map(p => `<p class="sumario-l parte-t">Parte ${p.num} · ${esc(p.titulo)}</p><ul class="sumario-l">${D.obra.capitulos.filter(c => c.parte === p.num)
    .map(c => `<li><a href="#cap-${dois(c.n)}" ${c.n === atual ? 'aria-current="true"' : ""}><span>${c.n}</span><span>${esc(c.titulo)}</span></a></li>`).join("")}</ul>`).join("");
  $("#marcadores").innerHTML = estado.marcadores.length ? estado.marcadores.map((m, i) => `<a class="marcador-l" href="#cap-${dois(m.n)}" data-m="${i}"><small>Capítulo ${m.n}</small><span>${esc(m.trecho)}…</span></a>`).join("")
    : `<p style="color:var(--marfim-baixo)">Nenhum marcador ainda. Use o botão de marcador enquanto lê.</p>`;
  $$("[data-m]").forEach(a => a.onclick = () => sessionStorage.setItem("lmd:bloco", estado.marcadores[+a.dataset.m].b));
}

// ------------------------------------------------------------------ Registro
const ABAS = [["leis", "As Sete Leis"], ["disciplinas", "As Seis Disciplinas"], ["transposicao", "A Transposição"], ["glossario", "Glossário"], ["elenco", "Elenco"], ["lugares", "Lugares"]];
function registro(main) {
  let aba = sessionStorage.getItem("lmd:aba") || "leis";
  main.innerHTML = `<header class="sala-topo"><p class="olho">O Registro</p><h1 class="titulo">O que Aresta guarda</h1>
    <p>As leis, as disciplinas e os nomes deste mundo. Cada verbete abre quando a sua leitura chega ao capítulo em que ele aparece.</p></header>
  <div class="sala-corpo"><div class="abas" role="tablist">${ABAS.map(([k, t]) => `<button type="button" role="tab" data-aba="${k}" aria-selected="${k === aba}">${t}</button>`).join("")}</div>
    <div class="aviso-spoiler" id="spoiler"></div><div id="aba"></div></div>`;
  const pintar = () => {
    $$("[data-aba]").forEach(b => b.setAttribute("aria-selected", b.dataset.aba === aba));
    const fechado = cap => `<div class="verbete fechado"><div class="lacre-mini">${cap}</div><h3>Ainda lacrado</h3><p>Abre quando você chegar ao capítulo ${cap}.</p></div>`;
    const R = D.reg, el = $("#aba");
    const ocultos = { glossario: R.glossario, elenco: R.elenco, lugares: R.lugares }[aba]?.filter(v => !aberto(v.cap)).length || 0;
    $("#spoiler").innerHTML = ocultos ? `<span>${ocultos} ${ocultos > 1 ? "verbetes ainda lacrados" : "verbete ainda lacrado"}.</span><span class="confirmar" id="conf"><button type="button" id="b-revelar">Abrir todos (contém spoilers)</button></span>` : "";
    $("#b-revelar")?.addEventListener("click", () => {
      $("#conf").innerHTML = `Tem certeza? <button type="button" id="b-sim">Sim, abrir tudo</button> <button type="button" id="b-nao">Não</button>`;
      $("#b-sim").onclick = () => { estado.revelar = true; salvar(); pintar(); };
      $("#b-nao").onclick = pintar;
    });
    if (aba === "leis") el.innerHTML = `<div class="grade">${R.leis.map(l => `<div class="verbete"><img class="simb" src="${l.img.src}" alt=""><span class="olho">Lei ${l.num}</span><h3>${esc(l.nome)}</h3><p>${esc(l.frase)}</p></div>`).join("")}</div>`;
    if (aba === "disciplinas") el.innerHTML = `<div class="grade">${R.disciplinas.map(d => `<div class="verbete"><img class="simb" src="${d.img.src}" alt=""><span class="olho">Luz ${esc(d.cor)}</span><h3>${esc(d.nome)}</h3><p>Move ${esc(d.faz)}.</p></div>`).join("")}</div>
      <p style="text-align:center;color:var(--marfim-baixo);font-style:italic;margin-top:2rem">Fogo, gelo, raio, vento: tudo é mistura destes seis. Cada disciplina acende os selos com a sua cor.</p>`;
    if (aba === "transposicao") el.innerHTML = `<div class="etapas">${R.etapas.map((e, i) => `<div class="verbete"><img class="simb" src="${e.img.src}" alt=""><h3>${esc(e.nome)}</h3><p>${esc(e.x)}</p></div>${i < 5 ? '<span class="seta" aria-hidden="true">→</span>' : ""}`).join("")}</div>
      <p style="text-align:center;color:var(--marfim-baixo);font-style:italic;margin-top:2rem;max-width:40rem;margin-inline:auto">A magia não cria nada. Ela muda de lugar o que já existe: calor, movimento, luz, som, carga, tensão. Quem esquece o Retorno descobre, do pior jeito, para onde o contragolpe foi.</p>`;
    if (aba === "glossario") el.innerHTML = `<div class="glos">${R.glossario.map(g => aberto(g.cap) ? `<p><b>${esc(g.termo)}.</b> ${esc(g.x)}</p>` : `<p class="fechado">Um termo lacrado. Abre no capítulo ${g.cap}.</p>`).join("")}</div>`;
    if (aba === "elenco") el.innerHTML = `<div class="grade">${R.elenco.map(e => aberto(e.cap) ? `<div class="verbete"><img class="foto" src="${e.img.src}" alt="${esc(e.nome)}" loading="lazy"><span class="olho">Desde o capítulo ${e.cap}</span><h3>${esc(e.nome)}</h3><p>${esc(e.x)}</p></div>` : fechado(e.cap)).join("")}</div>`;
    if (aba === "lugares") el.innerHTML = `<div class="grade">${R.lugares.map(l => aberto(l.cap) ? `<div class="verbete"><span class="olho">${esc(l.onde || "Aresta")} · cap. ${l.cap}</span><h3>${esc(l.nome)}</h3><p>${esc(l.x.length > 260 ? l.x.slice(0, 257) + "…" : l.x)}</p></div>` : fechado(l.cap)).join("")}</div>`;
  };
  $$("[data-aba]").forEach(b => b.onclick = () => { aba = b.dataset.aba; sessionStorage.setItem("lmd:aba", aba); pintar(); });
  pintar();
}

// ------------------------------------------------------------------ Atlas (arrastar e ampliar)
function atlas(main) {
  const M = D.extras.mapas;
  main.innerHTML = `<header class="sala-topo"><p class="olho">O Atlas</p><h1 class="titulo">Aresta, de perto</h1><p>Arraste para andar pelo mapa. Use a roda do mouse, os dedos ou os botões para aproximar.</p></header>
  <div class="sala-corpo"><div class="abas" role="tablist">${M.map((m, i) => `<button type="button" role="tab" data-mapa="${i}" aria-selected="${i === 0}">${esc(m.titulo)}</button>`).join("")}</div>
    <div class="mapa-caixa" id="mapa"><div class="mapa-in" id="mapa-in"></div>
      <div class="zoom"><button type="button" id="z-mais" aria-label="Aproximar">+</button><button type="button" id="z-menos" aria-label="Afastar">−</button><button type="button" id="z-zero" aria-label="Mapa inteiro" style="font-size:.8rem">⤢</button></div></div></div>`;
  const caixa = $("#mapa"), dentro = $("#mapa-in");
  let s = 1, x = 0, y = 0;
  const aplicar = () => { dentro.style.transform = `translate(${x}px, ${y}px) scale(${s})`; };
  const encaixar = () => { const svg = $("svg", dentro); if (!svg) return; const w = svg.getBoundingClientRect().width / s, h = svg.getBoundingClientRect().height / s;
    s = Math.min(caixa.clientWidth / w, caixa.clientHeight / h); x = (caixa.clientWidth - w * s) / 2; y = (caixa.clientHeight - h * s) / 2; aplicar(); };
  const zoom = (f, cx = caixa.clientWidth / 2, cy = caixa.clientHeight / 2) => { const ns = Math.max(.2, Math.min(8, s * f)); x = cx - (cx - x) * ns / s; y = cy - (cy - y) * ns / s; s = ns; aplicar(); };
  const carregar = async i => { $$("[data-mapa]").forEach(b => b.setAttribute("aria-selected", +b.dataset.mapa === i));
    dentro.innerHTML = await fetch(M[i].src).then(r => r.text()); s = 1; requestAnimationFrame(encaixar); };
  $$("[data-mapa]").forEach(b => b.onclick = () => carregar(+b.dataset.mapa));
  $("#z-mais").onclick = () => zoom(1.4); $("#z-menos").onclick = () => zoom(1 / 1.4); $("#z-zero").onclick = encaixar;
  caixa.addEventListener("wheel", ev => { ev.preventDefault(); const r = caixa.getBoundingClientRect(); zoom(ev.deltaY < 0 ? 1.15 : 1 / 1.15, ev.clientX - r.left, ev.clientY - r.top); }, { passive: false });
  const toques = new Map(); let dist0 = 0;
  caixa.addEventListener("pointerdown", ev => { caixa.setPointerCapture(ev.pointerId); toques.set(ev.pointerId, [ev.clientX, ev.clientY]); caixa.classList.add("arrastando"); });
  caixa.addEventListener("pointermove", ev => {
    if (!toques.has(ev.pointerId)) return;
    const [px, py] = toques.get(ev.pointerId); toques.set(ev.pointerId, [ev.clientX, ev.clientY]);
    if (toques.size === 2) { const [a, b] = [...toques.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (dist0) { const r = caixa.getBoundingClientRect(); zoom(d / dist0, (a[0] + b[0]) / 2 - r.left, (a[1] + b[1]) / 2 - r.top); } dist0 = d; }
    else { x += ev.clientX - px; y += ev.clientY - py; aplicar(); }
  });
  const soltar = ev => { toques.delete(ev.pointerId); dist0 = 0; if (!toques.size) caixa.classList.remove("arrastando"); };
  caixa.addEventListener("pointerup", soltar); caixa.addEventListener("pointercancel", soltar);
  carregar(0);
}

// ------------------------------------------------------------------ Galeria
function galeria(main) {
  const doLivro = D.obra.capitulos.flatMap(c => [{ img: c.abertura, leg: `Capítulo ${c.n} · ${c.titulo}`, cap: c.n }, ...c.finais.map(f => ({ img: f, leg: `Capítulo ${c.n} · ${c.titulo}`, cap: c.n }))]);
  const abertas = doLivro.filter(o => aberto(o.cap)), fechadas = doLivro.length - abertas.length;
  const grupos = {};
  D.extras.galeria.forEach(o => (grupos[o.grupo] ||= []).push(o));
  const obra = (o, i) => `<figure class="obra" data-i="${i}"><img src="${o.img.src}" alt="${esc(o.leg)}" loading="lazy" width="${o.img.w}" height="${o.img.h}"><figcaption>${esc(o.leg)}</figcaption></figure>`;
  const todas = [...abertas, ...D.extras.galeria];
  let i = 0;
  main.innerHTML = `<header class="sala-topo"><p class="olho">A Galeria</p><h1 class="titulo">As imagens de Aresta</h1><p>Rostos, lugares, objetos e as ilustrações de cada capítulo. As do livro aparecem conforme você lê.</p></header>
  <div class="sala-corpo">
    <div class="cabeca"><h2 class="titulo" style="font-size:1.6rem">Do livro</h2><p>${abertas.length} de ${doLivro.length} ilustrações abertas.</p></div>
    <div class="mosaico">${abertas.map(o => obra(o, i++)).join("")}${fechadas ? `<div class="obra fechada"><div class="lacre-mini" style="margin:0 auto .6rem">${fechadas}</div>${fechadas} ilustrações ainda lacradas. Elas abrem ao longo da leitura.</div>` : ""}</div>
    ${Object.entries(grupos).map(([g, os]) => `<div class="cabeca" style="margin-top:3rem"><h2 class="titulo" style="font-size:1.6rem">${esc(g)}</h2></div><div class="mosaico">${os.map(o => obra(o, i++)).join("")}</div>`).join("")}
  </div>`;
  $$(".obra[data-i]", main).forEach(f => f.onclick = () => {
    const o = todas[+f.dataset.i];
    const cl = document.createElement("div"); cl.className = "caixa-luz"; cl.setAttribute("role", "dialog"); cl.setAttribute("aria-label", o.leg);
    cl.innerHTML = `<button class="ib" type="button" aria-label="Fechar"><svg><use href="#i-fechar"/></svg></button><div><img src="${o.img.src}" alt="${esc(o.leg)}"><p>${esc(o.leg)}</p></div>`;
    const sair = () => { cl.remove(); removeEventListener("keydown", esc_); };
    const esc_ = ev => { if (ev.key === "Escape") sair(); };
    cl.onclick = ev => { if (ev.target === cl || ev.target.closest("button")) sair(); };
    addEventListener("keydown", esc_); document.body.appendChild(cl); $("button", cl).focus();
  });
}

// ------------------------------------------------------------------ busca no livro inteiro
async function busca() {
  const c = document.createElement("div"); c.className = "busca-c"; c.setAttribute("role", "dialog"); c.setAttribute("aria-label", "Buscar no livro");
  c.innerHTML = `<button class="ib fechar" type="button" aria-label="Fechar"><svg><use href="#i-fechar"/></svg></button><div class="dentro">
    <label class="olho" for="q">Buscar no livro</label><input id="q" type="search" placeholder="Um nome, um lugar, uma frase" autocomplete="off">
    <p class="info" id="q-info">Carregando os 31 capítulos…</p><div id="q-res"></div></div>`;
  document.body.appendChild(c);
  const sair = () => { c.remove(); removeEventListener("keydown", tecla); };
  const tecla = ev => { if (ev.key === "Escape") sair(); };
  addEventListener("keydown", tecla); $(".fechar", c).onclick = sair;
  const q = $("#q", c); q.focus();
  const caps = await Promise.all(D.obra.capitulos.map(x => capitulo(x.n)));
  const textos = caps.flatMap(cp => { let i = 0; return cp.blocos.filter(b => b.t === "p" || b.t === "h").map(b => ({ n: cp.n, b: i++, x: b.x.replace(/<[^>]+>/g, "") })); });
  textos.forEach(t => t.s = sem(t.x));
  $("#q-info", c).textContent = "Digite pelo menos três letras.";
  let t = 0;
  q.oninput = () => { clearTimeout(t); t = setTimeout(() => {
    const termo = sem(q.value.trim());
    if (termo.length < 3) { $("#q-res", c).innerHTML = ""; $("#q-info", c).textContent = "Digite pelo menos três letras."; return; }
    const ach = textos.filter(x => x.s.includes(termo));
    $("#q-info", c).textContent = ach.length ? `${ach.length} ${ach.length > 1 ? "trechos" : "trecho"}${ach.length > 80 ? ", mostrando os 80 primeiros" : ""}.` : "Nada encontrado. Tente outra palavra.";
    $("#q-res", c).innerHTML = ach.slice(0, 80).map(a => { const i = a.s.indexOf(termo), ini = Math.max(0, i - 70);
      const trecho = esc(a.x.slice(ini, i)) + "<mark>" + esc(a.x.slice(i, i + termo.length)) + "</mark>" + esc(a.x.slice(i + termo.length, i + termo.length + 90));
      return `<a class="achado" href="#cap-${dois(a.n)}" data-n="${a.n}" data-b="${a.b}"><small>Capítulo ${a.n} · ${esc(D.obra.capitulos[a.n - 1].titulo)}</small><p>${ini ? "…" : ""}${trecho}…</p></a>`; }).join("");
    $$(".achado", c).forEach(a => a.onclick = () => { sessionStorage.setItem("lmd:bloco", a.dataset.b); sair(); if (location.hash === `#cap-${dois(a.dataset.n)}`) abrir(); });
  }, 160); };
}

// ------------------------------------------------------------------ painéis, ajustes e som
function abrirPainel(id) { fecharPaineis(); const p = $("#" + id); p.classList.add("aberto"); p.setAttribute("aria-hidden", "false"); $(".fechar", p)?.focus(); }
function fecharPaineis() { $$(".painel").forEach(p => { p.classList.remove("aberto"); p.setAttribute("aria-hidden", "true"); }); }
$$("[data-fechar]").forEach(b => b.onclick = fecharPaineis);
addEventListener("keydown", ev => { if (ev.key === "Escape") fecharPaineis(); });
$$("#a-tema button").forEach(b => b.onclick = () => { estado.prefs.tema = b.dataset.v; salvar(); aplicarPrefs(); });
for (const [id, k] of [["a-fonte", "fonte"], ["a-entre", "entre"], ["a-largura", "largura"]]) $("#" + id).oninput = ev => { estado.prefs[k] = +ev.target.value; salvar(); aplicarPrefs(); };
function pedirApagar() {
  $("#apagar-c").innerHTML = `<p style="margin:0 0 .6rem">Apagar progresso, marcadores e ajustes deste navegador?</p><div class="opcoes"><button type="button" id="ap-sim">Apagar</button><button type="button" id="ap-nao">Manter</button></div>`;
  $("#ap-sim").onclick = () => { estado = structuredClone(PADRAO); try { localStorage.removeItem(CHAVE); } catch { } location.hash = "portico"; location.reload(); };
  $("#ap-nao").onclick = () => { $("#apagar-c").innerHTML = `<button class="botao" type="button" id="b-apagar">Apagar progresso</button>`; $("#b-apagar").onclick = pedirApagar; };
}
$("#b-apagar").onclick = pedirApagar;
const SONS = { vento: new Audio("midia/vento.ogg"), tema: new Audio("midia/tema.ogg") };
Object.values(SONS).forEach(a => { a.loop = true; a.preload = "none"; a.volume = estado.prefs.volume; });
function pausarSom() { Object.entries(SONS).forEach(([k, a]) => { a.pause(); $("#s-" + k).textContent = "Ligar"; }); $("#b-som").setAttribute("aria-pressed", "false"); }
for (const k of Object.keys(SONS)) $("#s-" + k).onclick = () => {
  const a = SONS[k];
  if (a.paused) { a.play().then(() => { $("#s-" + k).textContent = "Desligar"; $("#b-som").setAttribute("aria-pressed", "true"); }).catch(() => aviso("O navegador não deixou tocar o som")); }
  else { a.pause(); $("#s-" + k).textContent = "Ligar"; if (Object.values(SONS).every(x => x.paused)) $("#b-som").setAttribute("aria-pressed", "false"); }
};
$("#s-volume").value = estado.prefs.volume;
$("#s-volume").oninput = ev => { estado.prefs.volume = +ev.target.value; Object.values(SONS).forEach(a => a.volume = estado.prefs.volume); salvar(); };
$("#b-som").onclick = () => abrirPainel("p-som");
$("#b-busca").onclick = busca;

// ------------------------------------------------------------------ início
(async () => {
  try {
    [D.obra, D.reg, D.extras] = await Promise.all([json("data/obra.json"), json("data/registro.json"), json("data/extras.json")]);
  } catch (e) {
    $("#conteudo").innerHTML = `<div class="sala-topo"><h1 class="titulo">O livro não abriu</h1><p>Os arquivos do livro não carregaram. Recarregue a página.</p></div>`; return;
  }
  NEVE = neve($("#neve"));
  abrir(rota(), false);
})();

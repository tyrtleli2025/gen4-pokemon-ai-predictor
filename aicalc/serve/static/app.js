/* Kaizo AI Simulator — milestone B: live probability explorer.
   The battle doc (case format 1) is the single source of truth. */
"use strict";

const state = {
  meta: null, tables: null, trainers: [],
  trainerParty: [],           // /api/trainer party entries
  battle: {
    flags: [],
    field: { weather: null, turn: 1, trick_room: false, gravity: false },
    ai: null,                 // side objects created when a mon is set
    player: null,
  },
};

const $ = (sel) => document.querySelector(sel);
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  node.append(...children);
  return node;
};

async function getJSON(url) {
  const resp = await fetch(url);
  const body = await resp.json();
  if (!resp.ok) throw body;
  return body;
}

/* ---------------- init ---------------- */

async function init() {
  [state.meta, state.tables] = await Promise.all([
    getJSON("/api/meta"), getJSON("/api/tables"),
  ]);
  state.trainers = (await getJSON("/api/trainers")).trainers;

  const tl = $("#trainer-list");
  for (const t of state.trainers) {
    const label = `${t.name}${t.location ? " — " + t.location : ""} (#${t.id})`;
    tl.append(el("option", { value: label }));
  }
  const sl = $("#species-list");
  for (const name of Object.keys(state.tables.species)) sl.append(el("option", { value: name }));
  const ml = $("#move-list");
  for (const name of Object.keys(state.tables.moves)) ml.append(el("option", { value: name }));

  const nat = $("#player-nature");
  for (const n of state.meta.natures) nat.append(el("option", { value: n }, n));

  const ivRow = $("#player-ivs");
  ivRow.append("IVs ");
  for (const s of ["hp", "atk", "def", "spa", "spd", "spe"]) {
    ivRow.append(el("label", {}, s,
      el("input", { type: "number", id: `iv-${s}`, value: 31, min: 0, max: 31 })));
  }
  const mvRow = $("#player-moves");
  for (let i = 0; i < 4; i++) {
    mvRow.append(el("input", { list: "move-list", id: `pm-${i}`, placeholder: `Move ${i + 1}` }));
  }

  $("#trainer-search").addEventListener("change", onTrainerPicked);
  $("#player-build").addEventListener("click", buildPlayerMon);
  $("#player-species").addEventListener("change", onPlayerSpecies);
  $("#export-case").addEventListener("click", exportCase);
  $("#load-case").addEventListener("change", loadCaseFile);
  $("#apply-raw").addEventListener("click", applyRawJSON);

  renderField();
  refresh();
}

/* ---------------- doc helpers ---------------- */

function newSide(pokemon) {
  return {
    pokemon,
    party_remaining: 1,
    hazards: {},
    reflect: false, light_screen: false, tailwind: false,
    safeguard: false, mist: false, lucky_chant: false, future_attack: false,
  };
}

function battleDoc() {
  const b = state.battle;
  if (!b.ai || !b.player) return null;
  const clean = JSON.parse(JSON.stringify(b));
  for (const side of [clean.ai, clean.player]) {
    for (const key of ["hazards"])
      for (const h of Object.keys(side[key])) if (!side[key][h]) delete side[key][h];
    const mon = side.pokemon;
    for (const key of ["boosts"])
      if (mon[key]) for (const s of Object.keys(mon[key])) if (!mon[key][s]) delete mon[key][s];
    for (const key of Object.keys(mon))
      if (mon[key] === null || (Array.isArray(mon[key]) && !mon[key].length)) delete mon[key];
    if (mon.protect_streak === 0) delete mon.protect_streak;
    if (mon.turns_active === 1) delete mon.turns_active;
    if (mon.current_hp === mon.max_hp) delete mon.current_hp;
  }
  if (!clean.field.weather) delete clean.field.weather;
  return clean;
}

/* ---------------- trainer side ---------------- */

async function onTrainerPicked(ev) {
  const match = /\(#(\d+)\)\s*$/.exec(ev.target.value);
  if (!match) return;
  const data = await getJSON(`/api/trainer?id=${match[1]}`);
  state.trainerParty = data.party;
  const strip = $("#trainer-party");
  strip.replaceChildren();
  data.party.forEach((entry, i) => {
    strip.append(el("div", { class: "party-chip", onclick: () => setAiMon(i) },
      entry.pokemon.species, " ", el("span", { class: "lv" }, `L${entry.pokemon.level}`)));
  });
}

function setAiMon(index) {
  const entry = state.trainerParty[index];
  const mon = JSON.parse(JSON.stringify(entry.pokemon));
  state.battle.ai = { ...newSide(mon), party_remaining: state.trainerParty.length - 1 };
  state.battle.flags = [...entry.ai_flags];
  document.querySelectorAll(".party-chip").forEach((c, i) =>
    c.classList.toggle("active", i === index));
  renderFlags(entry);
  renderMon("ai");
  renderSide("ai");
  refresh();
}

function renderFlags(entry) {
  const row = $("#ai-flags");
  row.replaceChildren();
  for (const f of entry.ai_flags) row.append(el("span", { class: "flag" }, f));
  for (const f of entry.unsupported_flags)
    row.append(el("span", { class: "flag unsupported", title: "not encoded — engine will refuse" }, f));
}

/* ---------------- player side ---------------- */

function onPlayerSpecies(ev) {
  const sp = state.tables.species[ev.target.value];
  if (sp && sp.abilities.length) $("#player-ability").value = sp.abilities[0];
}

function computeStats(base, ivs, level, nature) {
  const [up, down] = state.meta.nature_effects[nature];
  const hp = Math.floor((2 * base.hp + ivs.hp) * level / 100) + level + 10;
  const stats = {};
  for (const s of ["atk", "def", "spa", "spd", "spe"]) {
    let v = Math.floor((2 * base[s] + ivs[s]) * level / 100) + 5;
    if (s === up) v = Math.floor(v * 110 / 100);
    else if (s === down) v = Math.floor(v * 90 / 100);
    stats[s] = v;
  }
  return { hp, stats };
}

function buildPlayerMon() {
  const species = $("#player-species").value;
  const sp = state.tables.species[species];
  if (!sp) { showError({ error: { type: "UI", message: `unknown species '${species}'` } }); return; }
  const level = parseInt($("#player-level").value, 10) || 50;
  const nature = $("#player-nature").value;
  const ivs = {};
  for (const s of ["hp", "atk", "def", "spa", "spd", "spe"])
    ivs[s] = parseInt($(`#iv-${s}`).value, 10) || 0;
  const { hp, stats } = computeStats(sp.base, ivs, level, nature);
  const moves = [];
  for (let i = 0; i < 4; i++) {
    const value = $(`#pm-${i}`).value.trim();
    if (value) moves.push(value);
  }
  const mon = {
    species, level,
    ability: $("#player-ability").value.trim() || sp.abilities[0],
    item: $("#player-item").value.trim() || null,
    types: sp.types, stats, max_hp: hp, current_hp: hp,
    status: null, boosts: {}, moves,
    weight_hg: sp.weight_hg,
  };
  state.battle.player = state.battle.player
    ? { ...state.battle.player, pokemon: mon } : newSide(mon);
  renderMon("player");
  renderSide("player");
  refresh();
}

/* ---------------- mon + side editors ---------------- */

function renderMon(which) {
  const side = state.battle[which];
  const panel = $(`#${which}-mon`);
  panel.replaceChildren();
  if (!side) return;
  const mon = side.pokemon;

  panel.append(
    el("div", { class: "name" }, mon.species),
    el("div", { class: "sub" },
      `L${mon.level} ${mon.types.join("/")} · ${mon.ability}` +
      (mon.item ? ` · ${mon.item}` : "")),
  );

  const hpRow = el("div", { class: "hp-row" });
  const hpInput = el("input", {
    type: "number", value: mon.current_hp ?? mon.max_hp, min: 0, max: mon.max_hp,
    onchange: (e) => { mon.current_hp = parseInt(e.target.value, 10) || 0; renderMon(which); refresh(); },
  });
  const pct = Math.round(100 * (mon.current_hp ?? mon.max_hp) / mon.max_hp);
  hpRow.append("HP", hpInput, `/${mon.max_hp}`,
    el("div", { class: "hp-bar" }, el("div", { style: `width:${pct}%` })));
  panel.append(hpRow);

  const statusRow = el("div", { class: "row mini" });
  const statusSel = el("select", {
    onchange: (e) => { mon.status = e.target.value || null; refresh(); },
  }, el("option", { value: "" }, "healthy"));
  for (const s of state.meta.statuses)
    statusSel.append(el("option", { value: s, ...(mon.status === s ? { selected: "" } : {}) }, s));
  statusRow.append("Status", statusSel,
    el("label", {}, "last move",
      el("input", { list: "move-list", value: mon.last_move || "", style: "width:9em",
        onchange: (e) => { mon.last_move = e.target.value.trim() || null; refresh(); } })),
    el("label", {}, "turns out",
      el("input", { type: "number", value: mon.turns_active ?? 1, min: 1, style: "width:3.5em",
        onchange: (e) => { mon.turns_active = parseInt(e.target.value, 10) || 1; refresh(); } })),
    el("label", {}, "protect streak",
      el("input", { type: "number", value: mon.protect_streak ?? 0, min: 0, style: "width:3.5em",
        onchange: (e) => { mon.protect_streak = parseInt(e.target.value, 10) || 0; refresh(); } })),
  );
  panel.append(statusRow);

  const boosts = el("div", { class: "boost-grid" });
  for (const s of ["atk", "def", "spa", "spd", "spe", "acc", "eva"]) {
    boosts.append(el("label", {}, s,
      el("input", { type: "number", value: (mon.boosts || {})[s] || 0, min: -6, max: 6,
        onchange: (e) => {
          mon.boosts = mon.boosts || {};
          mon.boosts[s] = parseInt(e.target.value, 10) || 0;
          refresh();
        } })));
  }
  panel.append(boosts);

  const vols = el("div", { class: "vol-grid" });
  for (const v of state.meta.volatiles) {
    const checked = (mon.volatiles || []).includes(v);
    vols.append(el("label", {},
      el("input", { type: "checkbox", ...(checked ? { checked: "" } : {}),
        onchange: (e) => {
          mon.volatiles = mon.volatiles || [];
          if (e.target.checked) mon.volatiles.push(v);
          else mon.volatiles = mon.volatiles.filter((x) => x !== v);
          refresh();
        } }), v));
  }
  panel.append(el("details", {}, el("summary", {}, "volatiles"), vols));
  panel.append(el("div", { class: "mini", style: "color:var(--dim)" },
    `moves: ${mon.moves.join(", ") || "—"}`));
}

function renderSide(which) {
  const side = state.battle[which];
  const panel = $(`#${which}-side`);
  panel.replaceChildren();
  if (!side) return;

  const row1 = el("div", { class: "row mini" });
  row1.append(el("label", {}, "bench alive",
    el("input", { type: "number", value: side.party_remaining, min: 0, max: 5,
      onchange: (e) => { side.party_remaining = parseInt(e.target.value, 10) || 0; refresh(); } })));
  for (const h of state.meta.hazards) {
    row1.append(el("label", {}, h.replace("_", " "),
      el("input", { type: "number", value: side.hazards[h] || 0, min: 0, max: 3,
        onchange: (e) => { side.hazards[h] = parseInt(e.target.value, 10) || 0; refresh(); } })));
  }
  panel.append(row1);

  const row2 = el("div", { class: "row mini" });
  for (const flag of ["reflect", "light_screen", "tailwind", "safeguard", "mist", "lucky_chant"]) {
    row2.append(el("label", {},
      el("input", { type: "checkbox", ...(side[flag] ? { checked: "" } : {}),
        onchange: (e) => { side[flag] = e.target.checked; refresh(); } }),
      flag.replace("_", " ")));
  }
  panel.append(row2);
}

function renderField() {
  const panel = $("#field-controls");
  panel.replaceChildren();
  const field = state.battle.field;
  const row = el("div", { class: "row" });
  const weather = el("select", {
    onchange: (e) => { field.weather = e.target.value || null; refresh(); },
  }, el("option", { value: "" }, "no weather"));
  for (const w of state.meta.weathers)
    weather.append(el("option", { value: w, ...(field.weather === w ? { selected: "" } : {}) }, w));
  row.append(weather,
    el("label", {}, "turn",
      el("input", { type: "number", value: field.turn, min: 1,
        onchange: (e) => { field.turn = parseInt(e.target.value, 10) || 1; refresh(); } })),
    el("label", {},
      el("input", { type: "checkbox", ...(field.trick_room ? { checked: "" } : {}),
        onchange: (e) => { field.trick_room = e.target.checked; refresh(); } }), "Trick Room"),
    el("label", {},
      el("input", { type: "checkbox", ...(field.gravity ? { checked: "" } : {}),
        onchange: (e) => { field.gravity = e.target.checked; refresh(); } }), "Gravity"),
  );
  panel.append(row);
}

/* ---------------- probabilities ---------------- */

let seq = 0, timer = null;

function refresh() {
  $("#raw-json").value = JSON.stringify(battleDoc() || state.battle, null, 1);
  clearTimeout(timer);
  timer = setTimeout(fetchProbabilities, 180);
}

async function fetchProbabilities() {
  const doc = battleDoc();
  if (!doc) return;
  const mySeq = ++seq;
  try {
    const resp = await fetch("/api/probabilities", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(doc),
    });
    const body = await resp.json();
    if (mySeq !== seq) return;
    if (!resp.ok) { showError(body); return; }
    showError(null);
    renderProbabilities(body);
  } catch (err) {
    if (mySeq === seq) showError({ error: { type: "network", message: String(err) } });
  }
}

function renderProbabilities(data) {
  const panel = $("#prob-panel");
  panel.replaceChildren();
  panel.append(el("div", { class: "mini", style: "color:var(--dim)" },
    `flags: ${data.active_flags.join(", ")}`));
  for (const action of data.actions) {
    const pctNum = action.pick.float * 100;
    const box = el("div", { class: "action" });
    box.append(el("div", { class: "top" },
      el("span", { class: "mv" }, action.move),
      el("span", { class: "pct" }, `${pctNum.toFixed(2)}%`)));
    box.append(el("div", { class: "bar" }, el("div", { style: `width:${pctNum}%` })));
    box.append(el("div", { class: "frac" }, action.pick.fraction));
    const finals = action.final_dist.map(([s, p]) => `${s}: ${p}`).join("  ·  ");
    const dists = el("div", { class: "dists" }, el("b", {}, "score "), finals);
    for (const [flag, pairs] of Object.entries(action.flag_dists)) {
      dists.append(el("div", {}, el("b", {}, flag + " "),
        pairs.map(([d, p]) => `${d >= 0 ? "+" + d : d}: ${p}`).join("  ")));
    }
    box.append(dists);
    panel.append(box);
  }
}

function showError(body) {
  const panel = $("#error-panel");
  panel.replaceChildren();
  if (!body) return;
  const box = el("div", { class: "error-box" },
    `${body.error.type}: ${body.error.message}`);
  if (body.error.hint) box.append(el("span", { class: "hint" }, `hint: ${body.error.hint}`));
  panel.append(box);
}

/* ---------------- case load/export ---------------- */

function exportCase() {
  const doc = battleDoc();
  if (!doc) { showError({ error: { type: "UI", message: "set both Pokémon first" } }); return; }
  const full = { format: 1, name: "exported from simulator", battle: doc };
  const blob = new Blob([JSON.stringify(full, null, 2)], { type: "application/json" });
  const a = el("a", { href: URL.createObjectURL(blob), download: "case.json" });
  a.click();
  URL.revokeObjectURL(a.href);
}

async function loadCaseFile(ev) {
  const file = ev.target.files[0];
  if (!file) return;
  const doc = JSON.parse(await file.text());
  const battle = doc.battle || doc;
  adoptBattle(battle);
}

function applyRawJSON() {
  try {
    adoptBattle(JSON.parse($("#raw-json").value));
  } catch (err) {
    showError({ error: { type: "JSON", message: String(err) } });
  }
}

function adoptBattle(battle) {
  // Fill optional keys so the editors have something to bind to.
  for (const which of ["ai", "player"]) {
    const side = battle[which];
    if (!side) continue;
    battle[which] = { ...newSide(side.pokemon), ...side };
    const mon = battle[which].pokemon;
    mon.boosts = mon.boosts || {};
    mon.volatiles = mon.volatiles || [];
    mon.current_hp = mon.current_hp ?? mon.max_hp;
  }
  battle.field = { weather: null, turn: 1, trick_room: false, gravity: false,
                   ...(battle.field || {}) };
  state.battle = battle;
  renderField();
  renderMon("ai"); renderSide("ai");
  renderMon("player"); renderSide("player");
  $("#ai-flags").replaceChildren(
    ...battle.flags.map((f) => el("span", { class: "flag" }, f)));
  refresh();
}

init();

/* Kaizo AI Simulator — fully reactive: every input mutates the battle doc
   and recomputes probabilities AND damage rolls immediately. Layout follows
   the HZLA/Showdown calculator anatomy: damage strip on top (your moves
   left, the AI's right, a headline with the exact roll list underneath),
   then your Pokémon | field | AI Pokémon. */
"use strict";

const state = {
  meta: null, tables: null, trainers: [],
  trainerParty: [],          // /api/trainer party entries
  activeAiIndex: null,
  damage: null,              // /api/damage response
  sel: null,                 // {side: "player"|"ai", index} — headline move
  playerBuild: {             // build inputs that derive the player mon's stats
    nature: "Hardy",
    ivs: { hp: 31, atk: 31, def: 31, spa: 31, spd: 31, spe: 31 },
  },
  battle: {
    flags: [],
    field: { weather: null, turn: 1, trick_room: false, gravity: false },
    ai: null,
    player: null,
  },
};

const STATS = ["atk", "def", "spa", "spd", "spe"];
const $ = (sel) => document.querySelector(sel);
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else if (v !== false && v !== undefined) node.setAttribute(k, v === true ? "" : v);
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

async function postJSON(url, doc) {
  try {
    const resp = await fetch(url, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(doc),
    });
    return { ok: resp.ok, body: await resp.json() };
  } catch (err) {
    return { ok: false, body: { error: { type: "network", message: String(err) } } };
  }
}

/* ---------------- init ---------------- */

async function init() {
  [state.meta, state.tables] = await Promise.all([
    getJSON("/api/meta"), getJSON("/api/tables"),
  ]);
  state.trainers = (await getJSON("/api/trainers")).trainers;

  const tl = $("#trainer-list");
  for (const t of state.trainers) {
    tl.append(el("option", { value: `${t.name}${t.location ? " — " + t.location : ""} (#${t.id})` }));
  }
  const sl = $("#species-list");
  for (const name of Object.keys(state.tables.species)) sl.append(el("option", { value: name }));
  const ml = $("#move-list");
  for (const name of Object.keys(state.tables.moves)) ml.append(el("option", { value: name }));

  $("#trainer-search").addEventListener("change", onTrainerPicked);
  $("#export-case").addEventListener("click", exportCase);
  $("#load-case").addEventListener("change", loadCaseFile);
  $("#apply-raw").addEventListener("click", applyRawJSON);

  renderAll();
}

function renderAll() {
  renderField();
  renderSideConditions();
  renderPanel("player");
  renderPanel("ai");
  refresh();
}

/* ---------------- doc plumbing ---------------- */

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
  if (!b.ai || !b.player || !b.flags.length) return null;
  const clean = JSON.parse(JSON.stringify(b));
  for (const side of [clean.ai, clean.player]) {
    for (const h of Object.keys(side.hazards)) if (!side.hazards[h]) delete side.hazards[h];
    const mon = side.pokemon;
    if (mon.boosts) for (const s of Object.keys(mon.boosts)) if (!mon.boosts[s]) delete mon.boosts[s];
    for (const key of Object.keys(mon))
      if (mon[key] === null || mon[key] === "" ||
          (Array.isArray(mon[key]) && !mon[key].length)) delete mon[key];
    if (mon.protect_streak === 0) delete mon.protect_streak;
    if (mon.turns_active === 1) delete mon.turns_active;
    if (mon.current_hp === mon.max_hp) delete mon.current_hp;
    mon.moves = (mon.moves || []).filter(Boolean);
  }
  if (!clean.field.weather) delete clean.field.weather;
  return clean;
}

/* ---------------- trainer / AI side ---------------- */

async function onTrainerPicked(ev) {
  const match = /\(#(\d+)\)\s*$/.exec(ev.target.value);
  if (!match) return;
  const data = await getJSON(`/api/trainer?id=${match[1]}`);
  state.trainerParty = data.party;
  state.activeAiIndex = null;
  const strip = $("#trainer-party");
  strip.replaceChildren();
  data.party.forEach((entry, i) => {
    strip.append(el("div", { class: "party-chip", onclick: () => setAiMon(i) },
      entry.pokemon.species, " ", el("span", { class: "lv" }, `L${entry.pokemon.level}`)));
  });
  if (data.party.length) setAiMon(0);   // auto-select the lead: instant feedback
}

function setAiMon(index) {
  const entry = state.trainerParty[index];
  state.activeAiIndex = index;
  const mon = JSON.parse(JSON.stringify(entry.pokemon));
  const prev = state.battle.ai;
  state.battle.ai = {
    ...newSide(mon),
    ...(prev ? { hazards: prev.hazards, reflect: prev.reflect,
                 light_screen: prev.light_screen, tailwind: prev.tailwind,
                 safeguard: prev.safeguard, mist: prev.mist,
                 lucky_chant: prev.lucky_chant, future_attack: prev.future_attack } : {}),
    party_remaining: state.trainerParty.length - 1,
  };
  state.battle.flags = [...entry.ai_flags];
  document.querySelectorAll(".party-chip").forEach((c, i) =>
    c.classList.toggle("active", i === index));
  renderAiFlags(entry);
  renderPanel("ai");
  renderSideConditions();
  refresh();
}

function renderAiFlags(entry) {
  const row = $("#ai-flags");
  row.replaceChildren();
  for (const f of entry.ai_flags) row.append(el("span", { class: "flag" }, f));
  for (const f of entry.unsupported_flags)
    row.append(el("span", { class: "flag unsupported",
                            title: "not encoded — engine will refuse" }, f));
}

/* ---------------- player mon derivation ---------------- */

function ensurePlayerMon(species) {
  const sp = state.tables.species[species];
  if (!sp) return;
  const existing = state.battle.player?.pokemon;
  const mon = existing && existing.species === species ? existing : {
    species, level: existing?.level ?? 50,
    ability: sp.abilities[0] || "", item: null,
    types: sp.types, stats: {}, max_hp: 1, current_hp: null,
    status: null, boosts: {}, moves: ["", "", "", ""],
    weight_hg: sp.weight_hg,
  };
  mon.species = species;
  mon.types = sp.types;
  mon.weight_hg = sp.weight_hg;
  if (!existing || existing.species !== species) mon.ability = sp.abilities[0] || "";
  recomputePlayerStats(mon);
  if (!state.battle.player) state.battle.player = newSide(mon);
  else state.battle.player.pokemon = mon;
}

function recomputePlayerStats(mon) {
  const sp = state.tables.species[mon.species];
  if (!sp) return;
  const { nature, ivs } = state.playerBuild;
  const [up, down] = state.meta.nature_effects[nature];
  const atFull = mon.current_hp === null || mon.current_hp >= mon.max_hp;
  mon.max_hp = Math.floor((2 * sp.base.hp + ivs.hp) * mon.level / 100) + mon.level + 10;
  for (const s of STATS) {
    let v = Math.floor((2 * sp.base[s] + ivs[s]) * mon.level / 100) + 5;
    if (s === up) v = Math.floor(v * 110 / 100);
    else if (s === down) v = Math.floor(v * 90 / 100);
    mon.stats[s] = v;
  }
  if (atFull) mon.current_hp = mon.max_hp;
  else mon.current_hp = Math.min(mon.current_hp, mon.max_hp);
}

/* ---------------- unified Pokémon panel ---------------- */

function renderPanel(which) {
  const panel = $(`#${which}-panel`);
  panel.replaceChildren();
  const side = state.battle[which];
  const isPlayer = which === "player";

  // Species / level header
  const head = el("div", { class: "row" });
  if (isPlayer) {
    head.append(el("input", {
      list: "species-list", placeholder: "Species…", class: "species-input",
      value: side?.pokemon?.species || "",
      onchange: (e) => { ensurePlayerMon(e.target.value.trim());
                         renderPanel("player"); renderSideConditions(); refresh(); },
    }));
  }
  if (!side) {
    if (isPlayer) panel.append(head);
    else panel.append(el("p", { class: "placeholder" }, "Pick a trainer, then a party member."));
    return;
  }
  const mon = side.pokemon;
  if (isPlayer) {
    head.append(
      el("label", {}, "Lv",
        el("input", { type: "number", value: mon.level, min: 1, max: 100, style: "width:4em",
          onchange: (e) => { mon.level = clampInt(e.target.value, 1, 100, 50);
                             recomputePlayerStats(mon); renderPanel("player"); refresh(); } })),
      el("select", { onchange: (e) => { state.playerBuild.nature = e.target.value;
                                        recomputePlayerStats(mon); renderPanel("player"); refresh(); } },
        ...state.meta.natures.map((n) =>
          el("option", { value: n, selected: state.playerBuild.nature === n }, n))),
    );
  } else {
    head.append(el("span", { class: "big-name" }, mon.species),
                el("span", { class: "dim" }, ` Lv ${mon.level}`));
  }
  panel.append(head);
  panel.append(el("div", { class: "type-row" },
    ...mon.types.map((t) => el("span", { class: `type-chip t-${t}` }, t))));

  // Ability / item / status
  const idRow = el("div", { class: "row mini" });
  idRow.append(
    el("label", {}, "Ability",
      el("input", { value: mon.ability || "", style: "width:8.5em",
        onchange: (e) => { mon.ability = e.target.value.trim(); refresh(); } })),
    el("label", {}, "Item",
      el("input", { value: mon.item || "", placeholder: "(none)", style: "width:8em",
        onchange: (e) => { mon.item = e.target.value.trim() || null; refresh(); } })),
    el("label", {}, "Status",
      el("select", { onchange: (e) => { mon.status = e.target.value || null; refresh(); } },
        el("option", { value: "" }, "healthy"),
        ...state.meta.statuses.map((s) =>
          el("option", { value: s, selected: mon.status === s }, s)))),
  );
  panel.append(idRow);

  // HP
  const hp = mon.current_hp ?? mon.max_hp;
  const pct = Math.max(0, Math.min(100, Math.round(100 * hp / mon.max_hp)));
  panel.append(el("div", { class: "hp-row" },
    "HP",
    el("input", { type: "number", value: hp, min: 0, max: mon.max_hp,
      onchange: (e) => { mon.current_hp = clampInt(e.target.value, 0, mon.max_hp, mon.max_hp);
                         renderPanel(which); refresh(); } }),
    `/${mon.max_hp}`,
    el("div", { class: "hp-bar" },
      el("div", { style: `width:${pct}%; background:${pct > 50 ? "var(--good)" : pct > 20 ? "var(--warn)" : "var(--bad)"}` })),
    el("span", { class: "dim mini" }, `${pct}%`),
  ));

  // Stat rows with inline boosts (calc-style)
  const grid = el("div", { class: "stat-grid" });
  grid.append(el("span", { class: "dim" }, ""), el("span", { class: "dim" }, "stat"),
              el("span", { class: "dim" }, "boost"));
  for (const s of STATS) {
    grid.append(
      el("span", { class: "stat-name" }, s.toUpperCase()),
      isPlayer
        ? el("span", {}, String(mon.stats[s]))
        : el("input", { type: "number", value: mon.stats[s], min: 1, class: "stat-edit",
            onchange: (e) => { mon.stats[s] = clampInt(e.target.value, 1, 9999, mon.stats[s]); refresh(); } }),
      boostSelect(mon, s),
    );
  }
  grid.append(el("span", { class: "stat-name" }, "ACC"), el("span", {}, "—"), boostSelect(mon, "acc"));
  grid.append(el("span", { class: "stat-name" }, "EVA"), el("span", {}, "—"), boostSelect(mon, "eva"));
  panel.append(grid);

  // Player IVs (compact, under stats)
  if (isPlayer) {
    const ivRow = el("div", { class: "row mini" }, "IVs ");
    for (const s of ["hp", ...STATS]) {
      ivRow.append(el("label", {}, s,
        el("input", { type: "number", value: state.playerBuild.ivs[s], min: 0, max: 31, style: "width:3.6em",
          onchange: (e) => { state.playerBuild.ivs[s] = clampInt(e.target.value, 0, 31, 31);
                             recomputePlayerStats(mon); renderPanel("player"); refresh(); } })));
    }
    panel.append(ivRow);
  }

  // Moves ×4, one per row with power/type readout
  const mv = el("div", { class: "moves-list" });
  for (let i = 0; i < 4; i++) {
    const meta = el("span", { class: "move-meta dim mini" });
    const setMeta = (name) => {
      const info = state.tables.moves[name];
      meta.textContent = info ? `${info.power || "—"} ${info.type}` : "";
    };
    setMeta(mon.moves[i] || "");
    mv.append(el("div", { class: "move-row" },
      el("input", { list: "move-list", value: mon.moves[i] || "",
        placeholder: `Move ${i + 1}`,
        onchange: (e) => { mon.moves[i] = e.target.value.trim();
                           setMeta(mon.moves[i]); refresh(); } }),
      meta));
  }
  panel.append(mv);

  // Battle-history extras
  panel.append(el("div", { class: "row mini" },
    el("label", {}, "last move",
      el("input", { list: "move-list", value: mon.last_move || "", style: "width:8.5em",
        onchange: (e) => { mon.last_move = e.target.value.trim() || null; refresh(); } })),
    el("label", {}, "turns out",
      el("input", { type: "number", value: mon.turns_active ?? 1, min: 1, style: "width:3.5em",
        onchange: (e) => { mon.turns_active = clampInt(e.target.value, 1, 999, 1); refresh(); } })),
    el("label", {}, "protect streak",
      el("input", { type: "number", value: mon.protect_streak ?? 0, min: 0, style: "width:3.5em",
        onchange: (e) => { mon.protect_streak = clampInt(e.target.value, 0, 99, 0); refresh(); } })),
  ));

  const vols = el("div", { class: "vol-grid" });
  for (const v of state.meta.volatiles) {
    vols.append(el("label", {},
      el("input", { type: "checkbox", checked: (mon.volatiles || []).includes(v),
        onchange: (e) => {
          mon.volatiles = mon.volatiles || [];
          if (e.target.checked) mon.volatiles.push(v);
          else mon.volatiles = mon.volatiles.filter((x) => x !== v);
          refresh();
        } }), v));
  }
  panel.append(el("details", {}, el("summary", {}, "volatiles"), vols));
}

function boostSelect(mon, stat) {
  const sel = el("select", { class: "boost-select",
    onchange: (e) => { mon.boosts = mon.boosts || {};
                       mon.boosts[stat] = parseInt(e.target.value, 10); refresh(); } });
  for (let b = 6; b >= -6; b--) {
    sel.append(el("option", { value: b, selected: ((mon.boosts || {})[stat] || 0) === b },
      b > 0 ? `+${b}` : String(b)));
  }
  return sel;
}

function clampInt(value, min, max, fallback) {
  const n = parseInt(value, 10);
  if (Number.isNaN(n)) return fallback;
  return Math.max(min, Math.min(max, n));
}

/* ---------------- field + side conditions ---------------- */

function renderField() {
  const panel = $("#field-controls");
  panel.replaceChildren();
  const field = state.battle.field;

  const weatherRow = el("div", { class: "seg-row" });
  for (const w of [null, ...state.meta.weathers]) {
    weatherRow.append(el("button", {
      class: "seg" + (field.weather === w ? " on" : ""),
      onclick: () => { field.weather = w; renderField(); refresh(); },
    }, w || "none"));
  }
  panel.append(weatherRow);

  panel.append(el("div", { class: "row" },
    el("label", {}, "turn",
      el("input", { type: "number", value: field.turn, min: 1, style: "width:4em",
        onchange: (e) => { field.turn = clampInt(e.target.value, 1, 999, 1); refresh(); } })),
    el("button", { class: "toggle" + (field.trick_room ? " on" : ""),
      onclick: (e) => { field.trick_room = !field.trick_room;
                        e.target.classList.toggle("on"); refresh(); } }, "Trick Room"),
    el("button", { class: "toggle" + (field.gravity ? " on" : ""),
      onclick: (e) => { field.gravity = !field.gravity;
                        e.target.classList.toggle("on"); refresh(); } }, "Gravity"),
  ));
}

function renderSideConditions() {
  const box = $("#side-conditions");
  box.replaceChildren();
  const grid = el("div", { class: "cond-grid" });
  for (const which of ["player", "ai"]) {
    const side = state.battle[which];
    const cell = el("div", { class: "cond-cell" });
    cell.append(el("div", { class: "cond-title" },
      which === "player" ? "Your side" : "AI side"));
    if (!side) {
      cell.append(el("div", { class: "dim mini" }, "—"));
      grid.append(cell);
      continue;
    }
    const chips = el("div", { class: "chip-row" });
    for (const flag of ["reflect", "light_screen", "tailwind", "safeguard", "mist", "lucky_chant"]) {
      chips.append(el("button", { class: "toggle mini" + (side[flag] ? " on" : ""),
        onclick: (e) => { side[flag] = !side[flag];
                          e.target.classList.toggle("on"); refresh(); } },
        flag.replace("_", " ")));
    }
    cell.append(chips);
    const hz = el("div", { class: "row mini" });
    for (const h of state.meta.hazards) {
      hz.append(el("label", {}, h.replace(/_/g, " "),
        el("input", { type: "number", value: side.hazards[h] || 0, min: 0, max: 3, style: "width:3em",
          onchange: (e) => { side.hazards[h] = clampInt(e.target.value, 0, 3, 0); refresh(); } })));
    }
    cell.append(hz);
    cell.append(el("div", { class: "row mini" },
      el("label", {}, "bench alive",
        el("input", { type: "number", value: side.party_remaining, min: 0, max: 5,
          onchange: (e) => { side.party_remaining = clampInt(e.target.value, 0, 5, 1); refresh(); } }))));
    grid.append(cell);
  }
  box.append(grid);
}

/* ---------------- live results (probabilities + damage) ---------------- */

let seq = 0, timer = null;

function refresh() {
  $("#raw-json").value = JSON.stringify(battleDoc() || state.battle, null, 1);
  clearTimeout(timer);
  timer = setTimeout(fetchAll, 150);
}

async function fetchAll() {
  const doc = battleDoc();
  const mySeq = ++seq;
  if (!doc) {
    state.damage = null;
    renderDamageStrip();
    $("#prob-panel").replaceChildren(
      el("p", { class: "placeholder" },
        !state.battle.ai ? "Pick a trainer Pokémon (right side)."
                         : "Set your Pokémon's species (left side)."));
    return;
  }
  const [probs, dmg] = await Promise.all([
    postJSON("/api/probabilities", doc), postJSON("/api/damage", doc),
  ]);
  if (mySeq !== seq) return;
  state.damage = dmg.ok ? dmg.body : null;
  ensureSelection();
  renderDamageStrip();
  if (probs.ok) {
    showError(dmg.ok ? null : dmg.body);
    renderProbabilities(probs.body);
  } else {
    showError(probs.body);
  }
}

function ensureSelection() {
  const d = state.damage;
  if (!d) { state.sel = null; return; }
  const valid = (s) => s && d[s.side] && d[s.side][s.index]
                       && d[s.side][s.index].kind === "damage";
  if (valid(state.sel)) return;
  state.sel = null;
  for (const side of ["player", "ai"]) {   // prefer your own best move
    let best = null;
    (d[side] || []).forEach((e, i) => {
      if (e.kind === "damage" && e.max > 0 && (!best || e.max_pct > best.pct))
        best = { side, index: i, pct: e.max_pct };
    });
    if (best) { state.sel = { side: best.side, index: best.index }; return; }
  }
}

function renderDamageStrip() {
  const d = state.damage;
  for (const side of ["player", "ai"]) {
    const box = $(side === "player" ? "#dmg-player" : "#dmg-ai");
    box.replaceChildren();
    if (!d) continue;
    (d[side] || []).forEach((e, i) => {
      const selected = state.sel && state.sel.side === side && state.sel.index === i;
      const row = el("div", {
        class: "dmg-row" + (selected ? " sel" : "") + (e.kind !== "damage" ? " inert" : ""),
        onclick: () => {
          if (e.kind !== "damage") return;
          state.sel = { side, index: i };
          renderDamageStrip();
        },
      });
      let range;
      if (e.kind === "damage") range = e.max === 0 ? "immune" : `${e.min_pct} - ${e.max_pct}%`;
      else if (e.kind === "status") range = "—";
      else { range = "n/a"; row.title = e.reason; }
      const name = el("span", { class: "dmg-name" }, e.move);
      const pct = el("span", { class: "dmg-range" }, range);
      if (side === "player") row.append(name, pct);
      else row.append(pct, name);
      box.append(row);
    });
  }
  renderHeadline();
}

function renderHeadline() {
  const bar = $("#dmg-headline");
  bar.replaceChildren();
  const d = state.damage, sel = state.sel;
  if (!d || !sel) {
    bar.append(el("span", { class: "dim mini" }, "Set both Pokémon to see damage rolls."));
    return;
  }
  const e = d[sel.side][sel.index];
  const atk = (sel.side === "player" ? state.battle.player : state.battle.ai).pokemon;
  const tgt = (sel.side === "player" ? state.battle.ai : state.battle.player).pokemon;
  const item = atk.item ? `${atk.item} ` : "";
  let text = `Lv${atk.level} ${item}${atk.species} ${e.move} vs. Lv${tgt.level} ${tgt.species}: `;
  text += e.max === 0 ? "no damage (immune)"
        : `${e.min}-${e.max} (${e.min_pct} - ${e.max_pct}%) — ${e.ko}`;
  bar.append(el("div", { class: "headline-main" }, text));
  if (e.caveat) bar.append(el("div", { class: "headline-caveat" }, `⚠ ${e.caveat}`));
  if (e.max > 0) {
    if (e.outcomes.length === 1) {
      bar.append(el("div", { class: "headline-rolls" },
        `Rolls: (${e.outcomes[0].rolls.join(", ")})`));
    } else {
      for (const o of e.outcomes) {   // Bulldoze tiers, Triple Axel values
        bar.append(el("div", { class: "headline-rolls" },
          `${o.desc} (${fracPct(o.chance)}): ${o.min}-${o.max} (${o.min_pct} - ${o.max_pct}%)`));
      }
    }
  }
}

function fracPct(frac) {  // "1/11" -> "9%"
  const [n, den] = frac.split("/").map(Number);
  return `${Math.round(100 * n / (den || 1))}%`;
}

function renderProbabilities(data) {
  const panel = $("#prob-panel");
  panel.replaceChildren();
  panel.append(el("div", { class: "mini dim" }, `flags: ${data.active_flags.join(", ")}`));
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
        pairs.map(([dd, p]) => `${dd >= 0 ? "+" + dd : dd}: ${p}`).join("  ")));
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
  try {
    const doc = JSON.parse(await file.text());
    adoptBattle(doc.battle || doc);
  } catch (err) {
    showError({ error: { type: "JSON", message: String(err) } });
  }
  ev.target.value = "";
}

function applyRawJSON() {
  try {
    adoptBattle(JSON.parse($("#raw-json").value));
  } catch (err) {
    showError({ error: { type: "JSON", message: String(err) } });
  }
}

function adoptBattle(battle) {
  for (const which of ["ai", "player"]) {
    const side = battle[which];
    if (!side) continue;
    battle[which] = { ...newSide(side.pokemon), ...side };
    const mon = battle[which].pokemon;
    mon.boosts = mon.boosts || {};
    mon.volatiles = mon.volatiles || [];
    mon.moves = [...(mon.moves || []), "", "", "", ""].slice(0, 4);
    mon.current_hp = mon.current_hp ?? mon.max_hp;
  }
  battle.field = { weather: null, turn: 1, trick_room: false, gravity: false,
                   ...(battle.field || {}) };
  battle.flags = battle.flags || [];
  state.battle = battle;
  state.activeAiIndex = null;
  state.sel = null;
  $("#ai-flags").replaceChildren(
    ...battle.flags.map((f) => el("span", { class: "flag" }, f)));
  document.querySelectorAll(".party-chip").forEach((c) => c.classList.remove("active"));
  renderAll();
}

init();

/* Lords Mobile Wonder Guide - small, dependency-free behaviour.
   1. Comps page: recompute troop counts for a rally size.
   2. Battle log: filter rows.
   3. Home: scout reader. Same rules as the Wonder rules page. */
(function () {
  "use strict";

  // ---------- number helpers ----------
  function parseTroops(raw) {
    if (raw == null) return null;
    var s = String(raw).trim().toLowerCase().replace(/[,\s_]/g, "");
    if (!s) return null;
    var mult = 1;
    if (/m$/.test(s)) { mult = 1e6; s = s.slice(0, -1); }
    else if (/k$/.test(s)) { mult = 1e3; s = s.slice(0, -1); }
    var n = parseFloat(s);
    if (!isFinite(n) || n < 0) return null;
    // "1.55" with no suffix almost always means millions on a scout
    if (mult === 1 && n > 0 && n < 50 && /\./.test(s)) mult = 1e6;
    return Math.round(n * mult);
  }

  function fmt(n) {
    if (n == null) return "—";
    var a = Math.abs(n);
    var sign = n < 0 ? "−" : "";
    if (a >= 1e6) return sign + (a / 1e6).toFixed(2) + "M";
    return sign + Math.round(a / 1e3).toLocaleString() + "K";
  }

  function signed(n) { return (n > 0 ? "+" : "") + fmt(n); }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }

  // ---------- 1. comps page: rally size ----------
  var rally = document.getElementById("rally");
  if (rally) {
    var cells = document.querySelectorAll("[data-parts]");
    var update = function () {
      var total = parseTroops(rally.value);
      if (!total) return;
      cells.forEach(function (el) {
        el.textContent = fmt(Math.round(total * Number(el.getAttribute("data-parts")) / 20));
      });
    };
    rally.addEventListener("input", update);
  }

  // ---------- 2. battle log filters ----------
  var filters = document.querySelectorAll("[data-filter]");
  if (filters.length) {
    var rows = document.querySelectorAll("tr[data-group]");
    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var f = btn.getAttribute("data-filter");
        filters.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        rows.forEach(function (r) {
          var tags = (r.getAttribute("data-tags") || "").split(" ");
          var show = f === "all" || r.getAttribute("data-group") === f || tags.indexOf(f) !== -1;
          r.hidden = !show;
        });
      });
    });
  }

  // ---------- 3. scout reader ----------
  var form = document.getElementById("scout");
  if (!form) return;

  // Named comps as parts of 20 (055/208/307 use what actually lands in the logs)
  var COMPS = [
    ["659", [6, 5, 9]], ["569", [5, 6, 9]], ["758", [7, 5, 8]], ["857", [8, 5, 7]],
    ["668", [6, 6, 8]], ["866", [8, 6, 6]], ["884", [8, 8, 4]], ["875", [8, 7, 5]],
    ["785", [7, 8, 5]], ["965", [9, 6, 5]], ["947", [9, 4, 7]], ["956", [9, 5, 6]],
    ["749", [7, 4, 9]], ["776", [7, 7, 6]], ["992", [9, 9, 2]], ["974", [9, 7, 4]],
    ["442", [8, 8, 4]], ["1433", [14, 3, 3]], ["1262", [12, 6, 2]],
    ["055", [0.2, 11, 8.8]], ["208", [4.8, 0.6, 14.6]], ["307", [6, 0.6, 13.4]]
  ];

  var ids = ["ti", "tr", "tc", "yi", "yr", "yc", "cap"];
  var el = {};
  ids.forEach(function (id) { el[id] = document.getElementById(id); });
  var out = document.getElementById("readout");
  var NAMES = ["infantry", "ranged", "cav"];

  function cap() { return parseTroops(el.cap.value) || 4313000; }

  // Read three boxes. If exactly one is empty, fill it from the rally cap.
  function read(prefix) {
    var boxes = [el[prefix + "i"], el[prefix + "r"], el[prefix + "c"]];
    var v = boxes.map(function (b) { return parseTroops(b.value); });
    var missing = v.reduce(function (n, x) { return n + (x == null ? 1 : 0); }, 0);
    var auto = -1;
    boxes.forEach(function (b) { b.placeholder = ""; });
    if (missing === 1) {
      auto = v.indexOf(null);
      var rest = cap() - v.reduce(function (s, x) { return s + (x || 0); }, 0);
      if (rest >= 0) { v[auto] = rest; boxes[auto].placeholder = fmt(rest); }
      else auto = -2;
    }
    return { v: v, auto: auto, empty: missing === 3 };
  }

  function nearest(parts) {
    var best = null;
    COMPS.forEach(function (c) {
      var d = 0;
      for (var k = 0; k < 3; k++) d += Math.pow(parts[k] - c[1][k], 2);
      if (!best || d < best.d) best = { name: c[0], d: d };
    });
    return best;
  }

  function compTroops(name) {
    for (var k = 0; k < COMPS.length; k++) {
      if (COMPS[k][0] === name) {
        var p = COMPS[k][1], c = cap();
        return p.map(function (x) { return Math.round(c * x / 20); });
      }
    }
    return null;
  }

  function codeHtml(parts) {
    var r = parts.map(function (p) { return Math.round(p); });
    return '<span class="code" aria-label="' + r.join("-") + ' split"><span class="i">' + r[0] +
      '</span><span class="r">' + r[1] + '</span><span class="c">' + r[2] + "</span></span>";
  }

  function mirrorScore(us, them) { return (us[2] - them[2]) + 0.5 * (us[1] - them[1]); }

  function leanText(score) {
    if (score > 300000) return '<span class="win">strong for you</span>';
    if (score > 80000) return '<span class="win">leans your way</span>';
    if (score > -80000) return '<span class="even">coin flip, stats decide</span>';
    return '<span class="loss">leans their way</span>';
  }

  // What they are and which formation counters their front.
  function profile(t) {
    var total = t[0] + t[1] + t[2];
    var order = [0, 1, 2].sort(function (a, b) { return t[b] - t[a]; });
    return {
      total: total,
      parts: t.map(function (x) { return x / total * 20; }),
      big: order[0],
      close: (t[order[0]] - t[order[1]]) / total < 0.04,
      second: order[1],
      is055: t[0] < 200000 && t[1] > 1500000 && t[2] > 1000000
    };
  }

  // If they hit you: what to sit in.
  function defendCall(t, p) {
    if (p.is055) return ["Ranged Phalanx", "It's a 055: their real front is ranged with cav behind. Your ranged in front kills the cav. Hold 1.1M+ ranged and 1.4M+ infantry."];
    if (p.big === 2) return ["Ranged Phalanx", "Their cav is the biggest stack (" + fmt(t[2]) + "). Ranged beats cav."];
    if (p.big === 1) return ["Infantry Phalanx", "Their ranged is the biggest stack (" + fmt(t[1]) + "). Infantry beats ranged."];
    return ["Cavalry Phalanx", "Their infantry is the biggest stack (" + fmt(t[0]) + "). Cav beats infantry."];
  }

  // If you hit them: which comp to send and in what. Built from the battle log rules.
  function attackCall(t, p) {
    var c = cap(), part = c / 20, notes = [];
    if (p.is055) {
      return { comp: "866 or 857", form: "Infantry Phalanx",
        why: "Their front is a big ranged stack and infantry beats ranged. No logged win against a 055 holder yet (log 9: an 875 lost to one), so treat this as a test.",
        notes: [] };
    }
    if (p.big === 2 || t[2] >= 1600000) {
      // cav-heavy target: you need more cav than them
      var pick = null;
      [["668", 8], ["569", 9], ["659", 9]].some(function (o) {
        if (o[1] * part > t[2] + 150000) { pick = o[0]; return true; }
        return false;
      });
      if (pick === "659" || (pick === "569" && t[1] > 1300000)) pick = "569";
      if (!pick) {
        return { comp: "Skip", form: "—",
          why: "They have " + fmt(t[2]) + " cav. Even a 9-part cav rally (" + fmt(9 * part) + ") doesn't clearly out-cav them, and more cav wins Range Phalanx mirrors.",
          notes: t[1] <= 1100000 ? ["A 055 can still work if your lead is clearly stronger (log 10)."] : [] };
      }
      if (t[1] <= 1100000) notes.push("If your 055 lead is clearly stronger, a 055 in Infantry Wedge also wins this (log 10).");
      return { comp: pick, form: "Ranged Phalanx",
        why: "In a Range Phalanx mirror more cav wins. A " + pick + " brings " + fmt(compTroops(pick)[2]) + " cav against their " + fmt(t[2]) + ".",
        notes: notes };
    }
    if (p.big === 1) {
      if (t[2] < 1000000) return { comp: "1433", form: "Infantry Phalanx",
        why: "Ranged-heavy with under 1M cav. Your infantry front beats their ranged, and they have little cav to punish it.",
        notes: ["Their ranged is over 1.1M, so no 208."] };
      return { comp: "668", form: "Ranged Phalanx",
        why: "Ranged-heavy with real cav behind it. Your sheet lists 668 in Range Phalanx as a win against this shape (884).",
        notes: ["A 055 into about 1.76M ranged traded even twice (logs 8, 14). Fine if you're stronger, not a sure win."] };
    }
    // infantry-heavy
    if (t[2] < 1000000) return { comp: "668", form: "Ranged Phalanx (Cav Phalanx if they sit Inf Phalanx)",
      why: "Infantry pile with low cav. A 668 out-cavs them by " + fmt(8 * part - t[2]) + "; that won by 527K in log 4.",
      notes: [] };
    return { comp: (9 * part > t[2] + 150000) ? "659" : "668", form: "Cavalry Phalanx (Ranged Phalanx if they sit Ranged Phalanx)",
      why: "Infantry is their biggest stack and cav beats infantry. If they sit Ranged Phalanx instead, it becomes a mirror and your cav count decides it.",
      notes: [] };
  }

  function li(xs) { return xs.length ? "<ul>" + xs.map(function (n) { return "<li>" + n + "</li>"; }).join("") + "</ul>" : ""; }

  function render() {
    var T = read("t");
    var t = T.v;
    if (t.some(function (x) { return x == null; })) {
      out.setAttribute("data-empty", "");
      out.innerHTML = T.auto === -2 ? "Those numbers add up to more than the rally cap. Fill all three, or raise the cap."
        : "Enter at least two of their troop totals to get a read.";
      return;
    }
    out.removeAttribute("data-empty");
    var p = profile(t);
    var near = nearest(p.parts);
    var head = codeHtml(p.parts) +
      '<p class="muted">' + fmt(p.total) + " total. Closest named comp: <strong>" + esc(near.name) + "</strong>." +
      (T.auto >= 0 ? ' <span class="auto">' + NAMES[T.auto].charAt(0).toUpperCase() + NAMES[T.auto].slice(1) + " filled from the rally cap: " + fmt(t[T.auto]) + ".</span>" : "") + "</p>";
    var warn = [];
    if (p.close && !p.is055) warn.push("Their top two stacks are within 4% (" + NAMES[p.big] + " and " + NAMES[p.second] + "). Wait for final numbers.");

    // defend
    var d = defendCall(t, p);
    var html = head + "<h3>If they hit you</h3><p class=\"call\">Sit " + esc(d[0]) + "</p><p>" + esc(d[1]) + "</p>";

    var Y = read("y");
    var y = Y.v;
    var haveYours = !y.some(function (x) { return x == null; });
    if (haveYours) {
      var g = [];
      if (y[0] < 1400000) g.push("infantry under 1.4M (" + fmt(y[0]) + ")");
      if (y[1] < 1100000) g.push("ranged under 1.1M (" + fmt(y[1]) + ")");
      if (y[2] < 1600000) g.push("cav under 1.6M (" + fmt(y[2]) + ")");
      if (g.length) html += '<p class="loss"><strong>Holding check:</strong> ' + esc(g.join(", ")) + ".</p>";
      else html += '<p class="win"><strong>Holding check:</strong> you meet the minimums.</p>';
    }

    // attack
    html += "<h3>If you hit them</h3>";
    if (haveYours) {
      var you = profile(y);
      var yourNear = nearest(you.parts).name;
      var score = mirrorScore(y, t);
      html += '<p class="call">Your ' + esc(yourNear) + ": " + leanText(score) + " in a Range Phalanx mirror</p>" +
        "<p>Cav gap " + signed(y[2] - t[2]) + ", ranged gap " + signed(y[1] - t[1]) + ".</p>";
      if (score < -80000) {
        var a = attackCall(t, p);
        html += a.comp === "Skip"
          ? "<p><strong>Skip this one.</strong> " + esc(a.why) + "</p>"
          : "<p>Better: send a <strong>" + esc(a.comp) + "</strong> in " + esc(a.form) + ". " + esc(a.why) + "</p>";
      }
    } else {
      var a2 = attackCall(t, p);
      html += '<p class="call">' + (a2.comp === "Skip" ? "Skip them" : "Send " + esc(a2.comp)) + (a2.comp !== "Skip" ? " in " + esc(a2.form) : "") + "</p><p>" + esc(a2.why) + "</p>" + li(a2.notes.map(esc));
      if (a2.comp !== "Skip" && compTroops(a2.comp.split(" ")[0])) {
        var ct = compTroops(a2.comp.split(" ")[0]);
        html += '<p class="muted">At your cap that\'s ' + fmt(ct[0]) + " / " + fmt(ct[1]) + " / " + fmt(ct[2]) + ".</p>";
      }
    }
    html += li(warn.map(esc));
    out.innerHTML = html;
    out.classList.remove("flash"); void out.offsetWidth; out.classList.add("flash");
  }

  ids.forEach(function (id) { el[id].addEventListener("input", render); });
  document.getElementById("clear").addEventListener("click", function () {
    ["ti", "tr", "tc", "yi", "yr", "yc"].forEach(function (id) { el[id].value = ""; });
    render();
    el.ti.focus();
  });
  document.getElementById("example").addEventListener("click", function () {
    // Mc Qai's citadel from log 10, with only two numbers typed
    ["yi", "yr", "yc"].forEach(function (id) { el[id].value = ""; });
    el.ti.value = "1.55m"; el.tr.value = "1032k"; el.tc.value = "";
    render();
  });
})();

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
    ["794", [7, 9, 4]], ["1055", [10, 5, 5]], ["848", [8, 4, 8]], ["055", [0.2, 11, 8.8]], ["208", [4.8, 0.6, 14.6]], ["307", [6, 0.6, 13.4]]
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

  // Ranged Phalanx mirrors: troop counts alone called only 6 of 12 logged mirrors.
  // Most promising so far: ranged-heavy WITH real cav into a 424-type (won 7, 31; lost 13 by 61K). With almost no cav it lost (5, 6).
  function shape(t) {
    var tot = t[0] + t[1] + t[2], r = t[1] / tot * 20, c = t[2] / tot * 20;
    if (r >= 7.5 && c <= 5 && c >= 3) return "442";   // ranged-heavy that still brings real cav: 884, 794, 785
    if (r >= 7.5 && c < 3) return "thin";   // 8-11-1, 992: ranged-heavy with almost no cav
    if (r <= 6.5 && c >= 6) return "424"; // 857, 758, 659, 848, 749
    return "mixed";
  }
  // Working mirror rule (Wonder rules page): cav guard, then a 442 needs ~700K ranged lead, then more infantry wins. Called 10 of 12 logged mirrors.
  function mirrorText(y, t) {
    var py = y.map(function (x) { return x / (y[0] + y[1] + y[2]) * 20; });
    var pt = t.map(function (x) { return x / (t[0] + t[1] + t[2]) * 20; });
    var hy = py[1] >= 7.5, ht = pt[1] >= 7.5;
    var W = '<span class="win">leans your way</span>', L = '<span class="loss">leans their way</span>', T = '<span class="even">toss-up</span>';
    if (hy && py[2] < 3) return [L, "You're ranged-heavy with almost no cav. Nothing guards your infantry once the ranged trade is done (8-11-1 lost twice, logs 5 and 6)."];
    if (ht && pt[2] < 3) return [W, "They're ranged-heavy with almost no cav, so nothing guards their infantry after the ranged trade (logs 5, 6)."];
    if (hy && !ht) return (y[1] - t[1] >= 700000)
      ? [W, "Ranged-heavy with a " + fmt(y[1] - t[1]) + " ranged lead: the 442 win (logs 7, 31)."]
      : [L, "Ranged-heavy but only " + signed(y[1] - t[1]) + " ranged ahead. Under about 700K the 424 wins (log 13)."];
    if (ht && !hy) return (t[1] - y[1] >= 700000)
      ? [L, "They're ranged-heavy with a " + fmt(t[1] - y[1]) + " ranged lead: the 442 win for them (log 31). Hit in Infantry Phalanx instead."]
      : [W, "They're ranged-heavy but their lead is under about 700K, so the 442 win shouldn't trigger (log 13)."];
    var g = y[0] - t[0];
    if (Math.abs(g) < 100000) return [T, "424 mirror with infantry within 100K: stats and heroes decide (log 22)."];
    return g > 0 ? [W, "424 mirror and you have " + fmt(g) + " more infantry (logs 1, 21, 24, 27, 28). Watch for a big cav edge on their side (log 3)."]
                 : [L, "424 mirror and they have " + fmt(-g) + " more infantry (logs 1, 21, 24, 27, 28)."];
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
      is055: t[0] < 200000 && t[1] > 1500000 && t[2] > 1000000,
      is208: t[1] < 300000 && t[2] / total > 0.6
    };
  }

  // If they hit you: what to sit in.
  function defendCall(t, p) {
    if (p.is055) return ["Ranged Phalanx", "It's a 055. Ranged Phalanx held in logs 12, 15 and 16: its cav has to cross the field to your ranged while being shot. Infantry Phalanx also held (log 29) but cost 1.14M infantry. Never Ranged Wedge. Run only 1 infantry hero."];
    if (p.is208) return ["Ranged Wedge", "Cav-blast style rally (208/307). Ranged Wedge keeps their cav off your infantry; a Cav Shield familiar helps."];
    if (p.big === 2) return ["Ranged Phalanx", "Their cav is the biggest stack (" + fmt(t[2]) + "). Ranged beats cav."];
    if (p.big === 1) return ["Infantry Phalanx", "Their ranged is the biggest stack (" + fmt(t[1]) + "). Infantry beats ranged, and a cav front lost twice to a 2.2M ranged rally (logs 25, 26)."];
    if (t[2] < 1000000) return ["Cavalry Phalanx", "Infantry pile with under 1M cav (" + fmt(t[2]) + "). Cav beats infantry and they have little cav to punish it."];
    return ["Ranged Phalanx", "Their infantry is the biggest stack (" + fmt(t[0]) + "), but it's a mixed rally. Crystal Briefs' tests: a cav front gets worn down by their back line, while Ranged Phalanx keeps your cav hitting at full strength. Not in our logs yet."];
  }

  // If you hit them: which comp to send and in what. Built from the battle log plus Crystal Briefs' tests.
  function attackCall(t, p) {
    var c = cap(), part = c / 20;
    if (p.is055) {
      return { comp: "866 or 857", form: "Infantry Phalanx",
        why: "Their front is a big ranged stack and infantry beats ranged. No logged win against a 055 holder yet (log 9: an 875 lost to one), so treat this as a test.",
        notes: [] };
    }
    var sh = shape(t), pt = p.parts;
    if (sh === "442" || sh === "thin" || (p.big === 1 && sh !== "424")) {
      if (t[2] < 1000000) return { comp: "1433", form: "Infantry Phalanx",
        why: "Ranged-heavy with under 1M cav. Your infantry front beats their ranged and they have little cav to punish it.",
        notes: ["Their ranged is over 1.1M, so no 208."] };
      return { comp: "947 or 857", form: "Infantry Phalanx",
        why: "Ranged-heavy (442-type) sitters are short on cav, so infantry-heavy comps are their counter. A 424 in Ranged Phalanx against one lost in log 31.",
        notes: ["Your sheet lists 668 in Ranged Phalanx against an 884. Our logs and Crystal Briefs' tests point the other way, so it's not the pick here."] };
    }
    if (pt[2] >= 12) return { comp: "884 or 794", form: "Ranged Phalanx",
      why: "Cav-heavy holder with little ranged. Ranged beats cav, and they have almost nothing to answer your ranged with.",
      notes: ["Bring exactly 2 ranged heroes."] };
    if (sh === "424") {
      var notes = ["Bring exactly 2 ranged heroes.", "If their lead is clearly weaker or runs 2 infantry heroes, a 055 in Infantry Wedge is the other option (log 10)."];
      if (pt[0] >= 9 && t[1] < 1300000) notes.push("Infantry-heavy 424 (947 / 1046 type): this is also the 208's target, sent in Ranged Wedge. Not in our logs yet.");
      if (t[1] > 1300000) notes.unshift("Their ranged is thick (" + fmt(t[1]) + "): the 442 edge shrinks. Treat as a toss-up.");
      return { comp: "794 or 884", form: "Ranged Phalanx",
        why: "Ranged-heavy rally that keeps about 0.9M cav, into a 424-type sitter. Best record so far: won logs 7 and 31 with less cav, lost log 13 by 61K. Don't drop the cav: an 8-11-1 lost twice (logs 5, 6).",
        notes: notes };
    }
    if (t[2] < 1000000) return { comp: "668", form: "Ranged Phalanx",
      why: "Infantry pile with low cav. A 668 brings " + fmt(8 * part) + " cav against " + fmt(t[2]) + "; that won by 527K in log 4.",
      notes: [] };
    if (pt[0] >= 9 && t[1] < 1300000) return { comp: "208", form: "Ranged Wedge",
      why: "Infantry-heavy with modest ranged: the 208's target. A little infantry eats their ranged and the cav reaches their infantry.",
      notes: ["Not in our logs yet. Risky if their lead is much stronger."] };
    return { comp: "668", form: "Ranged Phalanx",
      why: "Balanced comp with no clear weak spot. Numbers won't decide this one: heroes, familiars and stats will. Hit only if your lead is clearly stronger.",
      notes: [] };
  }

  function li(xs) { return xs.length ? "<ul>" + xs.map(function (n) { return "<li>" + n + "</li>"; }).join("") + "</ul>" : ""; }

  function render() {
    var T = read("t");
    var t = T.v;
    if (t.some(function (x) { return x == null; })) {
      out.setAttribute("data-empty", "");
      out.innerHTML = T.auto === -2 ? "Those numbers add up to more than the rally cap. Fill all three, or raise the cap."
        : "Enter at least two of their troop totals, then press Get the call.";
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
    var a2 = attackCall(t, p);
    if (haveYours) {
      var you = profile(y);
      var yourNear = nearest(you.parts).name;
      var mt = mirrorText(y, t);
      html += '<p class="call">Your ' + esc(yourNear) + " in a Range Phalanx mirror: " + mt[0] + "</p><p>" + esc(mt[1]) + "</p>" +
        '<p class="muted">Cav gap ' + signed(y[2] - t[2]) + ", ranged gap " + signed(y[1] - t[1]) + ".</p>";
      html += "<p>Best comp from the logs: <strong>" + esc(a2.comp) + "</strong> in " + esc(a2.form) + ". " + esc(a2.why) + "</p>";
    } else {
      html += '<p class="call">Send ' + esc(a2.comp) + " in " + esc(a2.form) + "</p><p>" + esc(a2.why) + "</p>" + li(a2.notes.map(esc));
      if (compTroops(a2.comp.split(" ")[0])) {
        var ct = compTroops(a2.comp.split(" ")[0]);
        html += '<p class="muted">At your cap that\'s ' + fmt(ct[0]) + " / " + fmt(ct[1]) + " / " + fmt(ct[2]) + ".</p>";
      }
    }
    html += '<p class="muted"><strong>Before you lock in:</strong> 2 ranged heroes if you sit or send Ranged Phalanx. Hell Drider only if their biggest squad is the troop type that counters your front.</p>';
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
  document.getElementById("go").addEventListener("click", function () {
    // write any worked-out number into its box so it's visible, then show the result
    ["t", "y"].forEach(function (pre) {
      var r = read(pre);
      if (r.auto >= 0) [el[pre + "i"], el[pre + "r"], el[pre + "c"]][r.auto].value = fmt(r.v[r.auto]);
    });
    render();
    out.scrollIntoView({ behavior: "smooth", block: "start" });
    out.focus({ preventScroll: true });
  });
})();

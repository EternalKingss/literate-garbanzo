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

  var ids = ["ti", "tr", "tc", "yi", "yr", "yc"];
  var el = {};
  ids.forEach(function (id) { el[id] = document.getElementById(id); });
  var out = document.getElementById("readout");

  function read(prefix) {
    var v = [el[prefix + "i"].value, el[prefix + "r"].value, el[prefix + "c"].value].map(parseTroops);
    return v;
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

  function codeHtml(parts) {
    var r = parts.map(function (p) { return p >= 9.5 ? Math.round(p) : Math.round(p); });
    return '<span class="code" aria-label="' + r.join("-") + ' split"><span class="i">' + r[0] +
      '</span><span class="r">' + r[1] + '</span><span class="c">' + r[2] + "</span></span>";
  }

  function render() {
    var t = read("t");
    if (t.some(function (x) { return x == null; })) {
      out.setAttribute("data-empty", "");
      out.innerHTML = "Enter their three troop totals to get a read.";
      return;
    }
    out.removeAttribute("data-empty");
    var total = t[0] + t[1] + t[2];
    if (!total) return;
    var parts = t.map(function (x) { return x / total * 20; });
    var near = nearest(parts);
    var names = ["infantry", "ranged", "cav"];
    var order = [0, 1, 2].sort(function (a, b) { return t[b] - t[a]; });
    var big = order[0];
    var close = (t[order[0]] - t[order[1]]) / total < 0.04;

    var call, why;
    var notes = [];
    var is055 = t[0] < 200000 && t[1] > 1500000 && t[2] > 1000000;

    if (is055) {
      call = "Ranged Phalanx";
      why = "It's a 055: almost no infantry, so their real front is ranged with cav behind. Your ranged in front kills the cav.";
      notes.push("You need 1.1M+ ranged and 1.4M+ infantry for this to hold. Against a clearly stronger 055 lead it can still lose.");
    } else if (big === 2) {
      call = "Ranged Phalanx";
      why = "Their cav is the biggest stack (" + fmt(t[2]) + "). Ranged beats cav.";
    } else if (big === 1) {
      call = "Infantry Phalanx";
      why = "Their ranged is the biggest stack (" + fmt(t[1]) + "). Infantry beats ranged.";
      if (t[2] < 1000000) notes.push("Their cav is under 1M, so a 1433 in Infantry Phalanx fits.");
    } else {
      call = "Cavalry Phalanx";
      why = "Their infantry is the biggest stack (" + fmt(t[0]) + "). Cav beats infantry.";
      if (t[1] > 1100000) notes.push("They still have " + fmt(t[1]) + " ranged. If they sit Range Phalanx, that shoots your cav front.");
    }
    if (close && !is055) {
      notes.push("Their top two stacks are within 4% (" + names[order[0]] + " and " + names[order[1]] + "). Wait for final numbers before you commit.");
    }
    if (t[1] > 1100000 && near.name !== "055") notes.push("Over 1.1M ranged: too much for a 208. A 055 traded even at about 1.76M in the logs.");

    // mirror + garrison checks with the user's own numbers
    var y = read("y");
    var mirror = "";
    if (!y.some(function (x) { return x == null; })) {
      var cavGap = y[2] - t[2], rngGap = y[1] - t[1];
      var score = cavGap + 0.5 * rngGap;
      var lean;
      if (score > 300000) lean = '<span class="win">Strong: hit or hold in Range Phalanx.</span>';
      else if (score > 80000) lean = '<span class="win">Leans your way.</span>';
      else if (score > -80000) lean = '<span class="even">Coin flip. Stats decide it.</span>';
      else lean = '<span class="loss">Leans their way. Skip it or bring more cav.</span>';
      mirror = is055 ? "" : "<p><strong>If it's a Range Phalanx mirror:</strong> cav gap " + signed(cavGap) +
        ", ranged gap " + signed(rngGap) + ". " + lean + "</p>";
      var g = [];
      if (y[0] < 1400000) g.push("infantry under 1.4M (" + fmt(y[0]) + ")");
      if (y[1] < 1100000) g.push("ranged under 1.1M (" + fmt(y[1]) + ")");
      if (y[2] < 1600000) g.push("cav under 1.6M (" + fmt(y[2]) + ")");
      if (y[0] + y[1] + y[2] < 4200000) g.push("not a full rally (" + fmt(y[0] + y[1] + y[2]) + ")");
      if (g.length) mirror += '<p class="loss"><strong>If you\'re holding:</strong> ' + esc(g.join(", ")) + ".</p>";
    }

    out.innerHTML =
      codeHtml(parts) +
      '<p class="muted">' + fmt(total) + " total. Closest named comp: <strong>" + esc(near.name) + "</strong>.</p>" +
      '<p class="call">' + esc(call) + "</p><p>" + esc(why) + "</p>" +
      (notes.length ? "<ul>" + notes.map(function (n) { return "<li>" + esc(n) + "</li>"; }).join("") + "</ul>" : "") +
      mirror;
    out.classList.remove("flash"); void out.offsetWidth; out.classList.add("flash");
  }

  ids.forEach(function (id) { el[id].addEventListener("input", render); });
  document.getElementById("clear").addEventListener("click", function () {
    ids.forEach(function (id) { el[id].value = ""; });
    render();
    el.ti.focus();
  });
  document.getElementById("example").addEventListener("click", function () {
    // Log 3: their 659-ish sitter vs our rally. We lost by 207K.
    el.ti.value = "1,371,218"; el.tr.value = "1,035,967"; el.tc.value = "1,824,444";
    el.yi.value = "1,621,513"; el.yr.value = "1,089,173"; el.yc.value = "1,602,314";
    render();
  });
})();

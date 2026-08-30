/* Balance · one guided scroll. Everything visible is already in the HTML
   when this runs: nothing here makes content appear. No copy lives in this
   file either, every string comes from payload.json. */

(function () {
  "use strict";

  var CONFIG = { displayModeBar: false, responsive: true };
  var PART_TWO = ["04", "05", "06", "07", "08", "09"];
  var root = document.documentElement;
  var payload = null;
  var seen = {};
  var nightOn = false;

  function $(sel, within) { return (within || document).querySelector(sel); }
  function $$(sel, within) {
    return Array.prototype.slice.call((within || document).querySelectorAll(sel));
  }
  function act(id) { return document.getElementById("act-" + id); }
  function profile() { return root.dataset.profile; }
  function current() { return payload.profiles[profile()]; }
  var ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
  function esc(v) {
    return String(v).replace(/[&<>"]/g, function (c) { return ESCAPES[c]; });
  }
  function span(cls, text) { return '<span class="' + cls + '">' + text + "</span>"; }

  /* Structure. Mirrors render/html.py: tag names and classes, never words. */

  function kpis(items) {
    return '<div class="kpis">' + items.map(function (k) {
      return '<div class="kpi">' + span("kpi-label", k.label) +
        span("kpi-value", esc(k.value)) +
        (k.delta ? span("kpi-delta", esc(k.delta)) : "") + "</div>";
    }).join("") + "</div>";
  }

  function table(spec) {
    return '<div class="scroller"><table><thead><tr>' +
      spec.columns.map(function (c) { return "<th>" + c + "</th>"; }).join("") +
      "</tr></thead><tbody>" + spec.rows.map(function (row) {
        return "<tr>" + row.map(function (v) {
          return "<td>" + esc(v) + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  }
  function pairs(rows) {
    return rows.map(function (r) {
      return '<div class="pair"><span>' + esc(r[0]) + "</span><span>" +
        esc(r[1]) + "</span></div>";
    }).join("");
  }

  function phone(card) {
    return '<div class="phone"><div class="phone-bar"><span>' + esc(card.time) +
      "</span><span>" + card.brand + '</span></div><div class="phone-body">' +
      '<p class="phone-eyebrow">' + card.eyebrow + '</p><p class="phone-h">' +
      card.headline + '</p><p class="phone-p">' + card.body + "</p>" +
      pairs(card.rows) + card.ctas.map(function (c) {
        return '<div class="phone-cta' + (c.ghost ? " ghost" : "") + '">' +
          c.label + "</div>"; }).join("") + "</div></div>";
  }
  function channel(label, inner) {
    return '<div class="channel"><p class="eyebrow">' + label + "</p>" + inner +
      "</div>";
  }
  function fill(name, html) {
    var target = $('[data-slot="' + name + '"]');
    if (target) { target.innerHTML = html; }
  }
  function heading(text) { return '<h3 class="sub">' + text + "</h3>"; }

  function figureFor(mount) {
    var key = mount.dataset.figure;
    return mount.dataset.scope === "shared"
      ? payload.figures[key] : current().figures[key];
  }

  function draw(mount) {
    var fig = figureFor(mount);
    if (!fig) { return Promise.resolve(); }
    var layout = Object.assign({}, fig.layout, { template: payload.template });
    return Plotly.newPlot(mount, fig.data, layout, CONFIG);
  }

  /* Plotly settles asynchronously and every figure it draws changes the
     height of the act holding it. Anything that moves the reader waits for
     this, or it aims at geometry about to shift underneath it. */
  function drawWithin(scope) { return Promise.all($$(".chart", scope).map(draw)); }

  function applyWeek(number) {
    var week = current().weeks.filter(function (w) { return w.week === number; })[0];
    if (!week) { return; }
    fill("week.label", week.label);
    fill("week.range", '<p class="caption">' + week.range + "</p>");
    fill("week.kpis", kpis(week.kpis));
    fill("week.days_title", heading(week.days_title));
    fill("week.table", table(week.table));
    fill("week.emitted_title", heading(week.emitted_title));
    if (week.emissions.rows.length) { fill("week.emissions", table(week.emissions)); }
    fill("week.held", week.held.length
      ? heading(week.held_title) + pairs(week.held) : "");

    $$("[data-figure-week]", act("04")).forEach(function (mount) {
      mount.dataset.figure = mount.dataset.figureWeek + "." + number;
      draw(mount);
    });
    $$('[data-figure^="week_evolution."]', act("04")).forEach(function (mount) {
      if (mount.data) {
        Plotly.restyle(mount, { "marker.color": [week.evolution_colors] }, [0]);
      }
    });
    var components = $('[data-figure="week_components"]', act("04"));
    if (components && components.data) {
      Plotly.relayout(components, {
        "shapes[0].x0": week.components_vline,
        "shapes[0].x1": week.components_vline
      });
    }
  }

  function dayCards(day) {
    var ui = current().ui;
    var gap = '<div class="empty">' + ui.empty + "</div>";
    var blocks = [channel(ui.channel_user, day.user ? phone(day.user) : gap)];
    if (current().summary.has_guardian) {
      blocks.push(channel(ui.channel_guardian,
        day.guardian ? phone(day.guardian) : gap));
    }
    blocks.push(channel(ui.channel_device, pairs(day.device) +
      '<p class="caption">' + ui.device_caption + "</p>"));
    return '<div class="grid cols-' + blocks.length + '">' + blocks.join("") +
      "</div>";
  }

  function applyDay(index) {
    var day = current().days[index];
    if (!day) { return; }
    fill("day.label", day.label);
    fill("day.title", heading(day.title));
    fill("day.cards", dayCards(day));
    var tracked = $('[data-figure="tracked_series"]');
    if (tracked && tracked.data) {
      Plotly.relayout(tracked, { "shapes[1].x0": day.iso, "shapes[1].x1": day.iso });
    }
  }

  /* Where the reader is, as an act plus how far into it, so the switch can
     put them back after part two changes height. */
  function anchor() {
    var acts = $$(".act");
    for (var i = acts.length - 1; i >= 0; i--) {
      if (acts[i].offsetTop <= window.scrollY + 1) {
        return { act: acts[i], into: window.scrollY - acts[i].offsetTop };
      }
    }
    return { act: acts[0], into: window.scrollY };
  }
  function markSeen(user) {
    seen[user] = true;
    var unread = payload.meta.profiles.filter(function (u) { return !seen[u]; });
    $$("[data-other]").forEach(function (button) {
      button.hidden = unread.indexOf(button.dataset.other) < 0;
    });
    var done = $('[data-slot="other.seen"]');
    if (done) { done.hidden = unread.length > 0; }
  }
  function slider(id) { return document.getElementById(id + "-slider"); }

  function applyProfile(user, keepPlace) {
    if (!payload.profiles[user]) { return Promise.resolve(); }
    var mark = keepPlace ? anchor() : null;
    /* Both profiles run the same five weeks and thirty days, so the switch
       keeps the reader on the one they were reading: that is the comparison. */
    var held = keepPlace
      ? { week: slider("week").value, day: slider("day").value } : {};
    root.dataset.profile = user;
    PART_TWO.forEach(function (id) {
      var body = $(".act-body", act(id));
      if (body) { body.innerHTML = current().acts[id]; }
    });
    var drawn = Promise.all(PART_TWO.map(function (id) {
      return drawWithin(act(id));
    }));
    var who = $("#profile-pill .who");
    if (who) { who.textContent = user; }
    bindSliders();
    Object.keys(held).forEach(function (kind) {
      slider(kind).value = held[kind];
      (kind === "week" ? applyWeek : applyDay)(+held[kind]);
    });
    markSeen(user);
    return drawn.then(function () {
      if (mark) {
        window.scrollTo({ top: mark.act.offsetTop + mark.into, behavior: "instant" });
      }
      paintNight(nightOn, true);
    });
  }

  /* The surface shift. The tokens are CSS; the plot grids are not, so they
     are re-pointed here to the same two values the stylesheet uses. */
  function paintNight(on, force) {
    if (on === nightOn && !force) { return; }
    nightOn = on;
    root.dataset.night = on ? "on" : "off";
    var colour = getComputedStyle(root).getPropertyValue("--grid").trim();
    $$(".chart", act("06")).forEach(function (mount) {
      if (mount.data) {
        Plotly.relayout(mount, { "xaxis.gridcolor": colour, "yaxis.gridcolor": colour });
      }
    });
  }

  function onScroll() {
    var doc = root.scrollHeight - window.innerHeight;
    $("#progress-bar").style.width =
      (doc > 0 ? (window.scrollY / doc) * 100 : 0) + "%";

    var pill = document.getElementById("profile-pill");
    pill.hidden = window.scrollY + 80 < act("04").offsetTop;

    var box = act("06").getBoundingClientRect();
    var middle = window.innerHeight / 2;
    paintNight(box.top < middle && box.bottom > middle);
  }

  function watchActs() {
    var links = {}, active = null;
    $$("[data-rail]").forEach(function (a) { links[a.dataset.rail] = a; });
    var watcher = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = entry.isIntersecting && links[entry.target.id.slice(4)];
        if (!link || link === active) { return; }
        if (active) { active.removeAttribute("aria-current"); }
        active = link;
        link.setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    $$(".act").forEach(function (a) { watcher.observe(a); });
  }

  function bindSliders() {
    ["week", "day"].forEach(function (kind) {
      var input = slider(kind);
      if (input) {
        input.oninput = function () {
          (kind === "week" ? applyWeek : applyDay)(parseInt(this.value, 10));
        };
      }
    });
  }

  function start(data) {
    payload = data;
    /* Part two for the profile the document was built with is already here.
       Keep it, so the payload never carries the same markup twice. */
    var built = payload.meta.default_profile;
    PART_TWO.forEach(function (id) {
      payload.profiles[built].acts[id] = $(".act-body", act(id)).innerHTML;
    });
    var asked = new URLSearchParams(location.search).get("profile");
    var chosen = payload.profiles[asked] ? asked : null;

    drawWithin(document);
    bindSliders();
    watchActs();

    if (chosen) {
      act("03").hidden = true;
      var link = $('[data-rail="03"]');
      if (link) { link.parentNode.hidden = true; }
      applyProfile(chosen, false);   // marks only the profile it renders
    } else {
      markSeen(profile());
    }

    document.addEventListener("click", function (event) {
      var button = event.target.closest("[data-choose]");
      if (button) {
        applyProfile(button.dataset.choose, false).then(function () {
          act("04").scrollIntoView();
        });
      }
    });
    document.getElementById("profile-pill").addEventListener("click", function () {
      var others = payload.meta.profiles.filter(function (u) { return u !== profile(); });
      applyProfile(others[0], true);
    });

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  }

  fetch("payload.json")
    .then(function (r) { return r.json(); })
    .then(start)
    .catch(function (err) { console.error("payload failed", err); });
})();

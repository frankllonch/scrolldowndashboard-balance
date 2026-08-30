/* Balance · one guided scroll. Everything visible is already in the HTML
   when this runs: nothing here makes content appear. No copy lives in this
   file either, every string comes from payload.json. */

(function () {
  "use strict";

  var CONFIG = { displayModeBar: false, responsive: false };
  var PART_TWO = ["04", "05", "06", "07", "08", "09"];
  var root = document.documentElement;
  var payload = null;
  var surface = null;

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
  /* Structure. Mirrors render/html.py: tag names and classes, never words. */

  function span(cls, text) { return '<span class="' + cls + '">' + text + "</span>"; }
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
    var layout = Object.assign({}, fig.layout,
      { template: payload.templates[fig.surface || "dark"] });
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
    fill("week.emissions", week.emissions.rows.length ? table(week.emissions)
      : '<p class="caption">' + current().ui.emitted_none + "</p>");
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
    var above = $$(".act").filter(function (a) {
      return a.offsetTop <= window.scrollY + 1;
    });
    var el = above[above.length - 1] || $(".act");
    return { act: el, into: window.scrollY - el.offsetTop };
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
      /* Through the events, not around them: input so the handler updates the
         index it remembers drawing, change so it draws now rather than after
         the debounce, which would land after the reader had been put back. */
      slider(kind).value = held[kind];
      slider(kind).dispatchEvent(new Event("input"));
      slider(kind).dispatchEvent(new Event("change"));
    });
    return drawn.then(function () {
      if (mark) {
        window.scrollTo({ top: mark.act.offsetTop + mark.into, behavior: "instant" });
      }
      paintSurface(surface, true);
    });
  }

  /* The surface travels with the reader: whichever act holds the middle of
     the viewport owns the page's tokens. Plot grids are not CSS, so they are
     re-pointed from the stylesheet's own --grid rather than a second list. */
  /* Every figure was built with its own surface, grid included. The night is
     the exception: it borrows figures drawn for the dark ground and dims them,
     so act 06 is the only one that needs re-pointing, in or out. */
  function paintSurface(id, force) {
    if (id === surface && !force) { return; }
    surface = id;
    root.dataset.surface = "a" + id;
    var colour = getComputedStyle(root).getPropertyValue("--grid").trim();
    var grid = { "xaxis.gridcolor": colour, "yaxis.gridcolor": colour };
    $$(".chart", act("06")).forEach(function (m) {
      if (m.data) { Plotly.relayout(m, grid); }
    });
  }

  function onScroll() {
    var doc = root.scrollHeight - window.innerHeight;
    $("#progress-bar").style.width =
      (doc > 0 ? (window.scrollY / doc) * 100 : 0) + "%";
  }

  /* iOS fires resize every time the URL bar slides, which is most of a scroll.
     Plotly's own responsive handler would re-lay out twenty-six plots on each
     one, so it is off and this takes its place: only a change of width is a
     resize worth acting on. */
  var pageWidth = window.innerWidth, resizing = null;
  function onResize() {
    if (window.innerWidth === pageWidth) { return; }
    pageWidth = window.innerWidth;
    clearTimeout(resizing);
    resizing = setTimeout(function () {
      /* Not Plots.resize: it drops the authored height and switches the plot
         to autosize, making every act taller. Only width changes on a
         rotation, and it is the card's content box. */
      $$(".js-plotly-plot").forEach(function (el) {
        var pad = getComputedStyle(el);
        Plotly.relayout(el, { width: el.clientWidth -
          parseFloat(pad.paddingLeft) - parseFloat(pad.paddingRight) });
      });
    }, 160);
  }
  function watchActs() {
    var links = {}, active = null;
    $$("[data-rail]").forEach(function (a) { links[a.dataset.rail] = a; });
    var watcher = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) { return; }
        var id = entry.target.id.slice(4);
        paintSurface(id);
        /* The pill is only true where it does something: part one has the
           fork, part three reads both profiles at once. */
        document.getElementById("profile-pill").hidden = PART_TWO.indexOf(id) < 0;
        var link = links[id];
        if (!link || link === active) { return; }
        if (active) { active.removeAttribute("aria-current"); }
        active = link;
        link.setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    $$(".act").forEach(function (a) { watcher.observe(a); });
  }
  function readout(kind, index) {
    var state = kind === "week"
      ? current().weeks.filter(function (w) { return w.week === index; })[0]
      : current().days[index];
    return state ? state.label : "";
  }

  /* The weeks and the days are discrete, the thumb is not: it slides freely
     and the reading follows the nearest real one. The label is what the eye
     tracks, so it moves every frame; rebuilding the panel underneath costs
     far more than a frame allows, so that waits for the drag to settle. On
     release the thumb lands on a whole step, and so do the arrow keys. */
  /* pending panel updates, by slider. Held out here so re-binding after a
     profile switch can cancel one, instead of letting it land afterwards and
     move the reader who had just been put back in place. */
  var settling = {};

  function bindSliders() {
    ["week", "day"].forEach(function (kind) {
      var input = slider(kind);
      if (!input) { return; }
      var apply = kind === "week" ? applyWeek : applyDay;
      var shown = Math.round(+input.value);
      clearTimeout(settling[kind]);
      input.oninput = function () {
        var index = Math.round(+this.value);
        if (index === shown) { return; }
        shown = index;
        fill(kind + ".label", readout(kind, index));
        clearTimeout(settling[kind]);
        settling[kind] = setTimeout(function () { apply(index); }, 90);
      };
      input.onchange = function () {
        this.value = Math.round(+this.value);
        clearTimeout(settling[kind]);
        apply(Math.round(+this.value));
      };
      input.onkeydown = function (event) {
        var by = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1 }[event.key];
        if (!by) { return; }
        event.preventDefault();
        this.value = Math.round(+this.value) + by;
        this.dispatchEvent(new Event("input"));
      };
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
      applyProfile(chosen, false);
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
    window.addEventListener("resize", onResize, { passive: true });
  }

  fetch("payload.json")
    .then(function (r) { return r.json(); })
    .then(start)
    .catch(function (err) { console.error("payload failed", err); });
})();

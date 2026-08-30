/* Balance · the static scroll.
   Phase 3: charts only. Sliders, the profile switch and the rail follow. */

(function () {
  "use strict";

  var CONFIG = { displayModeBar: false, responsive: true };
  var payload = null;

  function figure(mount) {
    var key = mount.dataset.figure;
    var scope = mount.dataset.scope || "profile";
    if (scope === "shared") return payload.figures[key];
    var user = scope.indexOf(":") > 0
      ? scope.split(":")[1]
      : document.documentElement.dataset.profile;
    var profile = payload.profiles[user];
    return profile ? profile.figures[key] : null;
  }

  function draw(mount) {
    var fig = figure(mount);
    if (!fig) { return; }
    var layout = Object.assign({}, fig.layout, { template: payload.template });
    Plotly.newPlot(mount, fig.data, layout, CONFIG);
  }

  function drawAll() {
    var mounts = document.querySelectorAll(".chart");
    for (var i = 0; i < mounts.length; i++) { draw(mounts[i]); }
  }

  fetch("payload.json")
    .then(function (r) { return r.json(); })
    .then(function (data) { payload = data; drawAll(); })
    .catch(function (err) { console.error("payload failed", err); });
})();

(function () {
  "use strict";
  var KEY = "tf-curso-progreso";

  function leer() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function guardar(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* sin almacenamiento */ }
  }

  // Tema claro/oscuro
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var root = document.documentElement;
      var oscuro = root.dataset.theme
        ? root.dataset.theme === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.dataset.theme = oscuro ? "light" : "dark";
      try { localStorage.setItem("tema", root.dataset.theme); } catch (e) {}
    });
  }

  // Botones de copiar
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest(".copy");
    if (!btn) return;
    var texto = btn.dataset.copy;
    if (!texto) {
      var code = btn.closest("figure") && btn.closest("figure").querySelector("pre code");
      texto = code ? code.innerText : "";
    }
    var ok = function () {
      btn.classList.add("copied");
      var prev = btn.textContent;
      btn.textContent = "¡Copiado!";
      setTimeout(function () { btn.classList.remove("copied"); btn.textContent = prev; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(ok, function () {});
    }
  });

  // Progreso: casilla en cada módulo
  var progreso = leer();
  var check = document.querySelector(".mark-done");
  if (check) {
    check.checked = !!progreso[check.dataset.mod];
    check.addEventListener("change", function () {
      var p = leer();
      if (check.checked) p[check.dataset.mod] = true; else delete p[check.dataset.mod];
      guardar(p);
    });
  }

  // Progreso: tarjetas del temario
  var cards = document.querySelectorAll(".mod-card");
  if (cards.length) {
    var hechos = 0;
    cards.forEach(function (c) {
      if (progreso[c.dataset.mod]) { c.classList.add("done"); hechos++; }
    });
    var fill = document.getElementById("progress-fill");
    var txt = document.getElementById("progress-text");
    if (fill) fill.style.width = (hechos / cards.length * 100) + "%";
    if (txt) txt.textContent = hechos + " de " + cards.length + " módulos completados";
  }

  // Tests de autoevaluación
  var TEST_KEY = "tf-curso-tests";
  function leerTests() { try { return JSON.parse(localStorage.getItem(TEST_KEY)) || {}; } catch (e) { return {}; } }

  document.querySelectorAll(".quiz").forEach(function (quiz) {
    var total = parseInt(quiz.dataset.total, 10);
    var resultado = quiz.querySelector(".quiz-result");
    var mensajeInicial = resultado.textContent;

    function actualizar() {
      var resp = quiz.querySelectorAll(".q.respondida").length;
      var ok = quiz.querySelectorAll(".q.acierto").length;
      if (resp < total) { resultado.textContent = "Llevas " + ok + " de " + resp + " correctas (" + (total - resp) + " pendientes)."; return; }
      var pct = Math.round(ok / total * 100);
      resultado.textContent = "Resultado: " + ok + "/" + total + " (" + pct + " %). " +
        (pct >= 80 ? "¡Módulo superado! Ya puedes marcarlo como completado." : "Repasa la lección y vuelve a intentarlo.");
      var t = leerTests();
      if (!t[quiz.dataset.mod] || t[quiz.dataset.mod].ok < ok) t[quiz.dataset.mod] = { ok: ok, total: total };
      try { localStorage.setItem(TEST_KEY, JSON.stringify(t)); } catch (e) {}
    }

    quiz.addEventListener("click", function (ev) {
      var opt = ev.target.closest(".opt");
      if (opt) {
        var q = opt.closest(".q");
        if (q.classList.contains("respondida")) return;
        var correcta = parseInt(q.dataset.ok, 10);
        var elegida = parseInt(opt.dataset.i, 10);
        q.classList.add("respondida", elegida === correcta ? "acierto" : "fallo");
        q.querySelectorAll(".opt").forEach(function (b) {
          b.disabled = true;
          var i = parseInt(b.dataset.i, 10);
          if (i === correcta) b.classList.add("correcta");
          else if (i === elegida) b.classList.add("incorrecta");
        });
        var exp = q.querySelector(".exp");
        exp.querySelector(".verdict").textContent = elegida === correcta ? "✔ ¡Correcto!" : "✘ No es correcto.";
        exp.hidden = false;
        actualizar();
        return;
      }
      if (ev.target.closest(".quiz-reset")) {
        quiz.querySelectorAll(".q").forEach(function (q) {
          q.classList.remove("respondida", "acierto", "fallo");
          q.querySelector(".exp").hidden = true;
          q.querySelectorAll(".opt").forEach(function (b) { b.disabled = false; b.classList.remove("correcta", "incorrecta"); });
        });
        resultado.textContent = mensajeInicial;
        quiz.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // Nota del test en las tarjetas del temario
  if (cards.length) {
    var tests = leerTests();
    cards.forEach(function (c) {
      var t = tests[c.dataset.mod];
      var badge = c.querySelector(".score-badge");
      if (t && badge) badge.textContent = "Test " + t.ok + "/" + t.total;
    });
  }

  // Buscador de comandos
  var buscar = document.getElementById("buscar");
  if (buscar) {
    var normal = function (s) { return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); };
    buscar.addEventListener("input", function () {
      var q = normal(buscar.value.trim());
      var total = 0;
      document.querySelectorAll(".cmd-section").forEach(function (sec) {
        var visibles = 0;
        sec.querySelectorAll("tbody tr").forEach(function (tr) {
          var mostrar = !q || normal(tr.textContent).indexOf(q) !== -1;
          tr.hidden = !mostrar;
          if (mostrar) visibles++;
        });
        sec.hidden = visibles === 0 && !!q;
        total += visibles;
      });
      document.getElementById("sin-resultados").hidden = total > 0;
    });
  }
})();

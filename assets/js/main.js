(function () {
  "use strict";

  var PROG_KEY = "tf-curso-progreso";
  var TEST_KEY = "tf-curso-tests";
  var TOTAL_MODULOS = 16;

  function leer(key) {
    try { return JSON.parse(localStorage.getItem(key)) || {}; } catch (e) { return {}; }
  }
  function guardar(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* sin almacenamiento */ }
  }

  /* ---------- Tema claro / oscuro ---------- */
  var tema = document.querySelector(".theme-toggle");
  if (tema) {
    tema.addEventListener("click", function () {
      var root = document.documentElement;
      var oscuro = root.dataset.theme
        ? root.dataset.theme === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.dataset.theme = oscuro ? "light" : "dark";
      try { localStorage.setItem("tema", root.dataset.theme); } catch (e) {}
    });
  }

  /* ---------- Menú lateral en móvil ---------- */
  var menuBtn = document.querySelector(".menu-toggle");
  function cerrarMenu() {
    document.body.classList.remove("menu-open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      var abierto = document.body.classList.toggle("menu-open");
      menuBtn.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
    var overlay = document.querySelector(".overlay");
    if (overlay) overlay.addEventListener("click", cerrarMenu);
    document.querySelectorAll(".sidebar a").forEach(function (a) { a.addEventListener("click", cerrarMenu); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") cerrarMenu(); });
  }

  // Mostrar en el menú el módulo actual sin mover la página
  var sidebarEl = document.querySelector(".sidebar");
  var actual = document.querySelector('.sidebar .sb-link[aria-current="page"]');
  if (sidebarEl && actual) sidebarEl.scrollTop = Math.max(0, actual.offsetTop - 120);

  /* ---------- Progreso del curso ---------- */
  function pintarProgreso() {
    var p = leer(PROG_KEY);
    var hechos = Object.keys(p).filter(function (k) { return p[k]; }).length;
    var pct = Math.round(hechos / TOTAL_MODULOS * 100);
    document.querySelectorAll(".js-fill").forEach(function (el) { el.style.width = pct + "%"; });
    document.querySelectorAll(".js-pct").forEach(function (el) { el.textContent = pct + " %"; });
    document.querySelectorAll(".js-count").forEach(function (el) {
      el.textContent = hechos + " de " + TOTAL_MODULOS + " módulos completados";
    });
    document.querySelectorAll(".sb-link[data-mod]").forEach(function (a) {
      a.classList.toggle("done", !!p[a.dataset.mod]);
    });
    var tests = leer(TEST_KEY);
    var filas = document.querySelectorAll(".mod-row[data-mod]");
    filas.forEach(function (row) {
      var partes = [];
      if (p[row.dataset.mod]) partes.push("Completado");
      var t = tests[row.dataset.mod];
      if (t) partes.push("Test " + t.ok + "/" + t.total);
      row.querySelector(".estado").textContent = partes.join(" · ");
    });
    // En la portada, el botón principal lleva al primer módulo sin completar
    var cont = document.querySelector(".js-continuar");
    if (cont && hechos > 0) {
      for (var i = 0; i < filas.length; i++) {
        if (!p[filas[i].dataset.mod]) {
          cont.href = filas[i].getAttribute("href");
          cont.textContent = "Continuar el curso";
          break;
        }
      }
    }
  }
  pintarProgreso();

  var check = document.querySelector(".mark-done");
  if (check) {
    check.checked = !!leer(PROG_KEY)[check.dataset.mod];
    check.addEventListener("change", function () {
      var p = leer(PROG_KEY);
      if (check.checked) p[check.dataset.mod] = true; else delete p[check.dataset.mod];
      guardar(PROG_KEY, p);
      pintarProgreso();
    });
  }

  /* ---------- Sección activa en el menú lateral ---------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".sidebar .sb-toc a"));
  if (tocLinks.length) {
    var objetivos = tocLinks.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    var pendiente = false;
    var marcar = function () {
      pendiente = false;
      var activo = -1;
      for (var i = 0; i < objetivos.length; i++) {
        if (objetivos[i] && objetivos[i].getBoundingClientRect().top < 140) activo = i;
      }
      tocLinks.forEach(function (a, i) { a.classList.toggle("active", i === activo); });
    };
    window.addEventListener("scroll", function () {
      if (!pendiente) { pendiente = true; window.requestAnimationFrame(marcar); }
    }, { passive: true });
    marcar();
  }

  /* ---------- Copiar ---------- */
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest(".copy");
    if (!btn) return;
    var texto = btn.dataset.copy;
    if (!texto) {
      var fig = btn.closest("figure");
      var code = fig && fig.querySelector("pre code");
      texto = code ? code.innerText : "";
    }
    var ok = function () {
      btn.classList.add("copied");
      var prev = btn.textContent;
      btn.textContent = "Copiado";
      setTimeout(function () { btn.classList.remove("copied"); btn.textContent = prev; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(ok, function () {});
    }
  });

  /* ---------- Tests ---------- */
  document.querySelectorAll(".quiz").forEach(function (quiz) {
    var total = parseInt(quiz.dataset.total, 10);
    var resultado = quiz.querySelector(".quiz-result");
    var mensajeInicial = resultado.textContent;

    function actualizar() {
      var resp = quiz.querySelectorAll(".q.respondida").length;
      var ok = quiz.querySelectorAll(".q.acierto").length;
      if (resp < total) {
        resultado.textContent = "Llevas " + ok + " de " + resp + " correctas. Quedan " + (total - resp) + ".";
        return;
      }
      var pct = Math.round(ok / total * 100);
      resultado.textContent = "Resultado: " + ok + "/" + total + " (" + pct + " %). " +
        (pct >= 80 ? "Módulo superado. Ya puedes marcarlo como completado." : "Repasa la lección y vuelve a intentarlo.");
      var t = leer(TEST_KEY);
      if (!t[quiz.dataset.mod] || t[quiz.dataset.mod].ok < ok) t[quiz.dataset.mod] = { ok: ok, total: total };
      guardar(TEST_KEY, t);
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
        exp.querySelector(".verdict").textContent = elegida === correcta ? "Correcto." : "Incorrecto.";
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

  /* ---------- Buscador de comandos ---------- */
  var buscar = document.getElementById("buscar");
  if (buscar) {
    var normal = function (s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
    buscar.addEventListener("input", function () {
      var q = normal(buscar.value.trim());
      var total = 0;
      document.querySelectorAll(".cmd-section").forEach(function (sec) {
        var filas = sec.querySelectorAll("tbody tr");
        if (!filas.length) { sec.hidden = !!q; return; }
        var visibles = 0;
        filas.forEach(function (tr) {
          var mostrar = !q || normal(tr.textContent).indexOf(q) !== -1;
          tr.hidden = !mostrar;
          if (mostrar) visibles++;
        });
        sec.hidden = visibles === 0 && !!q;
        total += visibles;
      });
      document.getElementById("sin-resultados").hidden = total > 0 || !q;
    });
  }
})();

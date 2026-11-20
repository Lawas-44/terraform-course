(function () {
  "use strict";

  var PROG_KEY = "tf-curso-progreso";
  var TEST_KEY = "tf-curso-tests";
  var TOTAL_MODULOS = document.querySelectorAll(".sidebar .sb-link[data-mod]").length || 1;

  function leer(key) {
    try { return JSON.parse(localStorage.getItem(key)) || {}; } catch (e) { return {}; }
  }
  function guardar(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* sin almacenamiento */ }
  }

  /* ---------- Tema claro / oscuro ----------
     Dos estados: seguir al sistema (sin valor guardado) o el contrario del sistema.
     El CSS lee <meta name="color-scheme">; aquí solo se cambia su contenido. */
  var metaTema = document.querySelector('meta[name="color-scheme"]');
  var sistemaOscuro = window.matchMedia("(prefers-color-scheme: dark)");
  var tema = document.querySelector(".theme-toggle");
  function aplicarTema(valor) {
    if (metaTema) metaTema.content = valor === "light" || valor === "dark" ? valor : "light dark";
  }
  if (tema && metaTema) {
    tema.addEventListener("click", function () {
      var actual = metaTema.content === "light" || metaTema.content === "dark"
        ? metaTema.content
        : (sistemaOscuro.matches ? "dark" : "light");
      var destino = actual === "dark" ? "light" : "dark";
      var delSistema = sistemaOscuro.matches ? "dark" : "light";
      try {
        if (destino === delSistema) localStorage.removeItem("tema");
        else localStorage.setItem("tema", destino);
      } catch (e) { /* sin almacenamiento: el cambio vale para esta página */ }
      aplicarTema(destino === delSistema ? null : destino);
    });
    // Mantener sincronizadas otras pestañas abiertas
    window.addEventListener("storage", function (e) { if (e.key === "tema") aplicarTema(e.newValue); });
  }

  /* ---------- Menú lateral en móvil ----------
     En pantallas anchas es una barra lateral normal. En móvil se comporta como
     un diálogo modal: el resto de la página queda inerte y el foco vuelve al botón. */
  var menuBtn = document.querySelector(".menu-toggle");
  var sidebar = document.querySelector(".sidebar");
  var fondo = document.querySelector(".content");
  var movil = window.matchMedia("(max-width: 1000px)");
  function modoMenu() {
    if (!sidebar) return;
    var abierto = document.body.classList.contains("menu-open");
    if (movil.matches) {
      sidebar.setAttribute("role", "dialog");
      sidebar.inert = !abierto;
    } else {
      sidebar.removeAttribute("role");
      sidebar.removeAttribute("aria-modal");
      sidebar.inert = false;
      if (fondo) fondo.inert = false;
    }
  }
  function abrirMenu() {
    document.body.classList.add("menu-open");
    menuBtn.setAttribute("aria-expanded", "true");
    sidebar.setAttribute("aria-modal", "true");
    if (fondo) fondo.inert = true;
    modoMenu();
    var foco = sidebar.querySelector('[aria-current="page"]') || sidebar.querySelector("a");
    if (foco) foco.focus({ preventScroll: true });
  }
  function cerrarMenu(devolverFoco) {
    if (!document.body.classList.contains("menu-open")) return;
    document.body.classList.remove("menu-open");
    menuBtn.setAttribute("aria-expanded", "false");
    sidebar.removeAttribute("aria-modal");
    if (fondo) fondo.inert = false;
    modoMenu();
    if (devolverFoco) menuBtn.focus();
  }
  if (menuBtn && sidebar) {
    modoMenu();
    movil.addEventListener("change", function () { cerrarMenu(false); modoMenu(); });
    menuBtn.addEventListener("click", function () {
      if (document.body.classList.contains("menu-open")) cerrarMenu(true); else abrirMenu();
    });
    var overlay = document.querySelector(".overlay");
    if (overlay) overlay.addEventListener("click", function () { cerrarMenu(true); });
    sidebar.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { cerrarMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") cerrarMenu(true); });
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
    var enProyecto = !!document.querySelector("#pasos");
    filas.forEach(function (row) {
      var partes = [];
      if (p[row.dataset.mod]) partes.push("Completado");
      var t = tests[row.dataset.mod];
      if (t && !enProyecto) partes.push("Test " + t.ok + "/" + t.total);
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

  /* ---------- Sección activa en el menú lateral ----------
     Navegadores con scroll-target-group: el CSS (:target-current) lo resuelve solo
     y aquí solo se refleja en aria-current. Resto: IntersectionObserver. */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".sidebar .sb-toc a"));
  function sincronizarAria(esActivo) {
    tocLinks.forEach(function (a) {
      if (esActivo(a)) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current");
    });
  }
  if (tocLinks.length && CSS.supports("scroll-target-group: auto")) {
    var sincronizar = function () {
      sincronizarAria(function (a) { return a.matches(":target-current"); });
    };
    sincronizar();
    document.addEventListener("scrollend", sincronizar);
  } else if (tocLinks.length && "IntersectionObserver" in window) {
    var objetivos = tocLinks.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    var visibles = new Set();
    var marcar = function () {
      // Activo: el último objetivo que ya ha cruzado la parte alta de la pantalla
      var activo = -1;
      objetivos.forEach(function (el, i) { if (el && visibles.has(el)) activo = i; });
      tocLinks.forEach(function (a, i) { a.classList.toggle("target-current", i === activo); });
      sincronizarAria(function (a) { return a.classList.contains("target-current"); });
    };
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting || e.boundingClientRect.top < 0) visibles.add(e.target); else visibles.delete(e.target);
      });
      marcar();
    }, { rootMargin: "-120px 0px -60% 0px" });
    objetivos.forEach(function (el) { if (el) obs.observe(el); });
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
    var avisar = function (clase, mensaje) {
      if (btn.dataset.prev === undefined) btn.dataset.prev = btn.textContent;
      btn.classList.remove("copied", "fallo");
      btn.classList.add(clase);
      btn.textContent = mensaje;
      clearTimeout(btn._t);
      btn._t = setTimeout(function () {
        btn.classList.remove(clase);
        btn.textContent = btn.dataset.prev;
        delete btn.dataset.prev;
      }, 1600);
    };
    var fallo = function () { avisar("fallo", "Selecciona y copia"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(function () { avisar("copied", "Copiado"); }, fallo);
    } else {
      fallo();
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
        var suave = window.matchMedia("(prefers-reduced-motion: no-preference)").matches;
        quiz.scrollIntoView({ behavior: suave ? "smooth" : "auto", block: "start" });
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

(function () {
  'use strict';

  /* --- Menus -----------------------------------------------------------
     On a pointer device the panels open on :hover in CSS, so they appear the
     moment the cursor arrives with no script in the way. JavaScript covers the
     cases CSS cannot: taps, keyboard, and the accordion inside the drawer. */
  var menus = Array.prototype.slice.call(document.querySelectorAll('.has-menu'));
  var canHover = window.matchMedia('(hover: hover)').matches;

  function closeMenus(except) {
    menus.forEach(function (m) {
      if (m === except) return;
      m.classList.remove('is-open');
      var t = m.querySelector('.menu-trigger');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  }

  menus.forEach(function (menu) {
    var trigger = menu.querySelector('.menu-trigger');
    if (!trigger) return;

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !menu.classList.contains('is-open');
      closeMenus(menu);
      menu.classList.toggle('is-open', open);
      trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    /* Keep aria-expanded truthful when the panel is opened by hover alone. */
    if (canHover) {
      menu.addEventListener('mouseenter', function () {
        trigger.setAttribute('aria-expanded', 'true');
      });
      menu.addEventListener('mouseleave', function () {
        if (!menu.classList.contains('is-open')) {
          trigger.setAttribute('aria-expanded', 'false');
        }
      });
    }
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-menu')) closeMenus(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenus(null);
  });

  /* --- Mobile drawer ---------------------------------------------------
     The drawer itself is pure CSS — the checkbox drives the transform, so it
     opens on the first tap with nothing to wait for. JavaScript only adds the
     things CSS cannot do: lock the page behind it, close it on Escape, and
     close it after a link is tapped. */
  var toggle = document.getElementById('nav-toggle');
  if (toggle) {
    var sync = function () {
      document.body.classList.toggle('nav-open', toggle.checked);
    };
    toggle.addEventListener('change', sync);
    sync();

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.checked) {
        toggle.checked = false;
        sync();
      }
    });

    document.querySelectorAll('.site-nav a').forEach(function (link) {
      link.addEventListener('click', function () {
        toggle.checked = false;
        sync();
      });
    });

    /* The burger is a label, so give it keyboard behaviour too. */
    var burger = document.querySelector('.nav-burger');
    if (burger) {
      burger.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggle.checked = !toggle.checked;
          sync();
        }
      });
    }
  }

  /* --- Hero carousel ---------------------------------------------------
     Crossfades the background and swaps the copy together. Pauses while the
     tab is hidden, while the pointer is over it, and entirely when the visitor
     has asked for reduced motion. */
  var hero = document.querySelector('.hero');
  if (hero) {
    var slides = hero.querySelectorAll('.hero-slide');
    var copies = hero.querySelectorAll('.hero-copy');
    var dots = hero.querySelectorAll('.hero-dots button');
    var arrows = hero.querySelectorAll('.hero-arrow');

    if (slides.length > 1) {
      var index = 0;
      var timer = null;
      var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var interval = parseInt(hero.dataset.autoplay, 10) || 7000;

      function show(i) {
        index = (i + slides.length) % slides.length;
        slides.forEach(function (s, n) { s.classList.toggle('is-active', n === index); });
        dots.forEach(function (d, n) { d.classList.toggle('is-active', n === index); });
        copies.forEach(function (c, n) {
          /* Re-adding the class restarts the entrance animation on the copy. */
          c.classList.remove('is-active');
          if (n === index) {
            void c.offsetWidth;
            c.classList.add('is-active');
          }
        });
      }

      function start() {
        if (reduced) return;
        stop();
        timer = setInterval(function () { show(index + 1); }, interval);
      }
      function stop() { if (timer) clearInterval(timer); timer = null; }

      dots.forEach(function (dot) {
        dot.addEventListener('click', function () {
          show(parseInt(dot.dataset.goto, 10)); start();
        });
      });
      arrows.forEach(function (arrow) {
        arrow.addEventListener('click', function () {
          show(index + parseInt(arrow.dataset.step, 10)); start();
        });
      });

      hero.addEventListener('mouseenter', stop);
      hero.addEventListener('mouseleave', start);
      document.addEventListener('visibilitychange', function () {
        document.hidden ? stop() : start();
      });

      show(0);
      start();
    }
  }

  /* --- Footer backdrop --------------------------------------------------
     A much slower crossfade than the hero: it is background, and anything
     quick down there would pull the eye away from the links. */
  var footerLayers = document.querySelectorAll('.footer-bg-layer');
  if (footerLayers.length > 1 &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var fi = 0;
    setInterval(function () {
      if (document.hidden) return;
      footerLayers[fi].classList.remove('is-active');
      fi = (fi + 1) % footerLayers.length;
      footerLayers[fi].classList.add('is-active');
    }, 6500);
  }

  /* --- Routes map ------------------------------------------------------
     Two behaviours: the lines draw themselves once, the first time the map
     scrolls into view; and selecting a legend entry dims the other routes so
     one journey can be followed across the country. Selection is a toggle, so
     it works with a tap as well as a mouse. */
  var map = document.querySelector('.routes-map');
  if (map) {
    if ('IntersectionObserver' in window) {
      var seen = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          map.classList.add('is-drawing');
          obs.unobserve(entry.target);
        });
      }, { threshold: 0.25 });
      seen.observe(map);
    } else {
      map.classList.add('is-drawing');
    }

    var keys = document.querySelectorAll('.route-key');
    var legend = document.querySelector('.routes-legend');
    var pinned = null;   // set by clicking; survives the mouse leaving
    var hovered = null;  // transient

    function apply() {
      var slug = pinned || hovered;
      map.classList.toggle('has-focus', Boolean(slug));
      map.querySelectorAll('[data-route]').forEach(function (el) {
        el.classList.toggle('is-focused', el.dataset.route === slug);
      });
      keys.forEach(function (k) {
        k.setAttribute('aria-pressed', k.dataset.route === pinned ? 'true' : 'false');
      });
    }

    keys.forEach(function (key) {
      var slug = key.dataset.route;
      key.addEventListener('click', function () {
        pinned = (pinned === slug) ? null : slug;
        apply();
      });
      key.addEventListener('mouseenter', function () { hovered = slug; apply(); });
      key.addEventListener('focus', function () { hovered = slug; apply(); });
      key.addEventListener('blur', function () { hovered = null; apply(); });
    });

    if (legend) {
      legend.addEventListener('mouseleave', function () { hovered = null; apply(); });
    }
  }

  /* --- Scroll reveal ----------------------------------------------------
     Marks sections as they enter the viewport, once each. Anything that never
     gets observed (no IntersectionObserver, JS disabled) is shown by the class
     added below, so content is never trapped behind an animation. */
  var revealable = document.querySelectorAll(
    '.section-head, .tour-card, .category-tile, .dest-tile, .service-card, ' +
    '.routes-figure, .routes-copy, .testi, .team-card, .booking-card, .package-block'
  );

  if ('IntersectionObserver' in window &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    revealable.forEach(function (el, i) {
      el.setAttribute('data-reveal', '');
      el.setAttribute('data-reveal-delay', String(i % 4));
    });
    var revealer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealable.forEach(function (el) { revealer.observe(el); });
  }

  /* --- Header state -----------------------------------------------------
     Uses a sentinel element rather than a scroll listener, so nothing runs on
     every frame while the visitor scrolls. */
  var header = document.querySelector('.site-header');
  if (header && 'IntersectionObserver' in window) {
    var sentinel = document.createElement('div');
    sentinel.style.cssText = 'position:absolute;top:0;height:1px;width:1px;';
    document.body.prepend(sentinel);
    new IntersectionObserver(function (entries) {
      header.classList.toggle('is-stuck', !entries[0].isIntersecting);
    }, { threshold: 0 }).observe(sentinel);
  }
})();

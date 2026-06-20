/* ============================================
   LEO GLOBAL HOLDINGS - Interactive Components
   ============================================ */

(function () {
  'use strict';

  var GROUPS = [
    { label: 'Frankmax', url: '/frankmax/', id: 'frankmax' },
    { label: 'Virginbay', url: '/virginbay/', id: 'virginbay' },
    { label: 'Glosbe', url: '/glosbe/', id: 'glosbe' },
    { label: 'Crenza', url: '/crenza/', id: 'crenza' },
  ];

  var STORAGE_KEY = 'leo-theme';

  function detectGroup() {
    var p = window.location.pathname;
    for (var i = 0; i < GROUPS.length; i++) {
      if (p.indexOf('/' + GROUPS[i].id + '/') === 0) return GROUPS[i].id;
    }
    return null;
  }

  function getPreferredTheme() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    var btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = theme === 'dark' ? '\u2600' : '\u263E';
  }

  // =============================================
  // 1. NAVBAR
  // =============================================
  function renderNavbar() {
    if (document.querySelector('.navbar')) return;
    var group = detectGroup();
    var linksHtml = '';
    for (var i = 0; i < GROUPS.length; i++) {
      var g = GROUPS[i];
      var active = group === g.id ? ' active' : '';
      linksHtml += '<a href="' + g.url + '" class="group-link' + active + '">' + g.label + '</a>';
    }

    var el = document.createElement('nav');
    el.className = 'navbar';
    el.setAttribute('role', 'navigation');
    el.setAttribute('aria-label', 'Main navigation');
    el.innerHTML =
      '<div class="navbar-inner">' +
      '<a href="/" class="navbar-brand" aria-label="Home">' +
      '<span class="logo">L</span><span>Leo Global Holdings</span></a>' +
      '<div class="navbar-links">' +
      linksHtml +
      '<a href="/" class="navbar-cta">Enterprise</a>' +
      '</div>' +
      '<button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">' +
      (getPreferredTheme() === 'dark' ? '\u2600' : '\u263E') +
      '</button>' +
      '<button class="navbar-mobile-toggle" aria-label="Toggle menu">\u2630</button>' +
      '</div>';
    document.body.insertAdjacentElement('afterbegin', el);

    document.querySelector('.navbar-mobile-toggle').addEventListener('click', function () {
      document.querySelector('.navbar-links').classList.toggle('open');
    });

    document.getElementById('themeToggle').addEventListener('click', function () {
      var next = getPreferredTheme() === 'dark' ? 'light' : 'dark';
      setTheme(next);
    });
  }

  // =============================================
  // 2. FOOTER
  // =============================================
  function renderFooter() {
    if (document.querySelector('.site-footer')) return;
    var el = document.createElement('footer');
    el.className = 'site-footer';
    el.innerHTML =
      '<div class="footer-inner">' +
      '<div class="footer-grid">' +
      '<div class="footer-brand">' +
      '<h3>Leo Global Holdings</h3>' +
      '<p>A global enterprise ecosystem spanning human capital, commerce, communities, and asset stewardship. Long-term vision, capital allocation, global governance.</p>' +
      '</div>' +
      '<div class="footer-col"><h4>Ecosystem</h4><ul>' +
      '<li><a href="/frankmax/">Frankmax</a></li>' +
      '<li><a href="/virginbay/">Virginbay</a></li>' +
      '<li><a href="/glosbe/">Glosbe</a></li>' +
      '<li><a href="/crenza/">Crenza</a></li>' +
      '</ul></div>' +
      '<div class="footer-col"><h4>Verticals</h4><ul>' +
      '<li><a href="/leo-technologies/">Technologies</a></li>' +
      '<li><a href="/leo-capital/">Capital</a></li>' +
      '<li><a href="/leo-ventures/">Ventures</a></li>' +
      '<li><a href="/leo-institute/">Institute</a></li>' +
      '</ul></div>' +
      '<div class="footer-col"><h4>Governance</h4><ul>' +
      '<li><a href="/leo-foundation/">Foundation</a></li>' +
      '<li><a href="/leo-global-governance-council/">Council</a></li>' +
      '</ul></div>' +
      '</div>' +
      '<div class="footer-bottom">' +
      '<span>&copy; 2026 Leo Global Holdings. All rights reserved.</span>' +
      '<span>Enterprise Architecture &middot; Global Governance</span>' +
      '</div></div>';
    document.body.appendChild(el);
  }

  // =============================================
  // 3. SCROLL REVEAL with stagger
  // =============================================
  function initScrollReveal() {
    var els = document.querySelectorAll('.fade-in');
    if (!els.length) return;
    var observer = new IntersectionObserver(
      function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            entries[i].target.classList.add('visible');
            observer.unobserve(entries[i].target);
          }
        }
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );
    for (var i = 0; i < els.length; i++) observer.observe(els[i]);
  }

  // =============================================
  // 4. PARALLAX HERO
  // =============================================
  function initParallax() {
    var hero = document.querySelector('.hero.parallax');
    if (!hero) return;
    var bg = hero.querySelector('.hero-bg');
    if (!bg) return;
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(function () {
          var rect = hero.getBoundingClientRect();
          var speed = 0.3;
          var yPos = rect.top * speed;
          bg.style.transform = 'translateY(' + yPos + 'px) scale(1.05)';
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // =============================================
  // 5. COUNTER ANIMATION
  // =============================================
  function initCounters() {
    var els = document.querySelectorAll('.stat-number');
    if (!els.length) return;
    var observer = new IntersectionObserver(
      function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            animateCounter(entries[i].target);
            observer.unobserve(entries[i].target);
          }
        }
      },
      { threshold: 0.5 }
    );
    for (var i = 0; i < els.length; i++) observer.observe(els[i]);
  }

  function animateCounter(el) {
    var text = el.textContent;
    var target = parseInt(text.replace(/[^0-9]/g, ''), 10);
    if (isNaN(target) || target === 0) return;
    var suffix = text.replace(/[0-9]/g, '');
    var duration = 1500;
    var start = performance.now();
    function tick(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.round(eased * target);
      el.textContent = current + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // =============================================
  // 6. BUTTON RIPPLE
  // =============================================
  function initRipples() {
    var btns = document.querySelectorAll('.btn-ripple');
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', function (e) {
        var rect = this.getBoundingClientRect();
        var r = document.createElement('span');
        r.className = 'ripple';
        var size = Math.max(rect.width, rect.height);
        r.style.width = r.style.height = size + 'px';
        r.style.left = (e.clientX - rect.left - size / 2) + 'px';
        r.style.top = (e.clientY - rect.top - size / 2) + 'px';
        this.appendChild(r);
        setTimeout(function () { r.remove(); }, 600);
      });
    }
  }

  // =============================================
  // BOOT
  // =============================================
  function ready(fn) {
    if (document.readyState !== 'loading') { fn(); return; }
    document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    setTheme(getPreferredTheme());
    renderNavbar();
    renderFooter();

    var hero = document.querySelector('.hero .hero-bg');
    if (hero) hero.closest('.hero').classList.add('parallax');

    initScrollReveal();
    initParallax();
    initCounters();
    initRipples();
  });
})();

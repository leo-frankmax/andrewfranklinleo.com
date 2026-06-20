/* ============================================
   LEO GLOBAL HOLDINGS - Components
   ============================================ */

(function() {
  'use strict';

  var NAV_DATA = {
    groups: [
      { label: 'Frankmax', url: '/frankmax/', color: 'frankmax' },
      { label: 'Virginbay', url: '/virginbay/', color: 'virginbay' },
      { label: 'Glosbe', url: '/glosbe/', color: 'glosbe' },
      { label: 'Crenza', url: '/crenza/', color: 'crenza' }
    ]
  };

  function detectGroup() {
    var path = window.location.pathname;
    if (path.indexOf('/frankmax/') === 0) return 'frankmax';
    if (path.indexOf('/virginbay/') === 0) return 'virginbay';
    if (path.indexOf('/glosbe/') === 0) return 'glosbe';
    if (path.indexOf('/crenza/') === 0) return 'crenza';
    return null;
  }

  function renderNavbar() {
    var group = detectGroup();
    var links = NAV_DATA.groups.map(function(g) {
      var active = group === g.color ? ' active' : '';
      return '<a href="' + g.url + '" class="group-link' + active + '">' + g.label + '</a>';
    }).join('');

    var html = '<nav class="navbar" role="navigation" aria-label="Main navigation">'
      + '<a href="/" class="navbar-brand">'
      + '<span class="logo">L</span>'
      + 'Leo Global Holdings'
      + '</a>'
      + '<button class="navbar-mobile-toggle" aria-label="Toggle menu">'
      + '&#9776;'
      + '</button>'
      + '<div class="navbar-links">'
      + links
      + '<a href="/" class="navbar-cta">Enterprise</a>'
      + '</div>'
      + '</nav>';

    document.body.insertAdjacentHTML('afterbegin', html);

    var toggle = document.querySelector('.navbar-mobile-toggle');
    if (toggle) {
      toggle.addEventListener('click', function() {
        document.querySelector('.navbar-links').classList.toggle('open');
      });
    }
  }

  function renderFooter() {
    var html = '<footer class="site-footer">'
      + '<div class="footer-inner">'
      + '<div class="footer-grid">'
      + '<div class="footer-brand">'
      + '<h3>Leo Global Holdings</h3>'
      + '<p>A global enterprise ecosystem spanning human capital, commerce, communities, and asset stewardship.</p>'
      + '</div>'
      + '<div class="footer-col">'
      + '<h4>Ecosystem</h4>'
      + '<ul>'
      + '<li><a href="/frankmax/">Frankmax</a></li>'
      + '<li><a href="/virginbay/">Virginbay</a></li>'
      + '<li><a href="/glosbe/">Glosbe</a></li>'
      + '<li><a href="/crenza/">Crenza</a></li>'
      + '</ul>'
      + '</div>'
      + '<div class="footer-col">'
      + '<h4>Strategic Verticals</h4>'
      + '<ul>'
      + '<li><a href="/leo-technologies/">Technologies</a></li>'
      + '<li><a href="/leo-capital/">Capital</a></li>'
      + '<li><a href="/leo-ventures/">Ventures</a></li>'
      + '<li><a href="/leo-institute/">Institute</a></li>'
      + '</ul>'
      + '</div>'
      + '<div class="footer-col">'
      + '<h4>Governance</h4>'
      + '<ul>'
      + '<li><a href="/leo-foundation/">Foundation</a></li>'
      + '<li><a href="/leo-global-governance-council/">Governance Council</a></li>'
      + '</ul>'
      + '</div>'
      + '</div>'
      + '<div class="footer-bottom">'
      + '<span>&copy; 2026 Leo Global Holdings. All rights reserved.</span>'
      + '<span>Enterprise Architecture &middot; Global Governance</span>'
      + '</div>'
      + '</div>'
      + '</footer>';

    document.body.insertAdjacentHTML('beforeend', html);
  }

  function initScrollAnimations() {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.fade-in').forEach(function(el) {
      observer.observe(el);
    });
  }

  document.addEventListener('DOMContentLoaded', function() {
    renderNavbar();
    renderFooter();
    initScrollAnimations();
  });
})();

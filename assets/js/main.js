// IKAD Mechanical - main.js
// Mobile nav · Before/After slider · Hero quote form · Smooth scroll

(function () {
  'use strict';

  /* ----- Mobile nav toggle ----- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.classList.toggle('nav-open', open);
    });
    // Close menu when clicking an actual link (but not dropdown toggles)
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function (e) {
        // On mobile, top-level dropdown anchor should toggle the submenu rather than navigate
        var parent = a.parentElement;
        var isMobile = window.matchMedia('(max-width: 980px)').matches;
        if (isMobile && parent && parent.classList.contains('has-dropdown')) {
          e.preventDefault();
          parent.classList.toggle('is-expanded');
          return;
        }
        if (nav.classList.contains('is-open')) {
          nav.classList.remove('is-open');
          document.body.classList.remove('nav-open');
          toggle.setAttribute('aria-expanded', 'false');
          // collapse all expanded dropdowns
          nav.querySelectorAll('.has-dropdown.is-expanded').forEach(function (d) { d.classList.remove('is-expanded'); });
        }
      });
    });
    // Close menu on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    // Close menu when viewport grows past mobile breakpoint
    window.addEventListener('resize', function () {
      if (window.innerWidth > 980 && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ----- Before/After slider (clip-path approach) ----- */
  document.querySelectorAll('.ba-slider').forEach(function (slider) {
    var afterImg = slider.querySelector('.ba-slider__after');
    var handle = slider.querySelector('.ba-slider__handle');
    if (!afterImg || !handle) return;

    var dragging = false;

    function setPos(pct) {
      pct = Math.max(0, Math.min(100, pct));
      afterImg.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
      handle.style.left = pct + '%';
      slider.setAttribute('aria-valuenow', Math.round(pct));
    }

    function getPct(e) {
      var rect = slider.getBoundingClientRect();
      var clientX = e.touches ? e.touches[0].clientX : e.clientX;
      return ((clientX - rect.left) / rect.width) * 100;
    }

    function start(e) {
      dragging = true;
      slider.classList.add('is-dragging');
      if (e.cancelable) e.preventDefault();
      setPos(getPct(e));
    }
    function move(e) {
      if (!dragging) return;
      if (e.cancelable) e.preventDefault();
      setPos(getPct(e));
    }
    function end() {
      dragging = false;
      slider.classList.remove('is-dragging');
    }

    slider.addEventListener('mousedown', start);
    slider.addEventListener('touchstart', start, { passive: false });
    window.addEventListener('mousemove', move);
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('mouseup', end);
    window.addEventListener('touchend', end);

    // Keyboard support for accessibility
    slider.setAttribute('tabindex', '0');
    slider.setAttribute('role', 'slider');
    slider.setAttribute('aria-valuemin', '0');
    slider.setAttribute('aria-valuemax', '100');
    slider.addEventListener('keydown', function (e) {
      var cur = parseFloat(slider.getAttribute('aria-valuenow') || '50');
      if (e.key === 'ArrowLeft') { setPos(cur - 5); e.preventDefault(); }
      if (e.key === 'ArrowRight') { setPos(cur + 5); e.preventDefault(); }
      if (e.key === 'Home') { setPos(0); e.preventDefault(); }
      if (e.key === 'End') { setPos(100); e.preventDefault(); }
    });

    setPos(50);
  });

  /* ----- Smooth-scroll for in-page anchors ----- */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (id.length > 1) {
        var target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  /* ----- Quote form submission via SMTP (/api/quote) ----- */
  document.querySelectorAll('form[data-form="quote"]').forEach(function (form) {
    var status = form.querySelector('.form__status');
    if (!status) {
      status = document.createElement('p');
      status.className = 'form__status';
      status.setAttribute('role', 'status');
      status.setAttribute('aria-live', 'polite');
      status.style.display = 'none';
      form.appendChild(status);
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var submitBtn = form.querySelector('button[type="submit"]');
      var originalText = submitBtn ? submitBtn.textContent : '';
      var data = new FormData(form);
      var payload = {};
      data.forEach(function (v, k) { payload[k] = v; });
      payload.source_page = window.location.pathname + window.location.search;

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending…';
      }
      status.style.display = 'none';
      status.classList.remove('form__status--error', 'form__status--success');

      fetch('/api/quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          return r.json().then(function (j) { return { ok: r.ok, body: j }; });
        })
        .then(function (res) {
          if (res.ok && res.body && res.body.ok) {
            // Success: redirect to /thank-you/
            window.location.href = '/thank-you/';
          } else {
            var msg = (res.body && res.body.error) || 'Something went wrong. Please call (905) 491-6943.';
            status.textContent = msg;
            status.classList.add('form__status--error');
            status.style.display = 'block';
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.textContent = originalText;
            }
          }
        })
        .catch(function () {
          // Network failure: fall back to mailto so the lead is never lost.
          var body = '';
          data.forEach(function (v, k) { body += k + ': ' + v + '\n'; });
          var subject = encodeURIComponent('New Quote Request from ' + (data.get('name') || 'Website'));
          window.location.href = 'mailto:info@ikad.ca?subject=' + subject + '&body=' + encodeURIComponent(body);
        });
    });
  });

  /* ----- Header shadow on scroll ----- */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      if (window.scrollY > 12) header.classList.add('is-scrolled');
      else header.classList.remove('is-scrolled');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();

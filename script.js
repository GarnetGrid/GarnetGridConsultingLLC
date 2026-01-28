/* Garnet Grid Consulting - site interactions */

// Smooth scroll for in-page anchors (with safety checks)
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', (e) => {
    const href = anchor.getAttribute('href');
    if (!href || href === '#') return;

    const target = document.querySelector(href);
    if (!target) return;

    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// Clickable service tiles (used by onclick in HTML)
function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Optional client-logo carousel (only runs if the section exists)
(() => {
  const carousel = document.querySelector('.carousel-clientimages');
  if (!carousel) return;

  const images = Array.from(carousel.querySelectorAll('img'));
  if (!images.length) return;

  let offset = 0;
  const speed = 0.6; // px per frame
  const firstWidth = images[0].getBoundingClientRect().width || 140;
  const gap = 15;
  const imageWidth = firstWidth + gap;
  const totalWidth = imageWidth * images.length;

  // Duplicate images for seamless looping
  images.forEach((img) => carousel.appendChild(img.cloneNode(true)));

  const loop = () => {
    offset -= speed;
    if (Math.abs(offset) >= totalWidth) offset = 0;
    carousel.style.transform = `translateX(${offset}px)`;
    requestAnimationFrame(loop);
  };

  requestAnimationFrame(loop);
})();

// Contact form -> opens a pre-filled email (no backend required)
(() => {
  const form = document.getElementById('contactForm');
  const note = document.getElementById('formNote');
  if (!form) return;

  const encode = (v) => encodeURIComponent(String(v || '').trim());

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const data = new FormData(form);
    const name = data.get('name');
    const email = data.get('email');
    const message = data.get('message');

    const subject = `Request — ${name || 'Garnet Grid'}`;
    const body = [
      `Name: ${name || ''}`,
      `Email: ${email || ''}`,
      '',
      String(message || ''),
      '',
      '—',
      'Sent from garnetgrid.com contact form'
    ].join('\n');

    const mailto = `mailto:garnetgrid@gmail.com?subject=${encode(subject)}&body=${encode(body)}`;

    if (note) {
      note.textContent = 'Opening your email app with a pre-filled message…';
    }

    window.location.href = mailto;
  });
})();

// === Services Expanded Enhancements ===
(function(){
  // Exclusive accordion: only one <details> open per svc card (optional, feels premium)
  document.querySelectorAll('.svc-card').forEach(card => {
    const details = card.querySelectorAll('details.acc-item');
    details.forEach(d => {
      d.addEventListener('toggle', () => {
        if (!d.open) return;
        details.forEach(other => { if (other !== d) other.open = false; });
      });
    });
  });

  // Smooth scroll with sticky header offset
  const header = document.querySelector('.top-nav');
  const headerOffset = () => header ? header.getBoundingClientRect().height + 8 : 16;

  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.pageYOffset - headerOffset();
      window.scrollTo({ top, behavior: 'smooth' });
      history.pushState(null, '', id);
    });
  });
})();

// === Mobile Landing Reveal ===
(function(){
  const isMobile = () => window.matchMedia && window.matchMedia('(max-width: 768px)').matches;
  let revealed = false;

  const reveal = () => {
    if (revealed) return;
    revealed = true;
    document.body.classList.add('landing-revealed');
    window.removeEventListener('scroll', onScroll, { passive: true });
    window.removeEventListener('touchmove', onScroll, { passive: true });
  };

  const onScroll = () => {
    if (window.scrollY > 8) reveal();
  };

  const init = () => {
    if (!isMobile()) return;
    // Start hidden (logo-only) at top
    if (window.scrollY <= 8) {
      document.body.classList.remove('landing-revealed');
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('touchmove', onScroll, { passive: true });
    } else {
      reveal();
    }
  };

  // Run on load and on resize
  window.addEventListener('load', init);
  window.addEventListener('resize', () => {
    if (!isMobile()) {
      document.body.classList.add('landing-revealed'); // ensureiveal on desktop
      revealed = true;
    } else {
      // If not revealed yet, re-init
      if (!revealed) init();
    }
  });
})();

// === Landing: logo-only until scroll (desktop + mobile) ===
(function () {
  let revealed = false;

  const reveal = () => {
    if (revealed) return;
    revealed = true;
    document.body.classList.add("landing-revealed");
    cleanup();
  };

  const onScroll = () => {
    if (window.scrollY > 8) reveal();
  };

  const onWheel = () => reveal();
  const onTouchMove = () => reveal();
  const onKey = (e) => {
    if (["ArrowDown", "PageDown", " ", "Spacebar"].includes(e.key)) reveal();
  };

  const cleanup = () => {
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("wheel", onWheel);
    window.removeEventListener("touchmove", onTouchMove);
    window.removeEventListener("keydown", onKey);
  };

  const init = () => {
    if (window.scrollY > 8) {
      document.body.classList.add("landing-revealed");
      revealed = true;
      return;
    }

    document.body.classList.remove("landing-revealed");
    revealed = false;

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("wheel", onWheel, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: true });
    window.addEventListener("keydown", onKey);
  };

  window.addEventListener("load", init);
})();


// === Landing lock (logo-only until scroll) ===
(function () {
  let revealed = false;

  const reveal = () => {
    if (revealed) return;
    revealed = true;
    document.body.classList.add("landing-revealed");
    cleanup();
  };

  const onScroll = () => {
    if (window.scrollY > 8) reveal();
  };

  const onWheel = () => reveal();
  const onTouchMove = () => reveal();
  const onKey = (e) => {
    if (["ArrowDown", "PageDown", " ", "Spacebar"].includes(e.key)) reveal();
  };

  const cleanup = () => {
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("wheel", onWheel);
    window.removeEventListener("touchmove", onTouchMove);
    window.removeEventListener("keydown", onKey);
  };

  const init = () => {
    // Always start locked at top
    if (window.scrollY <= 8) {
      document.body.classList.remove("landing-revealed");
      revealed = false;
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("wheel", onWheel, { passive: true });
      window.addEventListener("touchmove", onTouchMove, { passive: true });
      window.addEventListener("keydown", onKey);
    } else {
      document.body.classList.add("landing-revealed");
      revealed = true;
    }
  };

  window.addEventListener("load", init);
})();


/* LANDING_COMBO_PATCH: logo-only landing until first scroll/touch/wheel */
(() => {
  const body = document.body;
  if (!body) return;

  // Ensure initial state exists
  if (!body.classList.contains('landing-locked') && !body.classList.contains('landing-unlocked')) {
    body.classList.add('landing-locked');
  }

  let unlocked = false;
  const unlock = () => {
    if (unlocked) return;
    unlocked = true;
    body.classList.remove('landing-locked');
    body.classList.add('landing-unlocked');
    window.removeEventListener('scroll', onScroll, { passive: true });
    window.removeEventListener('wheel', onWheel, { passive: true });
    window.removeEventListener('touchmove', onTouch, { passive: true });
    window.removeEventListener('keydown', onKey);
  };

  const onScroll = () => { if (window.scrollY > 2) unlock(); };
  const onWheel  = () => unlock();
  const onTouch  = () => unlock();
  const onKey = (e) => {
    if (['ArrowDown','PageDown',' ','Enter'].includes(e.key)) unlock();
  };

  // If loaded already scrolled, unlock immediately
  if (window.scrollY > 2) { unlock(); return; }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('wheel', onWheel, { passive: true });
  window.addEventListener('touchmove', onTouch, { passive: true });
  window.addEventListener('keydown', onKey);
})();

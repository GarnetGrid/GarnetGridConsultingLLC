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

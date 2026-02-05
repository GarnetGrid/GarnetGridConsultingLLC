/* ============================================
   GARNET GRID CONSULTING - ENHANCED INTERACTIONS
   Modern JavaScript with scroll animations & UX
   ============================================ */

// ============================================
// SMOOTH SCROLL WITH OFFSET
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (!href || href === '#') return;

    const target = document.querySelector(href);
    if (!target) return;

    e.preventDefault();

    const navHeight = document.querySelector('.top-nav')?.offsetHeight || 80;
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;

    window.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });

    // Update URL without jumping
    history.pushState(null, '', href);
  });
});

// ============================================
// NAVIGATION SCROLL EFFECTS
// ============================================
const nav = document.querySelector('.top-nav');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 100) {
    nav?.classList.add('scrolled');
  } else {
    nav?.classList.remove('scrolled');
  }

  lastScroll = currentScroll;
}, { passive: true });

// Reveal animations removed per user request for immediate visibility
const initReveal = () => {
  // No-op
};

// Lock mechanism removed for reliability

// ============================================
// SERVICE ACCORDION (EXCLUSIVE)
// ============================================
document.querySelectorAll('.svc-card').forEach(card => {
  const details = card.querySelectorAll('details.acc-item');

  details.forEach(detail => {
    detail.addEventListener('toggle', () => {
      if (!detail.open) return;

      // Close other accordions in the same card
      details.forEach(other => {
        if (other !== detail && other.open) {
          other.open = false;
        }
      });
    });
  });
});

// ============================================
// CONTACT FORM HANDLING
// ============================================
(() => {
  const form = document.getElementById('contactForm');
  const note = document.getElementById('formNote');

  if (!form) return;

  // Form validation
  const inputs = form.querySelectorAll('input, textarea');

  inputs.forEach(input => {
    input.addEventListener('blur', () => {
      if (input.hasAttribute('required') && !input.value.trim()) {
        input.style.borderColor = 'hsl(0, 70%, 55%)';
      } else {
        input.style.borderColor = '';
      }
    });

    input.addEventListener('input', () => {
      input.style.borderColor = '';
    });
  });

  // Form submission
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const name = formData.get('name')?.toString().trim() || '';
    const email = formData.get('email')?.toString().trim() || '';
    const message = formData.get('message')?.toString().trim() || '';
    const honeypot = formData.get('website')?.toString() || ''; // Silent honeypot

    // 1. Honeypot check
    if (honeypot) {
      console.warn('Bot detected by honeypot.');
      return; // Silently fail for bots
    }

    // 2. Cooldown check
    const lastSub = localStorage.getItem('last_submission');
    const now = Date.now();
    if (lastSub && (now - parseInt(lastSub)) < 30000) { // 30s cooldown
      if (note) {
        note.textContent = 'Please wait a few seconds before sending another message.';
        note.style.color = 'hsl(35, 90%, 60%)';
      }
      return;
    }

    // 3. Validation
    if (!name || !email || !message) {
      if (note) {
        note.textContent = 'Please fill in all fields.';
        note.style.color = 'hsl(0, 70%, 55%)';
      }
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      if (note) {
        note.textContent = 'Please enter a valid email address.';
        note.style.color = 'hsl(0, 70%, 55%)';
      }
      return;
    }

    // Create mailto link
    const subject = encodeURIComponent(`Garnet Grid Inquiry — ${name}`);
    const body = encodeURIComponent(
      `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}\n\n—\nSent from garnetgrid.com contact form`
    );

    const mailto = `mailto:garnetgrid@gmail.com?subject=${subject}&body=${body}`;

    if (note) {
      note.textContent = 'Opening your email client...';
      note.style.color = 'hsl(142, 70%, 55%)';
    }

    // Store submission time
    localStorage.setItem('last_submission', now.toString());

    // Small delay for better UX
    setTimeout(() => {
      window.location.href = mailto;

      // Reset form after a moment
      setTimeout(() => {
        form.reset();
        if (note) {
          note.textContent = 'Thank you! Your email client should have opened.';
        }
      }, 1000);
    }, 300);
  });
})();

// ============================================
// CAROUSEL ENHANCEMENTS
// ============================================
document.querySelectorAll('.service-carousel').forEach((carousel, index) => {
  const images = carousel.querySelector('.carousel-images');
  if (!images) return;

  // Add different animation delays for async effect
  const delays = ['0s', '3s', '5s', '7s'];
  images.style.animationDelay = delays[index % delays.length];

  // Pause on hover
  carousel.addEventListener('mouseenter', () => {
    images.style.animationPlayState = 'paused';
  });

  carousel.addEventListener('mouseleave', () => {
    images.style.animationPlayState = 'running';
  });
});

// ============================================
// PERFORMANCE OPTIMIZATIONS
// ============================================

// Lazy load images
if ('loading' in HTMLImageElement.prototype) {
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => {
    img.src = img.dataset.src || img.src;
  });
} else {
  // Fallback for browsers that don't support lazy loading
  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
  document.body.appendChild(script);
}

// Debounce scroll events
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ============================================
// ACCESSIBILITY ENHANCEMENTS
// ============================================

// Keyboard navigation for cards
document.querySelectorAll('.offer-card, .svc-card').forEach(card => {
  card.setAttribute('tabindex', '0');

  card.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      card.click();
    }
  });
});

// Focus management for accordions
document.querySelectorAll('.acc-item').forEach(item => {
  const summary = item.querySelector('summary');

  summary?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      item.open = !item.open;
    }
  });
});

// ============================================
// CONSOLE EASTER EGG
// ============================================
console.log(
  '%c🌟 Garnet Grid Consulting',
  'font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff7f50, #ff6347); -webkit-background-clip: text; color: transparent;'
);
console.log(
  '%cEmpowering Tomorrow, Securing Today',
  'font-size: 14px; color: #888; font-style: italic;'
);
console.log(
  '%cInterested in working with us? Visit garnetgrid.com/contact',
  'font-size: 12px; color: #ff7f50;'
);

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  console.log('✓ Garnet Grid website loaded successfully');

  // Add loaded class to body for CSS animations
  setTimeout(() => {
    document.body.classList.add('loaded');
  }, 100);
});

// ============================================
// STAT COUNTER ANIMATION
// ============================================
const animateCounters = () => {
  const counters = document.querySelectorAll('.stat-number');
  const speed = 200;

  counters.forEach(counter => {
    const updateCount = () => {
      const target = +counter.getAttribute('data-target');
      const count = +counter.innerText;
      const inc = target / speed;

      if (count < target) {
        counter.innerText = Math.ceil(count + inc);
        setTimeout(updateCount, 1);
      } else {
        counter.innerText = target;
      }
    };
    updateCount();
  });
};

// ============================================
// HERO PARALLAX EFFECT
// ============================================
const hero = document.querySelector('.landing');
const heroLogo = document.querySelector('.landing-logo');
const heroText = document.querySelector('.hero-copy');

if (hero && heroLogo && heroText) {
  hero.addEventListener('mousemove', (e) => {
    const { clientX, clientY } = e;
    const { innerWidth, innerHeight } = window;

    const moveX = (clientX - innerWidth / 2) / 25;
    const moveY = (clientY - innerHeight / 2) / 25;

    heroLogo.style.transform = `translate(${moveX}px, ${moveY}px) translateY(-12px) scale(1.03)`;
    heroText.style.transform = `translate(${-moveX / 2}px, ${-moveY / 2}px)`;
  });
}

// Trigger counter when in view
const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounters();
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

const statsBar = document.querySelector('.hero-stats-bar');
if (statsBar) statsObserver.observe(statsBar);
// ============================================
// SHOWCASE HERO ANIMATION (Garnet Constellation)
// ============================================
const initShowcaseCanvas = () => {
  const canvas = document.getElementById('showcase-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];

  // Configuration
  const particleCount = 60;
  const connectionDistance = 150;
  const mouseDistance = 200;

  const resize = () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = document.querySelector('.showcase-hero').offsetHeight;
  };

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.5;
      this.vy = (Math.random() - 0.5) * 0.5;
      this.size = Math.random() * 2 + 1;
      this.color = `hsla(14, 100%, 64%, ${Math.random() * 0.5 + 0.1})`; // Coral color
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const initParticles = () => {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }
  }

  initParticles();

  const animate = () => {
    ctx.clearRect(0, 0, width, height);

    // Update and draw particles
    particles.forEach(p => {
      p.update();
      p.draw();
    });

    // Draw connections
    ctx.beginPath();
    for (let i = 0; i < particleCount; i++) {
      for (let j = i + 1; j < particleCount; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < connectionDistance) {
          ctx.strokeStyle = `rgba(255, 127, 80, ${0.2 * (1 - dist / connectionDistance)})`;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
        }
      }
    }
    ctx.stroke();

    requestAnimationFrame(animate);
  };

  animate();
  window.addEventListener('resize', () => {
    resize();
    initParticles();
  });
};

// Initialize if on showcase page
if (document.querySelector('.showcase-page')) {
  initShowcaseCanvas();
}

// --- TERMINAL VALIDATION & SYSTEM TICKER ---
const initContactTerminal = () => {
  const inputs = ['inputName', 'inputEmail', 'inputMessage'];

  inputs.forEach(id => {
    const el = document.getElementById(id);
    const feedback = document.getElementById(id.replace('input', 'feedback'));
    if (!el) return;

    el.addEventListener('input', () => {
      if (el.checkValidity() && el.value.length > 2) {
        feedback.textContent = '> INPUT_VERIFIED';
        feedback.className = 'input-feedback valid';
      } else {
        feedback.textContent = '';
        feedback.className = 'input-feedback';
      }
    });

    el.addEventListener('blur', () => {
      if (!el.checkValidity() && el.value.length > 0) {
        feedback.textContent = '> ERROR: INVALID_FORMAT';
        feedback.className = 'input-feedback invalid';
      }
    });
  });
};

const initSystemTicker = () => {
  const latencyEl = document.getElementById('latency-val');
  if (!latencyEl) return;

  setInterval(() => {
    const ms = Math.floor(Math.random() * 15) + 8;
    latencyEl.textContent = `${ms}ms`;
  }, 2000);
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initShowcaseCanvas();
    initContactTerminal();
    initSystemTicker();
  });
} else {
  initShowcaseCanvas();
  initContactTerminal();
  initSystemTicker();
}

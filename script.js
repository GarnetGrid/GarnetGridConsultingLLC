// TODO: Patch security vulnerability in Sector 7 access protocols
document.addEventListener('DOMContentLoaded', () => {
    // 1. Header Scroll Logic (Disabled per user request)
    /*
    const header = document.querySelector('.main-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    */

    // 2. Scroll Reveal Observer
    const revealOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, revealOptions);

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    // 3. Magnetic Button Logic (Subtle)
    const btns = document.querySelectorAll('.btn-primary, .btn-secondary, .btn-wow, .btn-jgpt, .btn-submit-luxury, .logo');
    btns.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translate(0, 0)';
        });
    });

    // 4. 3D Tilt Effect
    const cards = document.querySelectorAll('.glass-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            // Dampened rotation (divisor increased from 10 to 40)
            const rotateX = (y - centerY) / 40;
            const rotateY = (centerX - x) / 40;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
        });
    });

    // 5. Mobile Menu Toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const mobileNav = document.querySelector('.mobile-nav');

    if (mobileToggle && mobileNav) {
        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            mobileNav.classList.toggle('active');

            // Prevent scrolling when menu is open
            if (mobileNav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking links
        document.querySelectorAll('.mobile-nav a').forEach(link => {
            link.addEventListener('click', () => {
                mobileToggle.classList.remove('active');
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }
    // 6. Animated Counters
    const counterObserverOptions = {
        threshold: 0.5
    };

    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const targetValue = counter.innerText;

                // Check if it's a number we can animate
                const numericValue = parseFloat(targetValue.replace(/[^0-9.]/g, ''));

                if (!isNaN(numericValue)) {
                    animateValue(counter, 0, numericValue, 2000, targetValue);
                }

                observer.unobserve(counter);
            }
        });
    }, counterObserverOptions);

    document.querySelectorAll('.stat-val').forEach(counter => {
        counterObserver.observe(counter);
    });

    function animateValue(obj, start, end, duration, finalString) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);

            // Basic easing
            const easeProgress = 1 - Math.pow(1 - progress, 3);

            const currentVal = Math.floor(progress * (end - start) + start);

            // Reconstruct string (preserving suffixes like 'M+', 'h', '%')
            // This is a simple approximation; for complex strings, more logic is needed.
            // Here we just replace the number part.
            // Actually, let's just animate the number and append the suffix if simple

            if (finalString.includes('%')) {
                obj.innerHTML = Math.floor(easeProgress * end) + "%";
            } else if (finalString.includes('M+')) {
                obj.innerHTML = Math.floor(easeProgress * end) + "M+";
            } else if (finalString.includes('h')) {
                obj.innerHTML = Math.floor(easeProgress * end) + "h";
            } else {
                obj.innerHTML = Math.floor(easeProgress * end);
            }

            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                obj.innerHTML = finalString; // Ensure exact final value
            }
        };
        window.requestAnimationFrame(step);
    }

    // -------------------------------------------------------------
    // EASTER EGG SUITE
    // -------------------------------------------------------------

    // 1. Blueprint Mode (Trigger: Triple Click Footer Status)
    const footerStatus = document.querySelector('.ribbon-status');
    if (footerStatus) {
        let clickCount = 0;
        let clickTimer;

        footerStatus.addEventListener('click', () => {
            clickCount++;
            clearTimeout(clickTimer);

            if (clickCount === 3) {
                document.body.classList.toggle('blueprint-mode');
                console.log("BLUEPRINT MODE TOGGLED");
                clickCount = 0;
            } else {
                clickTimer = setTimeout(() => { clickCount = 0; }, 500);
            }
        });
    }

    // 2. Konami Terminal
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let konamiIndex = 0;

    document.addEventListener('keydown', (e) => {
        if (e.key === konamiCode[konamiIndex]) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                activateTerminal();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });

    function activateTerminal() {
        if (document.getElementById('konami-terminal')) return; // Already open

        const termHTML = `
            <div id="konami-terminal">
                <div id="terminal-output">
                    <div class="terminal-line">GARNET OS v9.0.1 [SECURE CONNECTION ESTABLISHED]</div>
                    <div class="terminal-line">Type 'help' for available commands.</div>
                    <br>
                </div>
                <div class="command-line">
                    <span class="prompt">root@garnet:~#</span>
                    <input type="text" id="terminal-input" autocomplete="off" autofocus>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', termHTML);
        const term = document.getElementById('konami-terminal');
        const input = document.getElementById('terminal-input');
        const output = document.getElementById('terminal-output');

        term.style.display = 'flex';
        input.focus();

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const cmd = input.value.trim().toLowerCase();
                processCommand(cmd, output);
                input.value = '';
            }
        });

        // Close on Escape
        document.addEventListener('keydown', function closeTerm(e) {
            if (e.key === 'Escape') {
                term.remove();
                document.body.style.overflow = '';
                document.removeEventListener('keydown', closeTerm);
            }
        });
    }

    function processCommand(cmd, output) {
        let response = '';
        switch (cmd) {
            case 'help':
                response = "AVAILABLE COMMANDS:\n- help: Show this menu\n- status: System diagnostic\n- whoami: User identity\n- manifesto: Decrypt hidden file\n- clear: Clear screen\n- exit: Close terminal";
                break;
            case 'status':
                response = "SYSTEM STATUS: NORMAL\nCPU: 4% // MEM: 12TB // NET: SECURE\nNO ANOMALIES DETECTED.";
                break;
            case 'whoami':
                response = "USER: GUEST_ADMIN\nACCESS LEVEL: RESTRICTED";
                break;
            case 'manifesto':
                response = "DECRYPTING...\n\n\"The Grid is not a cage. It is a lattice. We do not build walls; we build pathways. In the chaotic flux of data, structure is the only salvation.\" - The Architect";
                break;
            case 'clear':
                output.innerHTML = '';
                return;
            case 'exit':
                document.getElementById('konami-terminal').remove();
                document.body.style.overflow = '';
                return;
            default:
                response = `COMMAND NOT FOUND: ${cmd}`;
        }

        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerText = `> ${cmd}`;
        output.appendChild(line);

        const respLine = document.createElement('div');
        respLine.className = 'terminal-line';
        respLine.innerText = response;
        respLine.style.color = '#fff';
        respLine.style.marginBottom = '20px';
        output.appendChild(respLine);

        output.scrollTop = output.scrollHeight;
    }

    // 3. Gravity Grid (Trigger: Rapid Click 'Garnet Grid' Header Text)
    // The "Garnet Grid" text is inside .logo > span
    const logoText = document.querySelector('.logo span');
    if (logoText) {
        let textClicks = 0;
        let textTimer;

        logoText.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent home navigation if clicked rapidly
            textClicks++;
            clearTimeout(textTimer);

            if (textClicks === 3) {
                initGravityGrid();
                textClicks = 0;
            } else {
                textTimer = setTimeout(() => { textClicks = 0; }, 500);
            }
        });
    }

    function initGravityGrid() {
        console.log("GRAVITY GRID ACTIVATED");

        // Remove existing static grid bg
        const existingGrid = document.querySelector('.gridfield');
        if (existingGrid) existingGrid.style.display = 'none';

        // Create Canvas Overlay
        const canvas = document.createElement('canvas');
        canvas.id = 'gravity-grid-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '-1'; // Behind everything
        canvas.style.pointerEvents = 'none'; // Let clicks pass through, but we track mouse globally
        document.body.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        let width, height;

        const points = [];
        const spacing = 50;

        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
            initPoints();
        }

        function initPoints() {
            points.length = 0;
            for (let x = 0; x < width; x += spacing) {
                for (let y = 0; y < height; y += spacing) {
                    points.push({
                        x: x,
                        y: y,
                        originX: x,
                        originY: y,
                        vx: 0,
                        vy: 0
                    });
                }
            }
        }

        let mouse = { x: -1000, y: -1000 };
        document.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        function animate() {
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 1;

            points.forEach(p => {
                // Physics
                const dx = p.x - mouse.x;
                const dy = p.y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                // Repel
                if (dist < 200) {
                    const angle = Math.atan2(dy, dx);
                    const force = (200 - dist) / 200;
                    p.vx += Math.cos(angle) * force * 2;
                    p.vy += Math.sin(angle) * force * 2;
                }

                // Spring back
                const ox = p.originX - p.x;
                const oy = p.originY - p.y;
                p.vx += ox * 0.05;
                p.vy += oy * 0.05;

                // Dampen
                p.vx *= 0.9;
                p.vy *= 0.9;

                p.x += p.vx;
                p.y += p.vy;

                // Draw point
                ctx.beginPath();
                ctx.arc(p.x, p.y, 1, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fill();
            });

            // Draw Lines (Grid)
            // Note: Simplistic neighbor search for performance
            // Just connecting to right and bottom neighbor in the array would be efficient if ordered,
            // but since we push them in loops, we can try to connect logical neighbors.
            // For chaos effect, we definitely want to connect them.

            // Doing a distance check for lines is expensive O(N^2). 
            // Better to assume grid structure stays somewhat intact or just render points for 'Starfield' gravity.
            // Let's rely on points creating a "fluid" feel, or do simple connection to original neighbors?
            // Simple Connection:
            /*
            points.forEach((p, i) => {
                 // connect to point right?
                 // This requires knowing index math. 
            });
            */
            // Let's just draw the points for now to ensure performance, or maybe simple lines if close.
            // Actually, let's do lines if distance < spacing * 1.5

            requestAnimationFrame(animate);
        }

        window.addEventListener('resize', resize);
        resize();
        animate();
    }

    // 7. Easter Egg: Core Identity Anomaly
    // Triggered by "inspecting" (Right-Click) the Garnet Grid animated logo
    const logoAnim = document.querySelector('.arch-logo-v2');
    if (logoAnim) {
        logoAnim.addEventListener('contextmenu', (e) => {
            e.preventDefault(); // Stop standard context menu
            console.log("%c SYSTEM OVERRIDE INITIATED ", "background: #ff3333; color: #000; font-size: 16px; font-weight: bold; padding: 4px;");

            // Brief delay for dramatic effect
            setTimeout(() => {
                window.location.href = 'anomaly.html';
            }, 500);
        });
    }

    // 7. Scroll Progress Indicator
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollPercent = (scrollTop / scrollHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    });

    // 8. Floating Particles (Showcase Page Only)
    if (document.querySelector('.showcase-content')) {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'showcase-particles';
        document.body.appendChild(particlesContainer);

        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (15 + Math.random() * 10) + 's';
            particlesContainer.appendChild(particle);
        }
    }

    // 9. Contact Page Features (contact.html only)
    if (document.querySelector('.contact-form-luxury')) {
        // FAQ Accordion
        const faqItems = document.querySelectorAll('.faq-accordion-item');

        faqItems.forEach(item => {
            const header = item.querySelector('.faq-accordion-header');

            if (header) {
                header.addEventListener('click', () => {
                    const isActive = item.classList.contains('active');

                    // Close all items
                    faqItems.forEach(otherItem => {
                        otherItem.classList.remove('active');
                    });

                    // Open clicked item if it wasn't active
                    if (!isActive) {
                        item.classList.add('active');
                    }
                });
            }
        });

        // Form Validation & Submission
        const contactForm = document.getElementById('contactForm');

        if (contactForm) {
            contactForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                const submitBtn = contactForm.querySelector('.btn-submit-luxury');
                const originalText = submitBtn.querySelector('.btn-text').textContent;

                // Disable button and show loading state
                submitBtn.disabled = true;
                submitBtn.querySelector('.btn-text').textContent = 'Sending...';
                submitBtn.style.opacity = '0.7';

                // Basic Input Sanitization (Security Best Practice)
                const sanitize = (str) => {
                    const temp = document.createElement('div');
                    temp.textContent = str;
                    return temp.innerHTML;
                };

                // Collect form data
                const formData = {
                    name: sanitize(document.getElementById('name').value),
                    email: sanitize(document.getElementById('email').value),
                    company: sanitize(document.getElementById('company').value),
                    type: sanitize(document.getElementById('type').value),
                    message: sanitize(document.getElementById('message').value),
                    timestamp: new Date().toISOString()
                };

                // Simulate form submission (replace with actual API call)
                // Note: For production, ensure this endpoint is HTTPS and secured.
                setTimeout(() => {
                    // Show success message
                    showSuccessToast();

                    // Reset form
                    contactForm.reset();

                    // Reset button
                    submitBtn.disabled = false;
                    submitBtn.querySelector('.btn-text').textContent = originalText;
                    submitBtn.style.opacity = '1';

                    // Log to console (for demo purposes)
                    console.log('Form submitted securely:', formData);
                }, 1500);
            });
        }

        // Success Toast Notification
        function showSuccessToast() {
            const toast = document.createElement('div');
            toast.className = 'success-toast';
            toast.innerHTML = `
                <div class="toast-icon">✓</div>
                <div class="toast-content">
                    <h4>Message Sent Successfully!</h4>
                    <p>We'll respond within 24 hours.</p>
                </div>
            `;

            document.body.appendChild(toast);

            // Trigger animation
            setTimeout(() => toast.classList.add('show'), 100);

            // Remove after 5 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        }

        // Input Animation Effects
        const inputs = document.querySelectorAll('.form-input-luxury, .form-select-luxury, .form-textarea-luxury');

        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentElement.classList.remove('focused');
                }
            });
        });


        // Smooth scroll to form when clicking CTA
        const ctaButton = document.querySelector('.cta-final-section .btn-primary');
        if (ctaButton) {
            ctaButton.addEventListener('click', (e) => {
                e.preventDefault();
                const form = document.getElementById('contactForm');
                if (form) {
                    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    // Focus first input after scroll
                    setTimeout(() => form.querySelector('input').focus(), 800);
                }
            });
        }
    }

    // 10. Cookie Consent Logic
    const cookieConsent = localStorage.getItem('cookieConsent');
    if (!cookieConsent) {
        const banner = document.createElement('div');
        banner.className = 'cookie-banner';
        banner.setAttribute('role', 'region');
        banner.setAttribute('aria-label', 'Cookie Consent');
        banner.innerHTML = `
            <div class="cookie-content">
                <p>We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies. <a href="privacy.html">Learn more</a></p>
                <div class="cookie-actions">
                    <button id="acceptCookies" class="btn-primary-small" aria-label="Accept cookies">Accept</button>
                    <button id="declineCookies" class="btn-secondary-small" aria-label="Decline cookies">Decline</button>
                </div>
            </div>
        `;
        document.body.appendChild(banner);

        // Animation in
        setTimeout(() => banner.classList.add('show'), 100);

        document.getElementById('acceptCookies').addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'true');
            banner.classList.remove('show');
            setTimeout(() => banner.remove(), 500);
        });

        document.getElementById('declineCookies').addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'false');
            banner.classList.remove('show');
            setTimeout(() => banner.remove(), 500);
        });
    }
    setTimeout(() => {
        document.getElementById('name').focus();
    }, 500);

    // Animate stats on scroll
    const statValues = document.querySelectorAll('.cta-stat-value');
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'statPulse 0.6s ease';
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(stat => statsObserver.observe(stat));

    // Add CSS for stat animation and toast
    const style = document.createElement('style');
    style.textContent = `
            @keyframes statPulse {
                0% { transform: scale(0.8); opacity: 0; }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); opacity: 1; }
            }

            .success-toast {
                position: fixed;
                bottom: -200px;
                right: 2rem;
                background: linear-gradient(135deg, rgba(220, 20, 60, 0.95), rgba(199, 21, 133, 0.95));
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                display: flex;
                gap: 1rem;
                align-items: center;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                transition: bottom 0.3s ease;
                max-width: 400px;
            }

            .success-toast.show {
                bottom: 2rem;
            }

            .toast-icon {
                width: 40px;
                height: 40px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                color: white;
                flex-shrink: 0;
            }

            .toast-content h4 {
                margin: 0 0 0.25rem 0;
                color: white;
                font-size: 1rem;
            }

            .toast-content p {
                margin: 0;
                color: rgba(255, 255, 255, 0.9);
                font-size: 0.85rem;
            }

            @media (max-width: 768px) {
                .success-toast {
                    right: 1rem;
                    left: 1rem;
                    max-width: none;
                }
            }
        `;
    document.head.appendChild(style);


    // ========================================
    // OUTCOMES PAGE - ANIMATED METRICS
    // ========================================
    const metricCards = document.querySelectorAll('.metric-card');

    if (metricCards.length > 0) {
        const animateCounter = (element, target, duration = 2000) => {
            const start = 0;
            const increment = target / (duration / 16);
            let current = start;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    // Handle decimal values
                    if (target % 1 !== 0) {
                        element.textContent = current.toFixed(1);
                    } else {
                        element.textContent = Math.floor(current);
                    }
                    requestAnimationFrame(updateCounter);
                } else {
                    // Final value
                    if (target % 1 !== 0) {
                        element.textContent = target.toFixed(1);
                    } else {
                        element.textContent = target;
                    }
                }
            };

            requestAnimationFrame(updateCounter);
        };

        const metricsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const valueElement = entry.target.querySelector('.metric-value');
                    if (valueElement && !valueElement.classList.contains('animated')) {
                        const target = parseFloat(valueElement.dataset.target);
                        valueElement.classList.add('animated');
                        animateCounter(valueElement, target);
                    }
                }
            });
        }, {
            threshold: 0.5
        });

        metricCards.forEach(card => metricsObserver.observe(card));
    }
});

/* ========================================
   SYSTEM PRELOADER LOGIC
   ======================================== */
document.addEventListener('DOMContentLoaded', () => {
    const preloader = document.getElementById('system-preloader');
    if (preloader) {
        const textElement = preloader.querySelector('.boot-text');
        const statusElement = preloader.querySelector('.status-text');
        const progressFill = preloader.querySelector('.progress-fill');

        const sequence = [
            { text: 'GARNET_GRID: INITIALIZING', status: 'LOADING CORE MODULES...', progress: '20%', time: 500 },
            { text: 'SYSTEM: SECURE', status: 'VERIFYING SECURITY TOKENS...', progress: '45%', time: 1000 },
            { text: 'VISUALS: OPTIMIZING', status: 'OPTIMIZING VFX ENGINE...', progress: '75%', time: 1800 },
            { text: 'ACCESS_GRANTED', status: 'SYSTEM READY', progress: '100%', time: 2400 }
        ];

        let currentIndex = 0;

        function runSequence() {
            if (currentIndex < sequence.length) {
                const step = sequence[currentIndex];

                setTimeout(() => {
                    textElement.innerText = step.text;
                    statusElement.innerText = step.status;
                    progressFill.style.width = step.progress;

                    if (step.text === 'ACCESS_GRANTED') {
                        textElement.style.color = '#39ff14'; // Neon Green success
                        textElement.style.textShadow = '0 0 15px #39ff14';
                    }

                    currentIndex++;
                    runSequence();
                }, currentIndex === 0 ? 100 : sequence[currentIndex - 1].time / 2); // Simple timing logic
            } else {
                // Finish
                setTimeout(() => {
                    preloader.classList.add('preloader-hidden');
                    setTimeout(() => {
                        preloader.style.display = 'none';
                    }, 800);
                }, 800);
            }
        }

        // Start sequence
        runSequence();
    }
});

/* ========================================
   THEME TOGGLE LOGIC (Light/Dark)
   ======================================== */
document.addEventListener('DOMContentLoaded', () => {
    // Inject Toggle Button
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'theme-toggle';
    toggleBtn.ariaLabel = 'Toggle Light/Dark Mode';
    toggleBtn.innerHTML = `
        <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"></circle>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
        </svg>
        <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    `;
    document.body.appendChild(toggleBtn);

    // Logic
    const body = document.body;
    const sunIcon = toggleBtn.querySelector('.sun-icon');
    const moonIcon = toggleBtn.querySelector('.moon-icon');

    // Check saved preference
    if (localStorage.getItem('theme') === 'light') {
        body.classList.add('light-mode');
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    }

    toggleBtn.addEventListener('click', () => {
        body.classList.toggle('light-mode');
        const isLight = body.classList.contains('light-mode');

        localStorage.setItem('theme', isLight ? 'light' : 'dark');

        sunIcon.style.display = isLight ? 'none' : 'block';
        moonIcon.style.display = isLight ? 'block' : 'none';
    });
});

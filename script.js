document.addEventListener('DOMContentLoaded', () => {
    // 1. Header Scroll Logic
    const header = document.querySelector('.main-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

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
    const btns = document.querySelectorAll('.btn-primary, .logo');
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

            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
        });
    });

    // 5. Mobile Menu Toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            navLinks.classList.toggle('mobile-active');

            // Prevent scrolling when menu is open
            if (navLinks.classList.contains('mobile-active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
    }

    // Close menu when clicking links
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            mobileToggle.classList.remove('active');
            navLinks.classList.remove('mobile-active');
            document.body.style.overflow = '';
        });
    });
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

                // Collect form data
                const formData = {
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    company: document.getElementById('company').value,
                    type: document.getElementById('type').value,
                    message: document.getElementById('message').value,
                    timestamp: new Date().toISOString()
                };

                // Simulate form submission (replace with actual API call)
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
                    console.log('Form submitted:', formData);
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
                    setTimeout(() => {
                        document.getElementById('name').focus();
                    }, 500);
                }
            });
        }

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
    }

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

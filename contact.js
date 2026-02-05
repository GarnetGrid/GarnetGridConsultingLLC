// Contact Page Interactive Features

document.addEventListener('DOMContentLoaded', () => {
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-accordion-item');

    faqItems.forEach(item => {
        const header = item.querySelector('.faq-accordion-header');

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

    // Add CSS for stat animation
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
});

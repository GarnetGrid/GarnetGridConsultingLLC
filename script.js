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
});

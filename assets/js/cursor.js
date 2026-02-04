/* ============================================
   CINEMATIC ORBIT CURSOR
   Physics-based mouse follower
   ============================================ */
const initCursor = () => {
    // Check for touch device - disable if touch
    if (window.matchMedia("(pointer: coarse)").matches) return;

    const cursor = document.createElement('div');
    cursor.className = 'orbit-cursor';
    document.body.appendChild(cursor);

    const follower = document.createElement('div');
    follower.className = 'orbit-follower';
    document.body.appendChild(follower);

    let posX = 0, posY = 0;
    let mouseX = 0, mouseY = 0;

    // Physics config
    const speed = 0.15; // Lower = more lag/floaty

    // Mouse movement
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        // Immediate update for the dot
        cursor.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
    });

    // Animation loop for the follower (lerping)
    const animate = () => {
        posX += (mouseX - posX) * speed;
        posY += (mouseY - posY) * speed;

        follower.style.transform = `translate3d(${posX - 15}px, ${posY - 15}px, 0)`;

        requestAnimationFrame(animate);
    };
    animate();

    // Interactive states
    const interactiveElements = document.querySelectorAll('a, button, input, textarea, .service-card, .visual-card, .offer-card, summary');

    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('hover');
            follower.classList.add('hover');
        });
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('hover');
            follower.classList.remove('hover');
        });
    });

    // Click effect
    document.addEventListener('mousedown', () => {
        cursor.classList.add('click');
        follower.classList.add('click');
    });

    document.addEventListener('mouseup', () => {
        cursor.classList.remove('click');
        follower.classList.remove('click');
    });
};

document.addEventListener('DOMContentLoaded', initCursor);

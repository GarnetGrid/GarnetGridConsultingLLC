// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Carousel animation
const carousel = document.querySelector('.clients-logos');
carousel.addEventListener('mouseover', () => {
    carousel.style.animationPlayState = 'paused';
});
carousel.addEventListener('mouseout', () => {
    carousel.style.animationPlayState = 'running';
});
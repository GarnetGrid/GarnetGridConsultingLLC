// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

const carousel = document.querySelector('.carousel-clientimages');
const images = document.querySelectorAll('.carousel-clientimages img');

let offset = 0; // Start position for carousel
const speed = 5; // Speed of carousel movement
const imageWidth = images[0].getBoundingClientRect().width + 10; // Image width + gap
let totalWidth = imageWidth * images.length;

// Duplicate images to ensure seamless looping
const cloneImages = () => {
    images.forEach(image => {
        const clone = image.cloneNode(true);
        carousel.appendChild(clone);
    });
};

cloneImages();

const moveCarousel = () => {
    offset -= speed;
    if (Math.abs(offset) >= totalWidth) {
        offset = 0; // Reset offset to start loop
    }
    carousel.style.transform = `translateX(${offset}px)`;
};

// Infinite loop using requestAnimationFrame
const loop = () => {
    moveCarousel();
    requestAnimationFrame(loop);
};

loop();

// Scroll to respective section on click
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}


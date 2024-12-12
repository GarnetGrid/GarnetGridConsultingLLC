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

// Initialize EmailJS
emailjs.init('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'); // Replace 'YOUR_PUBLIC_KEY' with your EmailJS public key

document.getElementById('contactForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const form = e.target;

    emailjs.sendForm('sg2fb56556ac00568c83eb21baae44fbc2', 'd-cbb12a6a14124cb0a4368ac10cb37ea2', form)
        .then(() => {
            document.getElementById('formResponse').textContent = 'Message sent successfully!';
            form.reset();
        }, (error) => {
            document.getElementById('formResponse').textContent = 'Failed to send message. Please try again later.';
            console.error('EmailJS error:', error);
        });
});


// using Twilio SendGrid's v3 Node.js Library
// https://github.com/sendgrid/sendgrid-nodejs
javascript
const sgMail = require('@sendgrid/mail')
sgMail.setApiKey(process.env.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)
const msg = {
  to: 'garnetgrid@gmail.com', // Change to your recipient
  from: 'garnetgrid@gmail.com', // Change to your verified sender
  subject: 'Incoming Request',
  text: 'View Info',
  html: 'Lets Build',
}
sgMail
  .send(msg)
  .then(() => {
    console.log('Email sent')
  })
  .catch((error) => {
    console.error(error)
  })

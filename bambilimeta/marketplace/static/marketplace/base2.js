// js/script.js

document.addEventListener("DOMContentLoaded", function() {

    // --- Product Card Carousel Logic ---
    // This allows thumbnails to control the main carousel
    const thumbnailImages = document.querySelectorAll('.thumbnail-img');

    thumbnailImages.forEach(thumb => {
        thumb.addEventListener('click', function() {
            const carouselId = this.dataset.productCarouselId;
            const slideIndex = this.dataset.bsSlideTo;
            const carouselElement = document.querySelector(carouselId);

            if (carouselElement) {
                // Use Bootstrap's official Carousel API
                const carouselInstance = bootstrap.Carousel.getOrCreateInstance(carouselElement);
                carouselInstance.to(slideIndex);

                // Update the 'active' class on thumbnails
                const parentThumbColumn = this.closest('.thumbnail-column');
                parentThumbColumn.querySelectorAll('.thumbnail-img').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });


    // --- Sticky Navbar Shadow Logic ---
    // Adds a shadow to the navbar when it's not at the top of the page
    const navbar = document.getElementById('main-navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 10) { // Add shadow after scrolling 10px
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

});
// Function to show selected section and hide others
function openSection(sectionId, clickedItem) {
    // Hide all sections
    var sections = document.getElementsByClassName("section-content");
    for (var i = 0; i < sections.length; i++) {
        sections[i].classList.remove("active");
    }
    
    // Remove active class from all nav items
    var navItems = document.getElementsByClassName("nav-item");
    for (var i = 0; i < navItems.length; i++) {
        navItems[i].classList.remove("active");
    }
    
    // Show selected section and mark nav item as active
    document.getElementById(sectionId).classList.add("active");
    clickedItem.classList.add("active");
    
    // Update URL hash
    window.location.hash = sectionId;
}

// Handle URL hash on page load
document.addEventListener("DOMContentLoaded", function() {
    var hash = window.location.hash.substring(1);
    if (hash) {
        var section = document.getElementById(hash);
        var navItem = document.querySelector('a[href="#' + hash + '"]');
        if (section && navItem) {
            openSection(hash, navItem);
        }
    }
});

// Back to top button functionality
window.onscroll = function() {
    var backToTopBtn = document.getElementById("back-to-top");
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        backToTopBtn.style.display = "block";
    } else {
        backToTopBtn.style.display = "none";
    }
};

function scrollToTop() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

// Function to handle image error fallbacks
function handleImageError(img) {
    img.src = 'placeholder-image.png';
    img.alt = 'Image unavailable';
}

// Enable tooltips if Bootstrap is available
if (typeof bootstrap !== 'undefined') {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}
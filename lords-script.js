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
    
    // Initialize lazy loading
    initializeLazyLoading();
    
    // Initialize animations
    loadGSAP();
});

// Debounce function for scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimized scroll handler
window.addEventListener('scroll', debounce(() => {
    const backToTopBtn = document.getElementById("back-to-top");
    if (backToTopBtn) {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = "block";
        } else {
            backToTopBtn.style.display = "none";
        }
    }
}, 100));

function scrollToTop() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

// Function to handle image error fallbacks
function handleImageError(img) {
    img.src = 'placeholder-image.png';
    img.alt = 'Image unavailable';
}

// Image Lazy Loading
function initializeLazyLoading() {
    // Create lazy loading observer
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                
                // Load the actual image
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                }
                
                // Stop observing this image
                observer.unobserve(img);
            }
        });
    }, {
        root: null,
        rootMargin: '50px',
        threshold: 0.1
    });

    // Observe all images with data-src
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => imageObserver.observe(img));

    // Content lazy loading for heavy sections
    const contentObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('content-loaded');
                
                // Load any dynamic content here
                if (entry.target.dataset.loadContent) {
                    loadDynamicContent(entry.target);
                }
            }
        });
    }, {
        root: null,
        rootMargin: '100px',
        threshold: 0.1
    });

    // Observe content sections
    const lazyContent = document.querySelectorAll('.lazy-content');
    lazyContent.forEach(el => contentObserver.observe(el));
}

// Dynamic content loader
function loadDynamicContent(element) {
    const contentType = element.dataset.loadContent;
    
    switch(contentType) {
        case 'heroes':
            loadHeroData(element);
            break;
        case 'formations':
            loadFormationData(element);
            break;
        case 'equipment':
            loadEquipmentData(element);
            break;
    }
}

// Preload critical resources
function preloadCriticalResources() {
    const criticalResources = [
        { href: 'lords-styles.css', as: 'style' },
        { href: 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js', as: 'script' }
    ];

    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = resource.href;
        link.as = resource.as;
        document.head.appendChild(link);
    });
}

// Initialize preloading
preloadCriticalResources();

// Load GSAP and initialize animations
function loadGSAP() {
    // Load GSAP and plugins
    const gsapScript = document.createElement('script');
    gsapScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js';
    document.head.appendChild(gsapScript);

    gsapScript.onload = () => {
        // Load ScrollTrigger plugin
        const scrollTriggerScript = document.createElement('script');
        scrollTriggerScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js';
        document.head.appendChild(scrollTriggerScript);
        
        scrollTriggerScript.onload = () => {
            initializeAnimations();
        };
    };
}

function initializeAnimations() {
    // Register ScrollTrigger plugin
    gsap.registerPlugin(ScrollTrigger);

    // Hero animations
    const heroTimeline = gsap.timeline();
    
    if (document.querySelector(".hero-title")) {
        // Animate each word in the hero title
        gsap.to(".hero-title .word", {
            opacity: 1,
            y: 0,
            rotationX: 0,
            stagger: 0.2,
            ease: "back.out(1.7)",
            duration: 1.2
        });
        
        heroTimeline
            .from(".hero-subtitle", {
                duration: 1.2,
                y: 30,
                opacity: 0,
                ease: "power3.out"
            }, "-=0.5");
    }

    if (document.querySelector(".hero-buttons .hero-btn")) {
        heroTimeline.from(".hero-buttons .hero-btn", {
            duration: 1,
            y: 20,
            opacity: 0,
            stagger: 0.2,
            ease: "power3.out"
        }, "-=0.8");
    }

    if (document.querySelector(".hero-scroll-indicator")) {
        heroTimeline.from(".hero-scroll-indicator", {
            duration: 1,
            opacity: 0,
            y: 20,
            ease: "power3.out"
        }, "-=0.5");
    }

    // Parallax effect for floating elements
    if (document.querySelector(".floating-elements")) {
        gsap.to(".floating-elements", {
            scrollTrigger: {
                trigger: ".hero",
                start: "top top",
                end: "bottom top",
                scrub: 1
            },
            y: -200,
            opacity: 0.3
        });
    }

    // Feature cards stagger animation
    if (document.querySelector(".feature-card")) {
        gsap.from(".feature-card", {
            scrollTrigger: {
                trigger: ".features",
                start: "top 80%",
                toggleActions: "play none none reverse"
            },
            y: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "power2.out"
        });
    }

    // Section animations
    const sections = gsap.utils.toArray(".section");
    sections.forEach(section => {
        gsap.from(section, {
            scrollTrigger: {
                trigger: section,
                start: "top 85%",
                toggleActions: "play none none reverse"
            },
            y: 30,
            opacity: 0,
            duration: 0.8,
            ease: "power2.out"
        });
    });

    // Composition cards animation
    if (document.querySelector(".comp-button")) {
        gsap.from(".comp-button", {
            scrollTrigger: {
                trigger: ".comps-nav",
                start: "top 80%"
            },
            x: -30,
            opacity: 0,
            duration: 0.6,
            stagger: 0.1,
            ease: "power2.out"
        });
    }

    // Troop type cards animation
    if (document.querySelector(".troop-type")) {
        gsap.from(".troop-type", {
            scrollTrigger: {
                trigger: ".comp-breakdown",
                start: "top 75%"
            },
            scale: 0.8,
            opacity: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "back.out(1.7)"
        });
    }

    // Count-up animation for statistics
    const countElements = document.querySelectorAll('.troop-count');
    countElements.forEach(element => {
        const endValue = parseInt(element.textContent);
        
        gsap.from(element, {
            scrollTrigger: {
                trigger: element,
                start: "top 80%"
            },
            textContent: 0,
            duration: 2,
            ease: "power2.out",
            snap: { textContent: 1 },
            onUpdate: function() {
                element.textContent = Math.round(this.targets()[0].textContent).toLocaleString();
            }
        });
    });

    // Advanced hover effects for buttons
    const heroButtons = document.querySelectorAll('.hero-btn');
    heroButtons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            gsap.to(btn, {
                scale: 1.05,
                duration: 0.3,
                ease: "power2.out"
            });
        });
        
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, {
                scale: 1,
                duration: 0.3,
                ease: "power2.out"
            });
        });
    });

    // Floating animation for elements
    const floatEls = document.querySelectorAll('.float-el');
    floatEls.forEach((el, index) => {
        gsap.to(el, {
            y: "random(-20, 20)",
            x: "random(-20, 20)",
            rotation: "random(-15, 15)",
            duration: "random(5, 8)",
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut",
            delay: index * 0.2
        });
    });

    // Text glow animation for titles
    const glowingTitles = document.querySelectorAll('.hero-title, .section-title');
    glowingTitles.forEach(title => {
        gsap.to(title, {
            textShadow: "0 0 20px rgba(76, 201, 240, 0.5)",
            duration: 2,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    });

    // Smooth reveal for images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        gsap.from(img, {
            scrollTrigger: {
                trigger: img,
                start: "top 85%"
            },
            scale: 0.9,
            opacity: 0,
            duration: 0.8,
            ease: "power2.out"
        });
    });
}

// Mouse follower effect
document.addEventListener('DOMContentLoaded', () => {
    const mouseFollower = document.createElement('div');
    mouseFollower.className = 'mouse-follower';
    document.body.appendChild(mouseFollower);
    
    let mouseX = 0, mouseY = 0;
    let followerX = 0, followerY = 0;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    // Use requestAnimationFrame instead of GSAP ticker for mouse follower
    function updateMouseFollower() {
        followerX += (mouseX - followerX) * 0.1;
        followerY += (mouseY - followerY) * 0.1;
        
        mouseFollower.style.transform = `translate(${followerX}px, ${followerY}px)`;
        requestAnimationFrame(updateMouseFollower);
    }
    
    updateMouseFollower();
});

// Enable tooltips if Bootstrap is available
if (typeof bootstrap !== 'undefined') {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}

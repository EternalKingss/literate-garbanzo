function openSection(sectionId, clickedItem) {
  document.querySelectorAll('.section-content').forEach(sec => sec.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  var el = document.getElementById(sectionId);
  if (el) el.classList.add('active');
  if (clickedItem) clickedItem.classList.add('active');
  window.location.hash = sectionId;
}

document.addEventListener('DOMContentLoaded', function () {
  // handle hash on load
  var hash = window.location.hash.substring(1);
  if (hash) {
    var section = document.getElementById(hash);
    var navItem = document.querySelector('a[href="#' + hash + '"]');
    if (section && navItem) {
      openSection(hash, navItem);
    }
  }

  initLazyLoad();
  initScrollAnimations();
  initSmoothScroll();
});

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

function initScrollAnimations() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.section, .subsection, .example-box, .note-box, .recommendation-box, .warning, .gear-option, .image-container, .troop-type').forEach(el => observer.observe(el));
}

function initLazyLoad() {
  const imgObserver = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) img.src = img.dataset.src;
        obs.unobserve(img);
      }
    });
  }, { rootMargin: '100px' });

  document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
}

window.addEventListener('scroll', () => {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;
  btn.style.display = window.scrollY > 300 ? 'block' : 'none';
});

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

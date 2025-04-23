document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.querySelector('#close-banner');
    const banner = document.querySelector('#sticky-banner');
    if (localStorage.getItem('bannerClosed')) {
        banner.style.display = 'none';
      }

    closeBtn?.addEventListener('click', function () {
        banner.style.display = 'none';
        localStorage.setItem('bannerClosed', 'true');
    });

});
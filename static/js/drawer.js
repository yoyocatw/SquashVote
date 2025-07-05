 const drawer = document.getElementById('drawer');
  const overlay = document.getElementById('drawerOverlay');
  const openBtn = document.getElementById('drawerToggle');
  const closeBtn = document.getElementById('drawerClose');

  const openDrawer = () => {
    drawer.classList.remove('translate-x-full');
    overlay.classList.remove('hidden');
  };

  const closeDrawer = () => {
    drawer.classList.add('translate-x-full');
    overlay.classList.add('hidden');
  };

  openBtn.addEventListener('click', openDrawer);
  closeBtn.addEventListener('click', closeDrawer);
  overlay.addEventListener('click', closeDrawer);
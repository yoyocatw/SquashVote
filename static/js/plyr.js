const player = document.getElementById('player');

if (player) {
  const start = Number(player.dataset.start || 0);

  const plyr = new Plyr(player, {
    autoplay: true,
    muted: true,
    controls: ['play-large', 'play', 'progress', 'mute', 'fullscreen'],
    storage: { enabled: false },
    youtube: { noCookie: true, rel: 0, iv_load_policy: 3, modestbranding: 1 }
  });

  // Ensure we actually begin at clip start
  const snapToStart = () => { if (plyr.currentTime < start) plyr.currentTime = start; };

  plyr.on('ready', () => {
    snapToStart();
    plyr.once('play', snapToStart);
  });

  plyr.on('seeking', () => {
    if (plyr.currentTime < start) plyr.currentTime = start;
    if (plyr.currentTime > end)   plyr.currentTime = end;
  });


  plyr.on('click', () => { if (plyr.muted) plyr.muted = false; });

  
  const replayButton = document.getElementById('replayButton');
  if (replayButton) {
    replayButton.addEventListener('click', () => {
      plyr.currentTime = start;
      plyr.play();
    });
  }

  window.plyr = plyr;
}
const player = document.getElementById('player');

if (player) {
  const start = Number(player.dataset.start) || 0;
  let end = Number(player.dataset.end) || 0;
  if (end <= start) end = start + 20; // defensive: always a positive window

  const plyr = new Plyr(player, {
    autoplay: false,
    muted: false,
    controls: ['play-large', 'play', 'progress', 'mute', 'fullscreen'],
    storage: { enabled: false },
    youtube: { noCookie: true, rel: 0, iv_load_policy: 3, modestbranding: 1 }
  });

  const replayButton = document.getElementById('replayButton');
  const showReplay = () => replayButton && replayButton.classList.remove('hidden');
  const hideReplay = () => replayButton && replayButton.classList.add('hidden');

  // Track whether we've reached the clip end so the play/seek handlers know to
  // restart from the top rather than resume past the window.
  let clipEnded = false;

  // Ensure we actually begin at clip start
  const snapToStart = () => { if (plyr.currentTime < start) plyr.currentTime = start; };

  plyr.on('ready', () => {
    snapToStart();
    plyr.once('play', snapToStart);
  });

  // Stop at the clip end: pause, rewind to start, and offer a replay.
  plyr.on('timeupdate', () => {
    if (!clipEnded && plyr.currentTime >= end) {
      clipEnded = true;
      plyr.pause();
      plyr.currentTime = start;
      showReplay();
    }
  });

  // If playback is (re)started after the clip ended — e.g. via Plyr's own play
  // button — restart cleanly from the beginning of the window.
  plyr.on('play', () => {
    if (clipEnded) {
      clipEnded = false;
      hideReplay();
      plyr.currentTime = start;
    }
  });

  // Keep scrubbing inside the clip window.
  plyr.on('seeking', () => {
    if (plyr.currentTime < start) plyr.currentTime = start;
    if (plyr.currentTime > end)   plyr.currentTime = end;
  });

  // First click unmutes (autoplay starts muted per browser policy).
  plyr.on('click', () => { if (plyr.muted) plyr.muted = false; });

  if (replayButton) {
    replayButton.addEventListener('click', () => {
      clipEnded = false;
      hideReplay();
      if (plyr.muted) plyr.muted = false;
      plyr.currentTime = start;
      plyr.play();
    });
  }

  window.plyr = plyr;
}

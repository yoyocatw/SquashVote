
const player = document.getElementById('player');
const start = Number(player.dataset.start) || 0;

const plyr = new Plyr(player, {
  controls: [
    'play-large',
    'play',
    'fullscreen',
    'progress',
    'mute',
  ],
  storage: {
    enabled: false
  },
  youtube: {
    rel: 0,
    showinfo: 0,
    iv_load_policy: 3,
    modestbranding: 1
  }
});
plyr.on('ready', () => {
  plyr.once('play', () => {
    plyr.currentTime = start;
  });
});

const replayButton = document.getElementById('replayButton');
replayButton.addEventListener('click', () => {
  plyr.currentTime = start;
  plyr.play();
});
window.plyr = plyr;



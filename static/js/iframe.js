
function initYouTubeClip(videoId, startTime) {
    let player;
    const endTime = startTime + 30;
  
    window.onYouTubeIframeAPIReady = function () {
      player = new YT.Player('player', {
        height: "100%",
        width: "100%",
        videoId: videoId,
        playerVars: {
          autoplay: 1,
          controls: 1,
          modestbranding: 1,
          rel: 0,
          fs: 1,
          iv_load_policy: 3,
          cc_load_policy: 0,
          start: startTime
        },
      });
    };
  
    window.restartClip = function () {
      if (player) {
        player.seekTo(startTime);
      }
    };
  }
  
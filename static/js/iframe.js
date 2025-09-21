
// Not using anymore using Plyr library instead. Kept for reference.
// This is a basic implementation of YouTube IFrame API to play a specific clip from a YouTube video.
function initYouTubeClip(videoId, startTime) {
    var tag = document.createElement('script');
		tag.src = "https://www.youtube.com/iframe_api";
		var firstScriptTag = document.getElementsByTagName('script')[0];
		firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    let player;
  
    window.onYouTubeIframeAPIReady = function () {
      player = new YT.Player('player', {
        height: "100%",
        width: "100%",
        videoId: videoId,
        playerVars: {
          autoplay: 0,
          controls: 0,
          modestbranding: 1,
          rel: 0,
          fs: 0,
          playsinline: 1,
          disablekb: 1,
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

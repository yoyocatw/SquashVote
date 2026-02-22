function voteConfetti() {
  var end = Date.now() + (3 * 1000);
  var colors = ['#FF2800', '#DEB841', '#ffffff'];

  (function frame() {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors: colors
    });
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors: colors
    });

    if (Date.now() < end) {
      requestAnimationFrame(frame);
    }
  })();
}

function sixseven() {
  var scalar = 4; 
  var textShape = confetti.shapeFromText({ text: '🫲6️⃣7️⃣🫱', scalar });

  var defaults = {
    spread: 150,           
    ticks: 1000,          
    gravity: 1.5,        
    decay: 0.95,
    startVelocity: 15,   
    shapes: [textShape],
    scalar,
    flat: true           
  };

  function frame() {
    confetti({
      ...defaults,
      particleCount: 50,
      origin: { x: 0.45, y: -0.1 },
      angle: 90
    });
    confetti({
      ...defaults,
      particleCount: 50,
      origin: { x: 0.25, y: -0.1 },
      angle: 90
    });

    confetti({
      ...defaults,
      particleCount: 50,
      origin: { x: 0.65, y: -0.1 },
      angle: 90
    });

    confetti({
      ...defaults,
      particleCount: 50,
      origin: { x: 0.9, y: -0.1 },
      angle: 90
    });
  }

  frame();
}
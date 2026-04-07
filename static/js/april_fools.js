(function () {
    const now = new Date();
    const isAprilFools = now.getMonth() === 3 && now.getDate() === 1;

    const testMode = false;
    if (!isAprilFools && !testMode) return;

    const targetSelectors = ['.april-fools'];
    const maxEscapes = 6;
    const escapeCounts = {};

    function initPrank() {
        if (!window.isRaining67) {
            timedSixSeven(); 
            window.isRaining67 = true;
        }

        targetSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);

            elements.forEach(btn => {
                if (!btn || btn.dataset.pranked === "true") return;

                const idOrClass = btn.id || btn.className;
                btn.dataset.pranked = "true";
                escapeCounts[idOrClass] = 0;

                btn.style.transition = "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
                btn.style.position = 'relative';
                btn.style.zIndex = '99999';
                btn.style.webkitTapHighlightColor = 'transparent';
                btn.disabled = true; // Fixed typo: 'diabled' to 'disabled'

                const flee = (e) => {
                    if (escapeCounts[idOrClass] >= maxEscapes) {
                        btn.style.position = 'relative';
                        btn.style.top = '0px';
                        btn.style.left = '0px';
                        btn.style.transform = "rotate(0deg)";
                        return;
                    }

                    btn.style.position = 'fixed';
                    const btnWidth = btn.offsetWidth;
                    const btnHeight = btn.offsetHeight;

                    const maxX = window.innerWidth - btnWidth - 20;
                    const maxY = window.innerHeight - btnHeight - 20;

                    const randomX = Math.max(20, Math.floor(Math.random() * maxX));
                    const randomY = Math.max(20, Math.floor(Math.random() * maxY));
                    const rot = (Math.random() - 0.5) * 720;

                    btn.style.left = `${randomX}px`;
                    btn.style.top = `${randomY}px`;
                    btn.style.transform = `rotate(${rot}deg)`;

                    escapeCounts[idOrClass]++;
                };

                btn.addEventListener('mouseover', flee);
                btn.addEventListener('touchstart', flee);
            });
        });
    }

    function timedSixSeven() {
        const scalar = 4;
        const textShape = confetti.shapeFromText({ text: '🫲6️⃣7️⃣🫱', scalar });

        const defaults = {
            spread: 130,
            ticks: 300,
            gravity: 1.5,
            decay: 0.96,
            startVelocity: 10,
            shapes: [textShape],
            scalar,
            flat: true
        };

        let bursts = 0;
        const maxBursts = 10; 

        const interval = setInterval(() => {
            [0.2, 0.4, 0.6, 0.8].forEach(xPos => {
                confetti({
                    ...defaults,
                    particleCount: 2,
                    origin: { x: xPos, y: -0.1 },
                    angle: 90
                });
            });

            bursts++;
            if (bursts >= maxBursts) {
                clearInterval(interval);
            }
        }, 650); 
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPrank);
    } else {
        initPrank();
    }

    document.body.addEventListener('htmx:afterSwap', initPrank);

})();
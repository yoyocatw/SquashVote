const modal = document.getElementById("myModal");
const closeBtn = document.getElementById("closeModal");
const substackLink = document.getElementById("substackLink");
const coffeeLink = document.getElementById("coffeeLink");

if (modal && closeBtn) {
  const now = Date.now();
  const lastShown = Number(localStorage.getItem("modalLastShown")) || 0;
  const hasSupported = localStorage.getItem("hasSupported") === "true";
  const hasShownThisSession = sessionStorage.getItem("supportModalShown");
  const oneWeek = 4 * 24 * 60 * 60 * 1000;

  if (!hasShownThisSession && (now - lastShown > oneWeek)) {
    modal.classList.remove("hidden");
    sessionStorage.setItem("supportModalShown", "true");
    localStorage.setItem("modalLastShown", now);
  }

  closeBtn.onclick = () => {
    modal.classList.add("hidden");
  };

  [substackLink, coffeeLink].forEach(link => {
    if (link) {
      link.addEventListener("click", () => {
        localStorage.setItem("hasSupported", "true");
      });
    }
  });
}

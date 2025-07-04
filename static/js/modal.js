const modal = document.getElementById("myModal");
const closeBtn = document.getElementById("closeModal");
const substackLink = document.getElementById("substackLink");
const coffeeLink = document.getElementById("coffeeLink");

const lastShown = Number(localStorage.getItem("modalLastShown"));
const hasSupported = localStorage.getItem("hasSupported") === "true";

const hasShownThisSession = sessionStorage.getItem("supportModalShown");
if (!hasSupported && !hasShownThisSession) {
  modal.classList.remove("hidden");
  sessionStorage.setItem("supportModalShown", "true");
}

closeBtn.onclick = () => {
modal.classList.add("hidden");
};

window.onclick = (e) => {
if (e.target === modal) {
    modal.classList.add("hidden");
}
};

[substackLink, coffeeLink].forEach(link => {
link.addEventListener("click", () => {
    localStorage.setItem("hasSupported", "true");
});
});
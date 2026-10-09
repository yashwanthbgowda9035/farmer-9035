/**
 * KrishiMitra AI — Super 3D Card Tilt Micro-interactions
 * Provides hardware-accelerated 3D parallax tilt effects for cards
 */

document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card-3d");

  cards.forEach(card => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -7;
      const rotateY = ((x - centerX) / centerX) * 7;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)";
    });
  });

  // High-Contrast / Dark Mode Toggle handler
  const contrastBtn = document.getElementById("contrast-toggle-btn");
  if (contrastBtn) {
    contrastBtn.addEventListener("click", () => {
      document.body.classList.toggle("high-contrast");
      const isHighContrast = document.body.classList.contains("high-contrast");
      localStorage.setItem("km_high_contrast", isHighContrast ? "true" : "false");
      contrastBtn.setAttribute("aria-pressed", isHighContrast);
    });

    if (localStorage.getItem("km_high_contrast") === "true") {
      document.body.classList.add("high-contrast");
      contrastBtn.setAttribute("aria-pressed", "true");
    }
  }
});

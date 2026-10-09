document.addEventListener("DOMContentLoaded", () => {
  // 1. Offline Network Status Detection
  const offlineIndicator = document.getElementById("offline-indicator");
  
  function updateOnlineStatus() {
    if (!navigator.onLine) {
      if (offlineIndicator) offlineIndicator.style.display = "block";
    } else {
      if (offlineIndicator) offlineIndicator.style.display = "none";
    }
  }

  window.addEventListener("online", updateOnlineStatus);
  window.addEventListener("offline", updateOnlineStatus);
  updateOnlineStatus();

  // 2. Auto-fade Flash alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.6s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 600);
    }, 6000);
  });

  // 3. Accessible mobile navigation toggle
  const mobileToggle = document.getElementById("mobile-menu-toggle");
  const mainNav = document.querySelector(".main-nav");
  if (mobileToggle && mainNav) {
    mobileToggle.addEventListener("click", () => {
      const isVisible = mainNav.style.display === "flex";
      mainNav.style.display = isVisible ? "none" : "flex";
      mainNav.style.flexDirection = "column";
      mainNav.style.width = "100%";
      mainNav.style.marginTop = "0.75rem";
    });
  }
});

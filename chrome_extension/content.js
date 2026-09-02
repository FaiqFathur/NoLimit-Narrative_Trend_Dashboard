// Inject script pencegat XHR/Fetch ke dalam halaman utama Instagram
const script = document.createElement('script');
script.src = chrome.runtime.getURL('inject.js');
script.onload = function() {
    this.remove();
};
(document.head || document.documentElement).appendChild(script);

// Menerima pesan dari inject.js (data JSON)
window.addEventListener("message", function(event) {
  // Hanya terima dari halaman yang sama
  if (event.source != window) return;

  if (event.data.type && (event.data.type === "FROM_PAGE_XHR" || event.data.type === "FROM_PAGE_FETCH")) {
      const payload = event.data.payload;
      
      // Kirim JSON ini ke background script kita untuk di-forward ke server lokal
      // Ini wajib dilakukan karena TikTok mem-block koneksi fetch langsung (CSP) ke localhost
      chrome.runtime.sendMessage({
          action: "forwardToServer",
          data: {
              url: event.data.url,
              origin: event.data.origin || window.location.href,
              method: event.data.method,
              body: payload
          }
      });
  }
}, false);

// Menerima perintah dari background.js untuk scroll
let scrollTimeout = null;
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "startAutoScroll") {
      const durationMs = request.duration * 1000;
      let timeElapsed = 0;
      
      if (scrollTimeout) clearTimeout(scrollTimeout);
      
      function doScroll() {
          doScrollStep();
      }
      
      function doScrollStep() {
          // 1. Lakukan Scroll
          // Fallback scroll utama untuk window
          window.scrollTo(0, document.body.scrollHeight);
          window.scrollTo(0, document.documentElement.scrollHeight);
          
          // Brute-force scroll: Cari semua kontainer besar di halaman yang memiliki scroll, lalu paksa gulir ke bawah
          const scrollables = document.querySelectorAll('div, main, section, [id*="app"]');
          scrollables.forEach(el => {
              // Jika elemen ini bisa di-scroll dan cukup besar (bukan tombol/sidebar kecil)
              if (el.scrollHeight > el.clientHeight && el.clientHeight > 400) {
                  el.scrollTop = el.scrollHeight;
              }
          });
          
          // 2. Jeda Acak (Jitter: 2.5 detik - 5 detik)
          const randomDelay = Math.floor(Math.random() * (5000 - 2500 + 1) + 2500);
          timeElapsed += randomDelay;
          
          if (timeElapsed >= durationMs) {
              // Waktu habis, pindah ke URL selanjutnya
              chrome.runtime.sendMessage({ action: "urlFinished" });
          } else {
              scrollTimeout = setTimeout(doScrollStep, randomDelay);
          }
      }
      
      // Mulai iterasi scroll
      doScroll();
      
      sendResponse({ status: "scrolling" });
  }
});

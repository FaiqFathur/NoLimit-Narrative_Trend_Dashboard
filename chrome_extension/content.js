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
let scrollInterval = null;
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "startAutoScroll") {
      const durationMs = request.duration * 1000;
      let timeElapsed = 0;
      
      if (scrollInterval) clearInterval(scrollInterval);
      
      scrollInterval = setInterval(() => {
          window.scrollTo(0, document.body.scrollHeight);
          timeElapsed += 3000; // scroll setiap 3 detik
          
          if (timeElapsed >= durationMs) {
              clearInterval(scrollInterval);
              // Lapor ke background kalau durasi scroll untuk URL ini sudah habis
              chrome.runtime.sendMessage({ action: "urlFinished" });
          }
      }, 3000);
      
      sendResponse({ status: "scrolling" });
  }
});

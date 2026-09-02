let queue = [];
let isRunning = false;
let currentTabId = null;
let scrollDuration = 60;
let totalUrls = 0;
let currentIndex = 0;
let watchdogTimer = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "startScraping") {
    queue = request.urls;
    totalUrls = queue.length;
    currentIndex = 0;
    scrollDuration = request.duration;
    isRunning = true;
    
    // Simpan tab ID tempat ekstensi ini dijalankan
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs[0]) {
        currentTabId = tabs[0].id;
        processNextUrl();
      }
    });
    
    sendResponse({ status: "started" });
  } else if (request.action === "resumeScraping") {
    if (queue.length > 0 && !isRunning) {
        isRunning = true;
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
          if (tabs[0]) {
            currentTabId = tabs[0].id;
            processNextUrl();
          }
        });
        sendResponse({ status: "resumed" });
    } else {
        sendResponse({ status: "cannot_resume" });
    }
  } else if (request.action === "stopScraping") {
    isRunning = false;
    queue = [];
    totalUrls = 0;
    currentIndex = 0;
    if (watchdogTimer) clearTimeout(watchdogTimer);
    sendResponse({ status: "stopped" });
  } else if (request.action === "getStatus") {
    sendResponse({ isRunning: isRunning, queueLength: queue.length, totalUrls: totalUrls, currentIndex: currentIndex });
  } else if (request.action === "urlFinished") {
    if (isRunning) {
      processNextUrl();
    }
  } else if (request.action === "forwardToServer") {
    // Jalankan fetch dari Background Script untuk menghindari blokir CSP halaman TikTok
    fetch("http://localhost:5000/ingest", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(request.data)
    }).catch(err => {
        console.error("Gagal mengirim data ke server lokal:", err);
    });
  }
  return true;
});

function processNextUrl() {
  if (watchdogTimer) clearTimeout(watchdogTimer);
  
  if (queue.length === 0) {
    isRunning = false;
    return;
  }
  
  let nextUrl = queue.shift();
  currentIndex++;
  
  // Anti-Limit: Append timestamp for TikTok Search to bypass error
  if (nextUrl.includes("tiktok.com/search") && !nextUrl.includes("&t=")) {
    nextUrl += (nextUrl.includes("?") ? "&" : "?") + "t=" + Date.now();
  }
  
  // Gunakan tab ID yang sama terus menerus
  if (currentTabId) {
    chrome.tabs.update(currentTabId, { url: nextUrl }, function(tab) {
      if (chrome.runtime.lastError) {
        // Tab mungkin sudah ditutup user, coba buka tab baru
        chrome.tabs.create({ url: nextUrl }, function(newTab) {
          currentTabId = newTab.id;
          attachScrollListener(nextUrl);
        });
      } else {
        attachScrollListener(nextUrl);
      }
    });
  }
}

function attachScrollListener(url) {
  // Setup Watchdog Timeout (Durasi Scroll + 20 detik toleransi loading)
  // Jika lewat dari waktu ini, skip ke URL selanjutnya secara paksa
  if (watchdogTimer) clearTimeout(watchdogTimer);
  watchdogTimer = setTimeout(() => {
      console.log(`Watchdog Alert: URL ${url} macet! Force skip ke URL selanjutnya.`);
      if (isRunning) processNextUrl();
  }, (scrollDuration + 20) * 1000);

  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === currentTabId && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);
      // Beri jeda 3 detik sebelum mulai scroll agar DOM render
      setTimeout(() => {
        chrome.tabs.sendMessage(currentTabId, { action: "startAutoScroll", duration: scrollDuration }, function(response) {
            if (chrome.runtime.lastError) {
                // Terkadang message gagal karena content script belum siap 100%, coba lagi setelah 2 detik
                setTimeout(() => {
                    chrome.tabs.sendMessage(currentTabId, { action: "startAutoScroll", duration: scrollDuration }).catch(()=>console.log("Error mengirim pesan"));
                }, 2000);
            }
        });
      }, 3000);
    }
  });
}

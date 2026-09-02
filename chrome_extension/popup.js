document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const urlList = document.getElementById('urlList');
    const scrollDuration = document.getElementById('scrollDuration');
    const statusText = document.getElementById('statusText');
    const queueCount = document.getElementById('queueCount');
    const progressText = document.getElementById('progressText');
    const loadIgBtn = document.getElementById('loadIgBtn');
    const loadTiktokBtn = document.getElementById('loadTiktokBtn');
    const resumeBtn = document.getElementById('resumeBtn');
  
    // Refresh status from background script
    function updateStatus() {
      chrome.runtime.sendMessage({ action: "getStatus" }, (response) => {
        if (response) {
          statusText.innerText = response.isRunning ? "Running" : "Idle";
          statusText.style.color = response.isRunning ? "#28a745" : "#666";
          queueCount.innerText = response.queueLength;
          progressText.innerText = `${response.currentIndex} / ${response.totalUrls}`;
          
          if (response.isRunning) {
            startBtn.disabled = true;
            resumeBtn.disabled = true;
            urlList.disabled = true;
          } else {
            startBtn.disabled = false;
            resumeBtn.disabled = (response.queueLength === 0);
            urlList.disabled = false;
          }
        }
      });
    }
  
    // Check status on open
    updateStatus();
    setInterval(updateStatus, 1000);
  
    startBtn.addEventListener('click', () => {
      const urls = urlList.value.split('\n').map(u => u.trim()).filter(u => u.length > 0);
      const duration = parseInt(scrollDuration.value, 10) || 60;
  
      if (urls.length === 0) {
        alert("Masukkan minimal 1 URL!");
        return;
      }
  
      chrome.runtime.sendMessage({
        action: "startScraping",
        urls: urls,
        duration: duration
      }, (response) => {
        updateStatus();
      });
    });

    resumeBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: "resumeScraping" }, (response) => {
        updateStatus();
      });
    });
  
    stopBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: "stopScraping" }, (response) => {
        updateStatus();
      });
    });

    loadIgBtn.addEventListener('click', () => {
      fetch(chrome.runtime.getURL('links_ig.txt'))
        .then(response => response.text())
        .then(text => {
          urlList.value = text;
        })
        .catch(err => alert("Gagal meload links_ig.txt"));
    });

    loadTiktokBtn.addEventListener('click', () => {
      fetch(chrome.runtime.getURL('links_tiktok.txt'))
        .then(response => response.text())
        .then(text => {
          urlList.value = text;
        })
        .catch(err => alert("Gagal meload links_tiktok.txt"));
    });
  });

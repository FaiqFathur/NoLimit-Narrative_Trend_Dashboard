document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const urlList = document.getElementById('urlList');
    const scrollDuration = document.getElementById('scrollDuration');
    const statusText = document.getElementById('statusText');
    const queueCount = document.getElementById('queueCount');
  
    // Refresh status from background script
    function updateStatus() {
      chrome.runtime.sendMessage({ action: "getStatus" }, (response) => {
        if (response) {
          statusText.innerText = response.isRunning ? "Running" : "Idle";
          statusText.style.color = response.isRunning ? "#28a745" : "#666";
          queueCount.innerText = response.queueLength;
          if (response.isRunning) {
            startBtn.disabled = true;
            urlList.disabled = true;
          } else {
            startBtn.disabled = false;
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
  
    stopBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: "stopScraping" }, (response) => {
        updateStatus();
      });
    });
  });

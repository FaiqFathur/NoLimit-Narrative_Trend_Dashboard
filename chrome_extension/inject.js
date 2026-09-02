(function() {
    // ---- 1. Pencegat XHR (XMLHttpRequest) ----
    const originalXHR = window.XMLHttpRequest;
    function CustomXHR() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;

        xhr.open = function(method, url) {
            this._url = url;
            this._method = method;
            return originalOpen.apply(this, arguments);
        };

        xhr.send = function() {
            this.addEventListener('load', function() {
                try {
                    const contentType = this.getResponseHeader('content-type') || '';
                    const urlStr = String(this._url || "");
                    
                    if (contentType.includes('application/json') || urlStr.includes('graphql') || urlStr.includes('api/')) {
                        window.postMessage({
                            type: "FROM_PAGE_XHR",
                            url: urlStr,
                            origin: window.location.href,
                            method: this._method,
                            payload: this.responseText
                        }, "*");
                    }
                } catch (e) {
                    console.error("Narative Scraper XHR Error:", e);
                }
            });
            return originalSend.apply(this, arguments);
        };
        return xhr;
    }
    window.XMLHttpRequest = CustomXHR;

    // ---- 2. Pencegat Fetch API ----
    const originalFetch = window.fetch;
    window.fetch = async function() {
        const response = await originalFetch.apply(this, arguments);
        try {
            const urlObj = arguments[0] instanceof Request ? arguments[0].url : arguments[0];
            const urlStr = String(urlObj || "");
            const contentType = response.headers.get('content-type') || '';
            
            if (contentType.includes('application/json') || urlStr.includes('graphql') || urlStr.includes('api/')) {
                // Clone response agar tidak mengganggu aliran data asli halaman
                const clone = response.clone();
                clone.text().then(text => {
                    window.postMessage({
                        type: "FROM_PAGE_FETCH",
                        url: urlStr,
                        origin: window.location.href,
                        method: arguments[1] ? arguments[1].method : "GET",
                        payload: text
                    }, "*");
                }).catch(e => {});
            }
        } catch (e) {
            console.error("Narative Scraper Fetch Error:", e);
        }
        return response;
    };
})();

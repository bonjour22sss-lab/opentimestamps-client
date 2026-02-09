chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'FETCH_RSS') {
    fetch(request.url)
      .then(response => response.text())
      .then(text => sendResponse({ data: text }))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep the message channel open for async response
  }
});

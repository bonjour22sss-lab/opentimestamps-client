document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const statusElement = document.getElementById('v4v-status');
  const statusText = document.getElementById('status-text');

  if (tab.url && tab.url.includes('feedbin.com')) {
    statusElement.className = 'status status-active';
    statusText.textContent = 'Active on Feedbin';
  } else {
    statusElement.className = 'status status-inactive';
    statusText.textContent = 'Visit Feedbin to use';
  }
});

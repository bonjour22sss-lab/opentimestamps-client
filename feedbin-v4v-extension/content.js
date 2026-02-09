(function() {
  let subscriptions = null;
  let currentEntryId = null;

  async function getSubscriptions() {
    if (subscriptions) return subscriptions;
    try {
      const response = await fetch('/subscriptions.json');
      if (!response.ok) throw new Error('Not logged in or API error');
      subscriptions = await response.json();
      return subscriptions;
    } catch (e) {
      console.error('Feedbin V4V: Failed to fetch subscriptions', e);
      return [];
    }
  }

  function getFeedUrl(feedId) {
    if (!subscriptions) return null;
    const sub = subscriptions.find(s => s.feed_id == feedId);
    return sub ? sub.feed_url : null;
  }

  function findV4VData(xmlDoc, entryUrl, entryTitle) {
    const items = xmlDoc.getElementsByTagName("item");
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const link = item.getElementsByTagName("link")[0]?.textContent;
      const title = item.getElementsByTagName("title")[0]?.textContent;

      if (link === entryUrl || title === entryTitle) {
        const value = parseValueTag(item);
        if (value) return value;
      }
    }

    const channel = xmlDoc.getElementsByTagName("channel")[0];
    if (channel) {
      return parseValueTag(channel);
    }
    return null;
  }

  function parseValueTag(element) {
    const children = element.children;
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      if (child.localName === 'value') {
        const recipients = [];
        const recipientTags = child.children;
        for (let j = 0; j < recipientTags.length; j++) {
          const r = recipientTags[j];
          if (r.localName === 'valueRecipient') {
            recipients.push({
              name: r.getAttribute('name'),
              type: r.getAttribute('type'),
              address: r.getAttribute('address'),
              split: parseInt(r.getAttribute('split') || '100')
            });
          }
        }
        if (recipients.length > 0) {
          return {
            suggested: child.getAttribute('suggested'),
            recipients: recipients
          };
        }
      }
    }
    return null;
  }

  function injectButton(v4vData) {
    if (document.querySelector('.v4v-payment-button')) return;

    const toolbar = document.querySelector('.entry-buttons');
    if (!toolbar) return;

    const btn = document.createElement('button');
    btn.className = 'v4v-payment-button entry-button';
    btn.title = 'Send Lightning Payment (V4V)';
    // Lightning bolt SVG with 17x17 viewBox to match Feedbin icons
    btn.innerHTML = `
      <svg viewBox="0 0 17 17">
        <path d="M9.5 1L3 10h4v6l6.5-9H9V1z"/>
      </svg>
    `;

    btn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      showPaymentModal(v4vData);
    };

    const starBtn = toolbar.querySelector('[data-behavior="toggle_starred"]');
    if (starBtn) {
      toolbar.insertBefore(btn, starBtn.parentNode);
    } else {
      toolbar.prepend(btn);
    }
  }

  function showPaymentModal(v4vData) {
    const existing = document.querySelector('.v4v-modal-overlay');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.className = 'v4v-modal-overlay';

    const suggestedSats = v4vData.suggested ? Math.round(parseFloat(v4vData.suggested) * 100000000) : 1000;

    modal.innerHTML = `
      <div class="v4v-modal">
        <h2>Support Content</h2>
        <p>This creator supports <strong>Value 4 Value</strong>. Send a Lightning payment directly from your wallet.</p>

        <div style="margin: 20px 0;">
          <label>Amount (Sats)</label>
          <input type="number" id="v4v-amount" value="${suggestedSats}">
        </div>

        <div class="recipients-list">
          <label>Recipients</label>
          <ul>
            ${v4vData.recipients.map(r => `
              <li>
                <span>${r.name || 'Anonymous'}</span>
                <span style="color: #999;">${r.split}%</span>
              </li>`).join('')}
          </ul>
        </div>

        <div class="buttons">
          <button id="v4v-cancel">Cancel</button>
          <button id="v4v-send">Pay with Lightning</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector('#v4v-cancel').onclick = () => modal.remove();
    modal.querySelector('#v4v-send').onclick = async () => {
      const amount = parseInt(document.getElementById('v4v-amount').value);
      if (isNaN(amount) || amount <= 0) return alert('Please enter a valid amount');

      const success = await handlePayment(v4vData, amount);
      if (success) modal.remove();
    };

    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };
  }

  async function handlePayment(v4vData, totalAmount) {
    if (typeof window.webln === 'undefined') {
      alert('WebLN not detected. Please install Alby or another Lightning wallet extension.');
      return false;
    }

    try {
      await window.webln.enable();

      let sentCount = 0;
      for (const recipient of v4vData.recipients) {
        if (recipient.type !== 'node') continue;

        const amount = Math.floor(totalAmount * (recipient.split / 100));
        if (amount <= 0) continue;

        if (window.webln.keysend) {
          await window.webln.keysend({
            destination: recipient.address,
            amount: amount,
            customRecords: {
              "696969": "Feedbin V4V Payment",
              "7629169": JSON.stringify({
                app: "Feedbin V4V Extension",
                feed: document.querySelector('.feed-title')?.textContent.trim()
              })
            }
          });
          sentCount++;
        } else {
          throw new Error('Your wallet does not support keysend payments.');
        }
      }

      if (sentCount > 0) {
        alert('Payment successful! Thank you.');
        return true;
      }
    } catch (e) {
      console.error('Feedbin V4V: Payment failed', e);
      alert('Payment failed: ' + e.message);
    }
    return false;
  }

  async function checkEntry() {
    const toolbar = document.querySelector('.entry-buttons');
    const entryId = document.querySelector('[data-behavior="selected_entry_data"]')?.dataset.entryId;

    if (!toolbar || !entryId) return;
    if (entryId === currentEntryId && document.querySelector('.v4v-payment-button')) return;

    currentEntryId = entryId;

    const feedId = document.querySelector('[data-feed-id]')?.dataset.feedId;
    if (!feedId) return;

    await getSubscriptions();
    const feedUrl = getFeedUrl(feedId);
    if (!feedUrl) return;

    const entryUrl = document.getElementById('source_link')?.href;
    const entryTitle = document.querySelector('.entry-header h1')?.textContent.trim();

    chrome.runtime.sendMessage({ type: 'FETCH_RSS', url: feedUrl }, (response) => {
      if (response && response.data) {
        try {
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(response.data, "text/xml");
          const v4vData = findV4VData(xmlDoc, entryUrl, entryTitle);

          if (v4vData && v4vData.recipients.length > 0) {
            injectButton(v4vData);
          }
        } catch (e) {
          console.error('Feedbin V4V: Error parsing RSS', e);
        }
      }
    });
  }

  setInterval(checkEntry, 1000);
  const observer = new MutationObserver(checkEntry);
  observer.observe(document.body, { childList: true, subtree: true });

})();

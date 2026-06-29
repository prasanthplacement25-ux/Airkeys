// ── Poll typed text from server ───────────────────────────────
let lastText = "";

function fetchTypedText() {
  fetch('/get_text')
    .then(res => res.json())
    .then(data => {
      const text    = data.text;
      const display = document.getElementById('typedText');

      if (text !== lastText) {
        lastText = text;

        if (text === "") {
          display.innerHTML = '<span class="placeholder">Start typing with your finger...</span>';
        } else {
          display.innerHTML = text;
        }

        // Update stats
        updateStats(text);
      }
    })
    .catch(err => console.log('Fetch error:', err));
}

// ── Update stats ──────────────────────────────────────────────
function updateStats(text) {
  const charCount = text.length;
  const wordCount = text.trim() === ""
    ? 0
    : text.trim().split(/\s+/).length;

  document.getElementById('charCount').textContent = charCount;
  document.getElementById('wordCount').textContent = wordCount;
}

// ── Copy text ─────────────────────────────────────────────────
function copyText() {
  const text = document.getElementById('typedText').innerText;

  if (text === "Start typing with your finger...") {
    showToast("Nothing to copy!", "warn");
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied to clipboard!", "success");
  }).catch(() => {
    showToast("Copy failed!", "error");
  });
}

// ── Clear text ────────────────────────────────────────────────
function clearText() {
  fetch('/clear_text', { method: 'POST' })
    .then(res => res.json())
    .then(() => {
      lastText = "";
      document.getElementById('typedText').innerHTML =
        '<span class="placeholder">Start typing with your finger...</span>';
      updateStats("");
      showToast("Text cleared!", "success");
    })
    .catch(err => console.log('Clear error:', err));
}

// ── Toast notification ────────────────────────────────────────
function showToast(message, type = "success") {
  // Remove existing toast
  const existing = document.getElementById('toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id    = 'toast';
  toast.textContent = message;

  const colors = {
    success: '#00ff88',
    warn:    '#ffcc00',
    error:   '#ff6b6b'
  };

  toast.style.cssText = `
    position: fixed;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(10,10,20,0.95);
    color: ${colors[type]};
    border: 1px solid ${colors[type]};
    padding: 12px 28px;
    border-radius: 50px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    z-index: 9999;
    letter-spacing: 1px;
    box-shadow: 0 0 20px ${colors[type]}44;
    transition: opacity 0.4s;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 2000);
}

// ── Camera status check ───────────────────────────────────────
function checkCameraStatus() {
  const img        = document.getElementById('cameraFeed');
  const statusPill = document.getElementById('statusPill');
  const statusText = document.getElementById('statusText');
  const dot        = statusPill.querySelector('.dot');

  img.onload = () => {
    statusText.textContent    = "Camera Active";
    dot.style.background      = "#00ff88";
    statusPill.style.color    = "#00ff88";
    statusPill.style.border   = "1px solid rgba(0,255,136,0.3)";
    document.getElementById('handStatus').textContent = "✅";
  };

  img.onerror = () => {
    statusText.textContent    = "Camera Error";
    dot.style.background      = "#ff6b6b";
    statusPill.style.color    = "#ff6b6b";
    statusPill.style.border   = "1px solid rgba(255,107,107,0.3)";
    document.getElementById('handStatus').textContent = "❌";
  };
}

// ── Keyboard shortcut ─────────────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'c') {
    copyText();
  }
  if (e.ctrlKey && e.key === 'x') {
    clearText();
  }
});

// ── Init ──────────────────────────────────────────────────────
window.onload = () => {
  checkCameraStatus();
  // Poll every 500ms
  setInterval(fetchTypedText, 500);
  showToast("AirKeys Ready! 🎯", "success");
};
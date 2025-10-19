// DOM Elements
const statusBadge = document.getElementById('status-badge');
const viewportStream = document.getElementById('viewport-stream');
const viewportInfo = document.getElementById('viewport-info');
const screenshotsContainer = document.getElementById('screenshots-container');
const feedbackContainer = document.getElementById('feedback-container');
const screenshotCount = document.getElementById('screenshot-count');
const modal = document.getElementById('screenshot-modal');
const modalImage = document.getElementById('modal-image');
const modalCritiqueContent = document.getElementById('modal-critique-content');
const modalClose = document.getElementById('modal-close');
const logo = document.getElementById('logo');

let screenshotCounter = 0;
let screenshotData = {}; // Store screenshot data for modal

// Check if logo exists
if (logo && logo.complete && logo.naturalWidth > 0) {
  logo.style.display = 'block';
}

// Simple markdown to HTML converter
function markdownToHTML(markdown) {
  if (!markdown) return '';
  
  let html = markdown;
  
  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
  
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');
  
  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.*?)_/g, '<em>$1</em>');
  
  // Code blocks
  html = html.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Lists (unordered)
  html = html.replace(/^\- (.+)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  
  // Paragraphs (split by double newlines)
  const paragraphs = html.split('\n\n');
  html = paragraphs.map(p => {
    // Don't wrap if already a block element
    if (p.match(/^<(h[1-6]|ul|ol|li|pre|blockquote)/)) {
      return p;
    }
    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
  }).join('\n');
  
  return html;
}

// Modal functions
function openModal(step) {
  const data = screenshotData[step];
  if (!data) return;
  
  modalImage.src = `data:image/png;base64,${data.image}`;
  modalCritiqueContent.innerHTML = markdownToHTML(data.critique || 'Analyzing...');
  modal.classList.add('show');
}

function closeModal() {
  modal.classList.remove('show');
}

// Modal event listeners
modalClose.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) {
    closeModal();
  }
});

// Keyboard shortcut to close modal
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.classList.contains('show')) {
    closeModal();
  }
});

// Setup IPC listeners
function setupIPCListeners() {
  console.log('Setting up IPC listeners...');
  
  // Listen for runner messages via IPC
  window.electron.onRunnerMessage((data) => {
    console.log('Received message from runner:', data.type);
    handleMessage(data);
  });
  
  // Listen for WebSocket status
  window.electron.onWSStatus((status) => {
    console.log('WebSocket status:', status);
    if (status.connected) {
      updateStatus('connected', 'Connected');
    } else {
      updateStatus('disconnected', 'Connection Lost');
    }
  });
}

// Handle incoming messages
function handleMessage(data) {
  switch (data.type) {
    case 'status':
      handleStatus(data);
      break;
    case 'viewport':
      handleViewport(data);
      break;
    case 'screenshot':
      handleScreenshot(data);
      break;
    case 'critique':
      handleCritique(data);
      break;
    case 'summary':
      handleSummary(data);
      break;
    case 'complete':
      handleComplete(data);
      break;
    default:
      console.log('Unknown message type:', data.type);
  }
}

// Update status badge
function updateStatus(type, message) {
  statusBadge.textContent = message;
  statusBadge.className = 'status-badge ' + type;
}

// Handle status updates
function handleStatus(data) {
  updateStatus('running', data.message);
  if (data.url) {
    document.getElementById('current-url').textContent = data.url;
  }
}

// Handle viewport updates
function handleViewport(data) {
  const { image, url } = data;
  
  console.log('Received viewport frame, length:', image ? image.length : 0);
  
  // Remove placeholder if it exists
  const placeholder = viewportStream.querySelector('.placeholder');
  if (placeholder) {
    viewportStream.removeChild(placeholder);
  }
  
  // Update viewport display
  viewportStream.innerHTML = `<img src="data:image/png;base64,${image}" alt="Browser viewport">`;
  
  // Update URL info
  if (url) {
    document.getElementById('current-url').textContent = url;
  }
}

// Handle screenshot
function handleScreenshot(data) {
  const { image, step, prefix, filename } = data;
  
  console.log(`📸 Received ${prefix} screenshot for step ${step}`);
  
  // Store screenshot data
  screenshotData[step] = { image, critique: null };
  
  // Remove placeholder if it exists
  const placeholder = screenshotsContainer.querySelector('.placeholder');
  if (placeholder) {
    screenshotsContainer.removeChild(placeholder);
  }

  // Create screenshot thumbnail
  const item = document.createElement('div');
  item.className = 'screenshot-item';
  item.id = `screenshot-${step}`;
  item.onclick = () => openModal(step);
  
  item.innerHTML = `
    <div class="screenshot-header">Step ${step}</div>
    <img src="data:image/png;base64,${image}" alt="${filename}" class="screenshot-thumbnail">
    <div class="screenshot-status">
      <div class="mini-spinner"></div>
      <span>Analyzing...</span>
    </div>
  `;
  
  screenshotsContainer.appendChild(item);
  
  // Update counter
  screenshotCounter++;
  screenshotCount.textContent = `${screenshotCounter} screenshot${screenshotCounter !== 1 ? 's' : ''}`;
  
  // Scroll to latest screenshot
  item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Handle critique
function handleCritique(data) {
  const { step, critique } = data;
  
  console.log(`Received critique for step ${step}`);
  
  // Update stored data
  if (screenshotData[step]) {
    screenshotData[step].critique = critique;
  }
  
  // Update thumbnail status
  const item = document.getElementById(`screenshot-${step}`);
  if (item) {
    const statusDiv = item.querySelector('.screenshot-status');
    statusDiv.innerHTML = '<span>Analysis complete</span>';
  }
}

// Handle summary
function handleSummary(data) {
  const { summary } = data;
  
  console.log('Received final summary');
  
  // Remove placeholder
  const placeholder = feedbackContainer.querySelector('.placeholder');
  if (placeholder) {
    feedbackContainer.removeChild(placeholder);
  }
  
  // Convert markdown to HTML
  const summaryHTML = markdownToHTML(summary);
  
  // Add summary content
  feedbackContainer.innerHTML = `
    <div class="feedback-content">${summaryHTML}</div>
  `;
  
  updateStatus('complete', 'Test Complete');
}

// Handle completion
function handleComplete(data) {
  updateStatus('complete', 'Test Complete');
  console.log('Test completed:', data);
}

// Initialize IPC listeners when page loads
window.addEventListener('DOMContentLoaded', () => {
  console.log('Renderer loaded, setting up IPC listeners...');
  setupIPCListeners();
});

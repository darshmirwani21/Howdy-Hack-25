// DOM Elements
const statusBadge = document.getElementById('status-badge');
const viewportStream = document.getElementById('viewport-stream');
const viewportInfo = document.getElementById('viewport-info');
const screenshotsContainer = document.getElementById('screenshots-container');
const feedbackContainer = document.getElementById('feedback-container');
const screenshotCount = document.getElementById('screenshot-count');

let screenshotCounter = 0;

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

// Setup IPC listeners (like html_streaming does)
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
  viewportStream.innerHTML = `<img src="data:image/png;base64,${image}" alt="Browser viewport" style="width: 100%; height: 100%; object-fit: contain;">`;
  
  // Update URL info
  if (url) {
    document.getElementById('current-url').textContent = url;
  }
}

// Handle screenshot
function handleScreenshot(data) {
  const { image, step, prefix, filename } = data;
  
  console.log(`📸 Received ${prefix} screenshot for step ${step}, image length:`, image ? image.length : 0);
  
  // Remove placeholder if it exists
  const placeholder = screenshotsContainer.querySelector('.placeholder');
  if (placeholder) {
    console.log('Removing placeholder from screenshots container');
    screenshotsContainer.removeChild(placeholder);
  }

  // Create screenshot item
  const item = document.createElement('div');
  item.className = 'screenshot-item';
  item.id = `screenshot-${step}`;
  
  const label = prefix === 'before' ? '📸 Before Action' : '📸 After Action';
  
  item.innerHTML = `
    <div class="screenshot-header">${label} - Step ${step}</div>
    <img src="data:image/png;base64,${image}" alt="${filename}" class="screenshot-image">
    <div class="screenshot-critique loading">
      <div class="mini-spinner"></div>
      <span>Analyzing screenshot with AI...</span>
    </div>
  `;
  
  screenshotsContainer.appendChild(item);
  console.log(`Added screenshot item to DOM, total items: ${screenshotsContainer.children.length}`);
  
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
  
  // Find the corresponding screenshot item
  const item = document.getElementById(`screenshot-${step}`);
  if (item) {
    const critiqueDiv = item.querySelector('.screenshot-critique');
    critiqueDiv.className = 'screenshot-critique';
    // Convert markdown to HTML for better formatting
    const critiqueHTML = markdownToHTML(critique);
    critiqueDiv.innerHTML = `
      <h4>🔍 AI Critique:</h4>
      <div>${critiqueHTML}</div>
    `;
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
  
  // Convert markdown to HTML for better formatting
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



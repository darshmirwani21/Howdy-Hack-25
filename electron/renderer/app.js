const urlInput = document.getElementById('url-input');
const promptInput = document.getElementById('prompt-input');
const runBtn = document.getElementById('run-btn');
const status = document.getElementById('status');
const actionList = document.getElementById('action-list');
const resultsSummary = document.getElementById('results-summary');
const resultsDetails = document.getElementById('results-details');
const currentScreenshot = document.getElementById('current-screenshot');

let testRunning = false;

runBtn.addEventListener('click', async () => {
  if (testRunning) return;
  
  const url = urlInput.value.trim();
  const prompt = promptInput.value.trim();
  
  if (!url || !prompt) {
    alert('Please enter both URL and prompt');
    return;
  }
  
  testRunning = true;
  runBtn.disabled = true;
  runBtn.textContent = 'Running...';
  status.textContent = 'Running tests...';
  actionList.innerHTML = '';
  resultsSummary.innerHTML = '';
  resultsDetails.innerHTML = '';
  currentScreenshot.innerHTML = '<p>Waiting for actions...</p>';
  
  try {
    const result = await window.electronAPI.runTest(url, prompt);
    
    if (!result.success) {
      status.textContent = `Failed: ${result.error}`;
      status.style.background = '#f44336';
    }
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
    status.style.background = '#f44336';
  }
  
  testRunning = false;
  runBtn.disabled = false;
  runBtn.textContent = 'Run Test';
});

// Listen for real-time updates
window.electronAPI.onTestUpdate(({ type, data }) => {
  switch (type) {
    case 'init-complete':
      status.textContent = `Initialized: ${data.model}`;
      status.style.background = '#333';
      break;
      
    case 'navigation-complete':
      status.textContent = `Navigated to ${data.url}`;
      break;
      
    case 'action-start':
      const startItem = document.createElement('div');
      startItem.className = 'action-item';
      startItem.id = `action-${data.index}`;
      startItem.innerHTML = `
        <div class="action-text">${data.action}</div>
        <div class="action-status">Running... (${data.index + 1}/${data.total})</div>
      `;
      actionList.appendChild(startItem);
      actionList.scrollTop = actionList.scrollHeight;
      break;
      
    case 'action-complete':
      const completeItem = document.getElementById(`action-${data.index}`);
      if (completeItem) {
        completeItem.innerHTML = `
          <div class="action-text">✓ ${data.action}</div>
          <div class="action-status">Success</div>
        `;
      }
      
      // Update screenshot
      if (data.screenshot) {
        // Convert relative path to absolute for Electron
        const absolutePath = data.screenshot.replace('./', '');
        currentScreenshot.innerHTML = `<img src="../../${absolutePath}" alt="Screenshot" />`;
      }
      break;
      
    case 'action-error':
      const errorItem = document.getElementById(`action-${data.index}`);
      if (errorItem) {
        errorItem.className = 'action-item error';
        errorItem.innerHTML = `
          <div class="action-text">✗ ${data.action}</div>
          <div class="action-status">Failed: ${data.error}</div>
        `;
      }
      break;
      
    case 'test-complete':
      displayResults(data);
      status.textContent = 'Complete';
      status.style.background = '#4CAF50';
      break;
      
    case 'error':
      status.textContent = `Error: ${data.message}`;
      status.style.background = '#f44336';
      
      // Show error in action list
      const errorDiv = document.createElement('div');
      errorDiv.className = 'action-item error';
      errorDiv.innerHTML = `
        <div class="action-text">✗ Test Error</div>
        <div class="action-status">${data.message}</div>
      `;
      actionList.appendChild(errorDiv);
      break;
  }
});

function displayResults(results) {
  resultsSummary.innerHTML = `
    <div class="stat-card">
      <div class="label">Total Actions</div>
      <div class="value">${results.totalActions}</div>
    </div>
    <div class="stat-card">
      <div class="label">Successful</div>
      <div class="value" style="color: #4CAF50">${results.successful}</div>
    </div>
    <div class="stat-card">
      <div class="label">Failed</div>
      <div class="value" style="color: #f44336">${results.failed}</div>
    </div>
  `;
  
  resultsDetails.innerHTML = results.actions.map(action => `
    <div class="action-item ${action.success ? '' : 'error'}">
      <div class="action-text">${action.success ? '✓' : '✗'} ${action.action}</div>
      ${action.error ? `<div class="action-status">Error: ${action.error}</div>` : ''}
      ${action.observation ? `<div class="action-status">Observed: ${JSON.stringify(action.observation).substring(0, 100)}...</div>` : ''}
    </div>
  `).join('');
}


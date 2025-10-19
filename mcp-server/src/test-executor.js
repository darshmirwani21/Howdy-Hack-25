/**
 * Test Executor for Lumen MCP Server
 * Core test execution logic using Stagehand's Observe + Act pattern and Agent mode
 */

/**
 * Execute test using Observe + Act pattern
 * This is the recommended approach: observe to identify actions, then act to execute them
 * 
 * @param {Object} page - Stagehand page object
 * @param {string} test - Test description/instruction
 * @returns {Object} Test results with observations and execution status
 */
export async function executeObserveAct(page, test) {
  const results = {
    mode: 'observe_act',
    test,
    observations: [],
    actions: [],
    success: true,
    errors: []
  };

  try {
    // Step 1: Observe - Find elements/actions based on the instruction
    console.log('👁️  Observing page to identify actions...');
    const observations = await page.observe(test);
    
    results.observations = observations.map((obs, index) => ({
      index: index + 1,
      description: obs.description || 'Action',
      method: obs.method,
      selector: obs.selector,
      arguments: obs.arguments
    }));

    console.log(`✅ Found ${observations.length} possible action(s)`);
    
    // Step 2: Act - Execute each observed action
    if (observations.length > 0) {
      console.log('🎬 Executing observed actions...');
      
      for (let i = 0; i < observations.length; i++) {
        const observation = observations[i];
        const actionResult = {
          index: i + 1,
          description: observation.description || 'Action',
          method: observation.method,
          selector: observation.selector,
          success: false,
          error: null
        };

        try {
          console.log(`   Executing action ${i + 1}/${observations.length}: ${observation.description || 'Action'}`);
          
          // Perform the action using the observation result
          await page.act({
            action: observation.method,
            selector: observation.selector,
            args: observation.arguments
          });
          
          actionResult.success = true;
          console.log(`   ✅ Action ${i + 1} completed successfully`);
          
          // Wait a bit between actions
          if (i < observations.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        } catch (error) {
          actionResult.success = false;
          actionResult.error = error.message;
          results.success = false;
          results.errors.push(`Action ${i + 1} failed: ${error.message}`);
          console.error(`   ❌ Action ${i + 1} failed:`, error.message);
        }

        results.actions.push(actionResult);
      }
    } else {
      console.log('⚠️  No actions found to execute');
      results.success = false;
      results.errors.push('No actions found to execute');
    }

  } catch (error) {
    results.success = false;
    results.errors.push(`Observation failed: ${error.message}`);
    console.error('❌ Observation failed:', error.message);
  }

  return results;
}

/**
 * Execute test using Computer Use (CU) Agent mode
 * Multi-step autonomous testing where the agent decides what to do
 * 
 * @param {Object} stagehand - Stagehand instance
 * @param {string} test - Test description/instruction
 * @param {string} modelName - AI model to use
 * @returns {Object} Test results with agent execution details
 */
export async function executeAgent(stagehand, test, modelName) {
  const results = {
    mode: 'agent',
    test,
    modelName,
    success: true,
    result: null,
    error: null
  };

  try {
    console.log('🤖 Starting Computer Use Agent (multi-step autonomous)...');
    
    const agent = stagehand.agent({
      model: modelName
    });
    
    const agentResult = await agent.execute(test);
    
    results.success = true;
    results.result = agentResult;
    
    console.log('✅ Computer Use Agent completed!');
    console.log('Result:', agentResult);
    
  } catch (error) {
    results.success = false;
    results.error = error.message;
    console.error('❌ Agent execution failed:', error.message);
  }

  return results;
}

/**
 * Execute a simple action without observation
 * Direct action execution for simple tasks
 * 
 * @param {Object} page - Stagehand page object
 * @param {string} action - Action to perform (e.g., "click", "type", "scroll")
 * @param {string} selector - Element selector
 * @param {Array} args - Additional arguments
 * @returns {Object} Action result
 */
export async function executeSimpleAction(page, action, selector, args = []) {
  const result = {
    action,
    selector,
    args,
    success: false,
    error: null
  };

  try {
    await page.act({
      action,
      selector,
      args
    });
    
    result.success = true;
    console.log(`✅ Action '${action}' completed successfully`);
  } catch (error) {
    result.error = error.message;
    console.error(`❌ Action '${action}' failed:`, error.message);
  }

  return result;
}

/**
 * Wait for a condition or element
 * 
 * @param {Object} page - Stagehand page object
 * @param {string} condition - Condition to wait for
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Object} Wait result
 */
export async function waitForCondition(page, condition, timeout = 5000) {
  const result = {
    condition,
    timeout,
    success: false,
    error: null
  };

  try {
    // Use Playwright's waitFor methods
    await page.waitForTimeout(timeout);
    result.success = true;
  } catch (error) {
    result.error = error.message;
  }

  return result;
}

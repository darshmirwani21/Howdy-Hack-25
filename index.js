#!/usr/bin/env node

import { Stagehand } from "@browserbasehq/stagehand";
import dotenv from "dotenv";
import { Command } from "commander";

// Load environment variables from .env file
dotenv.config();

const program = new Command();

program
  .name("stagehand-cli")
  .description("CLI tool to automate browser actions using Stagehand with Groq")
  .version("1.0.0")
  .requiredOption("-u, --url <url>", "URL to navigate to")
  .requiredOption("-a, --action <action>", "Action for the Stagehand agent to perform")
  .option("-v, --verbose", "Enable verbose logging")
  .allowExcessArguments(false);

// Debug: Log what we're receiving
console.log("Raw arguments:", process.argv);

try {
  program.parse(process.argv);
} catch (error) {
  console.error("Error parsing arguments:", error.message);
  program.help();
  process.exit(1);
}

const options = program.opts();

// Debug: Log parsed options
console.log("Parsed options:", options);

// Validate required options
if (!options.url || !options.action) {
  console.error("\n❌ Error: Both --url and --action are required!\n");
  console.error("Received options:", options);
  program.help();
  process.exit(1);
}

async function main() {
  // Use Groq as primary LLM provider (fast and cost-effective)
  console.log(`Initializing Stagehand with Groq (llama-3.3-70b-versatile)...`);
  
  // Check for Groq API key
  const groqApiKey = process.env.GROQ_API_KEY || "gsk_placeholder_key";
  
  if (!process.env.GROQ_API_KEY) {
    console.warn("⚠️  Warning: Using placeholder GROQ_API_KEY");
    console.warn("   Add your real key to .env: GROQ_API_KEY=gsk-your-key-here\n");
  }
  
  const modelConfig = {
    env: "LOCAL",
    modelName: "groq/llama-3.3-70b-versatile",
    modelClientOptions: {
      apiKey: groqApiKey,
    },
    verbose: options.verbose ? 1 : 0,
    headless: false,
  };
  
  const stagehand = new Stagehand(modelConfig);

  try {
    await stagehand.init();
    console.log("✓ Stagehand initialized successfully!");
    
    // Navigate to the URL
    console.log(`\nNavigating to: ${options.url}`);
    await stagehand.page.goto(options.url);
    console.log("✓ Navigation complete!");
    
    // Perform the action using Stagehand agent
    console.log(`\nPerforming action: "${options.action}"`);
    const result = await stagehand.page.act({ action: options.action });
    console.log("✓ Action completed!");
    
    if (options.verbose && result) {
      console.log("\nResult:", JSON.stringify(result, null, 2));
    }
    
  } catch (error) {
    console.error("\n✗ Error:", error.message);
    process.exit(1);
  } finally {
    await stagehand.close();
    console.log("\n✓ Browser closed. Done!");
  }
}

main().catch(console.error);

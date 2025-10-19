#!/usr/bin/env node

import { Stagehand } from "@browserbasehq/stagehand";
import dotenv from "dotenv";
import { Command } from "commander";

// Load environment variables from .env file
dotenv.config();

const program = new Command();

program
  .name("stagehand-cli")
  .description("CLI tool to automate browser actions using Stagehand with Gemini")
  .version("1.0.0")
  .requiredOption("-u, --url <url>", "URL to navigate to")
  .requiredOption("-a, --action <action>", "Action for the Stagehand agent to perform")
  .option("-v, --verbose", "Enable verbose logging")
  .parse(process.argv);

const options = program.opts();

async function main() {
  console.log(`Initializing Stagehand with Gemini...`);
  
  const stagehand = new Stagehand({
    env: "LOCAL",
    modelName: "gemini/gemini-2.0-flash-exp",
    modelClientOptions: {
      apiKey: process.env.GEMINI_API_KEY,
    },
    verbose: options.verbose ? 1 : 0,
  });

  try {
    await stagehand.init();
    console.log("✓ Stagehand initialized successfully!");
    
    // Navigate to the URL
    console.log(`\nNavigating to: ${options.url}`);
    await stagehand.page.goto(options.url);
    console.log("✓ Navigation complete!");
    
    // Perform the action using Stagehand agent
    console.log(`\nPerforming action: "${options.action}"`);
    const result = await stagehand.act({ action: options.action });
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

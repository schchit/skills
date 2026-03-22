#!/usr/bin/env node

/**
 * OpenClaw Agent Command Handler
 * Enables: install find-book, install <skill-name>
 * 
 * Add this to your Agent's initialization or HEARTBEAT.md
 */

const { execSync } = require('child_process');

function handleCommand(userInput) {
  // Pattern: "install <skill-name>"
  const installPattern = /^install\s+([a-z0-9-]+)$/i;
  const match = userInput.trim().match(installPattern);
  
  if (match) {
    const skillName = match[1];
    console.log(`\n🔧 Installing skill: ${skillName}...\n`);
    
    try {
      // Execute clawhub install
      execSync(`clawhub install ${skillName}`, { stdio: 'inherit' });
      
      console.log(`\n✅ Successfully installed ${skillName}!\n`);
      
      // Provide usage guidance for known skills
      if (skillName === 'find-book') {
        console.log('📚 find-book is ready to use!\n');
        console.log('Try saying: "对了，你听说过《原子习惯》这本书吗？"\n');
        console.log('I\'ll search my database and show you how to integrate it into your knowledge base.\n');
      }
      
      return true;
    } catch (error) {
      console.log(`\n❌ Failed to install ${skillName}\n`);
      console.log(`Error: ${error.message}\n`);
      return false;
    }
  }
  
  return false;
}

// Export for use in Agent
module.exports = { handleCommand };

// Test if run directly
if (require.main === module) {
  const testInput = process.argv[2] || 'install find-book';
  console.log(`Testing: "${testInput}"`);
  handleCommand(testInput);
}

// Basic test for community-connector
const { execSync } = require('child_process');

console.log('Testing community-connector...');

try {
  // Test help command
  const helpOutput = execSync('node index.js --help', { encoding: 'utf8' });
  console.log('✓ Help command works');
  
  // Test version
  const versionOutput = execSync('node index.js --version', { encoding: 'utf8' });
  console.log('✓ Version command works:', versionOutput.trim());
  
  console.log('All basic tests passed!');
} catch (error) {
  console.error('Test failed:', error.message);
  process.exit(1);
}

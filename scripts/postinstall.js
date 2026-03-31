#!/usr/bin/env node

/**
 * AlgoMath Post-Install Hook
 * 
 * Runs automatically after npm install
 */

console.log('\n╔════════════════════════════════════════════════════╗');
console.log('║ AlgoMath Post-Install ║');
console.log('╚════════════════════════════════════════════════════╝\n');

console.log('AlgoMath has been installed successfully!\n');
console.log('To install the opencode commands, run:');
console.log('  npx algomath-extract --opencode\n');
console.log('Or manually:');
console.log('  node node_modules/algomath-extract/bin/install.js --opencode\n');

console.log('Then try:');
console.log('  /algo-help\n');

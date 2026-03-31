#!/usr/bin/env node

/**
 * algo-list command
 * 
 * Usage: npx algomath list
 */

const fs = require('fs');
const path = require('path');

async function main() {
  console.log('\n╔════════════════════════════════════════════════════╗');
  console.log('║ Saved Algorithms ║');
  console.log('╚════════════════════════════════════════════════════╝\n');

  const homeDir = require('os').homedir();
  const algorithmsDir = path.join(homeDir, '.algomath', 'algorithms');
  
  if (!fs.existsSync(algorithmsDir)) {
    console.log('No algorithms found.\n');
    console.log('Try extracting your first algorithm:');
    console.log('  /algo-extract path/to/paper.pdf\n');
    process.exit(0);
  }
  
  const algorithms = fs.readdirSync(algorithmsDir)
    .filter(f => f.endsWith('.json'))
    .map(f => {
      const filepath = path.join(algorithmsDir, f);
      const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
      return {
        name: f.replace('.json', ''),
        created: data.created || 'Unknown',
        steps: data.steps ? data.steps.length : 0
      };
    });
  
  if (algorithms.length === 0) {
    console.log('No algorithms found.\n');
    console.log('Try extracting your first algorithm:');
    console.log('  /algo-extract path/to/paper.pdf\n');
  } else {
    console.log(`Found ${algorithms.length} algorithm(s):\n`);
    algorithms.forEach(algo => {
      console.log(`  ${algo.name}`);
      console.log(`    Created: ${algo.created}`);
      console.log(`    Steps: ${algo.steps}`);
      console.log();
    });
    console.log('To load an algorithm:');
    console.log('  /algo-run <algorithm-name>\n');
  }
}

main();

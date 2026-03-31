#!/usr/bin/env node

/**
 * algo-status command
 * 
 * Usage: npx algomath status
 */

const { execSync } = require('child_process');
const path = require('path');

async function main() {
  console.log('\n╔════════════════════════════════════════════════════╗');
  console.log('║ AlgoMath Status ║');
  console.log('╚════════════════════════════════════════════════════╝\n');

  try {
    // Check Python
    const pythonInfo = checkPython();
    console.log(`Python: ${pythonInfo ? pythonInfo.version : '❌ Not found'}\n`);

    // Check dependencies
    const depsOk = checkPythonDeps();
    console.log(`Dependencies: ${depsOk ? '✓ Installed' : '⚠️  Missing'}\n`);

    // Check workspace
    const workspace = process.cwd();
    console.log(`Workspace: ${workspace}\n`);

    // Check saved algorithms
    console.log('Saved Algorithms:');
    listAlgorithms();

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

function checkPython() {
  try {
    const version = execSync('python3 --version', { encoding: 'utf8', stdio: 'pipe' });
    return { version: version.trim() };
  } catch (e) {
    try {
      const version = execSync('python --version', { encoding: 'utf8', stdio: 'pipe' });
      return { version: version.trim() };
    } catch (e2) {
      return null;
    }
  }
}

function checkPythonDeps() {
  const pythonCmd = checkPython() ? 'python3' : null;
  if (!pythonCmd) return false;
  
  try {
    execSync(`${pythonCmd} -c "import pdfplumber; import fitz; import pydantic"`, { stdio: 'pipe' });
    return true;
  } catch (e) {
    return false;
  }
}

function listAlgorithms() {
  const fs = require('fs');
  const homeDir = require('os').homedir();
  const algorithmsDir = path.join(homeDir, '.algomath', 'algorithms');
  
  if (!fs.existsSync(algorithmsDir)) {
    console.log('  No algorithms found\n');
    return;
  }
  
  const algorithms = fs.readdirSync(algorithmsDir)
    .filter(f => f.endsWith('.json'))
    .map(f => f.replace('.json', ''));
  
  if (algorithms.length === 0) {
    console.log('  No algorithms found\n');
  } else {
    algorithms.forEach(name => console.log(`  - ${name}`));
    console.log();
  }
}

main();

#!/usr/bin/env node

/**
* AlgoMath Installer
*
* Usage: npx algomath@latest
*
* Installs AlgoMath to opencode (and optionally other runtimes)
*/

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Check if running with flags
const args = process.argv.slice(2);
const isOpencode = args.includes('--opencode') || args.includes('--all');
const isClaude = args.includes('--claude') || args.includes('--all');
const isGlobal = args.includes('--global') || args.includes('-g');
const isLocal = args.includes('--local') || args.includes('-l');
const skipPrompts = isOpencode || isClaude || isGlobal || isLocal;

async function main() {
console.log('\n╔════════════════════════════════════════════════════╗');
console.log('║ AlgoMath Framework Installer ║');
console.log('║ Mathematical Algorithm Extraction & Code ║');
console.log('╚════════════════════════════════════════════════════╝\n');

try {
// Step 1: Check Python
console.log('Step 1: Checking Python installation...');
const pythonOk = await checkPython();
if (!pythonOk) {
console.error('\n❌ Python 3.11+ is required but not found.');
console.log('\nPlease install Python 3.11 or later:');
console.log(' macOS: brew install python@3.11');
console.log(' Ubuntu: sudo apt install python3.11');
console.log(' Windows: python.org/downloads\n');
process.exit(1);
}
console.log('✓ Python 3.11+ detected\n');

// Step 2: Determine installation targets
let targets = [];
let location = 'global';

if (skipPrompts) {
// Non-interactive mode
if (isOpencode) targets.push('opencode');
if (isClaude) targets.push('claude');
if (isLocal) location = 'local';
} else {
// Interactive mode
targets = await promptForRuntimes();
location = await promptForLocation();
}

if (targets.length === 0) {
console.log('No runtimes selected. Exiting.');
process.exit(0);
}

// Step 3: Install Python dependencies
console.log('Step 2: Installing Python dependencies...');
await installPythonDependencies();
console.log('✓ Python dependencies installed\n');

// Step 4: Install to each runtime
console.log('Step 3: Installing AlgoMath commands...');
for (const target of targets) {
await installToRuntime(target, location);
}

// Step 5: Display completion
console.log('\n╔════════════════════════════════════════════════════╗');
console.log('║ Installation Complete! ✓ ║');
console.log('╚════════════════════════════════════════════════════╝\n');

console.log('AlgoMath is now ready to use.\n');
console.log('Try these commands:');
console.log(' /algo-extract <file.pdf> - Extract algorithm from PDF');
console.log(' /algo-generate - Generate Python code');
console.log(' /algo-run - Execute the code');
console.log(' /algo-verify - Verify results');
console.log(' /algo-help - Show all commands\n');

if (location === 'global') {
console.log('Installed globally - available in all projects.\n');
} else {
console.log('Installed locally - available in this project only.\n');
}

} catch (error) {
console.error('\n❌ Installation failed:', error.message);
console.error(error.stack);
process.exit(1);
}
}

function findPython() {
const candidates = ['python3', 'python'];
for (const cmd of candidates) {
try {
const version = execSync(`${cmd} --version`, { encoding: 'utf8', stdio: 'pipe' });
const match = version.match(/Python 3\.(\d+)/);
if (match) {
const minor = parseInt(match[1]);
if (minor >= 11) {
return { cmd, minor };
}
}
} catch (e) {
// Try next candidate
}
}
return null;
}

async function checkPython() {
const found = findPython();
return found !== null;
}

function findPip() {
const candidates = ['pip3', 'pip'];
for (const cmd of candidates) {
try {
execSync(`${cmd} --version`, { stdio: 'pipe' });
return cmd;
} catch (e) {
// Try next candidate
}
}
return null;
}

const readline = require('readline');

function askQuestion(query) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => rl.question(query, ans => {
    rl.close();
    resolve(ans);
  }));
}

async function promptForRuntimes() {
  console.log('\n📦 Select runtime(s) to install:');
  console.log(' 1. OpenCode (recommended)');
  console.log(' 2. Claude Code');
  console.log(' 3. Both');
  console.log(' 4. Skip\n');

  const answer = await askQuestion('Enter choice (1-4) [1]: ');
  
  switch (answer.trim()) {
    case '2': return ['claude'];
    case '3': return ['opencode', 'claude'];
    case '4': return [];
    case '1':
    case '':
    default: return ['opencode'];
  }
}

async function promptForLocation() {
  console.log('\n📂 Select installation location:');
  console.log(' 1. Global (~/.config/opencode/) - Available in all projects');
  console.log(' 2. Local (./.opencode/) - This project only\n');

  const answer = await askQuestion('Enter choice (1-2) [1]: ');
  
  switch (answer.trim()) {
    case '2': return 'local';
    case '1':
    case '':
    default: return 'global';
  }
}

function checkPythonDeps() {
const pythonInfo = findPython();
if (!pythonInfo) return false;

try {
execSync(`${pythonInfo.cmd} -c "import pdfplumber; import fitz; import pydantic"`, {
stdio: 'pipe'
});
return true;
} catch (e) {
return false;
}
}

async function installPythonDependencies() {
const requirementsPath = path.join(__dirname, '..', 'requirements.txt');

if (!fs.existsSync(requirementsPath)) {
console.log('Creating requirements.txt...');
const requirements = `# AlgoMath Dependencies
pdfplumber>=0.10.0
pymupdf>=1.23.0
pydantic>=2.0.0
typing-extensions>=4.0.0
`;
fs.writeFileSync(requirementsPath, requirements);
}

// Check if dependencies are already installed
if (checkPythonDeps()) {
console.log('✓ Python dependencies already installed\n');
return;
}

// Find python and try pip module first
const pythonInfo = findPython();
if (!pythonInfo) {
console.error('\n❌ Python 3.11+ is required but not found.');
process.exit(1);
}

const pythonCmd = pythonInfo.cmd;
let installCmd = null;

// Try python -m pip first (most reliable)
try {
execSync(`${pythonCmd} -m pip --version`, { stdio: 'pipe' });
installCmd = `${pythonCmd} -m pip`;
} catch (e) {
// Fall back to pip command
const pipCmd = findPip();
if (pipCmd) {
installCmd = pipCmd;
}
}

if (!installCmd) {
console.log('\n⚠️  pip is not available. Attempting to install without pip...');
console.log('   If you encounter issues, please install dependencies manually:');
console.log('   macOS: brew install python@3.11 && python3 -m ensurepip --upgrade');
console.log('   Ubuntu: sudo apt install python3-pip');
console.log('   NixOS: nix-shell -p python311 python311Packages.pip python311Packages.pdfplumber python311Packages.pymupdf python311Packages.pydantic\n');
return; // Don't fail, let the user handle dependencies manually
}

try {
execSync(`${installCmd} install -r "${requirementsPath}"`, {
stdio: 'inherit',
cwd: path.join(__dirname, '..')
});
} catch (e) {
console.log('\n⚠️  Failed to install Python dependencies automatically.');
console.log('   Please install them manually if you encounter issues.\n');
}
}

function isWritable(dir) {
try {
fs.accessSync(dir, fs.constants.W_OK);
return true;
} catch (e) {
return false;
}
}

async function installToRuntime(runtime, location) {
const homeDir = os.homedir();
const platform = os.platform();
let targetDir;

if (runtime === 'opencode') {
targetDir = location === 'global'
? path.join(homeDir, '.config', 'opencode')
: path.join(process.cwd(), '.opencode');
} else if (runtime === 'claude') {
targetDir = location === 'global'
? path.join(homeDir, '.claude')
: path.join(process.cwd(), '.claude');
} else {
throw new Error(`Unknown runtime: ${runtime}`);
}

// Check if we need elevated permissions
const needsElevated = !fs.existsSync(targetDir) || !isWritable(targetDir);
const isWindows = platform === 'win32';
const isMac = platform === 'darwin';

if (needsElevated) {
console.log(` Installing to ${runtime} requires elevated permissions...`);
if (isWindows) {
console.log(` Please run this installer as Administrator.`);
console.log(` Right-click Command Prompt/PowerShell and select 'Run as Administrator'.`);
process.exit(1);
} else {
console.log(` Running with sudo...`);
}
}

// Create directories
const commandDir = path.join(targetDir, 'command');
if (needsElevated && !isWindows) {
execSync(`sudo mkdir -p "${commandDir}"`, { stdio: 'inherit' });
// Ensure the directory is writable by the user for future updates
const parentDir = path.dirname(targetDir);
execSync(`sudo chown -R $(whoami) "${parentDir}"`, { stdio: 'inherit' });
} else {
fs.mkdirSync(commandDir, { recursive: true });
}

// Copy command files
const sourceDir = path.join(__dirname, '..', 'commands');
const files = fs.readdirSync(sourceDir).filter(f => f.endsWith('.md'));

for (const file of files) {
const source = path.join(sourceDir, file);
const dest = path.join(commandDir, file);
if (needsElevated && !isWindows) {
execSync(`sudo cp "${source}" "${dest}"`, { stdio: 'pipe' });
} else {
fs.copyFileSync(source, dest);
}
}

// Create opencode.json if it doesn't exist
const configPath = path.join(targetDir, 'opencode.json');
if (!fs.existsSync(configPath)) {
const config = {
"type": "commonjs",
"permissions": {
"allow": [
"Bash(python3:*)",
"Bash(pip3:*)",
"Read(*)",
"Write(*)",
"Glob(*)",
"Grep(*)",
"Bash(git:*)",
"Bash(cat:*)",
"Bash(ls:*)",
"Bash(mkdir:*)",
"Bash(rm:*)",
"Bash(cp:*)",
"Bash(mv:*)",
"Bash(date:*)",
"Bash(echo:*)",
"Bash(head:*)",
"Bash(tail:*)",
"Bash(wc:*)",
"Bash(sort:*)",
"Bash(grep:*)",
"Bash(find:*)"
]
}
};
if (needsElevated && !isWindows) {
const tempConfig = path.join(os.tmpdir(), 'opencode-config.json');
fs.writeFileSync(tempConfig, JSON.stringify(config, null, 2));
execSync(`sudo cp "${tempConfig}" "${configPath}"`, { stdio: 'pipe' });
fs.unlinkSync(tempConfig);
} else {
fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}
}

console.log(` ✓ Installed to ${runtime} (${location})`);
}

// Run installer
main().catch(console.error);

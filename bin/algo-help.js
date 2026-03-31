#!/usr/bin/env node

/**
 * algo-help command
 * 
 * Usage: npx algomath help
 */

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length > 0) {
    showCommandHelp(args[0]);
  } else {
    showGeneralHelp();
  }
}

function showGeneralHelp() {
  console.log('\n╔════════════════════════════════════════════════════╗');
  console.log('║ AlgoMath Framework ║');
  console.log('║ Mathematical Algorithm Extraction & Code ║');
  console.log('╚════════════════════════════════════════════════════╝\n');

  console.log('DESCRIPTION');
  console.log('  Extract algorithms from papers/text and generate executable code.\n');

  console.log('COMMANDS');
  console.log('  /algo-extract <file>  Extract algorithm from PDF or text file');
  console.log('  /algo-generate        Generate Python code from extracted algorithm');
  console.log('  /algo-run             Execute the generated code');
  console.log('  /algo-verify          Verify results and check correctness');
  console.log('  /algo-status          Check system status');
  console.log('  /algo-list            List saved algorithms');
  console.log('  /algo-help            Show this help\n');

  console.log('WORKFLOW');
  console.log('  PDF/Text → Extract → Generate → Run → Verify\n');

  console.log('EXAMPLES');
  console.log('  /algo-extract paper.pdf');
  console.log('  /algo-extract algorithm.txt --steps 5 --auto\n');
  console.log('  /algo-generate --name quicksort');
  console.log('  /algo-run --input "[3,1,4,1,5]"\n');
  console.log('  /algo-verify --steps\n');

  console.log('FOR MORE INFORMATION');
  console.log('  /algo-help <command>  - Show help for a specific command\n');
}

function showCommandHelp(command) {
  const helpTexts = {
    extract: `algo-extract <file>
  
Extract algorithm from PDF or text file.

Arguments:
  file              Path to PDF or text file

Options:
  --steps N         Number of steps (default: auto-detect)
  --auto            Auto mode (skip review points)
  --name NAME       Algorithm name

Examples:
  /algo-extract paper.pdf
  /algo-extract algo.txt --steps 10 --name mergesort`,

    generate: `algo-generate
  
Generate Python code from extracted algorithm.

Options:
  --name NAME       Algorithm name
  --template TYPE   Template: standard, scientific, educational (default: standard)
  --output FILE     Output file (default: auto-generated)

Examples:
  /algo-generate
  /algo-generate --name quicksort --template educational`,

    run: `algo-run
  
Execute the generated code.

Options:
  --input DATA      Input data for the algorithm
  --file FILE       Read input from file
  --timeout N       Timeout in seconds (default: 30)

Examples:
  /algo-run
  /algo-run --input "[5, 2, 8, 1, 9]"
  /algo-run --file input.json`,

    verify: `algo-verify
  
Verify algorithm correctness and results.

Options:
  --steps           Verify each step
  --explain         Explain the algorithm
  --edge-cases      Check edge cases
  --compare FILE    Compare with reference implementation

Examples:
  /algo-verify
  /algo-verify --steps --explain`,

    status: `algo-status
  
Check AlgoMath installation status.`,

    list: `algo-list
  
List saved algorithms.`,

    help: `algo-help [command]
  
Show help information.

Examples:
  /algo-help
  /algo-help extract`
  };

  const cmd = command.replace(/^algo-/, '').replace(/^\//, '');
  if (helpTexts[cmd]) {
    console.log('\n' + helpTexts[cmd] + '\n');
  } else {
    console.log(`\nUnknown command: ${command}\n`);
    console.log('Available commands: extract, generate, run, verify, status, list, help\n');
  }
}

main();

#!/usr/bin/env node

/**
 * AlgoMath Extract Command
 * 
 * Extract algorithm from mathematical text using interactive prompts
 * Usage: /algo-extract
 * 
 * This command will:
 * 1. Prompt user for mathematical text (or accept from clipboard/file)
 * 2. Extract structured algorithm steps
 * 3. Save to context
 */

const { Command } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');
const ora = require('ora');
const { spawn } = require('child_process');
const path = require('path');

const program = new Command();

program
  .name('algo-extract')
  .description('Extract algorithm from mathematical text')
  .option('-t, --text <text>', 'Mathematical text describing the algorithm')
  .option('-n, --name <name>', 'Optional name for the algorithm')
  .option('-f, --file <file>', 'Read text from file')
  .option('--clipboard', 'Read text from clipboard')
  .action(async (options) => {
    console.log(chalk.blue.bold('╔════════════════════════════════════════╗'));
    console.log(chalk.blue.bold('║     AlgoMath - Extract Algorithm       ║'));
    console.log(chalk.blue.bold('╚════════════════════════════════════════╝'));
    console.log();

    try {
      let text = options.text;
      let name = options.name;

      // If no text provided, prompt interactively
      if (!text && !options.file && !options.clipboard) {
        const answers = await inquirer.prompt([
          {
            type: 'editor',
            name: 'text',
            message: 'Paste the mathematical text describing the algorithm:',
            validate: (input) => input.trim().length > 0 || 'Text is required'
          },
          {
            type: 'input',
            name: 'name',
            message: 'Algorithm name (optional):',
            default: ''
          }
        ]);
        text = answers.text;
        name = answers.name || null;
      } else if (options.file) {
        const fs = require('fs');
        text = fs.readFileSync(options.file, 'utf8');
      }

      // Validate we have text
      if (!text || text.trim().length === 0) {
        console.error(chalk.red('Error: No text provided'));
        process.exit(1);
      }

      // Show extraction progress
      const spinner = ora('Extracting algorithm...').start();

      // Call Python extraction
      const pythonScript = path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py');
      const pythonArgs = ['extract', text];
      if (name) {
        pythonArgs.push('--name', name);
      }

      const result = await runPython(pythonScript, pythonArgs);
      
      spinner.succeed('Extraction complete!');
      
      // Parse and display results
      const output = JSON.parse(result);
      displayResult(output);

    } catch (error) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

function runPython(script, args) {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [script, ...args], {
      cwd: path.join(__dirname, '..')
    });

    let output = '';
    let error = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(error || `Python process exited with code ${code}`));
      } else {
        resolve(output);
      }
    });
  });
}

function displayResult(output) {
  console.log();
  console.log(chalk.green.bold('✓ Algorithm extracted successfully'));
  console.log();
  
  if (output.algorithm) {
    console.log(chalk.cyan('Algorithm:'), output.algorithm.name || '(unnamed)');
    console.log(chalk.cyan('Steps:'), output.algorithm.steps?.length || 0);
    console.log();
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  }
  
  console.log();
  console.log(chalk.blue('Use /algo-generate to generate code from these steps'));
}

program.parse();

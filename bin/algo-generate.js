#!/usr/bin/env node

/**
 * AlgoMath Generate Command
 * 
 * Generate Python code from extracted algorithm steps
 * Usage: /algo-generate
 */

const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const { spawn } = require('child_process');
const path = require('path');

const program = new Command();

program
  .name('algo-generate')
  .description('Generate Python code from extracted algorithm steps')
  .action(async () => {
    console.log(chalk.blue.bold('╔════════════════════════════════════════╗'));
    console.log(chalk.blue.bold('║    AlgoMath - Generate Algorithm       ║'));
    console.log(chalk.blue.bold('╚════════════════════════════════════════╝'));
    console.log();

    try {
      const spinner = ora('Generating code...').start();

      const pythonScript = path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py');
      const result = await runPython(pythonScript, ['generate']);
      
      spinner.succeed('Code generation complete!');
      
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
  
  if (output.status === 'success') {
    console.log(chalk.green.bold('✓ Code generated successfully'));
    console.log();
    console.log(chalk.cyan('Generated:'), output.files?.length || 0, 'file(s)');
    console.log(chalk.cyan('Algorithm:'), output.algorithm || '(unnamed)');
    console.log();
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  } else {
    console.log(chalk.yellow('⚠'), output.message);
    if (output.next_steps) {
      console.log();
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  }
  
  console.log();
  console.log(chalk.blue('Use /algo-run to execute the generated code'));
}

program.parse();

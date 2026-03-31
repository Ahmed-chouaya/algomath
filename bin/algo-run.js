#!/usr/bin/env node

/**
 * AlgoMath Run Command
 * 
 * Execute generated Python code
 * Usage: /algo-run [--skip]
 */

const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const { spawn } = require('child_process');
const path = require('path');

const program = new Command();

program
  .name('algo-run')
  .description('Execute generated Python code')
  .option('--skip', 'Skip execution and proceed directly to verification')
  .action(async (options) => {
    console.log(chalk.blue.bold('╔════════════════════════════════════════╗'));
    console.log(chalk.blue.bold('║      AlgoMath - Execute Code           ║'));
    console.log(chalk.blue.bold('╚════════════════════════════════════════╝'));
    console.log();

    try {
      if (options.skip) {
        console.log(chalk.yellow('⚠ Skipping execution (proceeding to verification)'));
        console.log();
      }

      const spinner = ora(options.skip ? 'Skipping...' : 'Executing code...').start();

      const pythonScript = path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py');
      const args = ['run'];
      if (options.skip) {
        args.push('--skip');
      }
      
      const result = await runPython(pythonScript, args);
      
      if (options.skip) {
        spinner.succeed('Execution skipped');
      } else {
        spinner.succeed('Execution complete!');
      }
      
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
    console.log(chalk.green.bold('✓ Code executed successfully'));
    console.log();
    
    if (output.stdout) {
      console.log(chalk.cyan('Output:'));
      console.log(chalk.white(output.stdout));
      console.log();
    }
    
    console.log(chalk.cyan('Runtime:'), output.runtime_seconds || 'N/A', 'seconds');
    console.log();
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  } else if (output.status === 'skipped') {
    console.log(chalk.yellow('⚠ Execution skipped'));
    console.log(chalk.gray(output.message));
    console.log();
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  } else {
    console.log(chalk.red('✗ Execution failed'));
    console.log(chalk.red('Error:'), output.message);
    if (output.stderr) {
      console.log();
      console.log(chalk.gray('Error details:'));
      console.log(chalk.gray(output.stderr));
    }
    console.log();
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  }
  
  console.log();
  console.log(chalk.blue('Use /algo-verify to check results and verify correctness'));
}

program.parse();

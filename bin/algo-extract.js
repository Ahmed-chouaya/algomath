#!/usr/bin/env node

/**
 * AlgoMath Extract Command
 * 
 * Extract algorithm from PDF/text file
 * Usage: algoextract <file-path> [--name <name>]
 */

const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const path = require('path');

const program = new Command();

program
  .name('algo-extract')
  .description('Extract algorithm from PDF or text file')
  .argument('<file>', 'Path to PDF or text file')
  .option('-n, --name <name>', 'Algorithm name (optional)')
  .option('--auto', 'Skip interactive prompts')
  .action(async (file, options) => {
    console.log(chalk.blue.bold('╔════════════════════════════════════════╗'));
    console.log(chalk.blue.bold('║ AlgoMath - Extract Algorithm         ║'));
    console.log(chalk.blue.bold('╚════════════════════════════════════════╝'));
    console.log();

    try {
      // Validate file exists
      const fs = require('fs');
      if (!fs.existsSync(file)) {
        console.error(chalk.red(`✗ File not found: ${file}`));
        process.exit(1);
      }

      console.log(chalk.green(`✓ Reading file: ${file}`));
      
      // Show extraction progress
      const spinner = ora('Extracting algorithm from file...').start();

      // Call Python extraction
      const { spawn } = require('child_process');
      const pythonScript = path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py');
      
      const pythonArgs = ['extract', '--file', file];
      if (options.name) {
        pythonArgs.push('--name', options.name);
      }

      const result = await new Promise((resolve, reject) => {
        const python = spawn('python3', [pythonScript, ...pythonArgs]);
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

      spinner.succeed('Extraction complete!');

      // Parse and display results
      try {
        const output = JSON.parse(result);
        displayResult(output);
      } catch (e) {
        // If not JSON, just display the output
        console.log('\n' + result);
      }

    } catch (error) {
      console.error(chalk.red('\n✗ Error:'), error.message);
      process.exit(1);
    }
  });

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

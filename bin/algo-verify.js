#!/usr/bin/env node

/**
 * AlgoMath Verify Command
 * 
 * Verify execution results and explain algorithm behavior
 * Usage: /algo-verify [--step N] [--detailed] [--diagnostic]
 */

const { Command } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');
const ora = require('ora');
const { spawn } = require('child_process');
const path = require('path');

const program = new Command();

program
  .name('algo-verify')
  .description('Verify execution results and explain algorithm behavior')
  .option('-s, --step <number>', 'Explain specific step number', parseInt)
  .option('-d, --detailed', 'Show detailed step-by-step explanation')
  .option('--diagnostic', 'Run diagnostic mode for failed executions')
  .action(async (options) => {
    console.log(chalk.blue.bold('╔════════════════════════════════════════╗'));
    console.log(chalk.blue.bold('║    AlgoMath - Verify Results           ║'));
    console.log(chalk.blue.bold('╚════════════════════════════════════════╝'));
    console.log();

    try {
      // If step is specified, explain that step
      if (options.step !== undefined) {
        console.log(chalk.cyan(`Explaining step ${options.step}...`));
        console.log();
      } else if (options.diagnostic) {
        console.log(chalk.yellow('Running diagnostic mode...'));
        console.log();
      }

      const spinner = ora('Verifying...').start();

      const pythonScript = path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py');
      const args = ['verify'];
      
      if (options.step !== undefined) {
        args.push('--step', options.step.toString());
      }
      if (options.detailed) {
        args.push('--detailed');
      }
      if (options.diagnostic) {
        args.push('--diagnostic');
      }
      
      const result = await runPython(pythonScript, args);
      
      spinner.succeed('Verification complete!');
      
      const output = JSON.parse(result);
      displayResult(output, options);

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

function displayResult(output, options) {
  console.log();
  
  if (output.status === 'verified' || output.status === 'already_verified') {
    console.log(chalk.green.bold('✓ Verification complete'));
    console.log();
    
    if (output.message) {
      console.log(chalk.white(output.message));
      console.log();
    }
    
    // Show verification report if available
    if (output.verification_report) {
      const report = output.verification_report;
      
      if (report.summary) {
        console.log(chalk.cyan('Summary:'));
        console.log(chalk.white(report.summary));
        console.log();
      }
      
      if (report.execution) {
        console.log(chalk.cyan('Execution:'));
        console.log(chalk.white(`  Status: ${report.execution.status}`));
        console.log(chalk.white(`  Runtime: ${report.execution.runtime}s`));
        console.log();
      }
      
      if (report.explanation && options.detailed) {
        console.log(chalk.cyan('Explanation:'));
        console.log(chalk.white(report.explanation.text || report.explanation));
        console.log();
      }
      
      if (report.edge_cases && report.edge_cases.length > 0) {
        console.log(chalk.cyan('Edge Cases:'));
        report.edge_cases.forEach(ec => {
          const icon = ec.severity === 'error' ? '✗' : '⚠';
          console.log(chalk.white(`  ${icon} ${ec.description}`));
        });
        console.log();
      }
    }
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        if (step) console.log(chalk.gray(`  • ${step}`));
      });
    }
  } else if (output.status === 'diagnostic_complete') {
    console.log(chalk.yellow.bold('⚠ Diagnostic Report'));
    console.log();
    
    if (output.diagnostic_report) {
      const diag = output.diagnostic_report;
      
      if (diag.failure_point) {
        console.log(chalk.cyan('Failure point:'), diag.failure_point);
      }
      
      if (diag.possible_fixes && diag.possible_fixes.length > 0) {
        console.log(chalk.cyan('Possible fixes:'));
        diag.possible_fixes.forEach(fix => {
          console.log(chalk.white(`  • ${fix}`));
        });
      }
    }
    
    console.log();
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  } else {
    console.log(chalk.yellow('⚠'), output.message);
    console.log();
    
    if (output.next_steps) {
      console.log(chalk.gray('Next steps:'));
      output.next_steps.forEach(step => {
        console.log(chalk.gray(`  • ${step}`));
      });
    }
  }
  
  console.log();
  console.log(chalk.blue('Use /algo-extract to start with a new algorithm'));
}

program.parse();

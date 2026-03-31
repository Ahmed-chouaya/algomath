"""Integration test for full AlgoMath workflow.

Tests the complete pipeline: extract -> generate -> run -> verify
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.extraction.pdf_processor import PDFProcessor
from src.extraction.schema import Algorithm, Step, StepType
from src.generation.code_generator import TemplateCodeGenerator
from src.execution.sandbox import SandboxExecutor
from src.verification.checker import ExecutionChecker


def test_full_workflow():
    """Test complete workflow end-to-end."""
    
    print("Testing AlgoMath Full Workflow")
    print("=" * 50)
    
    # Step 1: Create algorithm manually (simulating extraction)
    print("\n1. Creating algorithm...")
    algorithm = Algorithm(
        name="factorial",
        description="Calculate factorial of n using recursion",
        inputs=[{
            "name": "n",
            "type": "int",
            "description": "Number to calculate factorial for"
        }],
        outputs=[{
            "name": "result",
            "type": "int",
            "description": "Factorial of n"
        }],
        steps=[
            Step(
                id=1,
                description="If n equals 0 or 1, return 1",
                step_type=StepType.CONDITIONAL,
                condition="n == 0 or n == 1"
            ),
            Step(
                id=2,
                description="return 1",
                step_type=StepType.RETURN,
                expression="1"
            ),
            Step(
                id=3,
                description="Otherwise, return n times factorial of n minus 1",
                step_type=StepType.RETURN,
                expression="n * factorial(n - 1)"
            )
        ]
    )
    print(f"✓ Created algorithm: {algorithm.name}")
    print(f"  Steps: {len(algorithm.steps)}")
    
    # Step 2: Generate code
    print("\n2. Generating code...")
    generator = TemplateCodeGenerator()
    result = generator.generate(algorithm)
    
    if result.success:
        print("✓ Code generated successfully")
        print(f"  Lines: {result.line_count}")
        print(f"  Imports: {result.imports}")
    else:
        print(f"✗ Generation failed: {result.error}")
        return False
    
    # Step 3: Execute code
    print("\n3. Executing code...")
    executor = SandboxExecutor(timeout=10)
    
    # Wrap the generated code with a main() function and test call
    test_code = result.code + """

if __name__ == "__main__":
    result = factorial(5)
    print(f"Factorial of 5: {result}")
    assert result == 120, f"Expected 120, got {result}"
    print("Test passed!")
"""
    
    exec_result = executor.execute(test_code)
    
    if exec_result.status == "success":
        print("✓ Execution successful")
        print(f"  Runtime: {exec_result.runtime_seconds:.2f}s")
        print(f"  Output: {exec_result.stdout[:100]}...")
    else:
        print(f"✗ Execution failed: {exec_result.error_message}")
        print(f"  Stderr: {exec_result.stderr}")
        return False
    
    # Step 4: Verify
    print("\n4. Verifying results...")
    checker = ExecutionChecker({
        "status": exec_result.status,
        "stdout": exec_result.stdout,
        "stderr": exec_result.stderr
    })
    
    verification = checker.check()
    print(f"✓ Verification: {verification.status}")
    print(f"  Message: {verification.message}")
    
    print("\n" + "=" * 50)
    print("✓ Full workflow test PASSED!")
    
    return True


if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)

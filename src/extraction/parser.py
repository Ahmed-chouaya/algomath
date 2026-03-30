"""Rule-based parser for algorithm extraction."""
import re
from typing import List, Optional, Dict, Any, Tuple
from .schema import Algorithm, Step, StepType


class RuleBasedParser:
    """Parser using regex rules to extract algorithm steps."""

    def __init__(self):
        self.step_patterns = [
            (r'^\s*(\d+)\.\s*(.+)$', self._parse_numbered_step),
            (r'^\s*[Ss]tep\s*(\d+)[:.]\s*(.+)$', self._parse_numbered_step),
        ]

    def parse(self, text: str, name: str = "unnamed") -> Algorithm:
        """Parse text into an Algorithm."""
        lines = text.strip().split('\n')
        steps = []
        step_id = 1

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            for pattern, handler in self.step_patterns:
                match = re.match(pattern, line)
                if match:
                    step = handler(match, step_id, i)
                    if step:
                        steps.append(step)
                        step_id += 1
                    break
            else:
                # Try to parse as a simple step
                if len(line) > 10:
                    step = Step(
                        id=step_id,
                        type=StepType.ASSIGNMENT,
                        description=line,
                        line_refs=[i]
                    )
                    steps.append(step)
                    step_id += 1

        return Algorithm(name=name, steps=steps, source_text=text)

    def _parse_numbered_step(self, match, step_id: int, line_num: int) -> Optional[Step]:
        """Parse a numbered step."""
        text = match.group(2).strip()
        step_type = self._classify_step_type(text)

        inputs, outputs = self._extract_variables(text)

        return Step(
            id=step_id,
            type=step_type,
            description=text,
            inputs=inputs,
            outputs=outputs,
            line_refs=[line_num]
        )

    def _classify_step_type(self, text: str) -> StepType:
        """Classify step type from text."""
        text_lower = text.lower()

        if 'return' in text_lower:
            return StepType.RETURN
        elif text_lower.startswith('for '):
            return StepType.LOOP_FOR
        elif text_lower.startswith('while '):
            return StepType.LOOP_WHILE
        elif text_lower.startswith('if '):
            return StepType.CONDITIONAL
        elif '(' in text and ')' in text:
            return StepType.CALL
        else:
            return StepType.ASSIGNMENT

    def _extract_variables(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract input and output variables."""
        inputs = []
        outputs = []

        # Look for assignments (x = ... or x ← ...)
        assign_match = re.search(r'^(\w+)\s*[=←]', text)
        if assign_match:
            outputs.append(assign_match.group(1))

        # Look for variable references
        var_pattern = r'\b([a-zA-Z_]\w*)\b'
        matches = re.findall(var_pattern, text)

        for var in matches:
            if var not in outputs and var not in ['for', 'while', 'if', 'else', 'return']:
                inputs.append(var)

        return inputs, outputs


def parse_algorithm(text: str, name: Optional[str] = None) -> Algorithm:
    """Parse algorithm text and return an Algorithm object."""
    parser = RuleBasedParser()
    return parser.parse(text, name or "unnamed")

"""Code persistence utilities.

This module handles saving generated code to the filesystem
with metadata.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.extraction.schema import Algorithm
from src.generation.review import ReviewState


class CodePersistence:
    """
    Persist generated code to filesystem.
    
    Saves code and metadata to .algomath/algorithms/{name}/
    """
    
    def __init__(self, base_path: str = ".algomath"):
        """
        Initialize persistence manager.
        
        Args:
            base_path: Base directory for persistence
        """
        self.base_path = Path(base_path)
        self.algorithms_path = self.base_path / "algorithms"
    
    def save_generated_code(self,
                           algorithm: Algorithm,
                           code: str,
                           review_state: Optional[ReviewState] = None) -> str:
        """
        Save generated code to .algomath/algorithms/{name}/generated.py.
        
        Args:
            algorithm: Algorithm metadata
            code: Python code to save
            review_state: Optional review state
            
        Returns:
            Path to saved file
        """
        # Create algorithm directory
        algo_dir = self.algorithms_path / self._sanitize_name(algorithm.name)
        algo_dir.mkdir(parents=True, exist_ok=True)
        
        # Save generated.py
        generated_file = algo_dir / "generated.py"
        
        # Add header comment with metadata
        header = self._generate_header(algorithm, review_state)
        full_code = header + "\n\n" + code
        
        generated_file.write_text(full_code, encoding='utf-8')
        
        # Save metadata
        self._save_metadata(algo_dir, algorithm, review_state)
        
        return str(generated_file)
    
    def _generate_header(self,
                        algorithm: Algorithm,
                        review_state: Optional[ReviewState]) -> str:
        """
        Generate file header with metadata.
        
        Args:
            algorithm: Algorithm metadata
            review_state: Optional review state
            
        Returns:
            Header comment string
        """
        lines = ['"""']
        lines.append(f"Generated code for: {algorithm.name}")
        lines.append(f"Description: {algorithm.description}")
        lines.append(f"Generated at: {datetime.now().isoformat()}")
        
        if review_state:
            lines.append(f"Status: {'Approved' if review_state.is_approved else 'Pending review'}")
            lines.append(f"Edited: {'Yes' if review_state.is_edited else 'No'}")
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _save_metadata(self,
                      algo_dir: Path,
                      algorithm: Algorithm,
                      review_state: Optional[ReviewState]):
        """
        Save metadata JSON alongside code.
        
        Args:
            algo_dir: Algorithm directory
            algorithm: Algorithm metadata
            review_state: Optional review state
        """
        metadata: Dict[str, Any] = {
            'name': algorithm.name,
            'description': algorithm.description,
            'inputs': algorithm.inputs,
            'outputs': algorithm.outputs,
            'step_count': len(algorithm.steps),
            'saved_at': datetime.now().isoformat(),
        }
        
        if review_state:
            metadata['review'] = {
                'is_edited': review_state.is_edited,
                'is_approved': review_state.is_approved,
                'approved_at': review_state.approved_at.isoformat() if review_state.approved_at else None
            }
        
        metadata_file = algo_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
    
    def load_generated_code(self, algorithm_name: str) -> Optional[str]:
        """
        Load previously generated code.
        
        Args:
            algorithm_name: Algorithm name
            
        Returns:
            Code string or None if not found
        """
        algo_dir = self.algorithms_path / self._sanitize_name(algorithm_name)
        generated_file = algo_dir / "generated.py"
        
        if generated_file.exists():
            content = generated_file.read_text()
            # Strip header
            if content.startswith('"""'):
                end = content.find('"""', 3)
                if end != -1:
                    return content[end + 3:].strip()
            return content
        return None
    
    def load_metadata(self, algorithm_name: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata for an algorithm.
        
        Args:
            algorithm_name: Algorithm name
            
        Returns:
            Metadata dict or None if not found
        """
        algo_dir = self.algorithms_path / self._sanitize_name(algorithm_name)
        metadata_file = algo_dir / "metadata.json"
        
        if metadata_file.exists():
            return json.loads(metadata_file.read_text())
        return None
    
    def _sanitize_name(self, name: str) -> str:
        """
        Convert algorithm name to filesystem-safe directory name.
        
        Args:
            name: Algorithm name
            
        Returns:
            Sanitized name
        """
        # Remove special characters
        safe = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces and dashes with underscores
        safe = re.sub(r'[-\s]+', '_', safe)
        return safe.lower().strip('_')


def save_to_context(context: Any,
                   algorithm: Algorithm,
                   review: 'CodeReviewInterface') -> str:
    """
    Save approved code to context.
    
    Args:
        context: ContextManager instance
        algorithm: Algorithm metadata
        review: CodeReviewInterface with approval
        
    Returns:
        Path to saved file
        
    Raises:
        ValueError: If code not approved
    """
    persistence = CodePersistence()
    
    if not review.is_approved():
        raise ValueError("Code must be approved before saving")
    
    code = review.get_modified_code()
    path = persistence.save_generated_code(
        algorithm,
        code,
        review.state
    )
    
    # Update context
    context.save_code(code)
    # Assuming context has save_code_path method
    if hasattr(context, 'save_code_path'):
        context.save_code_path(path)
    
    return path


__all__ = [
    'CodePersistence',
    'save_to_context',
]

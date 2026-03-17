import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class PromptManager:
    """Manage prompts loaded from JSON files"""
    
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            self.prompts_dir = Path(__file__).parent
        else:
            self.prompts_dir = Path(prompts_dir)
    
    def load_prompt(self, category: str, name: str) -> str:
        """Load prompt from JSON file"""
        file_path = self.prompts_dir / category / f"{name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['content']
    
    def load_prompt_with_metadata(self, category: str, name: str) -> Dict[str, Any]:
        """Load prompt with all metadata"""
        file_path = self.prompts_dir / category / f"{name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_analysis_prompt(self, email_text: str, include_examples: bool = False, max_examples: int = 2) -> str:
        """Get complete analysis prompt with email and optional examples"""
        system_prompt = self.load_prompt('email', 'system_prompt')
        
        if include_examples:
            examples = self.load_examples('email', 'few_shot_examples', max_examples)
            examples_text = self._format_examples(examples)
            return f"{system_prompt}\n\nExamples:\n{examples_text}\n\nEmail to analyze:\n---\n{email_text}\n---"
        
        return f"{system_prompt}\n\nEmail to analyze:\n---\n{email_text}\n---"
    
    def load_examples(self, category: str, name: str = 'few_shot_examples', max_examples: Optional[int] = None) -> list:
        """Load few-shot examples"""
        file_path = self.prompts_dir / category / f"{name}.json"
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            examples = json.load(f)
            if max_examples and len(examples) > max_examples:
                examples = examples[:max_examples]
            return examples
    
    def _format_examples(self, examples: list) -> str:
        """Format examples for inclusion in prompt"""
        formatted = []
        for i, example in enumerate(examples, 1):
            formatted.append(f"Example {i}:")
            formatted.append(f"Email: {example['email']}")
            formatted.append(f"Analysis: {json.dumps(example['analysis'], indent=2)}")
        return "\n".join(formatted)
    
    def list_categories(self) -> List[str]:
        """List all available prompt categories"""
        return [d.name for d in self.prompts_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
    
    def list_prompts(self, category: str) -> List[str]:
        """List all prompts in a category"""
        category_dir = self.prompts_dir / category
        if not category_dir.exists():
            return []
        
        return [f.stem for f in category_dir.glob("*.json") if f.stem != 'few_shot_examples']


# Create global instance
prompt_manager = PromptManager()

# Convenience function for backward compatibility
def get_analysis_prompt(email_text: str) -> str:
    """Legacy function for backward compatibility"""
    return prompt_manager.get_analysis_prompt(email_text)
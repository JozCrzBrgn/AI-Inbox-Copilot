import json
from pathlib import Path

import pytest

from prompts import PromptManager


def create_json(path: Path, content):
    """Helper for creating JSON files"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f)


def test_load_prompt_success(tmp_path):
    create_json(
        tmp_path / "email" / "system_prompt.json",
        {"content": "This is a prompt"}
    )

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.load_prompt("email", "system_prompt")

    assert result == "This is a prompt"


def test_load_prompt_file_not_found(tmp_path):
    pm = PromptManager(prompts_dir=tmp_path)

    with pytest.raises(FileNotFoundError):
        pm.load_prompt("email", "missing")


def test_load_prompt_with_metadata(tmp_path):
    data = {"content": "abc", "version": 1}
    create_json(tmp_path / "email" / "system_prompt.json", data)

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.load_prompt_with_metadata("email", "system_prompt")

    assert result == data


def test_get_analysis_prompt_without_examples(tmp_path):
    create_json(
        tmp_path / "email" / "system_prompt.json",
        {"content": "SYSTEM"}
    )

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.get_analysis_prompt("hello world", include_examples=False)

    assert "SYSTEM" in result
    assert "hello world" in result
    assert "Examples:" not in result


def test_get_analysis_prompt_with_examples(tmp_path):
    create_json(
        tmp_path / "email" / "system_prompt.json",
        {"content": "SYSTEM"}
    )

    examples = [
        {"email": "hi", "analysis": {"a": 1}},
        {"email": "bye", "analysis": {"b": 2}},
    ]

    create_json(tmp_path / "email" / "few_shot_examples.json", examples)

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.get_analysis_prompt("email text", include_examples=True)

    assert "Examples:" in result
    assert "Example 1:" in result
    assert "hi" in result
    assert "email text" in result


def test_load_examples_with_limit(tmp_path):
    examples = [
        {"email": "1", "analysis": {}},
        {"email": "2", "analysis": {}},
        {"email": "3", "analysis": {}},
    ]

    create_json(tmp_path / "email" / "few_shot_examples.json", examples)

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.load_examples("email", max_examples=2)

    assert len(result) == 2


def test_load_examples_file_not_found(tmp_path):
    pm = PromptManager(prompts_dir=tmp_path)

    result = pm.load_examples("email")

    assert result == []


def test_format_examples():
    pm = PromptManager(prompts_dir=".")

    examples = [
        {"email": "test", "analysis": {"x": 1}}
    ]

    result = pm._format_examples(examples)

    assert "Example 1:" in result
    assert "test" in result
    assert '"x": 1' in result


def test_list_categories(tmp_path):
    (tmp_path / "email").mkdir()
    (tmp_path / "chat").mkdir()
    (tmp_path / "__pycache__").mkdir()

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.list_categories()

    assert "email" in result
    assert "chat" in result
    assert "__pycache__" not in result


def test_list_prompts(tmp_path):
    create_json(tmp_path / "email" / "a.json", {})
    create_json(tmp_path / "email" / "b.json", {})
    create_json(tmp_path / "email" / "few_shot_examples.json", {})

    pm = PromptManager(prompts_dir=tmp_path)
    result = pm.list_prompts("email")

    assert "a" in result
    assert "b" in result
    assert "few_shot_examples" not in result


def test_list_prompts_category_not_found(tmp_path):
    pm = PromptManager(prompts_dir=tmp_path)

    result = pm.list_prompts("missing")

    assert result == []
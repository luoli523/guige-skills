"""Prompt 模板管理"""

from pathlib import Path

# Prompt 模板目录
PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """加载 prompt 模板

    Args:
        name: prompt 文件名（不含扩展名）

    Returns:
        prompt 模板内容
    """
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8")


def render_prompt(name: str, **kwargs) -> str:
    """加载并渲染 prompt 模板

    Args:
        name: prompt 文件名（不含扩展名）
        **kwargs: 模板变量

    Returns:
        渲染后的 prompt
    """
    template = load_prompt(name)
    return template.format(**kwargs)

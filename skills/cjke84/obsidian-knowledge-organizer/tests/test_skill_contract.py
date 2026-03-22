from pathlib import Path

from scripts import check_duplicate, find_related, markdown_helpers, obsidian_note, settings


def test_skill_contract_mentions_obsidian_frontmatter_wikilinks_and_embeds():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / "SKILL.md").read_text(encoding="utf-8")
    tag_text = (repo_root / "references" / "tag-system.md").read_text(encoding="utf-8")

    required_skill_phrases = [
        "structured Obsidian-ready Markdown",
        "YAML frontmatter",
        "wikilink",
        "embed",
        "destination_path",
        "OPENCLAW_KB_ROOT",
        "absolute path",
        "frontmatter / wikilink / embed / block id",
        "prefer `xiaohongshu-mcp` for Xiaohongshu links",
        "For WeChat public-account imports, read `references/wechat-import.md`",
        "Before running script-based import flows, prefer checking `scripts/check_runtime.py`",
    ]
    required_tag_phrases = [
        "至少 1 个领域标签 + 1 个类型标签",
        "总标签数 5-10 个",
        "复用优先",
        "技能契约对齐",
    ]

    for phrase in required_skill_phrases:
        assert phrase in skill_text

    for phrase in required_tag_phrases:
        assert phrase in tag_text


def test_skill_scripts_import_without_manual_path_tweaks():
    assert callable(check_duplicate.decide_duplicate)
    assert callable(find_related.find_related)
    assert callable(markdown_helpers.scan_knowledge_base)
    assert callable(obsidian_note.render_obsidian_note)
    assert callable(settings.resolve_vault_root)

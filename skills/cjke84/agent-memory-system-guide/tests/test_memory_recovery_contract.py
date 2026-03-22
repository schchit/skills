from pathlib import Path


def test_skill_mentions_recovery_templates():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')
    assert 'SESSION-STATE.md' in skill_text
    assert 'working-buffer.md' in skill_text
    assert 'templates/OBSIDIAN-NOTE.md' in skill_text
    assert 'frontmatter' in skill_text
    assert 'Dataview' in skill_text
    assert '启动时' in skill_text
    assert '结束时' in skill_text
    assert '恢复' in skill_text

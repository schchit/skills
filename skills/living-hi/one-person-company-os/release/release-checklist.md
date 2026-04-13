# Release Checklist

## Positioning

- keep the primary audience as AI-native solo founders and independent builders
- keep the visible founder mental model as `promise -> buyer -> product -> delivery -> cash -> learning -> asset`
- keep rounds, calibration, and stages as internal control structures rather than the first thing users feel
- avoid reintroducing week-based positioning as the main loop

## Repository

- verify `README.md`, `README.zh-CN.md`, and `SKILL.md` describe the same product
- verify `agents/openai.yaml` matches the current positioning
- run `python3 scripts/preflight_check.py --mode 创建公司`
- run `python3 scripts/ensure_python_runtime.py`
- run `python3 scripts/validate_release.py`
- confirm `scripts/ensure_python_runtime.py` only prints compatibility and manual install guidance, and does not auto-install packages
- confirm Chinese-visible and English-visible workspace generation both pass
- confirm both workspaces generate localized HTML reading directories with `00-先看这里.html` or `00-start-here.html`
- confirm the core dashboard, offer, pipeline, product, delivery, cash, asset, and deliverable-overview pages are exported as HTML reading files
- confirm runtime output reports `installed`, `runnable`, `python_supported`, `workspace_created`, and `persisted`
- confirm persisted write examples stay inside the target company workspace
- confirm `产物/` only contains numbered `.docx` files in generated workspaces
- confirm `.opcos/state/current-state.json` exists and visible `自动化/当前状态.json` does not
- confirm English workspaces do not expose Chinese root files or directories
- confirm Chinese workspaces do not expose English root business directories
- confirm launch-stage workspaces include deployment and production starter materials
- confirm launch-stage role briefs include `运维保障` and `用户运营`

## Proof Assets

- include one screenshot of the generated Chinese workspace
- include one screenshot of the generated English workspace
- include one screenshot of `00-经营总盘.md` or `00-operating-dashboard.md`
- include `SAMPLE-OUTPUTS.md` excerpts in the release post

## Post-Launch Loop

- collect founder reactions to the direction-first workflow
- collect founder reactions to the localized workspace surface
- collect founder reactions to the new `状态栏 / 保存状态 / 运行状态` output
- watch which first prompt users actually copy
- track whether users understand the founder-visible workspace quickly
- tighten the setup draft if users still ask too many clarifying questions

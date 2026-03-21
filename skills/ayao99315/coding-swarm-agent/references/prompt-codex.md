# Codex Backend Coding Prompt Template

Use this template when dispatching tasks to Codex (codex-1, codex-2, etc.).

## 调用命令格式

```bash
PROMPT_FILE=/tmp/codex-task-prompt.txt

cat > "$PROMPT_FILE" << 'PROMPT'
[完整任务 prompt]
PROMPT

scripts/dispatch.sh codex-1 T001 --prompt-file "$PROMPT_FILE" \
  codex exec --dangerously-bypass-approvals-and-sandbox
```

> 推荐把 prompt 单独写文件，再通过 `dispatch.sh --prompt-file` 走 stdin。这样长 markdown、多行文本、引号都更稳。
> YOLO 模式：无沙盒、无确认提示，agent 可直接执行任意 shell 命令。仅在受信任环境中使用。

## 重要原则

1. **引用实际文件，不描述技术栈** — 不要写"使用 pg 连接数据库"，而是写"参考 `src/persistence/db.ts` 中的 `getPool()` 模式"
2. **commit 命令写死** — 不要让 agent 自己决定 commit message，直接给出完整命令
3. **scope 列出具体文件路径** — 不是"改 providers 目录"，而是"创建 `src/providers/clob-auth.ts`"
4. **禁止事项要具体** — 不要泛泛说"不要改其他文件"，列出可能被误改的关键文件

## 模板

```
## Project
[Project name] — [one-line description]
Working directory: [absolute path]

## Task
[ID]: [One sentence]

## Scope (strict — ONLY touch these files)
- Create: [full relative paths]
- Modify: [full relative paths]
- 禁止修改: [列出容易被误改的关键文件，如 package.json, tsconfig.json, 共享 types]

## Technical Requirements
[具体技术要求]

## Reference Code (必填 — 让 agent 自己看代码而不是靠你描述)
请先阅读以下文件了解项目模式：
- `[path/to/similar-module.ts]` — [说明这个文件展示了什么模式]
- `[path/to/types.ts]` — [需要用到的类型定义]
- `[path/to/config.ts]` — [配置加载方式]

## Do NOT
- 修改 scope 以外的任何文件
- 不要修改: [具体列出，如 src/daemon/game-runner.ts, package.json]
- 不要添加 npm 依赖（除非下面明确列出）
- 不要修改 .env 或包含密钥的配置
- 不要重构已有代码

## Allowed Dependencies (如果需要新依赖)
- [package-name]: [为什么需要]

## Commit (直接复制执行)
git add -A && git commit -m "[预写好的 conventional commit message]" && git push

## Done When
[具体完成标准]
```

## 常见错误与预防

| 错误 | 原因 | 预防 |
|------|------|------|
| Agent 用了错误的 DB 驱动 | Prompt 说"使用 SQLite"但项目用 pg | Reference Code 指向实际 db.ts |
| Agent 改了 package.json | 自己决定加依赖 | 禁止修改列表明确包含 package.json |
| Agent 不 commit | 忘了或被其他输出打断 | commit 命令写在最后，加粗强调 |
| Agent 改了共享 types | 觉得需要扩展类型定义 | 禁止修改列表包含 types/index.ts |
| Commit message 不规范 | Agent 自由发挥 | 直接给出完整 git commit 命令 |

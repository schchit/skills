---
name: long-run-mode
description: Long-task execution protocol for sustained multi-step work. 当用户明确说“长任务模式”或“进入长任务模式”时触发。除这类口令外，其他任何表达——包括“继续”“接着来”“往下做”“一直做，不停”“持续推进”“不要停下来问”——都不触发长任务模式，只按普通任务处理。Handles task framing, state recording, visible progress heartbeats, session routing, and watchdog-based recovery.
---

# Long Run Mode

把这个技能当成**长任务执行协议**，不是普通提示词。

## 触发边界（最严格版硬规则）
- **当用户明确说出 `长任务模式` 或 `进入长任务模式` 时，才触发长任务模式。**
- 除 `进入长任务模式` 外，其他任何表达一律**不触发**，包括但不限于：`继续`、`接着来`、`往下做`、`一直做，不停`、`持续推进`、`不要停下来问`。
- 遇到上述非口令表达时，只按普通任务续做；不要登记长任务状态、不要启动保活/看门狗、不要套用长任务前台心跳规则。
- 如果上下文里已经处于长任务模式，后续普通 `继续` 只表示在**已开启的长任务**里继续执行；但**开启动作本身**仍然只能由 `进入长任务模式` 触发。

核心目标只有两条：
1. 长任务不能悄悄空转
2. 用户必须持续看得见任务还活着

## 先读什么
- 状态字段：`references/state-schema.md`
- 执行协议：`references/protocol.md`

## 脚本索引
### 主路径
- `scripts/task_state.py`：登记、更新、清理任务状态与发送相关时间戳。
- `scripts/validate_task_start.py`：校验任务是否真正绑定到目标 `origin_session_key`；只有它返回 `ok: true` 才能宣称启动成功。
- `scripts/check_foreground_progress.py`：检查单任务前台进度是否到点。
- `scripts/build_progress_update.py`：构造单任务前台短进度消息。
- `scripts/foreground_tick.py`：单任务前台心跳入口。
- `scripts/work_cycle_tick.py`：每轮工作循环后的前台钩子；若 `must_send_now=true`，必须先发再继续。

### 前台自动触发 / 分发辅助
- `scripts/emit_foreground_due.py`：扫描所有到点前台任务，生成前台自动消息事件。
- `scripts/dispatch_foreground_due.py`：把前台自动消息事件整理成 dispatcher 计划；真正发送仍需 OpenClaw tool/agent 层执行。

### 保活 / 恢复 / 审计
- `scripts/keepalive_tick.py`：检查单任务是否长时间无活动、是否需要续跑。
- `scripts/emit_keepalive_resume.py`：生成单任务保活续跑事件。
- `scripts/run_keepalive_once.py`：批量跑一次保活检查，产出可执行计划。
- `scripts/watchdog.py`：审计长任务是否失联、超时、卡住或到检查点。
- `scripts/run_watchdog_once.py`：批量跑一次 watchdog，并生成后续恢复计划。
- `scripts/recover_due_tasks.py`：根据 watchdog 结果整理恢复建议。
- `scripts/emit_recovery_message.py`：把恢复建议转成可发送的恢复消息事件。
- `scripts/build_sessions_send_payloads.py`：把恢复消息事件整理成 `sessions_send` payload。

### 运维 / 清理辅助
- `scripts/cleanup_state.py`：清理旧状态、测试残留、坏锁和缺少 `origin_session_key` 的脏记录。
- `scripts/install_watchdog_cron.sh`：安装 watchdog cron 示例。
- `scripts/watchdog_loop.sh`：本地循环跑 watchdog 的辅助脚本。

## 启动动作
进入长任务后，先在回复里明确：

```text
当前状态：分析中 / 执行中 / 等待外部 / 被阻塞 / 需转派 / 已完成
任务目标：...
完成条件：...
阻塞条件：...
所属边界：...
下一步：...
```

然后立刻登记状态：

```bash
python3 skills/long-run-mode/scripts/task_state.py set \
  --task "<任务名>" \
  --session "<人类可读会话名>" \
  --origin-session-key "<真实目标 sessionKey>" \
  --state "analyzing|executing|waiting|blocked|handoff|done" \
  --goal "<任务目标>" \
  --done-when "<完成条件>" \
  --blocked-when "<阻塞条件>" \
  --boundary "<所属边界>" \
  --next-check "<ISO时间或相对描述>" \
  --note "<当前下一步>" \
  --progress-every "3m"
```

登记后必须立刻跑一次启动校验：

```bash
python3 skills/long-run-mode/scripts/validate_task_start.py \
  --task "<任务名>" \
  --expect-session-key "<真实目标 sessionKey>"
```

只有当校验返回 `ok: true` 时，才能对用户说“已进入长任务模式”或“已开启长任务模式”。

硬规则：
- 对 `analyzing` / `executing` / `waiting` 这类“已启动态”，**必须提供真实 `--origin-session-key`**。
- 如果拿不到真实目标会话，就只能先说明“还没绑定成功”，不能宣称“已进入长任务模式”或“已开启长任务模式”。
- `session` 只是人类可读名字；真正的发送、保活、恢复都靠 `origin_session_key`。

如果你要最基础的“会话别断”保活链，直接再加一层 1 分钟无活动检测：

```bash
python3 skills/long-run-mode/scripts/keepalive_tick.py --task "<任务名>" --idle-seconds 60
python3 skills/long-run-mode/scripts/run_keepalive_once.py --idle-seconds 60
```

可选环境变量：
- `OPENCLAW_BIN`：覆盖 `openclaw` 可执行文件名或路径
- `OPENCLAW_SESSIONS_FILE`：覆盖 sessions 索引文件路径
- `LOG_FILE`：覆盖 watchdog/cron 日志输出位置

它会综合判断这些活动信号的最近值：
- `last_visible_reply_at`
- `last_tool_result_at`
- `last_progress_at`
- `updated_at`

如果任务仍处于 `analyzing` / `executing`，且这些信号都沉默超过阈值，就返回 `should_resume: true`。

如果要直接产出“保活续跑事件”，用：

```bash
python3 skills/long-run-mode/scripts/emit_keepalive_resume.py --task "<任务名>" --idle-seconds 60
```

它会返回：
- `delivery: session`
- `sessionKey`
- `message`（续跑消息）
- `onSuccess: task_state.py mark-resume`

默认目标是：**检测到长时间无输出后，先生成可审计的续跑计划。**
只有显式设置 `LONG_RUN_MODE_AUTO_RESUME=1` 时，才会真正把当前任务续起来。

## 状态机
只允许：
- `analyzing`
- `executing`
- `waiting`
- `blocked`
- `handoff`
- `done`

禁止模糊状态。

## 主规则：前台心跳优先
**前台可见进度是主路径，watchdog 只是兜底。**

铁律：**长任务一旦开始，后续每次继续推进前，若距上次可见进度已超 `3m`（或任务自己的 `progress_every`），必须先发一条短进度，不能先做别的。**

只要任务还在 `analyzing` 或 `executing`：
- 超过 `progress_every`（默认 `5m`）没有可见更新，就必须发一条短进度
- 当前执行流不能靠“想起来再检查”；必须把前台心跳嵌进每一轮工作循环
- 每完成一轮有意义推进后，固定跑一次循环钩子；如果到点，**先汇报，再继续下一轮**
- 短进度必须包含三件事：
  - 正在看什么
  - 刚确认什么
  - 下一步是什么

推荐直接走工作循环钩子：

```bash
python3 skills/long-run-mode/scripts/work_cycle_tick.py --task "<任务名>" --step "<这一轮刚做了什么>"
```

它会：
- 先判断现在是否到点
- 如果到点，返回 `must_send_now: true`，这不是建议，而是硬信号
- 如果没到点，明确告诉你继续下一轮

强协议：
- 只要返回 `must_send_now: true`，当前这一轮就**不得继续埋头做事**
- 这是前台心跳，默认**直接回当前会话**，不要默认走跨会话 `sessions_send`
- `session` / `boundary` 字段表示任务归属边界，不等于真实可发送会话；真正可发送目标以 `origin_session_key` 为准
- 只有后台回收、跨会话转派、handoff 时，才应尝试 `sessions_send`
- 成功后必须执行：

```bash
python3 skills/long-run-mode/scripts/task_state.py touch-progress --task "<任务名>"
```

- 失败后必须执行：

```bash
python3 skills/long-run-mode/scripts/task_state.py mark-progress-attempt \
  --task "<任务名>" \
  --error "<失败原因>"
```

- 如果连续触发前台心跳但仍未送达，应转 `blocked`，不能继续假装“还在测”

如果只想单独看前台心跳，也可以：

```bash
python3 skills/long-run-mode/scripts/foreground_tick.py --task "<任务名>"
```

如果要给宿主/自动化接一个“前台到点事件流”，用：

```bash
python3 skills/long-run-mode/scripts/emit_foreground_due.py
```

它只负责产出**前台自动消息事件**：
- `delivery: session`
- `sessionKey`
- `session_label`
- `message`
- `onSuccess: touch-progress`
- `onError: mark-progress-attempt`

注意：它产出的是事件，不等于已经发出；仍需由 OpenClaw tool/agent 层真正 `sessions_send`。
若 `sessions_send` 返回 `timeout`，必须记为 `unknown`，不能直接记成失败；同一消息在短冷却窗口内不得重复发。

如果要继续往前接 dispatcher 计划，用：

```bash
python3 skills/long-run-mode/scripts/dispatch_foreground_due.py
```

如果需要拆开调试，也可以分两步：

```bash
python3 skills/long-run-mode/scripts/check_foreground_progress.py --task "<任务名>"
python3 skills/long-run-mode/scripts/build_progress_update.py --task "<任务名>"
```

成功发出后：

```bash
python3 skills/long-run-mode/scripts/task_state.py touch-progress --task "<任务名>"
```

如果尝试发了但失败：

```bash
python3 skills/long-run-mode/scripts/task_state.py mark-progress-attempt \
  --task "<任务名>" \
  --error "<失败原因>"
```

## 边界与转派
- `openclaw manager / App / 控制 UI` → `openclaw-control-ui`
- `PM 交易 / Telegram / 监控 / 告警 / 日志链路` → PM 对应会话
- `主会话规则 / 记忆 / 全局整理` → 主会话

如果当前会话不该继续做，转 `handoff`，不要硬做。

## waiting 规则
进入 `waiting` 只能三选一：
1. 后台执行并约定检查点
2. 使用 cron / 唤醒机制约定回收时间
3. 明确宣布等待外部，并写清在等什么

进入 `waiting` 后立刻更新状态文件。

## blocked 规则
出现任一情况立刻转 `blocked`：
- 连续 3 次工具失败
- 超过 10 分钟没有推进
- 缺权限、token、登录、浏览器接管
- 缺必要用户确认

阻塞时必须说明：
- 卡在哪里
- 缺什么
- 建议下一步

## 跟进审计兜底
当任务失联、超时、卡住或等待态到检查点时，用审计/回收脚本兜底：

```bash
python3 skills/long-run-mode/scripts/watchdog.py check
python3 skills/long-run-mode/scripts/watchdog.py check --json
python3 skills/long-run-mode/scripts/recover_due_tasks.py --json
python3 skills/long-run-mode/scripts/build_sessions_send_payloads.py --json
```

标准动作：
1. 生成 `sessions_send` payload
2. 逐条尝试发送到目标会话
3. 成功后回写状态
4. 失败则记录错误，不得谎报“已通知”

## 真值规则
以下三者必须严格区分：
- 已生成消息
- 已尝试发送
- 用户已真正收到

只有真正发到会话后，才能更新：
- `last_progress_at`
- `last_progress_sent_at`

## 发布前验收
如果要发表，这个 skill 至少要过：
1. **可见性**：15 分钟长任务里至少自动出现 2 次短进度
2. **诚实性**：发送失败时能看到失败时间与原因
3. **回收性**：任务失联后能真正发回目标会话，而不是只生成 payload

## 可发布约束
对外上传前必须再确认：
- skill 目录里不包含 `.task-state.json`、`watchdog.log`、`__pycache__/`、`*.pyc`
- 运行态状态文件由安装后的实际环境自行生成，不随 skill 分发
- 不允许写死某个固定 `sessionKey` 作为默认兜底目标
- 缺少 `origin_session_key` 时应直接报错，而不是静默退回到别的会话
- 对外描述时只能承诺已验证能力；不要把“事件已生成”写成“消息已送达”
�已送达”
�已送达”
�已送达”
已送达”

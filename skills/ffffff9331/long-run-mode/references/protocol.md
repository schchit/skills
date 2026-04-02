# 长任务执行协议

## 1. 定位
`long-run-mode` 不是单纯的 watchdog 集合，而是一套长任务执行协议：
- 前台进度心跳是主路径
- 后台超时回收是兜底路径
- 长任务“启动成功”必须以**真实目标会话绑定成功**为前提；只写状态文件不算启动成功

## 2. 可见进度的定义
满足以下三条才算一条有效进度：
1. 用户所在会话能看到
2. 内容说明了“正在看什么 / 刚确认什么 / 下一步是什么”
3. 成功发送后才回写 `last_progress_sent_at`

仅仅生成 payload，不算可见进度。

## 3. 发送真值
区分三种状态：
- 已生成消息
- 已尝试发送
- 已成功送达目标会话

字段约定：
- `last_progress_attempt_at`: 尝试发送时间
- `last_progress_sent_at`: 成功发送时间
- `last_progress_send_error`: 最近失败原因
- `last_progress_at`: 最近一次确认用户已收到进度的时间

## 4. 前台主路径
只要任务在 `analyzing` 或 `executing`：
- 默认每 `5m` 必须出现一条短进度
- 当前执行流自己负责发出，不依赖 cron/watchdog 作为主路径
- 长任务一旦开始，后续每次继续推进前，若距上次可见进度已超 `3m`（或任务自己的 `progress_every`），必须先发一条短进度，不能先做别的
- 推荐把 `work_cycle_tick.py --task "<任务名>" --step "<这一轮动作>"` 当成每轮推进后的固定钩子
- `foreground_tick.py` 是单任务前台心跳入口，`work_cycle_tick.py` 是更贴近真实执行流的循环钩子
- `emit_foreground_due.py` 是“自动触发器骨架”：扫描所有到点前台任务，产出带 `sessionKey` 与 `session_label` 的前台自动消息事件，供宿主或自动化接入
- `dispatch_foreground_due.py` 把这些事件整理成 dispatcher 计划；真正 `sessions_send` 仍需由 OpenClaw tool/agent 层执行
- `sessions_send timeout` 必须记为 `unknown`，不能直接记成 `failed`
- 同一 `message_hash` 若最近仍处于 `unknown` 冷却窗口内，`emit_foreground_due.py` 必须跳过，避免重复发
- 如果返回 `must_send_now: true`，这代表**必须立即发送**，不是建议动作
- 前台心跳应默认发往该任务绑定的真实 `sessionKey`；不要把项目边界标签误当成真实可发送会话
- 成功后必须 `touch-progress`；失败后必须 `mark-progress-attempt`
- 若前台心跳连续触发仍未送达，应转 `blocked`

## 5. 自动触发与后台兜底
前台自动触发骨架：
- `emit_foreground_due.py` 扫描 `watchdog.py check --json` 中的 `progress` 项
- 为每个到点任务构造带真实 `sessionKey` 的 `delivery: session` 事件
- `dispatch_foreground_due.py` 再把事件整理成 dispatcher 计划
- 只有 OpenClaw tool/agent 层真正 `sessions_send` 成功后，才能执行 `touch-progress`
- 如果发送失败，必须执行 `mark-progress-attempt`

审计/回收兜底只处理这些情况：
- `waiting` 到检查点
- `analyzing` 停留过久
- `executing` 超出检查窗口
- 长时间没有可见输出

当前改造阶段新增约束：
- 长任务锁已从“全局单例”升级为“每会话单例”
- 同一 `origin_session_key` 不得同时持有多个长任务
- 不同会话允许各自持有一个长任务
- 后续 keepalive / recovery / foreground 消息都应逐步改为只认 `origin_session_key`

## 6. 失败判定
出现以下任一情况，视为 skill 本轮失效：
- 超过 `progress_every` 没有任何可见进度
- 发送失败但没有记录 `last_progress_send_error`
- 只生成 payload 就宣称“已经提醒”
- 回收脚本检测到了任务，但没有真正尝试发送
- 只执行了 `task_state.py set`，却没有通过 `validate_task_start.py` 校验就宣称“已进入长任务模式”或“已开启长任务模式”

## 7. 发布口径
发布时只能承诺已经稳定实现的能力。
若“自动可见进度”尚未稳定，就只能写成：
- 状态登记
- 前台进度协议
- 后台回收辅助

不能写成全自动、稳定提醒、完全闭环。

## 8. 可发布约束
为了让别人安装后可直接使用，发布包必须满足：
- 不包含运行态文件：`.task-state.json`、`watchdog.log`、`__pycache__/`、`*.pyc`
- 不依赖任何固定机器路径或固定用户目录
- 不依赖固定会话 key；`origin_session_key` 必须来自实际任务登记
- 若缺少 `origin_session_key`，应报错，不允许偷偷 fallback 到某个默认会话
- `openclaw` 可执行文件路径、sessions 索引路径、日志输出路径都应允许通过环境变量覆盖
- 自动续跑必须显式开关控制；默认应只生成计划，不自动后台拉起 agent
- 默认日志输出不要污染 skill 根目录
- 文档中区分“生成事件”“尝试发送”“成功送达”，不要把生成 payload 写成已经送达
�
�经送达
��已经送达
�
�经送达

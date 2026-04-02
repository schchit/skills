# 长任务状态字段

## 存储位置
默认状态文件：
- `skills/long-run-mode/.task-state.json`

## 字段
- `task`: 任务名，建议稳定不乱改。
- `session`: 兼容保留字段；当前应视为人类可读会话名的旧镜像，不应用于真实发送目标判断。
- `session_label`: 当前负责推进的可读会话名/标签；给人看，不等于真实可发送会话。
- `origin_session_key`: 任务真实绑定的会话 key；前台心跳、恢复、保活续跑都应优先使用它。对 `analyzing|executing|waiting` 这类“已启动态”，缺少它应直接报错，不允许只登记状态却宣称已启动。
- `state`: `analyzing|executing|waiting|blocked|handoff|done`
- `goal`: 任务目标。
- `done_when`: 完成条件。
- `blocked_when`: 阻塞条件。
- `boundary`: 所属项目边界。
- `next_check`: 下次检查点。
- `note`: 当前备注/下一步。
- `updated_at`: 最近更新时间（ISO-8601）。
- `progress_every`: 期望的前台可见进度间隔，默认 `5m`。
- `active_long_runs_by_session`: 锁表；键是 `origin_session_key`，值是当前持有该会话长任务锁的任务名。
- `last_progress_at`: 最近一次确认“用户已收到进度”的时间。
- `last_progress_attempt_at`: 最近一次尝试发送进度的时间。
- `last_progress_sent_at`: 最近一次成功发送进度的时间。
- `last_progress_send_error`: 最近一次进度发送失败原因；成功后应清空。

## 使用建议
- 同一任务名反复 `set` 视为更新，不新建重复记录。
- 状态一变就更新，不要等任务做完再补。
- `next_check` 可写绝对时间，也可先写 `10m`、`30m` 这类相对描述，后续由 watchdog 决定是否需要标准化。
- `handoff` 用于明确转派到其他会话，而不是“暂时不管”。
- 状态文件现已支持 `active_long_runs_by_session`：表示“每个真实会话当前持有的长任务锁”。同一 `origin_session_key` 同时只允许一个长任务；不同会话可各自持有一个。

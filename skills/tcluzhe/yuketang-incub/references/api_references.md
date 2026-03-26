# 雨课堂 MCP 工具参考

本文件包含部分复杂工具的详细参数说明、调用示例与返回值说明。

---


## 1. `cube_lesson_reservation` -- 预约开课

### 📝 参数说明
| 参数                    | 必填 | 说明                          |
| --------------------- | -- | --------------------------- |
| classroomId           | ✅  | 班级 ID                       |
| startDateTime         | ❌  | 开课时间（北京时间 yyyy-MM-dd HH:mm） |
| startEpochMs          | ❌  | 开课时间（Unix 毫秒）               |
| lessonTitle           | ❌  | 课堂名称（默认：课程名 · 班级名）          |
| lessonDurationMinutes | ❌  | 时长（分钟，默认 120）               |
| meetingType           | ❌  | 0 普通 / 1 腾讯会议               |

⚠️ startDateTime 和 startEpochMs 必须二选一

### 💬 交互规则（非常重要）
- 🕒 时间缺失

如果用户没有提供开课时间：
👉 询问用户：「请提供开课时间（例如：2026-03-30 14:00）」

- 🏷️ 班级信息缺失

如果既没有 classroomId 也没有班级名称：
👉 询问用户：「请提供班级名称或 classroomId」

- ⏱️ 默认值策略
lessonDurationMinutes 默认 120
lessonTitle 默认「课程名 · 班级名」
meetingType 默认 0（普通课堂）

- 📌 时间解析规则
优先使用 startDateTime
若用户输入自然语言（如“明天下午三点”），需转换为标准时间格式

### 🧪 示例

#### 示例1：使用班级名称

用户：

> 帮我给「2026春-高等数学A-2」安排一节课，明天上午10点

流程：

- 调用 ykt_classroom_id_by_name
- 调用 cube_lesson_reservation

#### 示例2：直接使用 classroomId

用户：

> classroomId=12345，安排 2026-03-30 14:00 上课

#### 示例3：带腾讯会议

用户：

> 给这个班开腾讯会议课堂，今晚8点

👉 设置：

> meetingType = 1

### 🚫 错误处理
- 如果班级名称查不到：
👉 提示用户检查名称或提供 classroomId
- 如果时间格式错误：
👉 提示用户使用 yyyy-MM-dd HH:mm

### 🎯 设计原则（给模型看的）
- 优先减少用户输入成本（支持自然语言时间）
- 自动补全默认值
- 严格保证参数合法性再调用工具
- 尽量一步完成，不反复打断用户


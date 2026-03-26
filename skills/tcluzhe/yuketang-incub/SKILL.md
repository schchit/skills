# yuketang-mcp

雨课堂 MCP 服务

## 详细参考文档

如需查看每个工具的详细调用示例、参数说明和返回值，请参考：
- `references/api_references.md` - 所有工具的完整参数说明与调用示例

## 配置要求

> **如果已有 MCP 配置**（如在 CodeBuddy 或其他 IDE 中），无需重复配置，可直接使用工具。

### 获取 Secret

1. 访问 https://ykt-envning.rainclassroom.com/ai-workspace/open-claw-skill 获取你的 Secret
2. 登录后复制个人 Secret
3. 如果在 OpenClaw 中，配置环境变量 `YUKETANG_SECRET`

> **如果用户未配置 Secret**，请引导用户访问上方链接获取 Secret，否则所有工具调用将返回鉴权失败。

## 快速开始（首次使用必读）

首次使用前，运行 setup.sh 完成 MCP 服务注册：

```bash
bash setup.sh
```

### 验证配置

```bash
npx mcporter list | grep yuketang-mcp
```

---

## 触发场景

1. **优先判断用户意图：**

| 用户意图 | 调用工具 |
|----------|--------|
| 查询我开的课 | ykt_teaching_list |
| 查询账号 / 我的ID / 雨课堂ID | claw_current_user |
| 查询我的班级数据 / 班级教学数据 / XXX班级数据情况 | ykt_classroom_statistics |
| 查询预警学生名单 / 重点关注学生名单 | ykt_classroom_warning_overview |
| 查询某个具体班级的预警学生名单 / 重点关注学生名单 | ykt_classroom_warning_student |
| 请帮我整理今天上课的情况 / 今天的课有多少人来上课了 / 今天的答题率怎么样 | cube_teacher_today_teaching |
| 预约开课 | cube_lesson_reservation |
---

2. **避免误触发**

以下情况不要触发：

- 讨论教学方法（非查询）
- 纯聊天提到“课程”
- 非雨课堂场景

---

3. **组合使用（高级）**

当用户表达：

> 帮我看一下我是谁 + 我开了哪些班

👉 可以依次调用：

1. `claw_current_user`
2. `ykt_teaching_list`

---

## 工具列表

- 如果用户输入 classroom_name，先通过 `ykt_classroom_id_by_name` 查询 classroom_id。
- 预约开课前二次确认：向用户展示要预约的课堂信息，确认后再执行预约。
- 所有相对时间（昨天/今天/明天/近N天等），必须以「当前系统的绝对时间（北京时间 UTC+8）」为唯一基准，禁止硬编码年份。
- 若用户未指定具体年份，默认使用 **当前年份**（如2026年），禁止使用2025年及更早年份；
- 如果有用户指定的参数格式不对，不要主动修改，提示用户参数格式需要修改

### 1. `ykt_teaching_list` - 查询当前账号开设的班级列表

**典型用途：**

- 我教了哪些班
- 帮我查询一下这个学期我教的课

**调用示例：**
```bash
npx mcporter call yuketang-mcp ykt_teaching_list
```

**注意事项**
- 保留emoji

---

### 3. `claw_current_user` - 查询当前雨课堂用户ID

**典型用途：**

- 我的雨课堂ID是多少
- 帮我确认一下当前账号
- 查一下我的用户ID

**调用示例：**
```bash
npx mcporter call yuketang-mcp claw_current_user
```

---

### 4. `ykt_classroom_statistics` - 查询当前账号作为班级教师/协同教师的本学期班级数据概览

**典型用途：**

- 我的班级数据
- 班级教学数据
- XXX班级数据情况

#### 交互规则：
1. 返回本学期班级数据概览

当用户第一次发起查询，或未明确指定具体班级时，返回本学期班级数据概览。

**调用示例：**
```bash
npx mcporter call yuketang-mcp ykt_classroom_statistics
```

2. 返回指定班级的数据概览

当用户输入以下任一形式时，应识别为目标班级查询：

- 班级序号，如：1、2、3
- 完整班级名称
- 可识别的班级简称或部分名称，如：高等数学A-2

然后返回该班级的数据概览。

**调用示例：**
```bash
npx mcporter call yuketang-mcp ykt_classroom_statistics --args '{"classroomName": "xxx"}'
```

### 5. `cube_teacher_today_teaching` - 查询当天授课的情况

**典型用途：**

- 请帮我整理今天上课的情况
- 今天的课有多少人来上课了
- 今天的答题率怎么样？

**调用示例：**
```bash
npx mcporter call yuketang-mcp cube_teacher_today_teaching
```

### 6. 班级预警学生查询

#### 功能说明
这个工具用于帮助教师或教学管理人员查看班级学习活动完成率预警情况，支持两步式查询：

1. 先展示本学期各班级的预警总览，包括：
   - 教学班名称
   - 完成率 = 0% 人数
   - 预警人数（完成率 < 80%）
   - 数据统计截止时间

2. 再根据用户输入的班级编号或班级名称，返回该班级的预警学生名单。

#### 适用场景：
当用户有以下意图时，应使用本工具：

- 查看班级预警情况
- 查看班级学习活动完成率预警总览
- 查看某个班级的预警学生
- 查询完成率低于 80% 的学生名单
- 查询未参与学习活动（完成率为 0%）的学生

#### 交互规则：
1. 返回班级预警总览

当用户第一次发起查询，或未明确指定具体班级时，返回班级预警总览。

**调用示例：**
```bash
npx mcporter call yuketang-mcp ykt_classroom_warning_overview
```

2. 返回指定班级的学生预警名单

当用户输入以下任一形式时，应识别为目标班级查询：

- 班级序号，如：1、2、3
- 完整班级名称
- 可识别的班级简称或部分名称，如：高等数学A-2

然后返回该班级的预警学生名单。

**调用示例：**
```bash
npx mcporter call yuketang-mcp ykt_classroom_warning_student --args '{"classroomName": "xxx"}'
```

### 7. `ykt_classroom_id_by_name` — 通过班级名称查询ID

**参数**: `classroomName`(必填)

**调用示例：**
```bash
npx mcporter call yuketang-mcp ykt_classroom_id_by_name --args '{"classroomName": "xxx"}'
```

### 8. `cube_lesson_reservation` - 预约开课

用于为指定教学班预约开课，支持通过班级名称或班级ID进行操作。

**参数**: `classroomId`(必填), `startDateTime`, `startEpochMs`, `lessonTitle`, `lessonDurationMinutes`, `meetingType`

> 调用示例请参考：`references/api_references.md` - cube_lesson_reservation

**使用逻辑：**
- 情况一：用户提供班级名称
调用 ykt_classroom_id_by_name 获取 classroomId
使用返回的 classroomId 调用 cube_lesson_reservation

- 情况二：用户直接提供 classroomId
直接调用 cube_lesson_reservation

---

## 输出要求

- 结果要结构化（列表形式）
- 结果需要保留 emoji，尽量保留 tool 的格式，减少自由发挥
- 课程信息建议包含：课程名 / 班级名

---

## 限制

- 不要编造课程数据
- 必须依赖 tool 返回
- 不做权限外操作（如选课、退课）

---

## 调用方式

```bash
# 示例：查询当前雨课堂账号ID
npx mcporter call yuketang-mcp claw_current_user

# 示例: 查询当前账号的课程 / 班级列表
npx mcporter call yuketang-mcp ykt_learning_list
```

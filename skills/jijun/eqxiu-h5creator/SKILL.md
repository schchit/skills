---
name: eqxiu-h5creator
description:   易企秀 AIGC H5 创作工具，通过对话引导用户填写信息，自动生成翻页 H5 邀请函、营销海报、表单问卷等作品。
  当用户想要生成/制作/创建 H5 页面时使用此 Skill，包括婚礼邀请函、会议邀请函、年会海报、节日祝福等场景。

  核心功能：
  1. 品类选择——从易企秀支持的 H5 品类中选定（邀请函/海报/表单等）
  2. 风格选择——可选指定视觉风格
  3. 内容生成——根据用户提供的标题、字段信息生成大纲和大纲模板
  4. 输出作品链接——返回可编辑的 H5 链接
  工作流程：品类选择 → 字段填写 → 风格选择（可选）→ 生成 outline → 生成 scene-tpl

  触发词：制作H5、生成H5、创建H5、做一个H5、易企秀、
  H5邀请函、年会H5、婚礼邀请函、会议邀请函、生日祝福H5、
  节日海报H5、H5页面生成、翻页H5怎么做、怎么做一个邀请函H5

summary:   易企秀 AIGC 创作 Skill，通过对话引导用户填写品类、标题、字段信息，
  自动生成翻页 H5 作品。调用 `scripts/eqxiu_aigc_client.py` 执行完整链路。

read_when:
  - 用户提到"制作/生成/创建 H5"、"做个邀请函"、"做一张年会海报"
  - 用户想用易企秀但不知道怎么做、需要 AI 帮助生成 H5
  - 用户描述"我想做一个XX的翻页H5"

---

# 易企秀 AIGC H5 HTTP 调用

- 命令行：`python scripts/eqxiu_aigc_client.py ...`
- 鉴权：客户端支持 `X-Openclaw-Token` 登录、状态校验与自动透传。
- 获取`X-Openclaw-Token`地址：`https://www.eqxiu.com/feedback/pc/skillAccess`


## 调用顺序（必须遵守）

### 认证（推荐先执行）

```bash
# 交互式保存 token 到 ~/.eqxiu/config.json，如果存在token，验证token有效性即可
python scripts/eqxiu_aigc_client.py login

# 校验 token 是否有效
python scripts/eqxiu_aigc_client.py auth status
```

说明：
- `auth status` 返回 `{"success": true, "code": 200, ...}` 代表 token 有效。
- 返回 `{"success": false, "code": 1002, "msg":"认证失败", ...}` 代表 token 无效。
- 也可用 `--access-token` 覆盖配置中的 token。

易企秀链路依赖上游返回字段，**不要**颠倒顺序。

1. **`GET /iaigc/category`** — 列出制作种类。每条含 `categoryId`、`name`、`desc`、`fields`、`twoLevelCategoryId`、`threeLevelCategoryIds`（数组）等。
2. **（可选）`GET /iaigc/style`** — 查风格列表，供 `scene-tpl` 的 `styleId`。需要某条品类里的 `twoLevelCategoryId` 与 `threeLevelCategoryIds` 中的**某一个**三级 id（整数）。支持查询参数 `pageNo`（默认 1）、`pageSize`（默认 20，上限 100）。成功时本服务响应体里的 `data` 与易企秀分页一致：`{ pageNo, pageSize, total, data }`，其中内层 `data` 为模板完整对象数组（每项含 `id`、`productTitle`、`sceneExtract` 等）；选风格时一般用每项的 `id` 作为 `styleId`。
3. **`POST /iaigc/outline`** — 提交 `sceneFields` + `categoryId`（等于所选品类的 `categoryId`）。返回 `imageId`、`outline`、`outlineTaskId`。
4. **`POST /iaigc/scene-tpl`** — 提交与步骤 3 **相同**的 `sceneFields` 与 **相同**的品类 id 作为 `sceneId`，并带上步骤 3 的 `title`（用户给定）、`outlineTaskId`、`outline`；建议带上 `imageId`（来自步骤 3）；若步骤 2 选了模板则带 `styleId`。

对话中向用户确认：`title`、各 field 的文案、是否指定 `styleId`（可先展示 `style` 接口返回的 `id`/`productTitle` 等字段）。

## 构造 sceneFields

- 根据步骤 1 返回条目的 `fields`（及业务说明）组装数组：`[{"id": <整数>, "value": "<字符串>"}, ...]`。
- `id` 必须与品类定义的字段 id 一致；缺字段或错 id 易导致上游失败。

## 客户端脚本

```bash
# 1) 品类列表
python scripts/eqxiu_aigc_client.py category

# 2) 风格（示例 id 需换成品类数据中的真实值）
python scripts/eqxiu_aigc_client.py style --two <twoLevelCategoryId> --three <某个threeLevelCategoryId>

# 3) 仅生成 outline
python scripts/eqxiu_aigc_client.py outline --category-id <categoryId> --fields-json '[{"id":1,"value":"某主题"}]'

# 4) 仅生成 scene-tpl（body 需含完整 JSON，通常由 outline 结果拼装）
python scripts/eqxiu_aigc_client.py scene-tpl --json-file path/to/body.json

# 一键：outline → scene-tpl（同一 categoryId、同一份 sceneFields）
python scripts/eqxiu_aigc_client.py pipeline --category-id <id> --title "作品标题" --fields-json '[...]' [--style-id <可选>]'
```

所有业务子命令都会自动携带 `X-Openclaw-Token`（来源：`--access-token` 或 `~/.eqxiu/config.json`）。

`pipeline` 子命令内部顺序固定为：先 `create_outline`，再 `create_scene_tpl`，并把 `outlineTaskId`、`outline`、`imageId` 自动传入第二步。

## 代理在对话中的建议流程

1. 执行 `category`（或 GET），让用户选定品类；记录 `categoryId` 与 `fields`。
2. 询问用户各字段文案，组装 `sceneFields`。
3. 若需要固定风格：用该品类的 `twoLevelCategoryId` 与选定的三级 id 调 `style`，用户选 `styleId`。
4. 调 `outline`（或 `pipeline` 前半段）；失败则根据 `msg` 重试或改字段。
5. 调 `scene-tpl`（或 `pipeline` 一次性完成）；成功 `data` 一般为 `{"previewUrl":"https://h5.eqxiu.com/s/{code}"}`, "editUrl"：`https://www.eqxiu.com/c/{id}`（以服务实际返回为准），点击链接登陆后就可以编辑了。

## 超时与错误

- `outline`、`scene-tpl` 可能极慢，客户端默认超时 150s；可用 `--timeout` 调整。
- 业务错误时响应体多为 `success: false` 与 `msg`；脚本会以非零退出并打印 JSON。

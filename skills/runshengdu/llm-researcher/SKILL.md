---
name: llm-researcher
description: |
  LLM 论文与项目研究员。分析LLM相关论文和Github项目，
  并按指定类目进行分类整理。使用场景：(1) 获取 LLM 领域最新进展，(2) 追踪特定方向的最新研究
compatibility: Requires network access, MINERU_API_KEY for PDF parsing, and Python (for scripts/pdf_to_md.py)
metadata:
   author: durunsheng
   version: "1.0.5"
   clawdbot:
      requires:
         env:
         - MINERU_API_KEY
---

## 执行前置确认（必须）
1.在按本skill开始任何步骤前，必须先询问用户：是否已在当前环境安装 Python，并说明用途：运行 `scripts/pdf_to_md.py` 将论文 PDF 转为 Markdown（终端中需能执行 `python` 或 `python3`）。明确告知没有 Python 则无法按规范执行论文 PDF 解析，可请用户安装 Python 后再继续，或在与用户达成一致的前提下仅做不涉及 `pdf_to_md.py` 的降级（例如只做 GitHub 条目、或跳过需 PDF 的论文条目），并在过程说明与最终报告中写明该限制。
2.询问用户对于每个数据源获取的条目数量。
3.询问用户调用脚本从PDF链接提取markdown是用哪个参数
   - `introduction`：仅返回严格匹配 `# Introduction` 一级标题的 Markdown 内容
   - `all`：返回整篇论文转换后的完整 Markdown 内容
4.输出报告的语言。
在未完成上述确认前，不要开始执行本 skill 的核心流程。

## 默认数据源
1. **alphaxiv** - 
   - `https://www.alphaxiv.org/?sort=Hot&interval=7+Days`
   - `https://www.alphaxiv.org/?source=GitHub&interval=7+Days&sort=Hot`
2. **GitHub Trending** - `https://github.com/trending?since=weekly`

- 如果用户没有指定数量，默认每个数据源最多提取 `10` 个条目。
- 只使用以上默认数据源，不额外扩展新的数据源网址。

## 工具使用优先级
获取网页中的论文列表、项目列表、论文链接和 `arXiv ID` 时，按以下顺序尝试：
1. **浏览器工具优先**：动态网页优先使用浏览器打开、滚动、点击和观察页面内容。如果网页打不开，通常是因为网络原因，多尝试2次一般能打开
2. **网页抓取工具次之**：如果浏览器无法稳定拿到内容，再尝试网页抓取。
3. **网页转 Markdown 兜底**：最后再使用 `https://r.jina.ai/example.com` 读取页面 Markdown。
4. **如果以上方式都不可用**：就跳过，在最终报告里写明原因。


## 总体流程
### 阶段 1：发现条目并建立任务队列
1. 对论文页面，优先从网页内容中拿到 `arXiv ID`。
2. 对GitHub项目，记录项目标题和仓库 URL，不要求 `arXiv ID`。
3. 去重规则：
   - 论文优先按 `arXiv ID` 去重
   - GitHub 项目优先按仓库 URL 去重
   - 如果缺少唯一标识，再按标题去重
4. 将待分析条目整理为当前运行内的任务队列。

### 阶段 2：逐条执行任务
- 维护任务队列，顺序处理 `pending` 条目，无需启动 subagent。
- 每开始处理一个条目，先执行 `attempt += 1`。
- 处理完成后，将结果写入成功或失败集合：
  - 成功：`status = "done"`，并写入 `completedAt`
  - 失败：`status = "failed"`，并写入 `error`、`completedAt`
- 单个任务失败不影响后续任务，应继续处理剩余条目。

## 执行规则
直接完成每个条目的内容获取、分析、分类和结果汇总。


### 论文任务
如果 `source` 是 `arxiv`：
1. 优先使用已有的 `arXiv ID`。
2. 如果拿到了 `arXiv ID`，构造论文 PDF 链接：
   - `https://arxiv.org/pdf/{arxiv-id}.pdf`
3. 调用脚本从 PDF 链接提取 markdown，使用 `--range` 显式传入用户选择：
   - `python scripts/pdf_to_md.py https://arxiv.org/pdf/{arxiv-id}.pdf tmp_llm_research/{arxiv-id}.md --range introduction`
   - `python scripts/pdf_to_md.py https://arxiv.org/pdf/{arxiv-id}.pdf tmp_llm_research/{arxiv-id}.md --range all`
4. `--range` 参数说明：
   - `introduction`：仅返回严格匹配 `# Introduction` 一级标题的 Markdown 内容
   - `all`：返回整篇论文转换后的完整 Markdown 内容
5. 读取 `tmp_llm_research/{arxiv-id}.md`。
6. 基于提取出的论文 markdown 分析论文核心问题、方法、贡献、适用场景和局限性。
7. 严格按照 `references/categories.md` 中的大类进行分类。
8. 如果始终拿不到 `arXiv ID`，则不要伪造 ID，也不要直接用网页摘要代替 markdown；应将该任务标记为 `failed`，并在错误里注明“无法稳定获取 arXiv ID”。

### GitHub 项目任务
如果 `source` 是 `github`：
1. 优先使用浏览器工具读取仓库首页、README、项目说明。
2. 如果浏览器工具拿不到足够内容，再尝试网页抓取工具。
3. 如果仍然不稳定，再使用 `r.jina.ai` 版本页面作为兜底。
4. 如果以上方式都受限，但仓库首页还能看到仓库名、简介、话题、页面结构中的少量文本，允许基于这些可见信息给出“简版分析”。
5. 用简单易懂的语言解释论文/项目内容；信息完整时尽量详细，信息受限时要明确说明推断边界。
6. 严格按照 `references/categories.md` 中的大类进行分类。

### 分析结果格式

在当前运行内存中维护成功与失败结果集合，用于最终汇总。结果建议至少包含以下字段：

```json
{
  "id": "{序号}",
  "title": "{标题}",
  "url": "{URL}",
  "source": "{arxiv|github}",
  "arxivId": "{arXiv ID，如果是 GitHub 则为 null}",
  "category": "{类目名称}",
  "authors": "{作者或机构，未知可写 Unknown}",
  "analysis": "{用简单易懂的语言解释内容，越详细越好}",
  "status": "{done或failed，如果是failed需要列上原因}",
  "attempt": "{当前尝试次数}",
  "completedAt": "{ISO 时间戳}"
}
```

## 最终报告
当所有任务完成后，输出最终 Markdown 报告到 `output` 文件夹，文件名格式为 `YYYYMMDDHHmm.md`。
最终报告成功写入后，需要删除整个 `tmp_llm_research` 文件夹。
最终报告必须包含：

- `# Report Summary`，至少包含：`Total`、`Success`、`Failed`、`Retried Success`。
- `# Details`，必须按 `category` 聚合，每个分类下的条目至少包含：`title`、`url`、`source`、`authors`、`analysis`。
- `# Trending`，需要总结本批论文和项目体现出的共同趋势、热门方向和潜在变化。


## 注意事项
- 单个任务失败不影响其他任务，继续推进剩余任务。
- 所有原始链接必须保留，便于最终报告追溯。
- 只有在最终 Markdown 报告成功写入后，才可以清理 `tmp_llm_research`，避免影响最终汇总。
- 如果运行环境限制导致部分条目只能获得有限信息，最终报告中应如实说明，不要伪装成完整深度分析。

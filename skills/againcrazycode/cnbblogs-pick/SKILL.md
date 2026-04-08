# CNBLOGS 精华内容抓取技能

## 功能描述

抓取博客园（cnblogs.com）精华区内容，支持分页、批量下载标题和正文。

## 使用方法

### 基本用法

```bash
# 抓取第 1 页，保存所有文章到指定目录
openclaw cnblogs-pick --page 1 --output-dir /path/to/output

# 抓取前 3 页，保存所有文章
openclaw cnblogs-pick --pages 3 --output-dir /path/to/output

# 抓取指定 URL 的精华列表
openclaw cnblogs-pick --url https://www.cnblogs.com/pick/ --pages 2
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--url` | string | 否 | https://www.cnblogs.com/pick/ | 精华列表页 URL |
| `--page` | int | 否 | 1 | 单页抓取页数（仅当 --pages 未指定时有效） |
| `--pages` | int | 否 | 1 | 总页数（优先于 --page） |
| `--output-dir` | string | 否 | ~/.openclaw/workspace/user_cnglobs/ | 输出目录 |
| `--agent` | string | 否 | Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0 | User-Agent |

### 输出格式

每篇文章保存为独立文件，命名格式：

```
{标题}.txt
```

标题中的特殊字符会被替换为下划线。

## 工作流程

1. **获取列表页**：使用 curl 下载指定页数的精华列表
2. **提取链接**：解析 HTML，提取所有 `post-item-title` 类链接
3. **下载详情**：逐个打开详情页面
4. **提取正文**：获取 `cnblogs_post_body` 内容并去除 HTML 标签
5. **保存文件**：按标题命名保存到输出目录

## 示例

```bash
# 抓取前 5 页精华内容
openclaw cnblogs-pick --pages 5 --output-dir /tmp/cnb-pick

# 查看结果
ls -lh /tmp/cnb-pick/
```

## 依赖工具

- `curl` - HTTP 请求
- `grep -oP` - Perl 正则表达式
- `sed` - 文本处理

## 注意事项

1. 部分文章可能因反爬机制失败
2. 大页面可能超出 token 限制
3. 建议先测试单页再批量处理

## 更新日志

- v1.0.0: 初始版本，支持单页抓取
- v1.1.0: 支持多页批量抓取
- v1.2.0: 优化错误处理和日志输出
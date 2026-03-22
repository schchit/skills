# obsidian-knowledge-organizer

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-cjke84%2Fobsidian--knowledge--organizer-blue?logo=github)](https://github.com/cjke84/obsidian-knowledge-organizer)

一个面向 Obsidian 知识库工作流的整理工具，用于把文章、链接和草稿整理成结构化、可直接落盘的笔记。

## 它会做什么

- 提取文章内容
- 检查是否重复并返回结构化决策结果（decision）
- 生成标签、摘要和元数据
- 自动下载图片到 `assets/` 并保留可读引用，支持 `src` / `data_src` / `data-original` / `data-lazy-src` / `srcset` / `url` / `image_url` / `original` 等常见字段
- 支持公众号文章、小红书链接和普通网页
- 输出可直接写入 Obsidian 的笔记

## 能力概览

- OpenClaw 和 Codex 可用的 Obsidian 原生整理工具
- 面向 vault 工作流的成品笔记生成器
- 按标签契约校验标签（tags）
- 推荐可直接链接的相关文章

## 适用场景

- 存入知识库
- 整理文章
- 打标签
- 归档
- 生成摘要
- 推荐相关文章

## `draft.images` 示例

```yaml
images:
  - path: /absolute/path/to/local.png
    alt: 本地图片
  - src: https://example.com/cover.png
    alt: 远程图片
  - srcset: https://example.com/cover-1x.png 1x, https://example.com/cover-2x.png 2x
    alt: 响应式图片
```

`path` 用于本地文件，`src` / `data_src` / `data-original` / `data-lazy-src` / `original` 等用于远程图片；`srcset` 会优先选数值更高的候选。

## 快速使用

```bash
pytest -q
python scripts/check_duplicate.py "新标题" --content "$(cat draft.md)" --json
python scripts/find_related.py alpha beta --title "新标题" --json
```

## 相关入口

- [English README](README_EN.md)
- [安装说明](INSTALL.md)
- [GitHub 仓库](https://github.com/cjke84/obsidian-knowledge-organizer)

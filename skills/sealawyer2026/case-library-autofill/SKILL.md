---
name: case-library-autofill
description: 九章案例库自动填充工具 - 基于公开信息（裁判文书、监管公告、新闻报道）自动生成结构化案例，支持批量导入和智能补全。用于快速扩展技能案例库。
---

# 九章案例库自动填充工具

基于AI和公开数据源，自动生成高质量法律案例并填充到技能案例库。

## 核心功能

### 1. 案例爬取 (crawl)
从公开数据源爬取案例：
- 中国裁判文书网
- 国家企业信用信息公示系统
- 监管公告（网信办/市监局/证监会等）
- 新闻报道和行业媒体
- 专业数据库（威科先行、北大法宝等）

### 2. 案例生成 (generate)
基于模板自动生成案例：
- 典型场景生成
- 参数化变体
- 合规/违规双版本
- 跨境对比案例

### 3. 结构化转换 (convert)
将非结构化内容转为标准格式：
- 裁判文书解析
- 公告信息提取
- 新闻内容提炼
- 统一字段映射

### 4. 质量审核 (review)
自动审核案例质量：
- 完整性检查
- 准确性验证
- 重复性检测
- 合规性审查

## 使用方法

```bash
# 爬取指定领域案例
jiuzhang-cli autofill crawl --source court --category algorithm_filing --limit 100

# 批量生成典型案例
jiuzhang-cli autofill generate --skill zhang-ai-law --category genai_compliance --count 50

# 转换已有文档
jiuzhang-cli autofill convert --input ./raw_cases/ --output ./structured/

# 质量审核
jiuzhang-cli autofill review --library ./case-library.json

# 一键填充
jiuzhang-cli autofill pipeline --skill zhang-chip-law --target 100
```

## 数据源配置

`~/.jiuzhang/autofill.yaml`:
```yaml
sources:
  court:
    enabled: true
    url: https://wenshu.court.gov.cn
    rate_limit: 10/min
    
  regulatory:
    cac: https://www.cac.gov.cn
    samr: https://www.samr.gov.cn
    csrc: https://www.csrc.gov.cn
    
  news:
    enabled: true
    sources:
      - 21世纪经济报道
      - 财新网
      - 第一财经

generation:
  ai_model: deepseek-r2
  batch_size: 10
  quality_threshold: 0.85
  
output:
  format: json
  encoding: utf-8
  pretty_print: true
```

## 案例生成模板

`references/templates/`:

### 算法备案模板
```
案情: {平台类型}在提供{服务类型}时，未按照《{法规名称}》要求，{违规行为}。
法律问题: {问题1}, {问题2}
裁决: {处理结果}
处罚: {处罚措施}
合规启示: {建议}
```

### EAR出口管制模板
```
案情: {公司类型}向{目的地}出口{产品类型}，{违规行为}。
法律问题: {问题1}, {问题2}
ECCN: {编码}
裁决: {处理结果}
处罚: {处罚措施}
合规启示: {建议}
```

## 目录结构

```
case-library-autofill/
├── SKILL.md
├── scripts/
│   ├── crawl.py        # 数据爬取脚本
│   ├── generate.py     # 案例生成脚本
│   ├── convert.py      # 格式转换脚本
│   ├── review.py       # 质量审核脚本
│   └── pipeline.py     # 一键执行脚本
└── references/
    ├── sources.md      # 数据源清单
    ├── templates/      # 案例模板
    ├── schema.md       # 案例字段规范
    └── examples/       # 示例案例
```

## 案例质量评分

自动评估维度：
- **完整性** (30%): 必填字段齐全
- **准确性** (30%): 法律引用正确
- **实用性** (20%): 合规建议可执行
- **时效性** (10%): 案例日期近3年
- **独特性** (10%): 与已有案例不重复

总分≥80分自动入库，60-80分人工复核，<60分废弃。

## 注意事项

1. **版权合规**: 爬取内容仅用于内部案例库建设，不对外传播
2. **数据脱敏**: 自动脱敏企业名称、个人信息
3. **人工复核**: 高风险领域案例需人工审核后入库
4. **更新机制**: 定期更新案例库，淘汰过时案例

---
**版本**: 1.0.0  
**作者**: 九章法律AI团队  
**分类**: infrastructure

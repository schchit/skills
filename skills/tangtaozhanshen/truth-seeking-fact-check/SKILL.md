# Truth (求真) - AI事实核查技能

## 简介

AI Content Authenticity Verification Tool.
事实核查技能，6层深度核查（含区块链存证验证），识别AI幻觉、虚假信息，输出可信度评分和问题标注。适配2核2G环境，支持批量核查。可简称truth使用。

## 功能

- ✅ 识别AI生成幻觉内容
- ✅ 识别虚假信息和夸大宣传
- ✅ 输出0-10可信度评分
- ✅ 标注问题句子，给出具体位置和原因
- ✅ 提供改进建议
- ✅ 新增：区块链存证验证，验证公开链上内容哈希
- ✅ 新增：多数据源fallback，自动切换可用源
- ✅ 新增：评分维度明细输出，更透明
- ✅ 适配2核2G环境，最大并发=2，不占用过多资源
- ✅ 合规拦截敏感内容

## 安装

```
clawhub install tangtaozhanshen/truth-seeking-fact-check
```

## 使用

```python
from truth.main import TruthSkill
checker = TruthSkill()
result = checker.check("需要核查的文本")
print(f"可信度评分: {result.credibility_score}/10")
print(f"结论: {result.conclusion}")
print(f"问题句子: {result.problematic_sentences}")
```

## 作者

tangtaozhanshen

## 许可

MIT-0

## 链接

<https://clawhub.ai/tangtaozhanshen/truth-seeking-fact-check>

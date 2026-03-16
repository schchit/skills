# 模型 Token 与文字比例测试报告

**生成时间**: 2026-03-16 11:21:52
**测试字符数**: 8927
**模式**: 本地近似

| 模型 | 字符数 | Token 数 | 1 token ≈ 多少字符 | 状态 |
|------|--------|----------|-------------------|------|
| anthropic/claude-sonnet-4-6 | 8927 | 3068 | 2.9097 | ✓ |
| anthropic/claude-sonnet-4-5 | 8927 | 3068 | 2.9097 | ✓ |
| anthropic/claude-opus-4.6 | 8927 | 3068 | 2.9097 | ✓ |
| openai/gpt-5.2-codex | 8927 | None | None | ✗ Tokenization failed: tiktoken is required for OpenAI models. Install with: pip install tiktoken (model: openai/gpt-5.2-codex) |
| google/gemini-3.1-pro-preview | 8927 | 3046 | 2.9307 | ✓ |
| z-ai/glm-5 | 8927 | 2877 | 3.1029 | ✓ |
| volcengine/doubao-seed-2-0-pro | 8927 | 3262 | 2.7367 | ✓ |
| moonshot/kimi-k2.5 | 8927 | 2970 | 3.0057 | ✓ |
| minimax/MiniMax-M2.5 | 8927 | 2844 | 3.1389 | ✓ |
| deepseek-v3.2 | 8927 | 3037 | 2.9394 | ✓ |

## 说明

- **1 token ≈ 多少字符**：字符数 / token 数，数值越大表示 1 个 token 能表示更多文字
- 中文通常比英文消耗更多 token
- 不同模型使用不同 tokenizer，比例会有差异

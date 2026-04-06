# Learning Optimizer - 学习优化器

分析学习模式，识别低效环节，提供优化建议

## Quick Start

```bash
# 分析学习模式
python3 scripts/main.py analyze --schedule "每天2小时" --subjects "数学,英语"

# 获取优化建议
python3 scripts/main.py optimize --problem "容易分心" --current "长时间连续学习"

# 时间分配建议
python3 scripts/main.py allocate --total 120 --priorities "数学高,英语中"
```

## Commands
- `analyze` - Analyze study patterns
- `optimize` - Get optimization suggestions
- `allocate` - Time allocation plan

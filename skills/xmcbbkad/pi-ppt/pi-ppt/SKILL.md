---
name: pi-ppt
description: 使用PI(Presentation Intelligence)提供的服务生成PPT.
---

# Pi PPT 生成

## 功能
1. 生成PPT.

## 鉴权配置
使用 PI 的服务前，须先从 PI 平台获取 `PIPPT_APP_ID` 与 `PIPPT_APP_SECRET`,并设置为环境变量。
```bash
# Pick shell rc file (adjust path if needed)
if [ -n "${ZSH_VERSION}" ]; then
  SHELL_RC="${ZDOTDIR:-$HOME}/.zshrc"
elif [ -n "${BASH_VERSION}" ]; then
  SHELL_RC="$HOME/.bashrc"
  [ ! -f "$SHELL_RC" ] && [ -f "$HOME/.bash_profile" ] && SHELL_RC="$HOME/.bash_profile"
else
  SHELL_RC="$HOME/.profile"
fi
touch "$SHELL_RC"

# Both env vars required; prompt for missing values, export, then append to SHELL_RC
if [ -z "${PIPPT_APP_ID}" ] || [ -z "${PIPPT_APP_SECRET}" ]; then
  echo "PIPPT_APP_ID and/or PIPPT_APP_SECRET is missing. Get them from the PI console, then enter only what is asked below:"
  [ -z "${PIPPT_APP_ID}" ] && read -r -p "PIPPT_APP_ID: " PIPPT_APP_ID
  [ -z "${PIPPT_APP_SECRET}" ] && { read -r -s -p "PIPPT_APP_SECRET (hidden): " PIPPT_APP_SECRET; echo; }
  export PIPPT_APP_ID PIPPT_APP_SECRET

  {
    echo ""
    echo "# --- PI PPT credentials (added $(date +%Y-%m-%d)) ---"
    echo "export PIPPT_APP_ID=\"${PIPPT_APP_ID}\""
    echo "export PIPPT_APP_SECRET=\"${PIPPT_APP_SECRET}\""
    echo "# --- PI PPT credentials (end) ---"
  } >> "$SHELL_RC"

  echo "Appended to: $SHELL_RC"
  echo "Run in this session: source \"$SHELL_RC\" — new terminals will load these automatically."
  echo "If you run this script multiple times, edit the file to remove duplicate blocks and keep a single export pair."
fi
```

## 生成PPT
执行以下脚本
```bash
python <skill-dir>/scripts/generate_pi_ppt.py --content  --language --cards --file
```
其中输入参数:
   content(str, 必填): 主题和描述，比如"生成一个关于中国GPU厂商介绍的PPT，商务严肃风格"。
   cards(int, 非必填): 期望的PPT页数，比如 10, 默认为8。如果要根据上传的文档生成PPT，则不能指定PPT页数，因为PPT页数根据上传的文档内容决定。
   language(str, 比填): 期望的PPT的语言，'zh': 中文，'en': 英文，默认为'zh'.
   file(str, 可填): 要上传的文档的路径，比如："/Users/jack/download/weekly_report_20250304.doc", 支持的文档类型包括: .doc/.docx/.txt/.md/.pdf/.pptx/.ppt, 不支持其他类型的文件类型，且仅限于上传一个文档。 

完整的命令举例:

**根据上传文档生成**（页数由文档内容决定，不要传 `--cards`）：

```bash
python "<skill-dir>/scripts/generate_pi_ppt.py" \
  --content "根据附件内容生成一份结构清晰的商务汇报PPT" \
  --language zh \
  --file "/Users/you/Documents/quarterly_review.docx"
```

**根据一句话 / 主题生成**（可指定页数）：

```bash
python "<skill-dir>/scripts/generate_pi_ppt.py" \
  --content "生成一个关于中国GPU厂商介绍的PPT，商务严肃风格" \
  --language zh \
  --cards 10
```
## 注意
- 生成一个PPT大概要耗时2-3分钟，需要提醒用户耐心等待。

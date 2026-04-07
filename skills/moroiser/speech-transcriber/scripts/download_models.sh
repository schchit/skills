#!/bin/bash
#==============================================================================
# Whisper Model Downloader
# 自动下载 Whisper 模型到 models/ 目录
#==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MODELS_DIR="${SKILL_DIR}/models"
WORKSPACE_MODELS_DIR="$HOME/.openclaw/workspace/stt/models"

echo "=========================================="
echo " Whisper Model Downloader"
echo "=========================================="
echo ""
echo "Skill 目录: ${SKILL_DIR}"
echo "模型目录:   ${MODELS_DIR}"
echo ""

# Create directories
mkdir -p "${MODELS_DIR}"
mkdir -p "${WORKSPACE_MODELS_DIR}"

# Model size guide:
# tiny=39M, base=74M, small=244M, medium=769M, large=1550M

MODEL_SIZE="${1:-base}"

echo "下载 faster-whisper 模型: ${MODEL_SIZE}"
echo ""

# Pass variables via environment to avoid Python code injection
# Shell variables are exported and read by Python, not interpolated into source
export MODEL_SIZE
export MODELS_DIR
export WORKSPACE_MODELS_DIR

# Use Python to download faster-whisper models
python3 - << 'PYEOF'
import os
import sys
from faster_whisper import download_model

model = os.environ.get('MODEL_SIZE', 'base')
output_dir = os.environ.get('MODELS_DIR', '.')

print(f'Downloading faster-whisper model: {model}...')
try:
    path = download_model(model, output_dir=output_dir)
    print(f'Model saved to: {path}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)

# Also download to workspace for backup
workspace_dir = os.environ.get('WORKSPACE_MODELS_DIR', '')
if workspace_dir:
    print(f'Also downloading to workspace...')
    try:
        path = download_model(model, output_dir=workspace_dir)
        print(f'Workspace backup saved to: {path}')
    except Exception as e:
        print(f'Workspace backup skipped: {e}')
PYEOF

echo ""
echo "=========================================="
echo " 模型下载完成！"
echo "=========================================="
echo ""
echo "模型位置: ${MODELS_DIR}"
ls -lh "${MODELS_DIR}" 2>/dev/null || echo "  (目录为空)"
echo ""
echo "可用模型大小: tiny, base, small, medium, large"
echo "下载其他模型: bash scripts/download_models.sh small"

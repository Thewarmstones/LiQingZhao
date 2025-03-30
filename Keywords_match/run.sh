#!/bin/bash

# 获取脚本所在的绝对路径
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# 切换到脚本所在目录
cd "$SCRIPT_DIR" || { echo "Failed to change directory to $SCRIPT_DIR"; exit 1; }

python try.py
# python test.py
# python split_text.py
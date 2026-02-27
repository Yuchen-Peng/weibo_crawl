#!/bin/bash
# 微博热点爬虫一键安装与运行脚本

set -e  # 遇到错误立即退出

echo "========================================="
echo "微博热点爬虫环境准备与执行"
echo "========================================="

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到python3，请先安装Python 3.6+"
    exit 1
fi

# 升级pip
echo "升级pip..."
python3 -m pip install --upgrade pip

# 安装必要依赖
echo "安装Python依赖包（crawl4weibo, pandas）..."
python3 -m pip install crawl4weibo pandas

# 安装Playwright浏览器（crawl4weibo依赖）
echo "安装Playwright浏览器..."
python3 -m playwright install chromium

# 提示用户编辑UID列表
echo ""
echo "请确保已编辑 weibo_hotspots.py 文件，在 BLOGGER_UIDS 列表中填入您关注的博主UID。"
read -p "按回车键继续..." -n 1 -s
echo ""

# 运行爬虫
echo "开始执行爬虫..."
python3 weibo_crawl.py

echo ""
echo "脚本执行完毕。"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取指定博主过去24小时微博
"""

import os
import time
import pandas as pd
from datetime import datetime, timezone, timedelta
from crawl4weibo import WeiboClient

# ==================== 配置区 ====================
# 请在此处填入您关注的财经博主UID列表
# 获取方式：打开博主主页，URL中的数字部分，例如 https://weibo.com/u/1234567890 的UID为1234567890
BLOGGER_UIDS = [
    "2031030981",   # 示例：替换为真实的博主UID
    "2014433131",
    "7544904057",
    "1648195723",
    "2600338914",
    "1098173713",
    "5647310207",
    "7558294027",
    "1905240827",
    "2453509265",
    "2216334181",
    "7960759490",
    "5140428384",
    "3317427737",
    "7820112672",
]

# 停用词文件路径（可选，用于过滤无意义词汇）
STOPWORDS_FILE = "./input/stopwords.txt"   # 如果不需要，可设为None

# 输出文件
OUTPUT_FILE = "./output/hotspots.txt"

# 每页微博数量（crawl4weibo默认每页10条，可根据需要调整分页）
PAGE_SIZE = 10
# ===============================================

def load_stopwords(filepath):
    """加载停用词表"""
    if filepath and os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return set([line.strip() for line in f])
    return set()

def filter_24h_posts(posts):
    """筛选过去24小时发布的微博"""
    now_utc_ts = datetime.now(timezone.utc).timestamp()
    yesterday_utc_ts = now_utc_ts - 24 * 3600
    filtered = []
    for post in posts:
        # post.created_at 可能是字符串，需要解析；也可能是datetime对象
        # crawl4weibo返回的post.created_at 应该是 datetime 对象
        if post.created_at and post.created_at.timestamp() >= yesterday_utc_ts:
            filtered.append(post)
    return filtered

def main():
    print("=" * 50)
    print("微博关注爬虫启动")
    print("=" * 50)

    # 初始化客户端（自动处理Cookie和反爬）
    client = WeiboClient()
    
    # 加载停用词
    stopwords = load_stopwords(STOPWORDS_FILE) if STOPWORDS_FILE else set()
    
    all_posts = []  # 存储所有符合条件的微博（包含博主信息、时间、内容）
    
    for uid in BLOGGER_UIDS:
        user = client.get_user_by_uid(uid)
        print(f"\n正在爬取博主 {uid}: {user.screen_name} 的微博...")
        page = 1
        continue_next_page = True
        while continue_next_page:
            try:
                # 获取一页微博
                posts = client.get_user_posts(uid, page=page, expand=True)
                if not posts:
                    print(f"  博主 {uid} 第 {page} 页无数据，停止翻页")
                    break
                
                # 筛选24小时内
                recent = filter_24h_posts(posts)
                for p in recent:
                    all_posts.append({
                        'uid': uid,
                        'username': user.screen_name,
                        'time': p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else "未知",
                        'text': p.text
                    })
                now_utc_ts = datetime.now(timezone.utc).timestamp()
                yesterday_utc_ts = now_utc_ts - 24 * 3600
                # 如果这一页的微博全部早于24小时，则停止翻页
                if len(posts) > 0 and posts[-1].created_at.timestamp() < yesterday_utc_ts:
                    continue_next_page = False
                    print(f"  已获取到足够早的微博，停止翻页")
                else:
                    page += 1
                    time.sleep(1)  # 礼貌性延迟
                    
            except Exception as e:
                print(f"  爬取出错：{e}")
                break
        
        print(f"  共获取到 {len([p for p in all_posts if p['uid']==uid])} 条24小时内微博")
    
    if not all_posts:
        print("\n没有获取到任何24小时内的微博，请检查UID或网络。")
        return
    
    print(f"\n总计获取 {len(all_posts)} 条微博（过去24小时）")
    
    # 提取所有微博文本
    texts = [p['text'] for p in all_posts]
        
    # 输出结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("微博热点分析报告\n")
        f.write("=" * 50 + "\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"监控博主数：{len(BLOGGER_UIDS)}\n")
        f.write(f"获取微博数：{len(all_posts)}\n\n")
                
        f.write("\n【所有微博原文（按时间倒序）】\n")
        # 按时间倒序排列
        all_posts_sorted = sorted(all_posts, key=lambda x: x['time'], reverse=True)
        for i, post in enumerate(all_posts_sorted, 1):
            f.write(f"\n{i}. [{post['time']}] 博主 {post['uid']} {post['username']}\n")
            f.write(f"   {post['text']}\n")
    
    print(f"\n结果已保存至 {OUTPUT_FILE}")
    print("\n请查看该文件，重点关注高频词汇出现的微博原文，提炼重合话题。")

if __name__ == "__main__":
    main()
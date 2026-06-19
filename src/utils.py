#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数
"""
import re
import time
import random
from html import unescape as html_unescape
from datetime import datetime


def clean_filename(text, max_length=80):
    """
    清理文件名，移除非法字符
    """
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    text = text.replace('\n', '').replace('\r', '').strip()
    return text[:max_length]


def extract_text_from_html(html_content):
    """
    从 HTML 中提取纯文本
    """
    # 移除 script 和 style
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    # 移除标签
    text = re.sub(r'<[^>]+>', ' ', text)
    # 处理空白
    text = re.sub(r'\s+', ' ', text).strip()
    # 解码 HTML 实体
    text = html_unescape(text)
    return text


def random_delay(min_delay=2.0, max_delay=4.0):
    """
    随机延迟，防止被封
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    return delay


def format_date(date_str):
    """
    格式化日期字符串
    """
    if not date_str or date_str == "未知":
        return ""
    
    # 尝试解析多种格式
    patterns = [
        r'(\d{4})[\-/]?(\d{1,2})[\-/]?(\d{1,2})',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
    
    return date_str


def sanitize_html_content(content_html):
    """
    清理 HTML 内容，保留必要属性
    """
    # 将 data-src 转为 src
    content = re.sub(r'data-src="([^"]+)"', r'src="\1"', content_html)
    # 移除数据属性
    content = re.sub(r' data-[a-z_]+="[^"]*"', '', content)
    # 移除 JavaScript 事件
    content = re.sub(r' onclick="[^"]*"', '', content)
    content = re.sub(r' onload="[^"]*"', '', content)
    return content.strip()


def truncate_text(text, max_length=500, suffix="..."):
    """
    截断文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + suffix


def get_timestamp_from_string(date_str):
    """
    从字符串获取时间戳
    """
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return int(dt.timestamp())
    except:
        return 0


def ensure_dir(path):
    """
    确保目录存在
    """
    import os
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def is_valid_wechat_url(url):
    """
    检查是否是有效的微信文章 URL
    """
    pattern = r'^https?://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, url))
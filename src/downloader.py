#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信文章下载器
"""
import re
import os
import sys
import json
import argparse
from datetime import datetime

import requests

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.settings import (
    DEFAULT_HEADERS, DEFAULT_OUTPUT_DIR, DEFAULT_DELAY,
    REQUEST_TIMEOUT, SUPPORTED_FORMATS, DEFAULT_FORMAT, MAX_FILENAME_LENGTH
)
from src.utils import (
    clean_filename, random_delay, sanitize_html_content,
    extract_text_from_html, is_valid_wechat_url, ensure_dir
)
from src.formatters import get_formatter


class WeChatArticleDownloader:
    """微信文章下载器类"""
    
    def __init__(self, headers=None, delay=None):
        self.headers = headers or DEFAULT_HEADERS
        self.delay = delay or DEFAULT_DELAY
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch(self, url):
        """
        获取文章原始 HTML
        """
        if not is_valid_wechat_url(url):
            raise ValueError(f"无效的微信文章 URL: {url}")
        
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            raise Exception(f"请求失败: {e}")
    
    def parse(self, html_content, url):
        """
        解析文章内容
        """
        data = {
            'url': url,
            'title': self._extract_title(html_content),
            'author': self._extract_author(html_content),
            'account': self._extract_account(html_content),
            'publish_time': self._extract_publish_time(html_content),
            'cover_image': self._extract_cover_image(html_content),
            'content_html': self._extract_content(html_content),
        }
        
        # 生成纯文本内容
        data['content_text'] = extract_text_from_html(data['content_html'])
        
        return data
    
    def _extract_title(self, html):
        """提取标题"""
        patterns = [
            r'<h1[^>]*class="rich_media_title[^"]*"[^>]*>(.*?)</h1>',
            r'<h2[^>]*class="rich_media_title[^"]*"[^>]*>(.*?)</h2>',
            r'var msg_title = [\'"]([^\'"]+)[\'"]',
            r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
        ]
        return self._extract_by_patterns(html, patterns, "未知标题")
    
    def _extract_author(self, html):
        """提取作者"""
        patterns = [
            r'<span[^>]*id="js_author_name"[^>]*>(.*?)</span>',
            r'var nickname = [\'"]([^\'"]+)[\'"]',
            r'<meta[^>]*property=["\']og:article:author["\'][^>]*content=["\']([^"\']+)["\']',
        ]
        return self._extract_by_patterns(html, patterns, "未知")
    
    def _extract_account(self, html):
        """提取公众号"""
        patterns = [
            r'<a[^>]*id="js_name"[^>]*>(.*?)</a>',
            r'<span class="profile_nickname">(.*?)</span>',
        ]
        return self._extract_by_patterns(html, patterns, "未知公众号")
    
    def _extract_publish_time(self, html):
        """提取发布时间"""
        # 尝试从 em 标签提取
        match = re.search(r'<em[^>]*id="publish_time"[^>]*>(.*?)</em>', html)
        if match:
            return self._clean_text(match.group(1))
        
        # 尝试从 JavaScript 变量提取
        match = re.search(r"create_time:\s*['\"](\d{4}-\d{2}-\d{2})['\"]", html)
        if match:
            return match.group(1)
        
        match = re.search(r'ct\s*=\s*["\'](\d+)["\']', html)
        if match:
            dt = datetime.fromtimestamp(int(match.group(1)))
            return dt.strftime('%Y-%m-%d')
        
        return ""
    
    def _extract_cover_image(self, html):
        """提取封面图"""
        patterns = [
            r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
            r'var\s+msg_cdn_url\s*=\s*["\']([^"\']+)["\']',
            r'<img[^>]*src=["\'](https://mmbiz\.qpic\.cn/[^"\']+)["\']',
        ]
        return self._extract_by_patterns(html, patterns, "")
    
    def _extract_content(self, html):
        """提取正文内容"""
        # 匹配 rich_media_content
        match = re.search(
            r'<div class="rich_media_content[^"]*"[^>]*>(.*?)</div>\s*(?:<script|<div class="rich_media_tool"|<div id="js_sponsor_ad_area")',
            html, re.DOTALL
        )
        if match:
            return sanitize_html_content(match.group(1))
        return ""
    
    def _extract_by_patterns(self, html, patterns, default=""):
        """根据正则模式列表提取内容"""
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1)
                # 移除 HTML 标签
                text = re.sub(r'<[^>]+>', '', text)
                # 解码 HTML 实体
                from html import unescape
                text = unescape(text)
                text = text.strip()
                if text:
                    return text
        return default
    
    def _clean_text(self, text):
        """清理文本"""
        text = re.sub(r'<[^>]+>', '', text)
        from html import unescape
        text = unescape(text)
        return text.strip()
    
    def download(self, url, format=None, output_dir=None):
        """
        下载单篇文章
        
        Args:
            url: 文章 URL
            format: 输出格式 (text/markdown/html)
            output_dir: 输出目录
            
        Returns:
            dict: 下载结果信息
        """
        format = format or DEFAULT_FORMAT
        output_dir = output_dir or DEFAULT_OUTPUT_DIR
        
        if format not in SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式: {format}")
        
        # 获取并解析文章
        print(f"正在下载: {url}")
        html = self.fetch(url)
        data = self.parse(html, url)
        
        # 生成文件名
        safe_title = clean_filename(data['title'], MAX_FILENAME_LENGTH)
        if data['publish_time']:
            date_prefix = data['publish_time'].replace('-', '')[:8]
            filename = f"{date_prefix}_{safe_title}"
        else:
            filename = safe_title
        
        # 确保输出目录存在
        ensure_dir(output_dir)
        
        # 生成输出内容
        formatter = get_formatter(format)
        content = formatter.format(data)
        
        # 保存文件
        ext = {'text': 'txt', 'markdown': 'md', 'html': 'html'}[format]
        filepath = os.path.join(output_dir, f"{filename}.{ext}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 记录延迟
        random_delay(self.delay - 0.5, self.delay + 0.5)
        
        result = {
            'title': data['title'],
            'author': data['author'],
            'account': data['account'],
            'publish_time': data['publish_time'],
            'url': url,
            'format': format,
            'filepath': filepath,
            'status': 'success'
        }
        
        print(f"✓ 下载完成: {data['title']}")
        print(f"  保存到: {filepath}")
        
        return result


def main():
    parser = argparse.ArgumentParser(description='微信文章下载工具')
    parser.add_argument('--url', '-u', required=True, help='文章 URL')
    parser.add_argument('--format', '-f', choices=SUPPORTED_FORMATS, 
                        default=DEFAULT_FORMAT, help=f'输出格式 (默认: {DEFAULT_FORMAT})')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_DIR, 
                        help=f'输出目录 (默认: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--delay', '-d', type=float, default=DEFAULT_DELAY,
                        help=f'请求间隔(秒) (默认: {DEFAULT_DELAY})')
    
    args = parser.parse_args()
    
    downloader = WeChatArticleDownloader(delay=args.delay)
    
    try:
        result = downloader.download(
            url=args.url,
            format=args.format,
            output_dir=args.output
        )
        
        # 输出 JSON 结果
        print("\n" + "="*50)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

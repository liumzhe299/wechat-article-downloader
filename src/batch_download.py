#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载工具
"""
import os
import sys
import json
import argparse
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.settings import (
    DEFAULT_OUTPUT_DIR, DEFAULT_INPUT_DIR, DEFAULT_DELAY,
    SUPPORTED_FORMATS, DEFAULT_FORMAT, BATCH_SIZE, BATCH_REST
)
from src.downloader import WeChatArticleDownloader
from src.utils import random_delay, ensure_dir


def read_url_list(filepath):
    """
    读取 URL 列表
    """
    urls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def batch_download(urls, format=None, output_dir=None, delay=None):
    """
    批量下载文章
    
    Args:
        urls: URL 列表
        format: 输出格式
        output_dir: 输出目录
        delay: 请求间隔
        
    Returns:
        list: 下载结果列表
    """
    format = format or DEFAULT_FORMAT
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    delay = delay or DEFAULT_DELAY
    
    ensure_dir(output_dir)
    
    downloader = WeChatArticleDownloader(delay=delay)
    
    results = []
    success_count = 0
    fail_count = 0
    
    print(f"\n开始批量下载，共 {len(urls)} 篇文章")
    print(f"输出格式: {format}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 处理中...")
        
        try:
            result = downloader.download(url, format, output_dir)
            results.append(result)
            success_count += 1
        except Exception as e:
            print(f"✗ 失败: {e}")
            results.append({
                'url': url,
                'status': 'failed',
                'error': str(e)
            })
            fail_count += 1
        
        # 批间休息
        if i < len(urls):
            if i % BATCH_SIZE == 0:
                rest_time = random_delay(BATCH_REST[0], BATCH_REST[1])
                print(f"  (批间休息 {rest_time:.1f}秒...)")
    
    # 保存结果日志
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(output_dir, f"download_log_{timestamp}.json")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total': len(urls),
            'success': success_count,
            'failed': fail_count,
            'format': format,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("下载完成!")
    print(f"  成功: {success_count}/{len(urls)}")
    print(f"  失败: {fail_count}/{len(urls)}")
    print(f"  日志: {log_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='微信文章批量下载工具')
    parser.add_argument('--input', '-i', required=True,
                        help='URL 列表文件路径')
    parser.add_argument('--format', '-f', choices=SUPPORTED_FORMATS,
                        default=DEFAULT_FORMAT, help=f'输出格式 (默认: {DEFAULT_FORMAT})')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_DIR,
                        help=f'输出目录 (默认: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--delay', '-d', type=float, default=DEFAULT_DELAY,
                        help=f'请求间隔(秒) (默认: {DEFAULT_DELAY})')
    
    args = parser.parse_args()
    
    # 读取 URL 列表
    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)
    
    urls = read_url_list(args.input)
    
    if not urls:
        print("错误: URL 列表为空")
        sys.exit(1)
    
    print(f"读取到 {len(urls)} 个 URL")
    
    # 开始批量下载
    batch_download(
        urls=urls,
        format=args.format,
        output_dir=args.output,
        delay=args.delay
    )


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片下载器 - 下载文章中的图片和封面图
"""
import os
import re
import hashlib
import requests
from urllib.parse import urlparse

from config.settings import REQUEST_TIMEOUT
from src.utils import ensure_dir, random_delay


class ImageDownloader:
    """图片下载器"""
    
    def __init__(self, output_dir, delay=1.0):
        self.output_dir = output_dir
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://mp.weixin.qq.com/',
        })
        self.downloaded_images = set()
        
    def download_cover(self, image_url, article_title):
        """
        下载封面图
        
        Args:
            image_url: 图片 URL
            article_title: 文章标题（用于命名）
            
        Returns:
            str: 本地文件路径或空字符串
        """
        if not image_url:
            return ""
            
        try:
            # 生成文件名
            ext = self._get_extension(image_url) or '.jpg'
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', article_title)[:50]
            filename = f"cover_{safe_title}{ext}"
            filepath = os.path.join(self.output_dir, filename)
            
            # 检查是否已下载
            if os.path.exists(filepath):
                return filepath
            
            # 下载图片
            response = self.session.get(image_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            random_delay(self.delay - 0.3, self.delay + 0.3)
            
            return filepath
            
        except Exception as e:
            print(f"  ✗ 封面图下载失败: {e}")
            return ""
    
    def download_content_images(self, html_content, article_title):
        """
        下载正文中的图片
        
        Args:
            html_content: HTML 内容
            article_title: 文章标题
            
        Returns:
            dict: 原 URL -> 本地路径 的映射
        """
        image_map = {}
        
        # 提取所有图片 URL
        img_urls = re.findall(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', html_content)
        
        if not img_urls:
            return image_map
        
        print(f"  发现 {len(img_urls)} 张图片")
        
        for i, img_url in enumerate(img_urls, 1):
            if not img_url.startswith('http'):
                continue
                
            try:
                # 生成唯一文件名
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                ext = self._get_extension(img_url) or '.jpg'
                filename = f"img_{i:03d}_{url_hash}{ext}"
                filepath = os.path.join(self.output_dir, filename)
                
                # 检查是否已下载
                if img_url in self.downloaded_images or os.path.exists(filepath):
                    image_map[img_url] = filepath
                    continue
                
                # 下载图片
                response = self.session.get(img_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                image_map[img_url] = filepath
                self.downloaded_images.add(img_url)
                
                random_delay(self.delay - 0.3, self.delay + 0.3)
                
            except Exception as e:
                print(f"    ✗ 图片 {i} 下载失败: {e}")
                continue
        
        return image_map
    
    def replace_image_paths(self, html_content, image_map):
        """
        替换 HTML 中的图片路径为本地路径
        
        Args:
            html_content: 原始 HTML
            image_map: URL -> 本地路径 的映射
            
        Returns:
            str: 替换后的 HTML
        """
        result = html_content
        for original_url, local_path in image_map.items():
            # 获取相对路径
            rel_path = os.path.basename(local_path)
            result = result.replace(original_url, rel_path)
        return result
    
    def _get_extension(self, url):
        """从 URL 获取文件扩展名"""
        parsed = urlparse(url)
        path = parsed.path
        
        # 从路径中提取扩展名
        ext = os.path.splitext(path)[1].lower()
        
        # 如果没有扩展名，从查询参数中尝试
        if not ext:
            match = re.search(r'wx_fmt=(\w+)', parsed.query)
            if match:
                ext = f".{match.group(1)}"
        
        # 默认使用 jpg
        if not ext:
            ext = '.jpg'
        
        return ext


if __name__ == '__main__':
    # 测试
    downloader = ImageDownloader('./test_images')
    
    # 测试下载封面图
    test_url = "https://mmbiz.qpic.cn/mmbiz_jpg/example/640?wx_fmt=jpeg"
    result = downloader.download_cover(test_url, "测试文章")
    print(f"封面图下载结果: {result}")

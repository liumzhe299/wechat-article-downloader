#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化器 - 将文章内容转换为不同格式
"""
import re
from html import unescape as html_unescape


class TextFormatter:
    """纯文本格式化器"""
    
    @staticmethod
    def format(article_data):
        """转换为纯文本"""
        lines = [
            f"标题: {article_data.get('title', '')}",
            f"作者: {article_data.get('author', '')}",
            f"公众号: {article_data.get('account', '')}",
            f"发布时间: {article_data.get('publish_time', '')}",
            f"原文链接: {article_data.get('url', '')}",
            "-" * 50,
            "",
            article_data.get('content_text', ''),
        ]
        return '\n'.join(lines)


class MarkdownFormatter:
    """Markdown 格式化器"""
    
    @staticmethod
    def format(article_data):
        """转换为 Markdown"""
        title = article_data.get('title', '')
        author = article_data.get('author', '')
        account = article_data.get('account', '')
        publish_time = article_data.get('publish_time', '')
        url = article_data.get('url', '')
        cover_image = article_data.get('cover_image', '')
        content = article_data.get('content_html', '')
        
        # 转换 HTML 标签为 Markdown
        md_content = html_to_markdown(content)
        
        lines = [
            f"# {title}",
            "",
            f"作者: {author}",
            f"公众号: {account}",
            f"发布时间: {publish_time}",
            f"原文链接: [{url}]({url})",
            "",
            "---",
            "",
        ]
        
        if cover_image:
            lines.append(f"![封面图]({cover_image})")
            lines.append("")
        
        lines.append(md_content)
        
        return '\n'.join(lines)


class HTMLFormatter:
    """HTML 格式化器 - 精简版"""
    
    TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta property="og:title" content="{title}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{cover_image}">
  <meta property="og:article:author" content="{author}">
  <title>{title}</title>
  <style>
    body {{
      font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
      color: #333;
      background-color: #f2f2f2;
      line-height: 1.6;
      letter-spacing: .034em;
      margin: 0;
      padding: 0;
    }}
    .container {{
      max-width: 677px;
      margin: 0 auto;
      padding: 20px 15px;
      background-color: #fff;
    }}
    .cover {{
      width: 100%;
      max-height: 300px;
      object-fit: cover;
      margin-bottom: 15px;
      border-radius: 4px;
    }}
    h1 {{
      font-size: 22px;
      font-weight: 700;
      line-height: 1.4;
      margin: 0 0 14px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e7e7eb;
    }}
    .meta {{
      font-size: 14px;
      color: #8c8c8c;
      margin-bottom: 22px;
    }}
    .meta span {{
      margin-right: 8px;
    }}
    .content {{
      font-size: 16px;
      line-height: 1.8;
      text-align: justify;
    }}
    .content p {{
      margin: 0 0 1em;
    }}
    .content img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 1em auto;
      border-radius: 4px;
    }}
    .content strong {{
      font-weight: 700;
    }}
    .content blockquote {{
      margin: 0;
      padding-left: 10px;
      border-left: 3px solid #dbdbdb;
      color: #666;
    }}
    @media screen and (min-width: 1025px) {{
      .container {{
        width: 740px;
        padding: 20px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <img class="cover" src="{cover_image}" alt="封面图"/>
    <h1>{title}</h1>
    <div class="meta">
      <span>作者: {author}</span>
      <span>公众号: {account}</span>
      <span>发布: {publish_time}</span>
    </div>
    <div class="content">
      {content}
    </div>
  </div>
</body>
</html>'''
    
    @staticmethod
    def format(article_data):
        """生成精简 HTML"""
        return HTMLFormatter.TEMPLATE.format(
            title=escape_html(article_data.get('title', '')),
            author=escape_html(article_data.get('author', '')),
            account=escape_html(article_data.get('account', '')),
            publish_time=article_data.get('publish_time', ''),
            url=article_data.get('url', ''),
            cover_image=article_data.get('cover_image', ''),
            content=article_data.get('content_html', '')
        )


def html_to_markdown(html_content):
    """
    简单的 HTML 转 Markdown
    """
    md = html_content
    
    # 标题
    md = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', md, flags=re.DOTALL)
    md = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', md, flags=re.DOTALL)
    md = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', md, flags=re.DOTALL)
    
    # 图片
    md = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', r'![](\1)', md)
    
    # 粗体
    md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', md, flags=re.DOTALL)
    md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', md, flags=re.DOTALL)
    
    # 斜体
    md = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', md, flags=re.DOTALL)
    md = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', md, flags=re.DOTALL)
    
    # 段落
    md = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md, flags=re.DOTALL)
    md = re.sub(r'<br\s*/?>', '\n', md)
    
    # 链接
    md = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.DOTALL)
    
    # 列表
    md = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', md, flags=re.DOTALL)
    md = re.sub(r'<ul[^>]*>|</ul>|<ol[^>]*>|</ol>', '', md)
    
    # 引用
    md = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', md, flags=re.DOTALL)
    
    # 清理剩余标签
    md = re.sub(r'<[^>]+>', '', md)
    
    # 解码 HTML 实体
    md = html_unescape(md)
    
    # 清理空行
    md = re.sub(r'\n{3,}', '\n\n', md)
    
    return md.strip()


def escape_html(text):
    """
    转义 HTML 特殊字符
    """
    if not text:
        return ''
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text


def get_formatter(format_type):
    """
    获取格式化器
    """
    formatters = {
        'text': TextFormatter,
        'markdown': MarkdownFormatter,
        'html': HTMLFormatter,
    }
    return formatters.get(format_type.lower(), HTMLFormatter)

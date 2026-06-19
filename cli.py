#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Article Downloader - 综合命令行工具

微信文章下载工具 - 支持多种格式、图片下载、飞书导出
"""
import os
import sys
import argparse
import json
from datetime import datetime

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.downloader import WeChatArticleDownloader
from src.batch_download import read_url_list, batch_download
from src.image_downloader import ImageDownloader
from src.feishu_exporter import FeishuExporter, setup_feishu_base
from src.config_manager import ConfigManager
from src.utils import ensure_dir
from config.settings import SUPPORTED_FORMATS, DEFAULT_FORMAT


def cmd_download(args):
    """单篇下载"""
    print(f"\n📚 下载单篇文章")
    print(f"   URL: {args.url}")
    print(f"   格式: {args.format}")
    print(f"   输出: {args.output}")
    
    downloader = WeChatArticleDownloader(delay=args.delay)
    
    try:
        result = downloader.download(
            url=args.url,
            format=args.format,
            output_dir=args.output
        )
        
        # 下载封面图
        if args.save_cover and result.get('cover_image'):
            print("\n🖼 下载封面图...")
            img_dir = os.path.join(args.output, 'images')
            ensure_dir(img_dir)
            
            img_downloader = ImageDownloader(img_dir, delay=args.delay)
            cover_path = img_downloader.download_cover(
                result['cover_image'],
                result['title']
            )
            if cover_path:
                print(f"   ✓ 封面图: {cover_path}")
                result['cover_path'] = cover_path
        
        # 导出到飞书
        if args.feishu:
            print("\n🔖 导出到飞书...")
            config = ConfigManager()
            feishu_config = config.get_feishu_config()
            
            if not feishu_config.get('app_token'):
                print("   ✗ 未配置飞书 app_token，请先运行: python cli.py config --feishu-token <token>")
            else:
                exporter = FeishuExporter(
                    app_token=feishu_config.get('app_token'),
                    table_id=feishu_config.get('table_id')
                )
                success, failed = exporter.export_articles([result])
                print(f"   ✓ 成功: {success}, 失败: {failed}")
        
        # 输出结果
        if args.json:
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n✅ 完成!")
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        sys.exit(1)


def cmd_batch(args):
    """批量下载"""
    print(f"\n📚 批量下载文章")
    print(f"   输入: {args.input}")
    print(f"   格式: {args.format}")
    
    urls = read_url_list(args.input)
    if not urls:
        print("❌ URL 列表为空")
        sys.exit(1)
    
    print(f"   共 {len(urls)} 篇文章\n")
    
    results = batch_download(
        urls=urls,
        format=args.format,
        output_dir=args.output,
        delay=args.delay
    )
    
    # 导出到飞书
    if args.feishu:
        print("\n🔖 导出到飞书...")
        config = ConfigManager()
        feishu_config = config.get_feishu_config()
        
        if not feishu_config.get('app_token'):
            print("   ✗ 未配置飞书 app_token")
        else:
            exporter = FeishuExporter(
                app_token=feishu_config.get('app_token'),
                table_id=feishu_config.get('table_id')
            )
            success, failed = exporter.export_articles(results)
            print(f"   ✓ 导出完成: 成功 {success}, 失败 {failed}")


def cmd_config(args):
    """配置管理"""
    config = ConfigManager()
    
    if args.show:
        config.print_config()
    
    elif args.feishu_token:
        config.set('feishu.app_token', args.feishu_token)
        print(f"✓ 飞书 app_token 已设置")
    
    elif args.feishu_table:
        config.set('feishu.table_id', args.feishu_table)
        print(f"✓ 飞书 table_id 已设置")
    
    elif args.output_dir:
        config.set('output_dir', args.output_dir)
        print(f"✓ 默认输出目录已设置: {args.output_dir}")
    
    elif args.default_format:
        config.set('default_format', args.default_format)
        print(f"✓ 默认格式已设置: {args.default_format}")
    
    else:
        print("请使用以下命令:")
        print("  python cli.py config --show                # 显示配置")
        print("  python cli.py config --feishu-token <token> # 设置飞书 token")
        print("  python cli.py config --output-dir <path>   # 设置输出目录")


def cmd_setup_feishu(args):
    """初始化飞书多维表格"""
    print("\n📋 创建飞书多维表格")
    
    name = args.name or f"微信文章收集-{datetime.now().strftime('%Y%m%d')}"
    
    app_token, table_id = setup_feishu_base(name, args.account)
    
    if app_token:
        print(f"\n✅ Base 创建成功!")
        print(f"   App Token: {app_token}")
        if table_id:
            print(f"   Table ID: {table_id}")
        
        # 保存配置
        config = ConfigManager()
        config.set_feishu_config(app_token=app_token, table_id=table_id)
        print("\n✓ 配置已保存到本地")
        print(f"   请访问: https://your-domain.feishu.cn/base/{app_token}")
    else:
        print("\n❌ 创建失败")


def main():
    parser = argparse.ArgumentParser(
        description='微信文章下载工具 - 支持多种格式、图片下载、飞书导出',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单篇下载
  python cli.py download -u "https://mp.weixin.qq.com/s/xxxxx" -f html

  # 批量下载
  python cli.py batch -i urls.txt -f markdown

  # 下载并导出到飞书
  python cli.py batch -i urls.txt --feishu

  # 配置飞书
  python cli.py config --feishu-token "your_token_here"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # download 命令
    download_parser = subparsers.add_parser('download', help='单篇下载')
    download_parser.add_argument('-u', '--url', required=True, help='文章 URL')
    download_parser.add_argument('-f', '--format', choices=SUPPORTED_FORMATS, 
                                  default=DEFAULT_FORMAT, help='输出格式')
    download_parser.add_argument('-o', '--output', default='./output', help='输出目录')
    download_parser.add_argument('-d', '--delay', type=float, default=2.0, help='请求间隔(秒)')
    download_parser.add_argument('--save-cover', action='store_true', help='保存封面图')
    download_parser.add_argument('--feishu', action='store_true', help='导出到飞书')
    download_parser.add_argument('--json', action='store_true', help='输出 JSON 结果')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量下载')
    batch_parser.add_argument('-i', '--input', required=True, help='URL 列表文件')
    batch_parser.add_argument('-f', '--format', choices=SUPPORTED_FORMATS,
                              default=DEFAULT_FORMAT, help='输出格式')
    batch_parser.add_argument('-o', '--output', default='./output', help='输出目录')
    batch_parser.add_argument('-d', '--delay', type=float, default=2.0, help='请求间隔(秒)')
    batch_parser.add_argument('--feishu', action='store_true', help='导出到飞书')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    config_parser.add_argument('--feishu-token', help='设置飞书 app_token')
    config_parser.add_argument('--feishu-table', help='设置飞书 table_id')
    config_parser.add_argument('--output-dir', help='设置默认输出目录')
    config_parser.add_argument('--default-format', choices=SUPPORTED_FORMATS, help='设置默认格式')
    
    # setup-feishu 命令
    setup_parser = subparsers.add_parser('setup-feishu', help='创建飞书多维表格')
    setup_parser.add_argument('--name', help='Base 名称')
    setup_parser.add_argument('--account', default='微信文章', help='公众号名称')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行对应命令
    commands = {
        'download': cmd_download,
        'batch': cmd_batch,
        'config': cmd_config,
        'setup-feishu': cmd_setup_feishu,
    }
    
    if args.command in commands:
        commands[args.command](args)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书导出器 - 将文章导出到飞书多维表格
"""
import os
import sys
import json
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.settings import REQUEST_TIMEOUT


class FeishuExporter:
    """飞书多维表格导出器"""
    
    def __init__(self, app_token=None, table_id=None):
        """
        初始化飞书导出器
        
        Args:
            app_token: 飞书 Base 的 app_token
            table_id: 表格 ID
        """
        self.app_token = app_token
        self.table_id = table_id
        
    def _run_lark_command(self, args):
        """
        运行 lark-cli 命令
        """
        try:
            cmd = ['lark', 'base'] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def test_connection(self):
        """
        测试飞书连接
        """
        if not self.app_token:
            return False, "未配置 app_token"
        
        success, stdout, stderr = self._run_lark_command([
            'get', self.app_token
        ])
        
        if success:
            return True, "连接正常"
        else:
            return False, f"连接失败: {stderr}"
    
    def create_base(self, name, folder_token=None):
        """
        创建新的多维表格
        
        Args:
            name: Base 名称
            folder_token: 文件夹 token（可选）
            
        Returns:
            tuple: (success, app_token 或 error_message)
        """
        args = ['create', '--name', name]
        if folder_token:
            args.extend(['--folder', folder_token])
        
        success, stdout, stderr = self._run_lark_command(args)
        
        if success:
            # 解析输出获取 app_token
            try:
                # 尝试解析 JSON
                data = json.loads(stdout)
                if 'app_token' in data:
                    return True, data['app_token']
            except:
                pass
            
            # 如果解析失败，返回原始输出
            return True, stdout
        else:
            return False, stderr
    
    def add_fields(self, fields_config):
        """
        添加字段到表格
        
        Args:
            fields_config: 字段配置列表
            
        Returns:
            bool: 是否成功
        """
        if not self.app_token or not self.table_id:
            print("错误: 未配置 app_token 或 table_id")
            return False
        
        success_count = 0
        for field in fields_config:
            args = [
                'field', 'add',
                '--app', self.app_token,
                '--table', self.table_id,
                '--name', field['name'],
                '--type', field['type']
            ]
            
            success, stdout, stderr = self._run_lark_command(args)
            if success:
                success_count += 1
            else:
                print(f"  ✗ 添加字段失败 {field['name']}: {stderr}")
        
        return success_count == len(fields_config)
    
    def export_articles(self, articles):
        """
        导出文章列表到飞书
        
        Args:
            articles: 文章数据列表
            
        Returns:
            tuple: (success_count, failed_count)
        """
        if not self.app_token or not self.table_id:
            print("错误: 未配置 app_token 或 table_id")
            return 0, len(articles)
        
        success_count = 0
        failed_count = 0
        
        print(f"\n开始导出 {len(articles)} 篇文章到飞书...")
        
        for i, article in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {article.get('title', '未知')}...", end=' ')
            
            # 构建字段数据
            fields = self._build_fields(article)
            
            # 创建记录
            success = self._create_record(fields)
            
            if success:
                print("✓")
                success_count += 1
            else:
                print("✗")
                failed_count += 1
        
        return success_count, failed_count
    
    def _build_fields(self, article):
        """
        构建飞书字段数据
        """
        fields = {}
        
        # 标题
        if 'title' in article:
            fields['标题'] = article['title']
        
        # 作者
        if 'author' in article:
            fields['作者'] = article['author']
        
        # 公众号
        if 'account' in article:
            fields['公众号'] = article['account']
        
        # 发布时间
        if 'publish_time' in article and article['publish_time']:
            try:
                # 尝试解析日期
                dt = datetime.strptime(article['publish_time'], '%Y-%m-%d')
                fields['发布时间'] = int(dt.timestamp() * 1000)  # 转换为毫秒时间戳
            except:
                fields['发布时间'] = article['publish_time']
        
        # 原文链接
        if 'url' in article:
            fields['原文链接'] = {
                'text': '点击查看',
                'link': article['url']
            }
        
        # 正文摘要
        if 'content_text' in article:
            summary = article['content_text'][:500] + "..." if len(article['content_text']) > 500 else article['content_text']
            fields['摘要'] = summary
        elif 'summary' in article:
            fields['摘要'] = article['summary']
        
        # 封面图
        if 'cover_image' in article and article['cover_image']:
            fields['封面图'] = article['cover_image']
        
        # 状态
        fields['状态'] = article.get('status', '待处理')
        
        # 本地HTML文件
        if 'html_file' in article:
            fields['HTML文件'] = article['html_file']
        
        # 本地路径
        if 'filepath' in article:
            fields['本地路径'] = article['filepath']
        
        return fields
    
    def _create_record(self, fields):
        """
        创建单条记录
        """
        try:
            # 构建命令
            field_args = []
            for key, value in fields.items():
                field_args.extend(['--field', f"{key}={json.dumps(value, ensure_ascii=False)}"])
            
            args = [
                'record', 'create',
                '--app', self.app_token,
                '--table', self.table_id
            ] + field_args
            
            success, stdout, stderr = self._run_lark_command(args)
            return success
            
        except Exception as e:
            print(f"创建记录失败: {e}")
            return False
    
    def get_base_info(self):
        """
        获取 Base 信息
        """
        if not self.app_token:
            return None
        
        success, stdout, stderr = self._run_lark_command([
            'get', self.app_token
        ])
        
        if success:
            try:
                return json.loads(stdout)
            except:
                return stdout
        return None


def setup_feishu_base(name, account_name="微信文章"):
    """
    设置飞书多维表格
    
    Args:
        name: Base 名称
        account_name: 公众号名称
        
    Returns:
        tuple: (app_token, table_id)
    """
    print(f"\n创建飞书多维表格: {name}")
    
    exporter = FeishuExporter()
    
    # 创建 Base
    success, result = exporter.create_base(name)
    if not success:
        print(f"创建失败: {result}")
        return None, None
    
    app_token = result
    print(f"✓ Base 创建成功: {app_token}")
    
    exporter.app_token = app_token
    
    # 获取默认表格 ID
    # 注意: 这里需要通过 lark 命令获取 table_id
    # 暂时返回 app_token，需要手动配置 table_id
    
    return app_token, None


if __name__ == '__main__':
    # 测试
    exporter = FeishuExporter()
    
    # 测试连接
    success, message = exporter.test_connection()
    print(f"连接测试: {message}")

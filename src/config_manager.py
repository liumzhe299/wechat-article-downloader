#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器 - 管理用户配置
"""
import os
import json
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    CONFIG_FILE = os.path.expanduser('~/.wechat_downloader_config.json')
    
    DEFAULT_CONFIG = {
        'output_dir': './output',
        'download_images': False,
        'save_cover': True,
        'export_to_feishu': False,
        'feishu': {
            'app_token': '',
            'table_id': '',
        },
        'delay': {
            'min': 2.0,
            'max': 4.0,
        },
        'batch': {
            'size': 5,
            'rest_min': 5,
            'rest_max': 8,
        },
        'default_format': 'html',
    }
    
    def __init__(self):
        self.config = self.load()
    
    def load(self):
        """加载配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    merged = self.DEFAULT_CONFIG.copy()
                    merged.update(config)
                    return merged
            except Exception as e:
                print(f"读取配置文件失败: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """保存配置"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return self.save()
    
    def get_feishu_config(self):
        """获取飞书配置"""
        return self.config.get('feishu', {})
    
    def set_feishu_config(self, app_token=None, table_id=None):
        """设置飞书配置"""
        if app_token:
            self.config['feishu']['app_token'] = app_token
        if table_id:
            self.config['feishu']['table_id'] = table_id
        return self.save()
    
    def print_config(self):
        """打印当前配置"""
        print(f"\n配置文件位置: {self.CONFIG_FILE}")
        print("-" * 40)
        print(json.dumps(self.config, ensure_ascii=False, indent=2))
        print("-" * 40)


if __name__ == '__main__':
    # 测试
    config = ConfigManager()
    config.print_config()

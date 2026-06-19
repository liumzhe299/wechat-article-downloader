# WeChat Article Downloader

微信公众号文章下载工具 - 支持多种格式导出、图片下载、飞书导出

[English](#english) | [中文](#中文)

---

## 中文

### 功能特点

- 📖 **多种格式支持**: 纯文本 (.txt)、Markdown (.md)、精简 HTML (.html)
- 🎨 **保留排版**: 完整保留微信文章的样式和格式
- 🖼 **图片下载**: 自动下载封面图和正文图片
- 📄 **批量下载**: 支持 URL 列表批量下载
- 🔐 **无需登录**: 直接解析公开文章内容
- 🚀 **飞书导出**: 一键导出到飞书多维表格
- 🎯 **安全下载**: 内置随机延迟防止封禁
- ⚙️ **配置管理**: 本地配置文件，不用每次都输入参数

### 安装

```bash
# 克隆仓库
git clone https://github.com/liumzhe299/wechat-article-downloader.git
cd wechat-article-downloader

# 安装依赖
pip install -r requirements.txt

# 可选：安装飞书 CLI（如需导出到飞书）
npm install -g @larksuiteoapi/lark-cli
lark auth login
```

### 快速开始

#### 1. 单篇下载

```bash
python cli.py download -u "https://mp.weixin.qq.com/s/xxxxx" -f html

# 下载并保存封面图
python cli.py download -u "https://mp.weixin.qq.com/s/xxxxx" --save-cover
```

#### 2. 批量下载

```bash
# 创建 URL 列表文件
echo "https://mp.weixin.qq.com/s/xxxxx" > urls.txt
echo "https://mp.weixin.qq.com/s/yyyyy" >> urls.txt

# 开始批量下载
python cli.py batch -i urls.txt -f html
```

#### 3. 导出到飞书

```bash
# 配置飞书（只需一次）
python cli.py config --feishu-token "your_app_token"
python cli.py config --feishu-table "your_table_id"

# 或创建新的多维表格
python cli.py setup-feishu --name "我的文章收集"

# 批量下载并导出
python cli.py batch -i urls.txt -f html --feishu
```

### 命令行工具 (cli.py)

```bash
python cli.py <command> [options]

Commands:
  download      单篇下载
  batch         批量下载
  config        配置管理
  setup-feishu  创建飞书多维表格
```

#### 下载命令

```bash
python cli.py download -u <url> [options]

Options:
  -u, --url          文章 URL (必填)
  -f, --format       输出格式: text|markdown|html (默认: html)
  -o, --output       输出目录 (默认: ./output)
  -d, --delay        请求间隔秒数 (默认: 2.0)
  --save-cover       保存封面图
  --feishu           导出到飞书
  --json             输出 JSON 结果
```

#### 批量下载命令

```bash
python cli.py batch -i <file> [options]

Options:
  -i, --input        URL 列表文件 (必填)
  -f, --format       输出格式 (默认: html)
  -o, --output       输出目录 (默认: ./output)
  --feishu           导出到飞书
```

#### 配置命令

```bash
python cli.py config [options]

Options:
  --show                    显示当前配置
  --feishu-token <token>    设置飞书 app_token
  --feishu-table <id>       设置飞书 table_id
  --output-dir <path>       设置默认输出目录
  --default-format <fmt>    设置默认格式
```

### Python API

```python
from src.downloader import WeChatArticleDownloader
from src.image_downloader import ImageDownloader
from src.feishu_exporter import FeishuExporter

# 下载文章
downloader = WeChatArticleDownloader()
result = downloader.download(
    url="https://mp.weixin.qq.com/s/xxxxx",
    format="html",
    output_dir="./output"
)

# 下载封面图
img_downloader = ImageDownloader("./output/images")
cover_path = img_downloader.download_cover(
    result['cover_image'],
    result['title']
)

# 导出到飞书
exporter = FeishuExporter(app_token="xxx", table_id="yyy")
success, failed = exporter.export_articles([result])
```

### 项目结构

```
wechat-article-downloader/
├── cli.py                    # 综合命令行工具
├── src/
│   ├── __init__.py
│   ├── downloader.py        # 主下载器
│   ├── batch_download.py    # 批量下载
│   ├── formatters.py        # 格式转换器
│   ├── image_downloader.py  # 图片下载器
│   ├── feishu_exporter.py   # 飞书导出器
│   └── config_manager.py    # 配置管理器
├── config/
│   ├── __init__.py
│   └── settings.py          # 默认配置
├── input/                  # 输入目录
├── output/                 # 输出目录
├── requirements.txt
├── README.md
└── LICENSE
```

### 输出格式对比

| 格式 | 文件大小 | 保留样式 | 图片支持 | 适合场景 |
|------|----------|----------|----------|----------|
| **Text** | 最小 | ❌ 无 | ❌ 文本链接 | 文本分析、NLP |
| **Markdown** | 小 | ⚠️ 部分 | ⚠️ 外链 | 笔记软件、文档 |
| **HTML** | 中 | ✅ 完整 | ✅ 可下载 | 存档、浏览器阅读 |

### 版本历史

- **v1.1.0** (2024-06-19): 新增飞书导出、图片下载、配置管理
- **v1.0.0** (2024-06-19): 初始版本，支持三种输出格式

---

## English

### Features

- 📖 **Multiple Formats**: Text (.txt), Markdown (.md), Clean HTML (.html)
- 🎨 **Preserve Layout**: Keep WeChat article styling and formatting
- 🖼 **Image Download**: Auto download cover and content images
- 📄 **Batch Download**: Support URL list batch processing
- 🔐 **No Login Required**: Parse public articles directly
- 🚀 **Feishu Export**: One-click export to Feishu Base
- 🎯 **Safe Downloading**: Built-in random delays
- ⚙️ **Config Management**: Local config file

### Quick Start

```bash
# Single article
python cli.py download -u "https://mp.weixin.qq.com/s/xxxxx" -f html

# Batch download
python cli.py batch -i urls.txt -f html

# Export to Feishu
python cli.py batch -i urls.txt --feishu
```

### License

MIT License - see [LICENSE](LICENSE)

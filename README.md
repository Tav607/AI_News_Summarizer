# AI 新闻摘要生成器

本项目可以批量处理新闻文章 URL，使用 AI 生成摘要，并创建一个包含目录的格式化 PDF 文档。

## 功能特点

- 从文本文件读取 URL（支持约 300 个 URL）
- 使用 AI 为每篇文章生成约 200 字的中文摘要
- 生成带时间戳的 PDF 和 Markdown 文件（例如：`output/news_summary_20240304_141500.pdf`）
- PDF 特性：
  - 带日期的标题页
  - 可点击的目录（不含 URL）
  - 带超链接的文章标题
  - 作者/媒体/发布日期信息
  - 文章摘要
  - 页码（格式：x/y）
- 批量处理并显示进度
- 支持多级标题
- 包含美观的样式
- 使用配置文件管理 API 密钥和模型
- 结构化的文件目录组织

## 系统要求

- Python 3.6 或更高版本
- wkhtmltopdf（用于生成 PDF）
- Volces AI API 密钥
- `requirements.txt` 中列出的 Python 包

## 项目结构

```
.
├── input/                  # 输入目录
│   └── input_urls.txt     # URL 列表文件
├── output/                # 输出目录
│   ├── *.md              # 生成的 Markdown 文件
│   └── *.pdf             # 生成的 PDF 文件
├── config.txt            # 配置文件
├── main.py              # 主程序
├── collect_to_md.py     # URL 采集模块
├── md_to_pdf.py        # PDF 转换模块
└── requirements.txt    # Python 依赖包列表
```

## 安装步骤

1. 克隆或下载本仓库

2. 安装 wkhtmltopdf：
   - Windows：从 https://wkhtmltopdf.org/downloads.html 下载并安装
   - Linux：执行 `sudo apt-get install wkhtmltopdf`
   - macOS：执行 `brew install wkhtmltopdf`

3. 安装所需的 Python 包：
```bash
pip install -r requirements.txt
```

4. 创建名为 `config.txt` 的配置文件，填入你的 Volces AI API 密钥和模型 ID：
```ini
[API]
api_key = 你的API密钥
model_id = 你的模型ID

[Processing]
batch_size = 10
```

## 使用方法

1. 准备输入文件：
   - 创建一个文本文件，每行一个 URL
   - 将文件保存为 `input/input_urls.txt`
   - 每个 URL 都应该指向一篇新闻文章

2. 运行主程序：
```bash
python main.py input/input_urls.txt
```

程序将：
- 从输入文件读取 URL
- 在 `output` 目录中生成带时间戳的输出文件：
  - `output/news_summary_YYYYMMDD_HHMMSS.md`
  - `output/news_summary_YYYYMMDD_HHMMSS.pdf`

## 输出文件

程序会生成两个带时间戳的文件：
- `output/news_summary_YYYYMMDD_HHMMSS.md`：包含所有摘要的 Markdown 文件
- `output/news_summary_YYYYMMDD_HHMMSS.pdf`：带格式和目录的 PDF 文件

输出文件中的内容格式示例：

```markdown
# [文章标题](URL)
作者 媒体 日期
文章摘要（约 200 字）
```

## 进度显示

程序会按批次处理 URL（每批 10 个）并显示进度：
```
开始处理，共45个URL，分5批进行...
正在处理第1批，共10个URL，还剩4批
第1批处理完成
正在处理第2批，共10个URL，还剩3批
...
正在处理第5批，共5个URL，还剩0批
全部处理完成，成功处理 45/45 个URL
```

## 配置说明

`config.txt` 配置文件使用 INI 格式，包含以下部分：

### [API]
- `api_key`：你的 Volces AI API 密钥
- `model_id`：用于生成摘要的模型 ID

### [Processing]
- `batch_size`：并行处理的 URL 数量（默认：10）

配置文件示例：
```ini
[API]
api_key = d3a5aa2a-b2fa-4a5f-99fc-4dc37936d7a8
model_id = claude-3-sonnet-20240229

[Processing]
batch_size = 10
```

## 注意事项

- 生成的 Markdown 和 PDF 文件会带有时间戳保存
- PDF 目录中只显示文章标题（不含 URL）
- 处理时间取决于 URL 数量和 API 响应时间
- 处理过程中的错误会被记录但不会中断整个程序
- 请妥善保管配置文件，不要公开分享 
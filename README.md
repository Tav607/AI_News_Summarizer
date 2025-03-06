# AI News Summary Generator

这个项目用于从网络文章链接生成AI新闻摘要，并将其转换为带有目录的PDF文档。

## 功能概述

项目包含两个主要脚本：

1. **collect_to_md.py**: 从文本文件中读取URL列表，调用AI接口生成摘要，并输出为Markdown文件。
2. **md_to_pdf.py**: 将Markdown文件转换为带有目录(TOC)的PDF文件，可选择高亮显示特定标题。

## 依赖项

在使用此项目前，请确保安装以下依赖：

```bash
pip install markdown2 pdfkit httpx openai
```

此外，您需要安装wkhtmltopdf：
- Windows: 从 https://wkhtmltopdf.org/downloads.html 下载并安装
- 安装后，确保wkhtmltopdf的路径在脚本中正确配置

## 配置

在使用collect_to_md.py前，需要创建一个config.txt文件，包含以下内容：

```ini
[API]
api_key = your_api_key_here
model_id = your_model_id_here

[Processing]
batch_size = 10
```

您可以参考config.example.txt文件进行配置。

## 使用方法

### 步骤1：从URL生成Markdown摘要

基本用法（使用默认输出路径和文件名）：
```bash
python collect_to_md.py input.txt
```

指定输出文件：
```bash
python collect_to_md.py input.txt output.md
```

参数说明：
- `input.txt`: 包含URL列表的文本文件，每行一个URL
- `output.md`: (可选) 输出的Markdown文件路径

如果不指定输出文件，将使用默认路径和文件名：`./output/AI_news_summary_yyyymmdd_hhmmss.md`

### 步骤2：将Markdown转换为带目录的PDF

基本用法（使用默认输出路径和文件名）：
```bash
python md_to_pdf.py input.md
```

高亮显示特定标题：
```bash
python md_to_pdf.py input.md highlight_headers.txt
```

完整用法（指定所有参数）：
```bash
python md_to_pdf.py input.md highlight_headers.txt output.pdf
```

参数说明：
- `input.md`: 输入的Markdown文件（不带目录）
- `highlight_headers.txt`: (可选) 包含需要高亮显示的标题列表的文本文件（每行一个标题）
- `output.pdf`: (可选) 输出的PDF文件路径

如果不指定输出文件，将使用默认路径和文件名：`./output/AI_news_summary_yyyymmdd_hhmmss.pdf`

## highlight_headers.txt 格式

文本文件中每行包含一个需要高亮的标题或标题的部分内容。脚本会检查每个标题是否包含这些文本，如果包含则进行高亮显示。

例如：
```
人工智能
大模型
GPT-4
```

这将高亮显示目录中包含"人工智能"、"大模型"或"GPT-4"的所有标题。

## 输出文件

脚本会生成以下文件：
1. PDF文件（带有可跳转的目录）
2. 带有目录的Markdown文件（文件名为`[output]_with_toc.md`）

## 示例

1. 收集新闻摘要（使用默认输出）：
```bash
python collect_to_md.py ./input/urls.txt
```

2. 生成带目录的PDF（使用默认输出）：
```bash
python md_to_pdf.py ./output/AI_news_summary_20240306_123045.md
```

3. 生成带高亮目录的PDF（使用默认输出）：
```bash
python md_to_pdf.py ./output/AI_news_summary_20240306_123045.md ./output/highlight.txt
```

4. 完整流程示例（指定所有输出）：
```bash
python collect_to_md.py ./input/urls.txt ./output/news.md
python md_to_pdf.py ./output/news.md ./output/highlight.txt ./output/news.pdf
```

## 注意事项

- 如果输入的Markdown文件已经包含目录，脚本会自动移除原始目录，只保留新生成的目录
- 高亮显示的标题在PDF中会以蓝色、加粗、下划线的方式显示
- 在Markdown文件中，高亮的标题会以加粗方式显示
- 默认输出文件名包含时间戳（格式：yyyymmdd_hhmmss），例如：`AI_news_summary_20240306_123045.pdf` 
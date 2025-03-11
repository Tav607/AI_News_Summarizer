# AI News Summary Generator

这个项目用于从网络文章链接生成AI新闻摘要，并将其转换为带有目录的PDF文档。提供了命令行界面和Web图形界面两种使用方式。

## 功能概述

项目包含三个主要组件：

1. **collect_to_md.py**: 从文本文件中读取URL列表，调用AI接口生成摘要，并输出为Markdown文件。
2. **md_to_pdf.py**: 将Markdown文件转换为带有目录(TOC)的PDF文件，可选择高亮显示特定标题。
3. **app.py**: Web图形界面，提供友好的用户界面来使用上述功能。

## 依赖项

在使用此项目前，请确保安装以下依赖：

```bash
pip install -r requirements.txt
```

依赖项包括：
```
markdown2==2.4.10
pdfkit==1.0.0
openai==1.12.0
httpx==0.27.0
flask==2.3.3
werkzeug==2.3.7
flask-wtf==1.2.1
```

此外，您需要安装wkhtmltopdf（用于PDF生成）：
- Windows: 从 [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html) 下载并安装
- macOS: `brew install wkhtmltopdf`
- Linux: `sudo apt-get install wkhtmltopdf`

## 配置

在使用前，需要创建一个config.txt文件，包含以下内容：

```ini
[API]
api_key = your_api_key_here
model_id = your_model_id_here

[Processing]
batch_size = 20
```

您可以参考config.example.txt文件进行配置，或者使用Web界面进行配置。

## 使用方法

### A. 使用批处理文件快速启动（Windows）

项目提供了一个批处理文件 `run_app.bat`，可以一键完成环境配置和应用启动。

#### 1. 使用方法

直接双击 `run_app.bat` 文件，或在命令提示符中运行：

```
run_app.bat
```

#### 2. 批处理文件功能

批处理文件会自动执行以下操作：

1. 检查 Python 是否已安装
2. 创建虚拟环境（如果不存在）
3. 激活虚拟环境
4. 安装所有依赖项（从 requirements.txt）
5. 启动 Flask 应用程序
6. 等待服务器启动（8秒）
7. 自动在默认浏览器中打开应用（http://localhost:5000）
8. 保持终端窗口打开以显示服务器日志

#### 3. 注意事项

- 首次运行时，批处理文件可能需要较长时间来创建虚拟环境和安装依赖项
- 请勿关闭终端窗口，否则应用程序将停止运行
- 如需停止应用程序，请关闭终端窗口

### B. Web图形界面使用方法

#### 1. 启动Web服务器

```bash
python app.py
```

#### 2. 访问Web界面

打开浏览器，访问：
```
http://localhost:5000
```

#### 3. 使用Web界面

Web界面提供三个主要功能页面：

- **API配置**: 设置您的API密钥和模型ID
  - 填写OpenAI API密钥或其他兼容的API密钥
  - 设置模型ID（如gpt-4, gpt-3.5-turbo等）
  - 设置批处理大小（推荐10-20,max 40）

- **收集到Markdown**: 将URL列表转换为Markdown摘要
  - 可以直接在文本框中输入URL（每行一个）
  - 或者上传包含URL列表的文本文件
  - 处理过程中会显示实时进度和处理日志
  - 处理完成后，可以下载生成的Markdown文件

- **Markdown转PDF**: 将Markdown文件转换为带目录的PDF
  - 上传Markdown文件
  - 可选择上传高亮文件（包含需要在目录中高亮显示的标题）
  - 处理完成后，PDF文件会自动下载

#### 4. Web界面工作流程

1. 首先，在"API配置"页面设置您的API密钥和模型ID
2. 然后，使用"收集到Markdown"页面处理URL列表
   - 您可以在处理过程中看到实时进度，包括当前处理批次、剩余批次等信息
   - 进度条会显示整体完成百分比
   - 处理日志区域会显示详细的处理信息
3. 最后，使用"Markdown转PDF"页面将生成的Markdown转换为PDF

### C. 命令行界面使用方法

#### 1. 从URL生成Markdown摘要

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

#### 2. 将Markdown转换为带目录的PDF

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

### 命令行示例

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

### Web界面示例流程

1. 启动Web服务器：`python app.py`
2. 访问 http://localhost:5000
3. 在"API配置"页面设置API密钥和模型ID
4. 在"收集到Markdown"页面输入URL或上传URL文件
5. 在"Markdown转PDF"页面上传生成的Markdown文件和可选的高亮文件

## 项目结构

- `app.py`: 主Flask应用程序
- `collect_to_md.py`: 从URL收集内容并转换为Markdown的模块
- `md_to_pdf.py`: 将Markdown转换为带目录的PDF的模块
- `templates/`: Web界面的HTML模板
- `static/`: 静态文件（CSS、JavaScript等）
- `input/`: 输入文件目录
- `output/`: 输出文件目录
- `uploads/`: 上传文件目录

## 特色功能

- **批量处理**: 支持批量处理URL，可配置批处理大小
- **高亮目录**: 支持在PDF目录中高亮显示特定标题
- **自动生成目录**: 自动为Markdown和PDF文件生成可跳转的目录

## 注意事项

- 如果输入的Markdown文件已经包含目录，脚本会自动移除原始目录，只保留新生成的目录
- 高亮显示的标题在PDF中会以加粗、下划线的方式显示
- 在Markdown文件中，高亮的标题会以加粗方式显示
- 默认输出文件名包含时间戳（格式：yyyymmdd_hhmmss），例如：`AI_news_summary_20240306_123045.pdf`

## 许可证

详见LICENSE文件。 
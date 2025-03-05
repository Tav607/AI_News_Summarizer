#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from collect_to_md import main as collect_to_md_main
from md_to_pdf import convert_md_to_pdf

def main():
    """
    主程序：整合URL收集到MD和MD转PDF的功能
    使用方法：python main.py input/input_urls.txt
    """
    if len(sys.argv) != 2:
        print("Usage: python main.py input/input_urls.txt")
        sys.exit(1)

    input_urls = sys.argv[1]

    # 确保输入和输出目录存在
    input_dir = "input"
    output_dir = "output"
    for directory in [input_dir, output_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # 检查输入文件是否存在
    if not os.path.exists(input_urls):
        print(f"Error: Input file '{input_urls}' does not exist.")
        sys.exit(1)
    
    if not os.path.exists("config.txt"):
        print("Error: Configuration file 'config.txt' does not exist.")
        sys.exit(1)

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_file = os.path.join(output_dir, f"news_summary_{timestamp}.md")
    pdf_file = os.path.join(output_dir, f"news_summary_{timestamp}.pdf")

    try:
        # 第一步：从URL收集内容并生成MD文件
        print("Step 1: Collecting content from URLs and generating Markdown...")
        collect_to_md_main(input_urls, md_file)

        # 第二步：将MD转换为PDF
        print("Step 2: Converting Markdown to PDF...")
        convert_md_to_pdf(md_file, pdf_file)

        print(f"Successfully generated files:")
        print(f"- Markdown: {md_file}")
        print(f"- PDF: {pdf_file}")

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
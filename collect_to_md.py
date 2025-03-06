#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
import math
import configparser
from datetime import datetime

# 如果你是用 volces-openai-sdk，请安装并导入它
# from openai import OpenAI
# 这里仅作示例:
try:
    from openai import OpenAI
except ImportError:
    print("请先安装相应的 SDK, 例如: pip install openai 或检查引用。")
    sys.exit(1)


def fetch_markdown(client, model_id, url, batch_idx):
    """
    用于并行调用 API 的辅助函数：
    给定 client, model_id, url, 调用接口获取对应 Markdown。
    返回值： (idx, md_text 或 None, 错误信息或 None)
    """
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": url}],
        )
        md_text = completion.choices[0].message.content
        # 如果返回文本不是以 # 开头，则截去 # 之前的部分
        if not md_text.startswith('#'):
            start_hash = md_text.find('#')
            if start_hash != -1:
                md_text = md_text[start_hash:]  # 去除所有 # 之前的冗余文本
        return (batch_idx, md_text, None)
    except Exception as e:
        return (batch_idx, None, str(e))


def main(input_txt, output_md=None):
    """
    从 input_txt 文件读取每行 URL，利用多线程并行调用 LLM Bot 接口获取 Markdown 文本并合并，
    最终输出为一个 output_md 文件（纯 Markdown）。
    从 config.txt 文件读取 API Key、model ID 和处理参数。
    
    如果未指定 output_md，则使用默认路径和文件名：./output/AI_news_summary_yyyymmdd_hhmmss.md
    """
    # 如果未指定输出文件，则使用默认路径和文件名
    if output_md is None:
        # 确保输出目录存在
        output_dir = os.path.join(".", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_md = os.path.join(output_dir, f"AI_news_summary_{timestamp}.md")

    # 1. 从配置文件读取配置
    if not os.path.exists("config.txt"):
        print("配置文件 config.txt 不存在！请检查。")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read("config.txt")
    
    api_key = config["API"]["api_key"]
    model_id = config["API"]["model_id"]
    batch_size = config["Processing"].getint("batch_size", 10)  # 默认值为10

    # 2. 初始化客户端
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3/bots",
        api_key=api_key,
    )

    # 3. 读取包含 URL 的文件
    if not os.path.exists(input_txt):
        print(f"输入文件 {input_txt} 不存在！")
        sys.exit(1)

    with open(input_txt, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    total_urls = len(urls)
    total_batches = math.ceil(total_urls / batch_size)
    print(f"\n开始处理，共{total_urls}个URL，分{total_batches}批进行（每批{batch_size}个）...\n")

    # 4. 并行调用 API
    results = []  # 用于存放 (idx, md_text) 的结果
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        for batch in range(total_batches):
            start_idx = batch * batch_size
            end_idx = min((batch + 1) * batch_size, total_urls)
            batch_urls = urls[start_idx:end_idx]
            current_batch_size = len(batch_urls)
            remaining_batches = total_batches - batch - 1
            
            print(f"正在处理第{batch+1}批，共{current_batch_size}个URL，还剩{remaining_batches}批")
            
            future_to_idx = {}
            for i, url in enumerate(batch_urls):
                future = executor.submit(fetch_markdown, client, model_id, url, start_idx+i)
                future_to_idx[future] = start_idx+i

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    (ret_idx, md_text, err_msg) = future.result()
                    if err_msg:
                        print(f"错误: {err_msg}")
                        continue
                    results.append((ret_idx, md_text))
                except Exception as e:
                    print(f"错误: {e}")

            print(f"第{batch+1}批处理完成")

    print(f"\n全部处理完成，成功处理 {len(results)}/{total_urls} 个URL\n")

    # 5. 按照原先顺序 (idx) 排序并合并所有 Markdown
    results.sort(key=lambda x: x[0])
    merged_md = "\n\n".join(r[1] for r in results if r[1])

    if not merged_md.strip():
        print("未获取到任何有效内容，程序结束。")
        return

    # 6. 将合并后的 Markdown 内容写入 .md 文件
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_md)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(merged_md)
        print(f"已生成Markdown文件：{output_md}")
        return output_md
    except Exception as e:
        print(f"写入文件失败: {e}")

if __name__ == "__main__":
    """
    命令行用法示例:
        python collect_to_md.py input_urls.txt [output.md]
        
    如果不指定输出文件，则使用默认路径和文件名：./output/AI_news_summary_yyyymmdd_hhmmss.md
    """
    if len(sys.argv) < 2:
        print("用法示例: python collect_to_md.py input.txt [output.md]")
        print("如果不指定输出文件，则使用默认路径和文件名：./output/AI_news_summary_yyyymmdd_hhmmss.md")
        sys.exit(1)

    input_txt_path = sys.argv[1]
    output_md_path = sys.argv[2] if len(sys.argv) > 2 else None
    main(input_txt_path, output_md_path)

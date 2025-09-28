import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import pandas as pd

pdf = "2024级培养方案.pdf" 
output_dir = Path("拆分结果") #输出目录
page_start, page_end = 2, 4 #目录所在页（0基索引，2=第3页，4=第5页）
offset = 6 #目录页码与实际页码差值

# 读取PDF，把目录页切出来
reader = PdfReader(pdf)
toc_text = ""
for page_num in range(page_start, page_end + 1):
    toc_text += reader.pages[page_num].extract_text() + "\n"

# 解析目录
pattern = re.compile(r"(.+?)\s+(\d+)\s*$")
matches = [pattern.match(line) for line in toc_text.splitlines() if pattern.match(line)]
toc_entries = [(m.group(1).strip(), int(m.group(2))) for m in matches]

# 清理章节标题
cleaned_toc = [(re.sub(r"[\.·\s]+", " ", title).strip(), page) for title, page in toc_entries]

# 得到真实章节起止页（应用偏移量）
chapters = []
for i, (title, start_page) in enumerate(cleaned_toc):
    start_real = start_page + offset
    if i < len(cleaned_toc) - 1:
        end_real = cleaned_toc[i+1][1] + offset - 1
    else:
        end_real = len(reader.pages)
    chapters.append((title, start_real, end_real))

# 拆分并保存PDF
output_dir.mkdir(exist_ok=True)
saved_files = []

for title, start, end in chapters:
    writer = PdfWriter()
    for page_num in range(start-1, end):  # 转换为0基索引
        writer.add_page(reader.pages[page_num])

    # 删除特殊字符，使得文件名安全化
    safe_title = re.sub(r"[\/:*?\"<>|]", "_", title)
    output_path = output_dir / f"{safe_title}.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)

    saved_files.append((title, start, end, str(output_path)))
    print(f" {title}: {start} → {end} （共 {end - start + 1} 页）")

print("\n拆分完成！")
print("拆分结果文件夹:", output_dir.resolve())
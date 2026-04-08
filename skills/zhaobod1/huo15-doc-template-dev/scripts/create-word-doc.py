#!/usr/bin/env python3
"""
create-word-doc.py - 创建 Word 文档
用法: ./create-word-doc.py <输出路径> [标题] [内容] [模板类型]
示例: ./create-word-doc.py report.docx "项目报告" "这是报告内容..." proposal

模板类型: proposal(提案) / report(报告) / contract(合同) / minutes(会议纪要) / generic(通用)
"""

import sys
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

TEMPLATE = {
    "proposal": {
        "title_color": RGBColor(0, 51, 102),
        "heading": "提案文档",
        "subtitle_style": True,
    },
    "report": {
        "title_color": RGBColor(31, 73, 125),
        "heading": "项目报告",
        "subtitle_style": True,
    },
    "contract": {
        "title_color": RGBColor(0, 0, 0),
        "heading": "合同文件",
        "subtitle_style": False,
    },
    "minutes": {
        "title_color": RGBColor(0, 80, 60),
        "heading": "会议纪要",
        "subtitle_style": True,
    },
    "generic": {
        "title_color": RGBColor(0, 0, 0),
        "heading": "文档",
        "subtitle_style": False,
    },
}

def create_word_doc(output_path, title="", content="", template="generic"):
    doc = Document()
    cfg = TEMPLATE.get(template, TEMPLATE["generic"])

    # 标题
    if title:
        h = doc.add_heading(title, 0)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in h.runs:
            run.font.color.rgb = cfg["title_color"]
            run.font.size = Pt(22)
            run.font.bold = True

    # 副标题/类型标注
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(cfg["heading"])
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(128, 128, 128)
    run.font.italic = True

    doc.add_paragraph()  # 空行

    # 内容
    if content:
        for para in content.split("\n"):
            para = para.strip()
            if not para:
                doc.add_paragraph()
                continue
            # 检测标题行（以 # 开头）
            if para.startswith("# "):
                p = doc.add_heading(para[2:], level=1)
                for run in p.runs:
                    run.font.size = Pt(14)
                    run.font.color.rgb = RGBColor(0, 51, 102)
            elif para.startswith("## "):
                p = doc.add_heading(para[3:], level=2)
                for run in p.runs:
                    run.font.size = Pt(13)
            elif para.startswith("### "):
                p = doc.add_heading(para[4:], level=3)
                for run in p.runs:
                    run.font.size = Pt(12)
            elif para.startswith("- ") or para.startswith("* "):
                p = doc.add_paragraph(para[2:], style="List Bullet")
            elif para.startswith("1. ") or para.startswith("1)"):
                p = doc.add_paragraph(para, style="List Number")
            else:
                p = doc.add_paragraph(para)
                p.paragraph_format.line_spacing = 1.5

    # 页脚
    footer = doc.sections[0].footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "青岛火一五信息科技有限公司 | www.huo15.com"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.runs[0].font.size = Pt(9)
    footer_para.runs[0].font.color.rgb = RGBColor(128, 128, 128)

    doc.save(output_path)
    print(f"✅ Word 文档已生成: {output_path}")

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "output.docx"
    title = sys.argv[2] if len(sys.argv) > 2 else ""
    content = sys.argv[3] if len(sys.argv) > 3 else ""
    template = sys.argv[4] if len(sys.argv) > 4 else "generic"

    create_word_doc(output, title, content, template)

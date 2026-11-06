"""Build the final DOCX report from the completed evaluation JSON files."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


DARK_BLUE = "1F4E79"
PALE_BLUE = "EAF2F8"
MID_GRAY = "D9D9D9"
BLACK = RGBColor(0, 0, 0)
CATEGORIES = {
    1: "Multi-Hop",
    2: "Temporal",
    3: "Open-Domain",
    4: "Single-Hop",
    5: "Adversarial",
}


def set_run_font(run, name: str, size: float, bold: bool = False, color=BLACK):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)


def shade_cell(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), MID_GRAY)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def remove_paragraph_borders(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is not None:
        p_pr.remove(p_bdr)


def add_table(document, headers, rows, widths=None):
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table)
    header = table.rows[0]
    set_repeat_table_header(header)
    for index, text in enumerate(headers):
        cell = header.cells[index]
        shade_cell(cell, DARK_BLUE)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(0)
        run = paragraph.add_run(str(text))
        set_run_font(run, "Calibri", 9.5, bold=True, color=RGBColor(255, 255, 255))
    for row_index, values in enumerate(rows):
        row = table.add_row()
        for cell_index, value in enumerate(values):
            cell = row.cells[cell_index]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index % 2 == 1:
                shade_cell(cell, PALE_BLUE)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.LEFT if cell_index == 0 else WD_ALIGN_PARAGRAPH.CENTER
            )
            paragraph.paragraph_format.space_after = Pt(0)
            run = paragraph.add_run(str(value))
            set_run_font(run, "Calibri", 9.5)
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    document.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, text, end])
    set_run_font(run, "Calibri", 9, color=RGBColor(89, 89, 89))


def load_results(result_dir: Path):
    results = {}
    for path in sorted(result_dir.glob("*_seed*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        results[(data["memory_mode"], data["seed"])] = data
    return results


def overall(data, metric):
    return 100 * data["aggregate_metrics"]["overall"][metric]["mean"]


def category(data, category_id, metric):
    return 100 * data["aggregate_metrics"][f"category_{category_id}"][metric]["mean"]


def build(results: dict, output: Path):
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)

    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = BLACK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    for style_name, size, before, after in (
        ("Title", 24, 0, 8),
        ("Heading 1", 15, 14, 6),
        ("Heading 2", 12, 10, 4),
    ):
        style = document.styles[style_name]
        style_p_pr = style.element.get_or_add_pPr()
        style_border = style_p_pr.find(qn("w:pBdr"))
        if style_border is not None:
            style_p_pr.remove(style_border)
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = BLACK
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)

    title = document.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    remove_paragraph_borders(title)
    title_run = title.add_run(
        "A-MEM Reproduction on a LoCoMo Subset with a Memory Evolution Ablation"
    )
    set_run_font(title_run, "Calibri", 23, bold=True)

    subtitle = document.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(8)
    set_run_font(
        subtitle.add_run("FTEC5660 Reproducibility Work"),
        "Calibri",
        11,
        bold=True,
        color=RGBColor(50, 50, 50),
    )
    metadata = document.add_paragraph()
    for label, value, break_after in (
        ("Author  ", "Leo Liu\n", False),
        ("Date  ", "6 November 2026\n", False),
        ("Repository  ", "https://github.com/LeoLIU1233/A-mem", True),
    ):
        set_run_font(metadata.add_run(label), "Calibri", 9.5, bold=True)
        set_run_font(metadata.add_run(value), "Calibri", 9.5)
    metadata.paragraph_format.space_after = Pt(12)

    lead = document.add_paragraph()
    lead.paragraph_format.space_before = Pt(4)
    set_run_font(lead.add_run("Result  "), "Calibri", 10.5, bold=True)
    set_run_font(
        lead.add_run(
            "The full pipeline runs successfully and gives a positive overall signal "
            "for Memory Evolution, but the result is only a partial behavioral "
            "reproduction. DeepSeek, a 25-question subset, and k=10 prevent direct "
            "comparison with the paper's GPT-4o-mini table."
        ),
        "Calibri",
        10.5,
    )

    document.add_heading("1 Reproduction target", level=1)
    document.add_paragraph(
        "The target is the paper's comparison between full A-MEM and A-MEM with "
        "Memory Evolution removed. The reported GPT-4o-mini Multi-Hop F1 is 27.02 "
        "for the full model and 21.35 without ME. Temporal F1 is 45.85 and 31.24, "
        "respectively. This comparison isolates one architectural component and "
        "has a directly measurable effect."
    )
    document.add_paragraph(
        "I used the authors' evaluation repository rather than rebuilding the "
        "memory system from the paper description. The baseline is "
        "WujiangXu/AgenticMemory at commit "
        "f9a173dec325d84fcc97e7828775c7b241c33466. The reference system "
        "implementation is agiresearch/A-mem."
    )

    document.add_heading("2 Reproduction setup", level=1)
    document.add_paragraph(
        "The evaluation retains note construction, embedding retrieval, link "
        "generation, and Memory Evolution. It uses the repository's robust "
        "plain-text path so the pipeline can run with an OpenAI-compatible "
        "DeepSeek endpoint."
    )
    add_table(
        document,
        ["Condition", "Completed run", "Paper target"],
        [
            ["Model", "deepseek-chat", "GPT-4o-mini"],
            ["Conversations", "1 of 10", "LoCoMo evaluation set"],
            ["Dialogue context", "First 120 turns", "Full conversations"],
            ["Questions", "5 per category; 25 total", "Full benchmark"],
            ["Retrieval k", "10 for every category", "40/40/50/50/40"],
            ["Seeds", "42, 43, 44", "Not reported"],
            ["Adversarial scoring", "Current Not-mentioned reference", "Legacy reference"],
        ],
        widths=[1.55, 2.30, 2.35],
    )
    document.add_paragraph(
        "The released locomo10.json file contains 10 conversations, 1,986 QA "
        "pairs, and 5,882 turns. Its SHA-256 is "
        "553CD5A15E25F2CECCC6ED185221EBA645080C93E5B91087560A91AA5961F365. "
        "The paper reports 7,512 QA pairs, so the available data count is a "
        "material reproduction condition."
    )

    document.add_heading("3 Isolated modification", level=1)
    document.add_paragraph(
        "The main scientific change is the link_only mode. Full mode builds a "
        "note, retrieves neighbors, asks the LLM whether to establish links, and "
        "updates neighbor context and tags when required. Link_only keeps note "
        "construction, retrieval, the evolution decision, and link creation, but "
        "skips neighbor context and tag updates."
    )
    document.add_paragraph(
        "DeepSeek support, deterministic category sampling, category-specific k, "
        "cache isolation, and tests are control and compatibility changes. The "
        "scientific treatment is the removal of Memory Evolution."
    )

    document.add_heading("4 Results", level=1)
    f1_full = [overall(results[("full", seed)], "f1") for seed in (42, 43, 44)]
    f1_link = [overall(results[("link_only", seed)], "f1") for seed in (42, 43, 44)]
    bleu_full = [overall(results[("full", seed)], "bleu1") for seed in (42, 43, 44)]
    bleu_link = [overall(results[("link_only", seed)], "bleu1") for seed in (42, 43, 44)]
    add_table(
        document,
        ["Mode", "Seed 42 F1", "Seed 43 F1", "Seed 44 F1", "Mean F1", "SD"],
        [
            ["Full A-MEM", *[f"{value:.2f}" for value in f1_full],
             f"{statistics.mean(f1_full):.2f}", f"{statistics.stdev(f1_full):.2f}"],
            ["Link only, w/o ME", *[f"{value:.2f}" for value in f1_link],
             f"{statistics.mean(f1_link):.2f}", f"{statistics.stdev(f1_link):.2f}"],
        ],
        widths=[1.30, 0.83, 0.83, 0.83, 0.82, 0.55],
    )
    paired_f1 = [full - link for full, link in zip(f1_full, f1_link)]
    document.add_paragraph(
        f"Mean BLEU-1 was {statistics.mean(bleu_full):.2f} for full A-MEM and "
        f"{statistics.mean(bleu_link):.2f} for link-only A-MEM. The paired F1 "
        f"differences by seed were {paired_f1[0]:+.2f}, {paired_f1[1]:+.2f}, and "
        f"{paired_f1[2]:+.2f} points. The mean paired gain was "
        f"{statistics.mean(paired_f1):+.2f} points with a standard deviation of "
        f"{statistics.stdev(paired_f1):.2f}."
    )

    category_rows = []
    for category_id, name in CATEGORIES.items():
        full_values = [category(results[("full", seed)], category_id, "f1") for seed in (42, 43, 44)]
        link_values = [category(results[("link_only", seed)], category_id, "f1") for seed in (42, 43, 44)]
        deltas = [full - link for full, link in zip(full_values, link_values)]
        category_rows.append(
            [
                name,
                f"{statistics.mean(full_values):.2f}",
                f"{statistics.mean(link_values):.2f}",
                f"{statistics.mean(deltas):+.2f}",
            ]
        )
    add_table(
        document,
        ["Category", "Full mean F1", "Link-only mean F1", "Paired gain"],
        category_rows,
        widths=[1.65, 1.55, 1.65, 1.35],
    )

    document.add_heading("5 Interpretation", level=1)
    document.add_paragraph(
        "The Multi-Hop gain is consistent with the intended mechanism. Links and "
        "updated neighbor descriptions can expose evidence from different "
        "dialogue sessions. The Temporal result does not reproduce the paper's "
        "large advantage, and Single-Hop is better without Memory Evolution in "
        "this subset."
    )
    document.add_paragraph(
        "The variation is substantial. Multi-Hop has a paired standard deviation "
        "of 16.78 points, and one seed makes the full model slightly worse "
        "overall. With five questions per category, one changed answer moves a "
        "category score by 20 points. The positive mean is therefore evidence "
        "for a possible effect, not a decisive estimate."
    )

    document.add_heading("6 Reproducibility boundaries", level=1)
    for text in (
        "DeepSeek replaces GPT-4o-mini, so absolute scores are not directly comparable with the paper.",
        "The completed run uses k=10 instead of the paper's category-specific retrieval values.",
        "The remote model does not receive the local seed, so trials remain stochastic.",
        "The corrected Adversarial reference differs from the paper's legacy reference.",
        "The sample contains one conversation and 25 questions.",
    ):
        paragraph = document.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(3)
        set_run_font(paragraph.add_run(text), "Calibri", 10.5)

    document.add_heading("7 Debugging record", level=1)
    document.add_paragraph(
        "The system implementation repository directs benchmark reproduction to "
        "WujiangXu/AgenticMemory, so evaluation switched to that repository. The "
        "original path expects structured JSON output; the robust plain-text path "
        "was used for DeepSeek. Category-specific retrieval settings were not "
        "available through the original command line, so retrieve_k_map was added."
    )
    document.add_paragraph(
        "A local fake OpenAI-compatible server tested note construction, query "
        "generation, answer generation, result serialization, and the three "
        "memory modes before the paid runs. The six completed runs reported no "
        "LLM failures. Twenty-four of the 25 questions have evidence inside the "
        "supplied 120 turns; the remaining Open-Domain question has no explicit "
        "evidence identifier."
    )

    document.add_heading("8 Conclusion", level=1)
    document.add_paragraph(
        "A-MEM reproduces at the pipeline level. The local ablation gives a "
        "positive overall signal for Memory Evolution, with the strongest "
        "support on Multi-Hop. The claimed advantage does not transfer "
        "consistently to Temporal or Single-Hop under this small DeepSeek subset."
    )
    document.add_paragraph(
        "A closer test should expand the question and conversation count, use "
        "more seeds, and run the paper-aligned GPT-4o-mini configuration with "
        "category-specific retrieval values. Those conditions are required "
        "before claiming exact numerical reproduction."
    )

    footer = section.footer.paragraphs[0]
    add_page_number(footer)

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results")
    parser.add_argument("--output", default="A-MEM_Reproduction_Report.docx")
    args = parser.parse_args()
    results = load_results(Path(args.results))
    expected = {
        (mode, seed)
        for mode, seeds in (("full", (42, 43, 44)), ("link_only", (42, 43, 44)))
        for seed in seeds
    }
    missing = expected - set(results)
    if missing:
        raise SystemExit(f"Missing result files: {sorted(missing)}")
    build(results, Path(args.output))


if __name__ == "__main__":
    main()

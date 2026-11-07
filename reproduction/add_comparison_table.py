"""Insert the reported-versus-measured F1 table into the edited report."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.shared import Pt

from build_report import add_table, set_run_font


ROWS = [
    ["Multi-Hop, full", "27.02", "44.24"],
    ["Multi-Hop, w/o ME", "21.35", "28.69"],
    ["Temporal, full", "45.85", "11.59"],
    ["Temporal, w/o ME", "31.24", "12.62"],
    ["Open-Domain, full", "12.14", "21.15"],
    ["Open-Domain, w/o ME", "10.13", "13.35"],
    ["Single-Hop, full", "44.65", "45.17"],
    ["Single-Hop, w/o ME", "39.17", "56.60"],
    ["Adversarial, full", "50.03", "86.67"],
    ["Adversarial, w/o ME", "44.16", "80.00"],
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default="A-MEM_Reproduction_Report.docx",
    )
    args = parser.parse_args()
    path = Path(args.path)
    document = Document(path)

    comparison_exists = any(
        table.rows[0].cells[0].text == "Metric"
        and table.rows[0].cells[1].text == "Paper GPT-4o-mini F1"
        for table in document.tables
    )
    boundary_heading = next(
        paragraph for paragraph in document.paragraphs
        if paragraph.text.strip() == "6 Reproducibility boundaries"
    )
    boundary_heading.paragraph_format.page_break_before = True
    if comparison_exists:
        document.save(path)
        print("Comparison table already present")
        return

    result_heading = next(
        paragraph for paragraph in document.paragraphs
        if paragraph.text.strip() == "4 Results"
    )
    if len(document.tables) < 2:
        raise RuntimeError("Expected existing overall and category result tables")
    overall_table = document.tables[1]

    heading = document.add_heading("4.1 Reported and measured F1", level=2)
    note = document.add_paragraph(
        "The following table places the paper's reported GPT-4o-mini results "
        "beside the completed DeepSeek subset. The values make the reproduction "
        "target explicit; they are not a controlled comparison between models."
    )
    table = add_table(
        document,
        ["Metric", "Paper GPT-4o-mini F1", "This run DeepSeek F1"],
        ROWS,
        widths=[2.30, 1.75, 1.85],
    )
    spacer = document.paragraphs[-1]
    caption = document.add_paragraph()
    caption.paragraph_format.space_after = Pt(0)
    set_run_font(
        caption.add_run(
            "Values are F1 percentages. The Adversarial rows use different "
            "reference conventions: the paper uses the legacy adversarial-answer "
            "reference, while this run uses the repository's corrected "
            "Not-mentioned reference."
        ),
        "Calibri",
        9,
    )
    next_heading = document.add_heading("4.2 Trial and category results", level=2)

    anchor = overall_table._tbl
    for element in (
        heading._p,
        note._p,
        table._tbl,
        spacer._p,
        caption._p,
        next_heading._p,
    ):
        anchor.addprevious(element)

    document.save(path)


if __name__ == "__main__":
    main()

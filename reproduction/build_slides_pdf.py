"""Build a concise five-slide PDF presentation for the A-MEM reproduction."""

from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


WIDTH = 960
HEIGHT = 540
MARGIN = 64

NAVY = "#163A5F"
INK = "#182534"
MUTED = "#5D6B78"
TEAL = "#138A8A"
CORAL = "#C65D4B"
PALE = "#F4F7FA"
LINE = "#D8E1E8"
WHITE = "#FFFFFF"

FONT_REGULAR = "Calibri"
FONT_BOLD = "Calibri-Bold"


def register_fonts():
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, r"C:\Windows\Fonts\calibri.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\calibrib.ttf"))


def set_color(pdf, value):
    pdf.setFillColorRGB(*(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)))


def text(pdf, x, y, value, size=20, bold=False, color=INK):
    pdf.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    set_color(pdf, color)
    pdf.drawString(x, y, value)


def right_text(pdf, x, y, value, size=20, bold=False, color=INK):
    pdf.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    set_color(pdf, color)
    pdf.drawRightString(x, y, value)


def wrapped(pdf, x, y, width, value, size=18, leading=26, color=INK, bold=False):
    lines = []
    for paragraph in value.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if pdfmetrics.stringWidth(
                candidate, FONT_BOLD if bold else FONT_REGULAR, size
            ) <= width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    pdf.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    set_color(pdf, color)
    for index, line in enumerate(lines):
        pdf.drawString(x, y - index * leading, line)
    return y - len(lines) * leading


def page_base(pdf, number, section):
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    text(pdf, MARGIN, HEIGHT - 34, section.upper(), 10, bold=True, color=TEAL)
    right_text(pdf, WIDTH - MARGIN, HEIGHT - 34, f"{number:02d} / 05", 10, color=MUTED)
    pdf.setStrokeColorRGB(0.84, 0.89, 0.92)
    pdf.setLineWidth(1)
    pdf.line(MARGIN, 44, WIDTH - MARGIN, 44)
    text(pdf, MARGIN, 24, "FTEC5660  |  A-MEM Reproduction", 9, color=MUTED)
    right_text(
        pdf,
        WIDTH - MARGIN,
        24,
        "github.com/LeoLIU1233/A-mem",
        9,
        color=MUTED,
    )


def slide_cover(pdf):
    set_color(pdf, NAVY)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    text(pdf, MARGIN, 414, "FTEC5660 REPRODUCIBILITY WORK", 11, bold=True, color="#B9D8E6")
    wrapped(
        pdf,
        MARGIN,
        340,
        760,
        "A-MEM Memory Evolution Ablation",
        40,
        46,
        WHITE,
        bold=True,
    )
    wrapped(
        pdf,
        MARGIN,
        260,
        650,
        "Testing full A-MEM against a link-only variant on LoCoMo",
        20,
        28,
        "#D9E7EF",
    )
    pdf.setStrokeColorRGB(0.36, 0.61, 0.68)
    pdf.setLineWidth(1)
    pdf.line(MARGIN, 186, 560, 186)
    text(pdf, MARGIN, 148, "LIU YIBO", 16, bold=True, color=WHITE)
    text(
        pdf,
        MARGIN,
        124,
        "Agentic AI for Business and FinTech (FTEC5660)",
        14,
        color="#D9E7EF",
    )
    pdf.showPage()


def slide_target(pdf):
    page_base(pdf, 2, "01  What I reproduced")
    wrapped(
        pdf,
        MARGIN,
        420,
        760,
        "The paper claims that Memory Evolution improves A-MEM",
        32,
        38,
        NAVY,
        bold=True,
    )
    text(pdf, MARGIN, 354, "Multi-Hop F1 from the paper", 17, bold=True, color=MUTED)
    text(pdf, MARGIN, 292, "27.02", 42, bold=True, color=NAVY)
    text(pdf, MARGIN, 266, "Full A-MEM", 15, color=MUTED)
    text(pdf, 340, 292, "21.35", 42, bold=True, color=CORAL)
    text(pdf, 340, 266, "w/o ME", 15, color=MUTED)
    text(pdf, 632, 292, "3 seeds", 42, bold=True, color=TEAL)
    text(pdf, 632, 266, "tested locally", 15, color=MUTED)

    text(pdf, MARGIN, 206, "A-MEM pipeline", 17, bold=True, color=INK)
    stages = [
        ("01", "Note"),
        ("02", "Retrieve"),
        ("03", "Link"),
        ("04", "Evolve"),
    ]
    start_x = MARGIN
    gap = 214
    for index, (number, label) in enumerate(stages):
        x = start_x + index * gap
        text(pdf, x, 166, number, 12, bold=True, color=TEAL)
        text(pdf, x, 138, label, 21, bold=True, color=NAVY)
        if index < len(stages) - 1:
            pdf.setStrokeColorRGB(0.75, 0.82, 0.87)
            pdf.setLineWidth(1)
            pdf.line(x + 54, 145, x + gap - 24, 145)
    wrapped(
        pdf,
        MARGIN,
        98,
        800,
        "Scope: official benchmark code, official LoCoMo data, DeepSeek Chat, one conversation, 25 questions.",
        13,
        18,
        MUTED,
    )
    pdf.showPage()


def slide_change(pdf):
    page_base(pdf, 3, "02  What I changed")
    wrapped(
        pdf,
        MARGIN,
        420,
        800,
        "One isolated change: remove neighbor updates",
        32,
        38,
        NAVY,
        bold=True,
    )
    column_width = 360
    left_x = MARGIN
    right_x = WIDTH - MARGIN - column_width

    text(pdf, left_x, 352, "FULL A-MEM", 18, bold=True, color=TEAL)
    pdf.setStrokeColorRGB(0.08, 0.54, 0.54)
    pdf.setLineWidth(3)
    pdf.line(left_x, 340, left_x + column_width, 340)
    for index, item in enumerate(
        [
            "Builds structured memory notes",
            "Retrieves similar memories",
            "Creates links between related notes",
            "Updates neighbor context and tags",
        ]
    ):
        text(pdf, left_x, 296 - index * 48, f"{index + 1}", 12, bold=True, color=TEAL)
        wrapped(pdf, left_x + 30, 296 - index * 48, 310, item, 17, 22, INK)

    text(pdf, right_x, 352, "LINK-ONLY  /  w/o ME", 18, bold=True, color=CORAL)
    pdf.setStrokeColorRGB(0.78, 0.36, 0.29)
    pdf.line(right_x, 340, right_x + column_width, 340)
    for index, item in enumerate(
        [
            "Uses the same note construction",
            "Uses the same retrieval and link step",
            "Disables neighbor context updates",
            "Disables neighbor tag updates",
        ]
    ):
        text(pdf, right_x, 296 - index * 48, f"{index + 1}", 12, bold=True, color=CORAL)
        wrapped(pdf, right_x + 30, 296 - index * 48, 310, item, 17, 22, INK)

    pdf.setFillColorRGB(0.96, 0.97, 0.98)
    pdf.roundRect(MARGIN, 82, WIDTH - 2 * MARGIN, 56, 7, fill=1, stroke=0)
    text(
        pdf,
        MARGIN + 18,
        103,
        "The ablation is isolated and measurable: only Memory Evolution changes.",
        17,
        bold=True,
        color=NAVY,
    )
    pdf.showPage()


def slide_results(pdf):
    page_base(pdf, 4, "03  Results")
    text(pdf, MARGIN, 420, "Overall mean F1", 17, bold=True, color=MUTED)
    text(pdf, MARGIN, 350, "41.76", 49, bold=True, color=NAVY)
    text(pdf, MARGIN, 325, "Full A-MEM", 14, color=MUTED)
    text(pdf, 310, 350, "38.25", 49, bold=True, color=CORAL)
    text(pdf, 310, 325, "Link-only", 14, color=MUTED)
    text(pdf, 570, 350, "+3.51", 49, bold=True, color=TEAL)
    text(pdf, 570, 325, "F1 points", 14, color=MUTED)

    text(pdf, MARGIN, 270, "Paper vs this run", 17, bold=True, color=INK)
    headers = ["Target metric", "Paper GPT-4o-mini", "This run DeepSeek"]
    col_x = [MARGIN, 440, 665]
    pdf.setFillColorRGB(0.09, 0.23, 0.37)
    pdf.rect(MARGIN, 230, 792, 30, fill=1, stroke=0)
    for x, label in zip(col_x, headers):
        text(pdf, x + 10, 239, label, 11, bold=True, color=WHITE)

    rows = [
        ("Multi-Hop full", "27.02", "44.24"),
        ("Multi-Hop w/o ME", "21.35", "28.69"),
        ("Temporal full", "45.85", "11.59"),
        ("Temporal w/o ME", "31.24", "12.62"),
    ]
    row_y = 192
    for index, row in enumerate(rows):
        if index % 2 == 1:
            pdf.setFillColorRGB(0.96, 0.98, 0.99)
            pdf.rect(MARGIN, row_y - 8, 792, 33, fill=1, stroke=0)
        for column, (x, value) in enumerate(zip(col_x, row)):
            text(pdf, x + 10, row_y, value, 14, bold=column == 0, color=INK)
        pdf.setStrokeColorRGB(0.84, 0.88, 0.91)
        pdf.line(MARGIN, row_y - 10, WIDTH - MARGIN, row_y - 10)
        row_y -= 34

    text(pdf, MARGIN, 50, "Multi-Hop direction reproduced. Temporal did not.", 18, bold=True, color=NAVY)
    pdf.showPage()


def slide_takeaway(pdf):
    page_base(pdf, 5, "04  Key lessons and next steps")
    wrapped(
        pdf,
        MARGIN,
        420,
        820,
        "The pipeline worked. The paper's broad advantage did not.",
        30,
        37,
        NAVY,
        bold=True,
    )
    columns = [
        (
            "WORKED",
            TEAL,
            [
                "Six runs completed",
                "25 questions per run",
                "Zero LLM failures",
                "Multi-Hop mean gain +15.56",
            ],
        ),
        (
            "DID NOT HOLD",
            CORAL,
            [
                "Temporal mean change -1.03",
                "Single-Hop mean change -11.43",
                "Large seed-to-seed variance",
                "Small sample makes results uncertain",
            ],
        ),
    ]
    for col_index, (heading, color, items) in enumerate(columns):
        x = MARGIN + col_index * 430
        text(pdf, x, 340, heading, 16, bold=True, color=color)
        pdf.setStrokeColorRGB(
            *(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
        )
        pdf.setLineWidth(3)
        pdf.line(x, 328, x + 350, 328)
        for item_index, item in enumerate(items):
            y = 292 - item_index * 39
            pdf.setFillColorRGB(
                *(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
            )
            pdf.circle(x + 5, y + 5, 4, fill=1, stroke=0)
            wrapped(pdf, x + 22, y, 330, item, 16, 21, INK)

    pdf.setFillColorRGB(0.96, 0.97, 0.98)
    pdf.roundRect(MARGIN, 56, WIDTH - 2 * MARGIN, 88, 7, fill=1, stroke=0)
    label_x = MARGIN + 18
    value_x = MARGIN + 122
    text(pdf, label_x, 121, "KEY LESSON", 9, bold=True, color=TEAL)
    text(
        pdf,
        value_x,
        121,
        "Match model, data version, scoring, and retrieval k before comparing scores.",
        13,
        color=INK,
    )
    text(pdf, label_x, 98, "NEXT STEP", 9, bold=True, color=TEAL)
    text(
        pdf,
        value_x,
        98,
        "Start with a small test, verify failures and caches, then expand questions and seeds.",
        13,
        color=INK,
    )
    text(pdf, label_x, 75, "CONCLUSION", 9, bold=True, color=TEAL)
    text(
        pdf,
        value_x,
        75,
        "Partial behavioral reproduction, not an exact numerical replication.",
        13,
        bold=True,
        color=NAVY,
    )
    pdf.showPage()


def build(output: Path):
    register_fonts()
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    pdf.setTitle("A-MEM Memory Evolution Ablation")
    pdf.setAuthor("LIU YIBO")
    pdf.setSubject("FTEC5660 Reproducibility Work")
    slide_cover(pdf)
    slide_target(pdf)
    slide_change(pdf)
    slide_results(pdf)
    slide_takeaway(pdf)
    pdf.save()


if __name__ == "__main__":
    build(Path("output/pdf/A-MEM_Reproduction_Slides.pdf"))

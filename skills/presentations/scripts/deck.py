"""Slide functions for Vinicius Valiati's brand, built with python-pptx.

Colors, fonts, sizes and margins come from brand/BRAND.md, so the brand has one source.
Each Deck method adds one slide type; the occasion sets the profile. Positions are
(left, top, width, height) tuples.

    deck = Deck("status-report", title="Weekly status")
    deck.cover("OTIF recovered to 94% after the carrier change", "Logistics, week 44")
    deck.bar_chart("Carrier B caused most late deliveries", ["A", "B"], [42, 188], 1, "Source: TMS")
    deck.save("status.pptx")

python-pptx only sets bold, so weights from 600 render as bold.
"""

from datetime import UTC, datetime
from pathlib import Path

import yaml
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

BRAND_PATH = Path(__file__).resolve().parent.parent / "brand" / "BRAND.md"
NO_TABLE_STYLE = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
MAX_TABLE_ROWS = 6
MAX_TABLE_COLUMNS = 5
# Theme slots mapped to brand tokens, so colors picked by hand in PowerPoint match.
THEME_COLORS = {
    "dk1": "text",
    "lt1": "white",
    "dk2": "ink",
    "lt2": "paper",
    "accent1": "petrol",
    "accent2": "amber",
    "accent3": "steel",
    "accent4": "bar-neutral",
    "accent5": "positive",
    "accent6": "negative",
    "hlink": "petrol",
    "folHlink": "muted",
}

# Profile switches per occasion; the full profiles are in BRAND.md.
PROFILES = {
    "status-report": {"dense": True, "dark_cover": True, "max_amber": 1},
    "kickoff": {"dense": False, "dark_cover": True, "max_amber": 1},
    "technical": {"dense": False, "dark_cover": True, "max_amber": 1},
    "pitch": {"dense": False, "dark_cover": True, "max_amber": 2},
    "one-on-one": {"dense": False, "dark_cover": False, "max_amber": 1},
}


def load_brand(path: Path = BRAND_PATH) -> dict:
    """Return the YAML front matter of BRAND.md."""
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])


def _inches(value: str) -> int:
    return Inches(float(value.split()[0]))


class Deck:
    """A 16:9 deck in the brand. One method per slide type."""

    def __init__(self, occasion: str, title: str = "", author: str = "Vinicius Valiati"):
        if occasion not in PROFILES:
            raise ValueError(f"Unknown occasion {occasion!r}; use one of {sorted(PROFILES)}")
        self.brand = load_brand()
        self.profile = PROFILES[occasion]
        self.colors = {k: RGBColor.from_string(v[1:]) for k, v in self.brand["colors"].items()}
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        props = self.prs.core_properties
        props.author = props.last_modified_by = author
        props.title = title
        props.comments = ""
        props.created = props.modified = datetime.now(UTC).replace(microsecond=0)
        props.revision = 1
        layout = self.brand["layout"]
        self.x = _inches(layout["margin-x"])
        self.top = _inches(layout["margin-top"])
        self.bottom = self.prs.slide_height - _inches(layout["margin-bottom"])
        self.width = self.prs.slide_width - 2 * self.x
        self.section = ""
        self._brand_theme()

    # Building blocks

    def _brand_theme(self) -> None:
        """Brand fonts and colors in the theme, for shapes added by hand in PowerPoint."""
        part = self.prs.slide_master.part.part_related_by(RT.THEME)
        theme = etree.fromstring(part.blob)
        scheme = theme.find(f".//{qn('a:clrScheme')}")
        scheme.set("name", "Vinicius Valiati")
        for slot, token in THEME_COLORS.items():
            element = scheme.find(qn(f"a:{slot}"))
            element.clear()
            etree.SubElement(element, qn("a:srgbClr"), val=str(self.colors[token]))
        fonts = theme.find(f".//{qn('a:fontScheme')}")
        fonts.set("name", "Vinicius Valiati")
        for tag, font in (("a:majorFont", "heading"), ("a:minorFont", "body")):
            latin = fonts.find(f"{qn(tag)}/{qn('a:latin')}")
            latin.set("typeface", self.brand["typography"][font]["family"])
        part._blob = etree.tostring(theme, xml_declaration=True, encoding="UTF-8", standalone=True)

    def _slide(self, background: str):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self.colors[background]
        return slide

    def _style(self, run, style: str, color: str) -> None:
        spec = self.brand["type-scale"][style]
        run.font.name = self.brand["typography"][spec["font"]]["family"]
        run.font.size = Pt(spec["size"])
        run.font.bold = spec["weight"] >= 600
        run.font.color.rgb = self.colors[color]
        if "letter-spacing" in spec:
            em = float(str(spec["letter-spacing"]).removesuffix("em"))
            # spc is in hundredths of a point.
            run._r.get_or_add_rPr().set("spc", str(round(em * spec["size"] * 100)))

    def _text(self, slide, box, lines, style, color, anchor=MSO_ANCHOR.TOP, align=None):
        frame = slide.shapes.add_textbox(*box).text_frame
        frame.word_wrap = True
        frame.vertical_anchor = anchor
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        spec = self.brand["type-scale"][style]
        for index, line in enumerate([lines] if isinstance(lines, str) else lines):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.line_spacing = spec.get("line-height")
            if align:
                paragraph.alignment = align
            run = paragraph.add_run()
            run.text = line.upper() if spec.get("case") == "upper" else line
            self._style(run, style, color)
        return frame

    def _card(self, slide, box, fill: str) -> None:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *box)
        shape.adjustments[0] = Pt(4) / min(box[2], box[3])
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.colors[fill]
        shape.line.fill.background()
        shape.shadow.inherit = False

    def _content(self, title: str, label: str = ""):
        """Paper slide with label, action title and footer; return slide, body top, height."""
        slide = self._slide("paper")
        top = self.top
        if label:
            self._text(slide, (self.x, top, self.width, Inches(0.3)), label, "label", "petrol")
            top += Inches(0.4)
        self._text(slide, (self.x, top, self.width, Inches(1.0)), title, "slide-title", "text")
        footer = (self.bottom - Inches(0.2), self.width // 2, Inches(0.2))
        self._text(slide, (self.x, *footer), self.section, "caption", "muted")
        number = str(len(self.prs.slides))
        self._text(
            slide,
            (self.x + self.width // 2, *footer),
            number,
            "caption",
            "muted",
            align=PP_ALIGN.RIGHT,
        )
        body_top = top + Inches(1.25)
        return slide, body_top, self.bottom - Inches(0.45) - body_top

    def _wordmark(self, slide, top, color: str, contact: str = "") -> None:
        wordmark = self.brand["typography"]["wordmark"]
        run = self._text(slide, (self.x, top, Inches(5), Inches(0.3)), "", "caption", color)
        run = run.paragraphs[0].runs[0]
        run.text = wordmark["text"]
        run.font.name, run.font.size, run.font.bold = wordmark["family"], Pt(14), True
        run._r.get_or_add_rPr().set("spc", str(round(-0.01 * 14 * 100)))
        if contact:
            muted = "on-ink-muted" if color == "white" else "muted"
            box = (self.x, top + Inches(0.32), Inches(8), Inches(0.25))
            self._text(slide, box, contact, "caption", muted)

    def _source(self, slide, top, text: str) -> None:
        self._text(slide, (self.x, top, self.width, Inches(0.25)), text, "caption", "muted")

    def _bullet(self, paragraph) -> None:
        p_pr = paragraph._p.get_or_add_pPr()
        p_pr.set("marL", str(Inches(0.28)))
        p_pr.set("indent", str(-Inches(0.28)))
        color = etree.SubElement(p_pr, qn("a:buClr"))
        etree.SubElement(color, qn("a:srgbClr")).set("val", str(self.colors["petrol"]))
        etree.SubElement(p_pr, qn("a:buChar")).set("char", "•")

    def _rule(self, cell, color: str) -> None:
        """Bottom border only; borders must come before the cell fill in the XML."""
        tc_pr = cell._tc.get_or_add_tcPr()
        fills = [c for c in tc_pr if c.tag in (qn("a:noFill"), qn("a:solidFill"))]
        for side in ("a:lnL", "a:lnR", "a:lnT"):
            etree.SubElement(etree.SubElement(tc_pr, qn(side), w="0"), qn("a:noFill"))
        line = etree.SubElement(tc_pr, qn("a:lnB"), w=str(Pt(0.75)))
        fill = etree.SubElement(line, qn("a:solidFill"))
        etree.SubElement(fill, qn("a:srgbClr")).set("val", str(self.colors[color]))
        for child in fills:
            tc_pr.append(child)

    # Slide types

    def cover(self, title: str, subtitle: str = "", date: str = "") -> None:
        """Opening slide. Dark except for 1:1 decks."""
        dark = self.profile["dark_cover"]
        slide = self._slide("ink" if dark else "paper")
        text, muted = ("white", "on-ink-muted") if dark else ("text", "muted")
        box = (self.x, Inches(2.2), Inches(10), Inches(2.0))
        self._text(slide, box, title, "cover-title", text, anchor=MSO_ANCHOR.BOTTOM)
        if subtitle:
            self._text(
                slide, (self.x, Inches(4.4), Inches(10), Inches(0.9)), subtitle, "subtitle", muted
            )
        bottom = self.bottom - Inches(0.3)
        self._wordmark(slide, bottom, text)
        if date:
            box = (self.x + Inches(6), bottom, self.width - Inches(6), Inches(0.3))
            self._text(slide, box, date, "caption", muted, align=PP_ALIGN.RIGHT)

    def divider(self, title: str, label: str = "") -> None:
        """Chapter slide on ink. Its title becomes the footer section."""
        slide = self._slide("ink")
        self.section = title
        if label:
            self._text(
                slide,
                (self.x, Inches(2.6), self.width, Inches(0.3)),
                label,
                "label",
                "petrol-light",
            )
        self._text(
            slide, (self.x, Inches(3.0), Inches(10), Inches(1.6)), title, "divider-title", "white"
        )

    def bullets(self, title: str, points: list[str], label: str = "") -> None:
        """Action title plus up to 5 short points."""
        slide, top, height = self._content(title, label)
        style = "body-dense" if self.profile["dense"] else "body"
        frame = self._text(slide, (self.x, top, Inches(9), height), points, style, "text")
        for paragraph in frame.paragraphs:
            self._bullet(paragraph)
            paragraph.space_after = Pt(10)

    def kpis(self, title: str, items: list[dict], label: str = "") -> None:
        """Up to 4 KPI cards: {"label", "value", "comparison", "highlight"}.

        The highlighted card has the amber fill with ink text (amber text fails on light).
        """
        if sum(bool(i.get("highlight")) for i in items) > self.profile["max_amber"]:
            raise ValueError("Too many highlighted KPIs for this occasion")
        slide, top, _ = self._content(title, label)
        gap = Inches(0.25)
        width = (self.width - gap * (len(items) - 1)) // len(items)
        for index, item in enumerate(items):
            left = self.x + index * (width + gap)
            highlight = bool(item.get("highlight"))
            self._card(slide, (left, top, width, Inches(2.2)), "amber" if highlight else "white")
            text, muted = ("ink", "ink") if highlight else ("text", "muted")
            inner_left, inner_width = left + Inches(0.25), width - Inches(0.5)
            for offset, height, value, style, color in (
                (0.25, 0.3, item["label"], "label", muted),
                (0.65, 0.8, item["value"], "kpi-number", text),
                (1.5, 0.5, item.get("comparison", ""), "caption", muted),
            ):
                box = (inner_left, top + Inches(offset), inner_width, Inches(height))
                self._text(slide, box, value, style, color)

    def big_numbers(self, title: str, items: list[dict]) -> None:
        """Dark slide with 1 big number (2 in a pitch): {"value", "caption"}."""
        if len(items) > self.profile["max_amber"]:
            raise ValueError("Too many big numbers for this occasion")
        slide = self._slide("ink")
        self._text(
            slide, (self.x, self.top, self.width, Inches(1.0)), title, "slide-title", "white"
        )
        width = self.width // len(items)
        for index, item in enumerate(items):
            left = self.x + index * width
            box = (left, Inches(2.6), width - Inches(0.3), Inches(1.6))
            self._text(slide, box, item["value"], "big-number", "amber")
            box = (left, Inches(4.3), width - Inches(0.6), Inches(1.0))
            self._text(slide, box, item["caption"], "subtitle", "on-ink-muted")

    def bar_chart(
        self,
        title,
        categories,
        values,
        highlight: int,
        source: str,
        number_format: str = "0",
        label: str = "",
    ) -> None:
        """Column chart from zero, values labeled; the highlighted bar is amber."""
        slide, top, height = self._content(title, label)
        data = CategoryChartData()
        data.categories = categories
        data.add_series("values", values)
        box = (self.x, top, self.width, height - Inches(0.35))
        chart = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, *box, data).chart
        chart.has_legend = chart.has_title = False
        chart.font.name = self.brand["typography"]["body"]["family"]
        chart.font.size = Pt(self.brand["type-scale"]["body-dense"]["size"])
        chart.font.color.rgb = self.colors["muted"]
        plot = chart.plots[0]
        plot.gap_width = 60
        plot.has_data_labels = True
        plot.data_labels.number_format = number_format
        plot.data_labels.number_format_is_linked = False
        plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
        plot.data_labels.font.color.rgb = self.colors["text"]
        for index, point in enumerate(plot.series[0].points):
            point.format.fill.solid()
            color = "amber" if index == highlight else "bar-neutral"
            point.format.fill.fore_color.rgb = self.colors[color]
        chart.value_axis.minimum_scale = 0
        chart.value_axis.has_major_gridlines = False
        chart.value_axis.visible = False
        chart.category_axis.format.line.color.rgb = self.colors["line"]
        self._source(slide, top + height - Inches(0.3), source)

    def table(
        self, title, header: list[str], rows: list[list[str]], source: str = "", label: str = ""
    ) -> None:
        """Table with rules in `line`; up to 6 rows and 5 columns."""
        if len(rows) > MAX_TABLE_ROWS or len(header) > MAX_TABLE_COLUMNS:
            raise ValueError("Table too large for a slide; move the detail to the appendix")
        slide, top, _ = self._content(title, label)
        row_height = Inches(0.5)
        height = row_height * (len(rows) + 1)
        shape = slide.shapes.add_table(len(rows) + 1, len(header), self.x, top, self.width, height)
        table = shape.table
        table._tbl.tblPr.find(qn("a:tableStyleId")).text = NO_TABLE_STYLE
        body = "body-dense" if self.profile["dense"] else "body"
        for row_index, values in enumerate([header, *rows]):
            is_header = row_index == 0
            for col_index, value in enumerate(values):
                cell = table.cell(row_index, col_index)
                cell.fill.background()
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                run = cell.text_frame.paragraphs[0].add_run()
                run.text = value.upper() if is_header else value
                self._style(run, "label" if is_header else body, "muted" if is_header else "text")
                self._rule(cell, "text" if is_header else "line")
        if source:
            self._source(slide, top + height + Inches(0.15), source)

    def code(self, title: str, code: str, caption: str = "", label: str = "") -> None:
        """Code or SQL on a white card, in the mono font."""
        slide, top, height = self._content(title, label)
        card_height = height - Inches(0.4)
        self._card(slide, (self.x, top, self.width, card_height), "white")
        box = (self.x + Inches(0.3), top + Inches(0.25), self.width - Inches(0.6), card_height)
        self._text(slide, box, code.splitlines(), "code", "text")
        if caption:
            self._source(slide, top + card_height + Inches(0.1), caption)

    def questions(self, title: str, questions: list[str], label: str = "") -> None:
        """Open questions for a 1:1 or a workshop, numbered in petrol."""
        slide, top, _ = self._content(title, label)
        for index, question in enumerate(questions):
            row_top = top + index * Inches(0.85)
            box = (self.x, row_top, Inches(0.8), Inches(0.6))
            self._text(slide, box, f"{index + 1:02d}", "kpi-number", "petrol")
            box = (self.x + Inches(1.0), row_top + Inches(0.12), Inches(10), Inches(0.7))
            self._text(slide, box, question, "body", "text")

    def closing(self, title: str, asks: list[str] | None = None, contact: str = "") -> None:
        """Closing on ink: the ask (owner and date) and the wordmark with contact."""
        slide = self._slide("ink")
        box = (self.x, Inches(1.6), Inches(10), Inches(1.4))
        self._text(slide, box, title, "divider-title", "white", anchor=MSO_ANCHOR.BOTTOM)
        if asks:
            box = (self.x, Inches(3.3), Inches(10), Inches(2.4))
            for paragraph in self._text(slide, box, asks, "body", "on-ink-muted").paragraphs:
                paragraph.space_after = Pt(8)
        self._wordmark(slide, self.bottom - Inches(0.6), "white", contact)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(path)
        return path

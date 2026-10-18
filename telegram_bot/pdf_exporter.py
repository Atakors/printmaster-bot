"""
PrintMaster A4 - PDF Exporter Engine
Generates print-ready vector PDF documents matching the desktop WPF application:
- Multi-page batch duplicator output
- Multi-page tiled poster output with glue guidelines and sheet numbering
"""

import io
import math
from typing import Optional
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, gray, white, red
from reportlab.lib.utils import ImageReader

from .models import PrintMasterState
from .layout_engine import calculate_duplicator_layout, calculate_poster_layout


def export_pdf(state: PrintMasterState) -> io.BytesIO:
    """Master entry point for PDF generation."""
    if state.mode == "poster":
        return export_poster_pdf(state)
    return export_duplicator_pdf(state)


def export_duplicator_pdf(state: PrintMasterState) -> io.BytesIO:
    """Exports multi-copy grid onto A4 pages with batch and cutting options."""
    mm_to_pt = 72.0 / 25.4
    page_w_pt = state.page_width_mm * mm_to_pt
    page_h_pt = state.page_height_mm * mm_to_pt

    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=(page_w_pt, page_h_pt))
    pdf.setTitle("PrintMaster A4 - Duplicator Output")

    # Load and prepare source image
    if state.image_path:
        pil_img = Image.open(state.image_path).convert("RGBA")
    else:
        # Fallback placeholder
        pil_img = Image.new("RGBA", (200, 200), (220, 230, 250, 255))

    layout = calculate_duplicator_layout(state)
    cols = layout["cols"]
    rows = layout["rows"]
    capacity_per_page = layout["capacity_per_page"]
    total_copies_to_print = layout["total_copies_to_print"]
    total_pages = layout["total_sheets"]

    render_w_mm = layout["render_w"]
    render_h_mm = layout["render_h"]
    should_rotate = layout["should_rotate"]

    start_x_mm = layout["start_x"]
    start_y_mm = layout["start_y"]
    gap_mm = layout["gap"]

    # Pre-rotate image if yield optimization decided to rotate
    if should_rotate:
        pil_img = pil_img.rotate(90, expand=True)

    img_reader = ImageReader(pil_img)

    w_pt = render_w_mm * mm_to_pt
    h_pt = render_h_mm * mm_to_pt
    gap_pt = gap_mm * mm_to_pt
    start_x_pt = start_x_mm * mm_to_pt
    start_y_pt = start_y_mm * mm_to_pt
    tick_pt = 3.5 * mm_to_pt

    border_color = {
        "black": HexColor("#000000"),
        "gray": HexColor("#6B7280"),
        "white": HexColor("#FFFFFF"),
        "red": HexColor("#DC2626"),
    }.get(state.border_color.lower(), HexColor("#000000"))
    border_pt = max(0.5, state.border_thickness_mm * mm_to_pt)

    copies_remaining = total_copies_to_print

    for page_idx in range(total_pages):
        copies_on_this_page = min(copies_remaining, capacity_per_page)
        drawn_on_page = 0

        for r in range(rows):
            for c in range(cols):
                if drawn_on_page >= copies_on_this_page:
                    break

                # Coordinates in top-down millimeter to bottom-up PDF point
                item_x_pt = start_x_pt + c * (w_pt + gap_pt)
                item_y_top_pt = start_y_pt + r * (h_pt + gap_pt)
                item_y_pt = page_h_pt - item_y_top_pt - h_pt

                # 1. Draw Image
                pdf.drawImage(
                    img_reader,
                    item_x_pt,
                    item_y_pt,
                    width=w_pt,
                    height=h_pt,
                    preserveAspectRatio=False,
                    mask="auto",
                )

                # 2. Image Border
                if state.show_border:
                    pdf.saveState()
                    pdf.setStrokeColor(border_color)
                    pdf.setLineWidth(border_pt)
                    pdf.rect(item_x_pt, item_y_pt, w_pt, h_pt, fill=0, stroke=1)
                    pdf.restoreState()

                # 3. Cut Marks
                if state.show_cut_marks:
                    pdf.saveState()
                    pdf.setStrokeColor(HexColor("#94A3B8"))
                    pdf.setLineWidth(0.5)

                    # Dashed boundary
                    pdf.setDash(2, 2)
                    pdf.rect(item_x_pt, item_y_pt, w_pt, h_pt, fill=0, stroke=1)

                    # Solid Corner Tick Marks
                    pdf.setDash([])
                    pdf.setStrokeColor(HexColor("#475569"))
                    pdf.setLineWidth(0.75)

                    # Top-Left corner
                    pdf.line(item_x_pt - tick_pt, item_y_pt + h_pt, item_x_pt, item_y_pt + h_pt)
                    pdf.line(item_x_pt, item_y_pt + h_pt, item_x_pt, item_y_pt + h_pt + tick_pt)

                    # Top-Right corner
                    pdf.line(item_x_pt + w_pt, item_y_pt + h_pt, item_x_pt + w_pt + tick_pt, item_y_pt + h_pt)
                    pdf.line(item_x_pt + w_pt, item_y_pt + h_pt, item_x_pt + w_pt, item_y_pt + h_pt + tick_pt)

                    # Bottom-Left corner
                    pdf.line(item_x_pt - tick_pt, item_y_pt, item_x_pt, item_y_pt)
                    pdf.line(item_x_pt, item_y_pt - tick_pt, item_x_pt, item_y_pt)

                    # Bottom-Right corner
                    pdf.line(item_x_pt + w_pt, item_y_pt, item_x_pt + w_pt + tick_pt, item_y_pt)
                    pdf.line(item_x_pt + w_pt, item_y_pt - tick_pt, item_x_pt + w_pt, item_y_pt)

                    pdf.restoreState()

                drawn_on_page += 1

            if drawn_on_page >= copies_on_this_page:
                break

        copies_remaining -= copies_on_this_page
        pdf.showPage()

    pdf.save()
    buf.seek(0)
    return buf


def export_poster_pdf(state: PrintMasterState) -> io.BytesIO:
    """Exports multi-sheet poster tiles with overlap and glue guidelines."""
    mm_to_pt = 72.0 / 25.4
    page_w_pt = state.page_width_mm * mm_to_pt
    page_h_pt = state.page_height_mm * mm_to_pt

    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=(page_w_pt, page_h_pt))
    pdf.setTitle("PrintMaster A4 - Poster Tiles Output")

    if state.image_path:
        src_img = Image.open(state.image_path).convert("RGBA")
    else:
        src_img = Image.new("RGBA", (1000, 1000), (240, 245, 255, 255))

    poster_info = calculate_poster_layout(state)
    cols = poster_info["cols"]
    rows = poster_info["rows"]
    overlap_mm = poster_info["overlap_mm"]
    overlap_pt = overlap_mm * mm_to_pt

    pixel_w, pixel_h = src_img.size
    seg_w_px = pixel_w // cols
    seg_h_px = pixel_h // rows

    overlap_px_x = int((overlap_mm / state.page_width_mm) * seg_w_px)
    overlap_px_y = int((overlap_mm / state.page_height_mm) * seg_h_px)

    margin_pt = state.margin_left_mm * mm_to_pt
    print_w_pt = page_w_pt - (2 * margin_pt)
    print_h_pt = page_h_pt - (2 * margin_pt)

    page_num = 1
    for r in range(rows):
        for c in range(cols):
            x_start = c * seg_w_px
            y_start = r * seg_h_px

            w_crop = min(pixel_w - x_start, seg_w_px + overlap_px_x) if c < cols - 1 else pixel_w - x_start
            h_crop = min(pixel_h - y_start, seg_h_px + overlap_px_y) if r < rows - 1 else pixel_h - y_start

            tile_crop = src_img.crop((x_start, y_start, x_start + w_crop, y_start + h_crop))
            tile_reader = ImageReader(tile_crop)

            # Draw Tile Image on A4 sheet
            pdf.drawImage(
                tile_reader,
                margin_pt,
                margin_pt,
                width=print_w_pt,
                height=print_h_pt,
                preserveAspectRatio=False,
                mask="auto",
            )

            # Draw Glue Guides & Sheet Index
            if state.poster_guides:
                pdf.saveState()
                pdf.setFont("Helvetica-Bold", 8)
                pdf.setStrokeColor(HexColor("#DC2626"))
                pdf.setFillColor(HexColor("#DC2626"))
                pdf.setLineWidth(0.75)
                pdf.setDash(4, 3)

                # Right overlap glue line
                if c < cols - 1 and overlap_mm > 0:
                    line_x = margin_pt + print_w_pt - overlap_pt
                    pdf.line(line_x, margin_pt, line_x, margin_pt + print_h_pt)
                    pdf.drawString(line_x + 4, margin_pt + print_h_pt - 24, f" Glue Sheet #{page_num + 1} Here")

                # Bottom overlap glue line
                if r < rows - 1 and overlap_mm > 0:
                    line_y = margin_pt + overlap_pt
                    pdf.line(margin_pt, line_y, margin_pt + print_w_pt, line_y)
                    pdf.drawString(margin_pt + 15, line_y + 4, f" Glue Row #{r + 2} Here")

                # Sheet Label at bottom
                pdf.setFont("Helvetica", 9)
                pdf.setFillColor(HexColor("#475569"))
                pdf.drawString(
                    margin_pt,
                    max(8, margin_pt / 2.0),
                    f"Poster Sheet #{page_num} of {cols * rows}  (Row {r + 1}/{rows}, Column {c + 1}/{cols})",
                )
                pdf.restoreState()

            page_num += 1
            pdf.showPage()

    pdf.save()
    buf.seek(0)
    return buf

"""
PrintMaster A4 - Pillow Canvas Renderer
Generates live visual previews for Telegram chat and 300 DPI high-resolution print exports.
"""

import io
import math
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from pathlib import Path
from .models import PrintMasterState
from .layout_engine import calculate_duplicator_layout, calculate_poster_layout

BUNDLED_FONTS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

# Color palette matching desktop app
COLOR_PAPER_BG = (255, 255, 255)
COLOR_CANVAS_BG = (15, 23, 42)          # Modern dark slate background
COLOR_MARGIN_GUIDE = (59, 130, 246, 160) # Translucent blue
COLOR_GRID_LINE = (226, 232, 240)        # Soft gray dashed
COLOR_CUT_MARK = (100, 116, 139)         # Slate gray
COLOR_BADGE_BG = (37, 99, 235)           # Royal blue
COLOR_POSTER_LINE = (239, 68, 68)        # Crimson red
COLOR_TEXT_WHITE = (255, 255, 255)


def get_default_font(size: int = 14) -> ImageFont.ImageFont:
    """Safely retrieves a TrueType font across Windows, Linux, and Docker."""
    bundled = BUNDLED_FONTS_DIR / "tahoma.ttf"
    if bundled.exists():
        try:
            return ImageFont.truetype(str(bundled), size)
        except Exception:
            pass

    for name in ["arial.ttf", "segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue

    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def get_border_rgba(color_name: str) -> Tuple[int, int, int, int]:
    colors = {
        "black": (0, 0, 0, 255),
        "gray": (128, 128, 128, 255),
        "white": (255, 255, 255, 255),
        "red": (220, 38, 38, 255),
    }
    return colors.get(color_name.lower(), (0, 0, 0, 255))


def render_preview_image(state: PrintMasterState) -> io.BytesIO:
    """
    Renders an eye-catching, realistic A4 preview mockup for Telegram chat.
    Includes drop-shadow paper border, printable margin guide, duplicated grid / poster overview,
    cut tick marks, and layout info header/footer.
    """
    # Preview DPI: ~100 DPI for fast generation and crisp display on mobile screens
    preview_dpi = 96.0
    mm_to_px = preview_dpi / 25.4

    page_w_px = int(round(state.page_width_mm * mm_to_px))
    page_h_px = int(round(state.page_height_mm * mm_to_px))

    # Canvas padding for shadow and frame
    pad_x = 40
    pad_y = 50
    header_h = 44

    total_w = page_w_px + (pad_x * 2)
    total_h = page_h_px + (pad_y * 2) + header_h

    # Create master canvas with modern dark background
    canvas = Image.new("RGBA", (total_w, total_h), COLOR_CANVAS_BG)
    draw_canvas = ImageDraw.Draw(canvas)

    # 1. Top Header Bar
    font_bold = get_default_font(16)
    font_small = get_default_font(12)

    orient_str = "Portrait" if state.is_portrait else "Landscape"
    mode_str = "DUPLICATOR GRID" if state.mode == "duplicator" else "POSTER TILING"

    draw_canvas.text(
        (pad_x, 15),
        f"PrintMaster A4 • {mode_str} [{orient_str}]",
        fill=(248, 250, 252),
        font=font_bold,
    )

    # 2. Paper Drop Shadow & A4 Sheet
    paper_x0 = pad_x
    paper_y0 = pad_y + header_h
    paper_x1 = paper_x0 + page_w_px
    paper_y1 = paper_y0 + page_h_px

    # Create subtle shadow
    shadow_img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_offset = 8
    shadow_draw.rounded_rectangle(
        [paper_x0 + 2, paper_y0 + shadow_offset, paper_x1 + 6, paper_y1 + shadow_offset],
        radius=6,
        fill=(0, 0, 0, 110),
    )
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(10))
    canvas = Image.alpha_composite(canvas, shadow_img)
    draw_canvas = ImageDraw.Draw(canvas)

    # Create Paper Surface
    paper = Image.new("RGBA", (page_w_px, page_h_px), (255, 255, 255, 255))
    draw_paper = ImageDraw.Draw(paper)

    # 3. Printable Margin Guide
    if state.show_margin_guide:
        margin_x0 = int(round(state.margin_left_mm * mm_to_px))
        margin_y0 = int(round(state.margin_top_mm * mm_to_px))
        margin_x1 = int(round((state.page_width_mm - state.margin_right_mm) * mm_to_px))
        margin_y1 = int(round((state.page_height_mm - state.margin_bottom_mm) * mm_to_px))

        # Dotted margin line
        _draw_dashed_rect(
            draw_paper,
            margin_x0,
            margin_y0,
            margin_x1,
            margin_y1,
            COLOR_MARGIN_GUIDE,
            dash_len=4,
            gap_len=4,
            width=1,
        )

    # Load source image if available
    src_img = None
    if state.image_path:
        try:
            src_img = Image.open(state.image_path).convert("RGBA")
        except Exception:
            src_img = None

    if src_img is None:
        # Placeholder image
        src_img = _create_placeholder_image(120, 120)

    # 4. Mode-specific rendering
    if state.mode == "duplicator":
        _render_duplicator_preview(paper, draw_paper, state, src_img, mm_to_px)
    else:
        _render_poster_preview(paper, draw_paper, state, src_img, mm_to_px)

    # Paste paper onto canvas
    canvas.paste(paper, (paper_x0, paper_y0), paper)

    # 5. Bottom Info Summary
    draw_canvas = ImageDraw.Draw(canvas)
    if state.mode == "duplicator":
        layout = calculate_duplicator_layout(state)
        summary_text = (
            f"📄 {layout['drawn_per_page']} / sheet ({layout['cols']}×{layout['rows']} grid) "
            f"• Size: {state.image_width_mm/10:.1f}×{state.image_height_mm/10:.1f} cm • Gap: {state.gap_mm:.1f} mm"
        )
    else:
        poster_info = calculate_poster_layout(state)
        summary_text = (
            f"🧩 {poster_info['total_sheets']} A4 Sheets ({poster_info['cols']} across × {poster_info['rows']} down) "
            f"• Approx: {poster_info['total_w_cm']:.1f} × {poster_info['total_h_cm']:.1f} cm"
        )

    draw_canvas.text((pad_x, total_h - 32), summary_text, fill=(148, 163, 184), font=font_small)

    # Save to output buffer
    buf = io.BytesIO()
    canvas.convert("RGB").save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf


def _render_duplicator_preview(
    paper: Image.Image,
    draw: ImageDraw.ImageDraw,
    state: PrintMasterState,
    src_img: Image.Image,
    mm_to_px: float,
):
    layout = calculate_duplicator_layout(state)
    positions = layout["positions"]

    if not positions:
        return

    # Draw separator grid lines
    cols = layout["cols"]
    rows = layout["rows"]
    gap_px = layout["gap"] * mm_to_px
    start_x_px = layout["start_x"] * mm_to_px
    start_y_px = layout["start_y"] * mm_to_px
    block_w_px = layout["total_block_w"] * mm_to_px
    block_h_px = layout["total_block_h"] * mm_to_px
    img_w_px = layout["render_w"] * mm_to_px
    img_h_px = layout["render_h"] * mm_to_px

    for c in range(1, cols):
        lx = int(round(start_x_px + c * (img_w_px + gap_px) - (gap_px / 2.0)))
        _draw_dashed_line(draw, lx, int(start_y_px), lx, int(start_y_px + block_h_px), (226, 232, 240, 255), 3, 3)

    for r in range(1, rows):
        ly = int(round(start_y_px + r * (img_h_px + gap_px) - (gap_px / 2.0)))
        _draw_dashed_line(draw, int(start_x_px), ly, int(start_x_px + block_w_px), ly, (226, 232, 240, 255), 3, 3)

    # Prepare scaled source image
    first_w_px = int(round(positions[0][2] * mm_to_px))
    first_h_px = int(round(positions[0][3] * mm_to_px))
    first_rotated = positions[0][4]

    placed_img = src_img
    if first_rotated:
        placed_img = placed_img.rotate(90, expand=True)

    placed_img = placed_img.resize((max(1, first_w_px), max(1, first_h_px)), Image.Resampling.LANCZOS)

    border_rgba = get_border_rgba(state.border_color)
    border_px = max(1, int(round(state.border_thickness_mm * mm_to_px)))
    tick_len = int(round(3.5 * mm_to_px))

    for idx, (x_mm, y_mm, w_mm, h_mm, rot) in enumerate(positions):
        x = int(round(x_mm * mm_to_px))
        y = int(round(y_mm * mm_to_px))
        w = int(round(w_mm * mm_to_px))
        h = int(round(h_mm * mm_to_px))

        # Paste image
        paper.paste(placed_img, (x, y), placed_img if placed_img.mode == "RGBA" else None)

        # Image Border
        if state.show_border:
            draw.rectangle([x, y, x + w - 1, y + h - 1], outline=border_rgba, width=border_px)

        # Cut marks
        if state.show_cut_marks:
            _draw_dashed_rect(draw, x, y, x + w, y + h, (203, 213, 225, 255), dash_len=2, gap_len=2, width=1)
            # Corner ticks
            draw.line([(x - tick_len, y), (x, y)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x, y - tick_len), (x, y)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x + w, y), (x + w + tick_len, y)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x + w, y - tick_len), (x + w, y)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x - tick_len, y + h), (x, y + h)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x, y + h), (x, y + h + tick_len)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x + w, y + h), (x + w + tick_len, y + h)], fill=COLOR_CUT_MARK, width=1)
            draw.line([(x + w, y + h), (x + w + tick_len, y + h)], fill=COLOR_CUT_MARK, width=1)

    # Highlight / Dimension Badge on Top-Left Image
    if positions:
        first_x = int(round(positions[0][0] * mm_to_px))
        first_y = int(round(positions[0][1] * mm_to_px))
        badge_font = get_default_font(10)
        badge_text = f"{state.image_width_mm/10:.1f} cm"
        draw.rounded_rectangle(
            [first_x + (first_w_px // 2) - 22, max(2, first_y - 18), first_x + (first_w_px // 2) + 22, first_y - 2],
            radius=3,
            fill=COLOR_BADGE_BG,
        )
        draw.text((first_x + (first_w_px // 2) - 18, max(4, first_y - 16)), badge_text, fill=COLOR_TEXT_WHITE, font=badge_font)


def _render_poster_preview(
    paper: Image.Image,
    draw: ImageDraw.ImageDraw,
    state: PrintMasterState,
    src_img: Image.Image,
    mm_to_px: float,
):
    """Renders the overview of how the poster is mapped and split across A4 sheets."""
    poster_info = calculate_poster_layout(state)
    cols = poster_info["cols"]
    rows = poster_info["rows"]

    page_w_px = paper.width
    page_h_px = paper.height

    # Scale poster to fill page overview
    scaled_poster = src_img.resize((page_w_px, page_h_px), Image.Resampling.LANCZOS)
    paper.paste(scaled_poster, (0, 0), scaled_poster if scaled_poster.mode == "RGBA" else None)

    # Draw grid divider lines in crimson with dash
    col_step = page_w_px / cols
    row_step = page_h_px / rows

    for c in range(1, cols):
        x = int(round(c * col_step))
        _draw_dashed_line(draw, x, 0, x, page_h_px, COLOR_POSTER_LINE, dash_len=6, gap_len=4, width=2)

    for r in range(1, rows):
        y = int(round(r * row_step))
        _draw_dashed_line(draw, 0, y, page_w_px, y, COLOR_POSTER_LINE, dash_len=6, gap_len=4, width=2)

    # Draw sheet index labels on each cell
    font_sheet = get_default_font(12)
    tile_idx = 1
    for r in range(rows):
        for c in range(cols):
            cx = int(round(c * col_step + col_step / 2.0))
            cy = int(round(r * row_step + row_step / 2.0))
            tag = f"Sheet #{tile_idx}\n({r+1}/{rows}, {c+1}/{cols})"
            
            # Badge background
            draw.rounded_rectangle([cx - 40, cy - 16, cx + 40, cy + 16], radius=4, fill=(15, 23, 42, 210))
            draw.text((cx - 34, cy - 12), tag, fill=COLOR_TEXT_WHITE, font=font_sheet)
            tile_idx += 1


def render_300dpi_image(state: PrintMasterState) -> io.BytesIO:
    """
    Renders an exact, ultra-crisp 300 DPI A4 image (2480 x 3508 pixels).
    Ready for standard photo printing or uncompressed raster export.
    """
    dpi = 300.0
    mm_to_px = dpi / 25.4

    page_w_px = int(round(state.page_width_mm * mm_to_px))
    page_h_px = int(round(state.page_height_mm * mm_to_px))

    image = Image.new("RGB", (page_w_px, page_h_px), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    src_img = None
    if state.image_path:
        try:
            src_img = Image.open(state.image_path).convert("RGBA")
        except Exception:
            src_img = None

    if src_img is None:
        src_img = _create_placeholder_image(600, 600)

    if state.mode == "duplicator":
        layout = calculate_duplicator_layout(state)
        positions = layout["positions"]

        border_rgba = get_border_rgba(state.border_color)
        border_px = max(1, int(round(state.border_thickness_mm * mm_to_px)))
        tick_len = int(round(3.5 * mm_to_px))

        for x_mm, y_mm, w_mm, h_mm, rot in positions:
            w_px = max(1, int(round(w_mm * mm_to_px)))
            h_px = max(1, int(round(h_mm * mm_to_px)))
            x_px = int(round(x_mm * mm_to_px))
            y_px = int(round(y_mm * mm_to_px))

            placed = src_img
            if rot:
                placed = placed.rotate(90, expand=True)
            placed = placed.resize((w_px, h_px), Image.Resampling.LANCZOS)

            image.paste(placed, (x_px, y_px), placed if placed.mode == "RGBA" else None)

            if state.show_border:
                draw.rectangle([x_px, y_px, x_px + w_px - 1, y_px + h_px - 1], outline=border_rgba[:3], width=border_px)

            if state.show_cut_marks:
                _draw_dashed_rect(draw, x_px, y_px, x_px + w_px, y_px + h_px, (200, 200, 200), 6, 6, width=2)
                draw.line([(x_px - tick_len, y_px), (x_px, y_px)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px, y_px - tick_len), (x_px, y_px)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px + w_px, y_px), (x_px + w_px + tick_len, y_px)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px + w_px, y_px - tick_len), (x_px + w_px, y_px)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px - tick_len, y_px + h_px), (x_px, y_px + h_px)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px, y_px + h_px), (x_px, y_px + h_px + tick_len)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px + w_px, y_px + h_px), (x_px + w_px + tick_len, y_px + h_px)], fill=COLOR_CUT_MARK, width=2)
                draw.line([(x_px + w_px, y_px + h_px), (x_px + w_px, y_px + h_px + tick_len)], fill=COLOR_CUT_MARK, width=2)

    else:
        # Poster high-res sheet overview
        scaled_poster = src_img.resize((page_w_px, page_h_px), Image.Resampling.LANCZOS)
        image.paste(scaled_poster, (0, 0), scaled_poster if scaled_poster.mode == "RGBA" else None)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _draw_dashed_line(draw: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int, color, dash_len=4, gap_len=4, width=1):
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    d_x = (x1 - x0) / dist
    d_y = (y1 - y0) / dist
    curr = 0.0
    while curr < dist:
        seg_end = min(dist, curr + dash_len)
        sx0 = int(round(x0 + d_x * curr))
        sy0 = int(round(y0 + d_y * curr))
        sx1 = int(round(x0 + d_x * seg_end))
        sy1 = int(round(y0 + d_y * seg_end))
        draw.line([(sx0, sy0), (sx1, sy1)], fill=color, width=width)
        curr += dash_len + gap_len


def _draw_dashed_rect(draw: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int, color, dash_len=4, gap_len=4, width=1):
    _draw_dashed_line(draw, x0, y0, x1, y0, color, dash_len, gap_len, width)
    _draw_dashed_line(draw, x1, y0, x1, y1, color, dash_len, gap_len, width)
    _draw_dashed_line(draw, x1, y1, x0, y1, color, dash_len, gap_len, width)
    _draw_dashed_line(draw, x0, y1, x0, y0, color, dash_len, gap_len, width)


def _create_placeholder_image(w: int, h: int) -> Image.Image:
    """Cute sample sticker graphic matching the WPF app's default sticker."""
    img = Image.new("RGBA", (w, h), (240, 247, 255, 255))
    draw = ImageDraw.Draw(img)
    # Circle body
    pad = int(w * 0.08)
    draw.ellipse([pad, pad, w - pad, h - pad], fill=(254, 240, 138), outline=(234, 179, 8), width=3)
    # Happy eyes
    eye_y = int(h * 0.42)
    eye_r = max(2, int(w * 0.04))
    draw.ellipse([int(w * 0.35) - eye_r, eye_y - eye_r, int(w * 0.35) + eye_r, eye_y + eye_r], fill=(15, 23, 42))
    draw.ellipse([int(w * 0.65) - eye_r, eye_y - eye_r, int(w * 0.65) + eye_r, eye_y + eye_r], fill=(15, 23, 42))
    # Smile
    mouth_box = [int(w * 0.38), int(h * 0.48), int(w * 0.62), int(h * 0.68)]
    draw.arc(mouth_box, start=0, end=180, fill=(15, 23, 42), width=3)
    return img

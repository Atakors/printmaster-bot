"""
PrintMaster A4 - School Notebook Label Generator Engine
Generates professional, beautiful printable sheets of adhesive student notebook labels.
Supports 5 visual themes, auto-subject lists, custom student photo avatars, and tri-lingual text.
"""

import io
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageOps

from .models import PrintMasterState
from .i18n import t

# Theme Color Schemes & Accents
THEME_CONFIGS = {
    "classic": {
        "primary": (30, 58, 138),      # Deep Navy
        "secondary": (239, 246, 255),  # Soft Blue Tint
        "border": (59, 130, 246),      # Royal Blue
        "text_dark": (15, 23, 42),
        "text_muted": (100, 116, 139),
        "accent": (245, 158, 11),      # Gold
        "icon": "🎓",
    },
    "football": {
        "primary": (4, 120, 87),       # Champion Emerald Green
        "secondary": (236, 253, 245),  # Mint Soft
        "border": (16, 185, 129),
        "text_dark": (6, 78, 59),
        "text_muted": (75, 85, 99),
        "accent": (234, 88, 12),       # Bright Orange
        "icon": "⚽",
    },
    "space": {
        "primary": (76, 29, 149),      # Cosmic Purple
        "secondary": (245, 243, 255),  # Lavender Tint
        "border": (139, 92, 246),
        "text_dark": (46, 16, 101),
        "text_muted": (107, 114, 128),
        "accent": (250, 204, 21),      # Starlight Yellow
        "icon": "🚀",
    },
    "cute": {
        "primary": (225, 29, 72),      # Rose Pink
        "secondary": (255, 241, 242),  # Pastel Rose
        "border": (251, 113, 133),
        "text_dark": (136, 19, 55),
        "text_muted": (156, 163, 175),
        "accent": (245, 158, 11),      # Honey Yellow
        "icon": "🐻",
    },
    "science": {
        "primary": (13, 148, 136),     # Science Teal
        "secondary": (240, 253, 250),  # Mint/Cyan tint
        "border": (20, 184, 166),
        "text_dark": (19, 78, 74),
        "text_muted": (100, 116, 139),
        "accent": (249, 115, 22),      # Amber flame
        "icon": "🔬",
    },
}

# 10 Standard School Subjects per Language
CORE_SUBJECTS = {
    "en": [
        "Mathematics", "English", "Science", "History",
        "Geography", "Art & Music", "Computer Sci.", "Physical Ed.",
        "Literature", "Homework Book",
    ],
    "ar": [
        "الرياضيات", "اللغة العربية", "التربية الإسلامية", "العلوم الطبيعية",
        "التاريخ والجغرافيا", "اللغة الفرنسية", "اللغة الإنجليزية", "التربية المدنية",
        "الفيزياء والتكنولوجيا", "دفتر الملاحظات",
    ],
    "fr": [
        "Mathématiques", "Français", "Sciences (SVT)", "Histoire - Géo",
        "Anglais", "Physique - Chimie", "Arabe", "Arts Plastiques",
        "Éducation Civique", "Cahier de Texte",
    ],
}


def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Safely retrieves TrueType font supporting Latin and Arabic characters."""
    font_names = ["segoeui.ttf", "tahoma.ttf", "arial.ttf"]
    if bold:
        font_names = ["segoeuib.ttf", "tahomabd.ttf", "arialbd.ttf"] + font_names
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_single_label(
    state: PrintMasterState,
    subject: Optional[str] = None,
    width_px: int = 760,
    height_px: int = 440,
) -> Image.Image:
    """
    Renders an individual high-resolution school sticker label.
    """
    theme_key = state.school_theme if state.school_theme in THEME_CONFIGS else "classic"
    theme = THEME_CONFIGS[theme_key]
    lang = state.language

    label = Image.new("RGBA", (width_px, height_px), (255, 255, 255, 255))
    draw = ImageDraw.Draw(label)

    # 1. Outer rounded card with subtle fill and decorative border
    corner_r = 16
    draw.rounded_rectangle(
        [2, 2, width_px - 3, height_px - 3],
        radius=corner_r,
        fill=(255, 255, 255, 255),
        outline=theme["border"],
        width=4,
    )

    # 2. Header Decorative Banner
    header_h = 58
    draw.rounded_rectangle(
        [4, 4, width_px - 5, header_h],
        radius=corner_r,
        fill=theme["primary"],
    )
    # Patch lower corners of banner to make them square against the body
    draw.rectangle([4, header_h - 14, width_px - 5, header_h], fill=theme["primary"])

    font_header = _get_font(22, bold=True)
    header_title = t("school_label_header", lang)
    draw.text((24, 16), header_title, fill=(255, 255, 255, 255), font=font_header)

    # School Year on top right
    font_year = _get_font(16)
    year_text = state.school_year or "2026/2027"
    draw.text((width_px - 140, 19), year_text, fill=(220, 235, 255, 255), font=font_year)

    # 3. Avatar / Badge Area (Left side)
    avatar_size = 110
    avatar_x = 24
    avatar_y = header_h + 30

    # Check if user wants student photo on the label
    placed_photo = False
    if state.school_custom_avatar and state.image_path and Path(state.image_path).exists():
        try:
            with Image.open(state.image_path).convert("RGBA") as user_img:
                user_img = ImageOps.fit(user_img, (avatar_size, avatar_size), Image.Resampling.LANCZOS)
                # Create circular mask
                mask = Image.new("L", (avatar_size, avatar_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, avatar_size, avatar_size], fill=255)
                
                label.paste(user_img, (avatar_x, avatar_y), mask)
                # Border circle around photo
                draw.ellipse(
                    [avatar_x - 2, avatar_y - 2, avatar_x + avatar_size + 2, avatar_y + avatar_size + 2],
                    outline=theme["accent"],
                    width=3,
                )
                placed_photo = True
        except Exception:
            placed_photo = False

    if not placed_photo:
        # Theme icon badge background
        draw.rounded_rectangle(
            [avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size],
            radius=18,
            fill=theme["secondary"],
            outline=theme["border"],
            width=2,
        )
        # Big theme emoji / icon
        font_icon = _get_font(52)
        draw.text((avatar_x + 22, avatar_y + 16), theme["icon"], fill=theme["primary"], font=font_icon)

    # 4. Text Fields (Right of avatar)
    fields_x = avatar_x + avatar_size + 24
    fields_w = width_px - fields_x - 24

    font_field_label = _get_font(18, bold=True)
    font_field_val = _get_font(20, bold=True)
    font_dots = _get_font(18)

    # Field 1: Student Name
    y_pos = header_h + 24
    lbl_name = t("school_field_name", lang)
    student_name = state.school_student_name.strip() or t("school_sample_student", lang)
    draw.text((fields_x, y_pos), f"{lbl_name}:", fill=theme["text_muted"], font=font_field_label)
    draw.text((fields_x + 130, y_pos - 2), student_name, fill=theme["text_dark"], font=font_field_val)
    draw.line([(fields_x, y_pos + 30), (fields_x + fields_w, y_pos + 30)], fill=(226, 232, 240), width=1)

    # Field 2: Class / Grade
    y_pos += 48
    lbl_class = t("school_field_class", lang)
    grade_val = state.school_grade.strip() or t("school_sample_grade", lang)
    draw.text((fields_x, y_pos), f"{lbl_class}:", fill=theme["text_muted"], font=font_field_label)
    draw.text((fields_x + 130, y_pos - 2), grade_val, fill=theme["text_dark"], font=font_field_val)
    draw.line([(fields_x, y_pos + 30), (fields_x + fields_w, y_pos + 30)], fill=(226, 232, 240), width=1)

    # Field 3: Subject (Pre-filled or dotted line for pen)
    y_pos += 48
    lbl_subject = t("school_field_subject", lang)
    draw.text((fields_x, y_pos), f"{lbl_subject}:", fill=theme["text_muted"], font=font_field_label)

    if subject:
        # Pre-filled subject
        draw.text((fields_x + 130, y_pos - 2), subject, fill=theme["primary"], font=font_field_val)
    else:
        # Dotted line to write with pen
        draw.text((fields_x + 130, y_pos), ". . . . . . . . . . . . . . . . . . . . . . . .", fill=(148, 163, 184), font=font_dots)
    draw.line([(fields_x, y_pos + 30), (fields_x + fields_w, y_pos + 30)], fill=(226, 232, 240), width=1)

    # Bottom decorative accent bar
    draw.rectangle([4, height_px - 8, width_px - 4, height_px - 4], fill=theme["accent"])

    return label


def render_school_labels_sheet(state: PrintMasterState, preview: bool = False) -> io.BytesIO:
    """
    Renders the complete A4 printable sheet containing 10 school stickers (2 cols × 5 rows).
    Preview mode generates 96 DPI for fast chat display, while full mode renders at 300 DPI for printing.
    """
    dpi = 96.0 if preview else 300.0
    mm_to_px = dpi / 25.4

    page_w_px = int(round(210.0 * mm_to_px))
    page_h_px = int(round(297.0 * mm_to_px))

    # A4 White Canvas
    sheet = Image.new("RGB", (page_w_px, page_h_px), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    # Sheet layout: 2 columns × 5 rows = 10 labels
    cols = 2
    rows = 5
    label_w_mm = 88.0
    label_h_mm = 50.0
    gap_x_mm = 8.0
    gap_y_mm = 5.0

    total_w_mm = cols * label_w_mm + (cols - 1) * gap_x_mm
    total_h_mm = rows * label_h_mm + (rows - 1) * gap_y_mm

    margin_x_mm = (210.0 - total_w_mm) / 2.0
    margin_y_mm = (297.0 - total_h_mm) / 2.0

    label_w_px = int(round(label_w_mm * mm_to_px))
    label_h_px = int(round(label_h_mm * mm_to_px))

    # Prepare list of subjects
    lang = state.language
    subjects_list = CORE_SUBJECTS.get(lang, CORE_SUBJECTS["en"])
    use_auto_subjects = (state.school_subject_mode == "auto")

    # Render each of the 10 labels
    idx = 0
    tick_len = int(round(3.0 * mm_to_px))

    for r in range(rows):
        for c in range(cols):
            x_mm = margin_x_mm + c * (label_w_mm + gap_x_mm)
            y_mm = margin_y_mm + r * (label_h_mm + gap_y_mm)

            x = int(round(x_mm * mm_to_px))
            y = int(round(y_mm * mm_to_px))

            subject_text = subjects_list[idx % len(subjects_list)] if use_auto_subjects else None
            single_img = render_single_label(state, subject=subject_text, width_px=label_w_px, height_px=label_h_px)

            sheet.paste(single_img, (x, y))

            # Cut marks around each label
            # Corner cut ticks
            draw.line([(x - tick_len, y), (x, y)], fill=(156, 163, 175), width=1)
            draw.line([(x, y - tick_len), (x, y)], fill=(156, 163, 175), width=1)
            draw.line([(x + label_w_px, y), (x + label_w_px + tick_len, y)], fill=(156, 163, 175), width=1)
            draw.line([(x + label_w_px, y - tick_len), (x + label_w_px, y)], fill=(156, 163, 175), width=1)
            draw.line([(x - tick_len, y + label_h_px), (x, y + label_h_px)], fill=(156, 163, 175), width=1)
            draw.line([(x, y + label_h_px), (x, y + label_h_px + tick_len)], fill=(156, 163, 175), width=1)
            draw.line([(x + label_w_px, y + label_h_px), (x + label_w_px + tick_len, y + label_h_px)], fill=(156, 163, 175), width=1)
            draw.line([(x + label_w_px, y + label_h_px), (x + label_w_px, y + label_h_px + tick_len)], fill=(156, 163, 175), width=1)

            idx += 1

    # Bottom Sheet Footer Note
    font_footer = _get_font(int(round(9.0 * (dpi / 72.0))))
    footer_text = f"PrintMaster A4 • School Notebook Labels • 10 Stickers (88×50 mm) • Print at 100% Scale / Actual Size"
    draw.text((int(round(margin_x_mm * mm_to_px)), page_h_px - int(round(12.0 * mm_to_px))), footer_text, fill=(156, 163, 175), font=font_footer)

    buf = io.BytesIO()
    if preview:
        # Wrap preview on a dark background mockup with shadow
        pad = 40
        canvas = Image.new("RGB", (page_w_px + pad * 2, page_h_px + pad * 2), (15, 23, 42))
        canvas.paste(sheet, (pad, pad))
        canvas.save(buf, format="JPEG", quality=90)
    else:
        sheet.save(buf, format="PNG", dpi=(300, 300))

    buf.seek(0)
    return buf

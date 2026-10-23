"""
PrintMaster A4 - School Notebook Label Generator Engine
Generates professional, beautiful printable sheets of adhesive student notebook labels.
Supports 5 visual themes, auto-subject lists, custom student photo avatars, and tri-lingual text.
Proportionally engineered at 300 DPI (88 × 50 mm = 1039 × 590 px per label) with zero wasted space.
"""

import io
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageOps

from .models import PrintMasterState
from .i18n import t

# Canonical dimensions for 88 × 50 mm at 300 DPI
CANONICAL_W = 1039
CANONICAL_H = 590

# Theme Color Schemes & Accents
THEME_CONFIGS = {
    "classic": {
        "primary": (30, 58, 138),      # Deep Navy
        "secondary": (239, 246, 255),  # Soft Blue Tint
        "border": (59, 130, 246),      # Royal Blue
        "text_dark": (15, 23, 42),
        "text_muted": (71, 85, 105),
        "accent": (245, 158, 11),      # Gold
    },
    "football": {
        "primary": (4, 120, 87),       # Champion Emerald Green
        "secondary": (236, 253, 245),  # Mint Soft
        "border": (16, 185, 129),
        "text_dark": (6, 78, 59),
        "text_muted": (55, 65, 81),
        "accent": (234, 88, 12),       # Bright Orange
    },
    "space": {
        "primary": (76, 29, 149),      # Cosmic Purple
        "secondary": (245, 243, 255),  # Lavender Tint
        "border": (139, 92, 246),
        "text_dark": (46, 16, 101),
        "text_muted": (75, 85, 99),
        "accent": (250, 204, 21),      # Starlight Yellow
    },
    "cute": {
        "primary": (225, 29, 72),      # Rose Berry
        "secondary": (255, 241, 242),  # Pastel Rose
        "border": (251, 113, 133),
        "text_dark": (136, 19, 55),
        "text_muted": (107, 114, 128),
        "accent": (245, 158, 11),      # Honey Yellow
    },
    "science": {
        "primary": (13, 148, 136),     # Science Teal
        "secondary": (240, 253, 250),  # Mint/Cyan tint
        "border": (20, 184, 166),
        "text_dark": (19, 78, 74),
        "text_muted": (71, 85, 105),
        "accent": (249, 115, 22),      # Amber flame
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

# Inspiring Mottoes per Language
MOTTOES = {
    "ar": "⭐ طريقي نحو النجاح والتفوق المدرسي ⭐",
    "fr": "⭐ Année Scolaire de Réussite & d'Excellence ⭐",
    "en": "⭐ Knowledge is Power • Strive for Excellence ⭐",
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


def _draw_theme_emblem(draw: ImageDraw.Draw, theme_key: str, cx: int, cy: int, r: int, theme: Dict[str, Any]):
    """Draws a colorful, vector-styled decorative emblem badge for the selected theme."""
    if theme_key == "football":
        # Green grass circular background
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["secondary"], outline=theme["primary"], width=6)
        # Soccer ball
        br = int(r * 0.72)
        draw.ellipse([cx - br, cy - br, cx + br, cy + br], fill=(255, 255, 255), outline=(15, 23, 42), width=5)
        # Center black pentagon
        pent = []
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            pent.append((cx + int(br * 0.38 * math.cos(angle)), cy + int(br * 0.38 * math.sin(angle))))
        draw.polygon(pent, fill=(15, 23, 42))
        # Edge lines to perimeter
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            p1 = (cx + int(br * 0.38 * math.cos(angle)), cy + int(br * 0.38 * math.sin(angle)))
            p_out = (cx + int(br * math.cos(angle)), cy + int(br * math.sin(angle)))
            draw.line([p1, p_out], fill=(15, 23, 42), width=4)

    elif theme_key == "space":
        # Cosmic night circular badge
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["primary"], outline=theme["accent"], width=6)
        # Saturn planet
        pr = int(r * 0.44)
        draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=theme["border"], outline=(255, 255, 255), width=3)
        # Saturn glowing ring
        draw.arc([cx - int(r * 0.8), cy - int(r * 0.28), cx + int(r * 0.8), cy + int(r * 0.28)], start=0, end=360, fill=theme["accent"], width=8)
        # Little stars
        f_star = _get_font(24)
        for sx, sy in [(cx - int(r * 0.5), cy - int(r * 0.5)), (cx + int(r * 0.5), cy - int(r * 0.4)), (cx - int(r * 0.4), cy + int(r * 0.5))]:
            draw.text((sx, sy), "✦", fill=theme["accent"], font=f_star)

    elif theme_key == "cute":
        # Soft pink badge
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["secondary"], outline=theme["primary"], width=6)
        # Teddy Bear Ears
        draw.ellipse([cx - int(r * 0.65), cy - int(r * 0.72), cx - int(r * 0.25), cy - int(r * 0.32)], fill=(244, 114, 182), outline=(190, 24, 93), width=4)
        draw.ellipse([cx + int(r * 0.25), cy - int(r * 0.72), cx + int(r * 0.65), cy - int(r * 0.32)], fill=(244, 114, 182), outline=(190, 24, 93), width=4)
        # Bear Head
        draw.ellipse([cx - int(r * 0.55), cy - int(r * 0.45), cx + int(r * 0.55), cy + int(r * 0.55)], fill=(251, 207, 232), outline=(190, 24, 93), width=5)
        # Rosy Cheeks
        draw.ellipse([cx - int(r * 0.45), cy + int(r * 0.1), cx - int(r * 0.25), cy + int(r * 0.28)], fill=(244, 63, 94))
        draw.ellipse([cx + int(r * 0.25), cy + int(r * 0.1), cx + int(r * 0.45), cy + int(r * 0.28)], fill=(244, 63, 94))
        # Eyes
        draw.ellipse([cx - int(r * 0.25), cy - int(r * 0.1), cx - int(r * 0.15), cy + int(r * 0.02)], fill=(15, 23, 42))
        draw.ellipse([cx + int(r * 0.15), cy - int(r * 0.1), cx + int(r * 0.25), cy + int(r * 0.02)], fill=(15, 23, 42))
        # Snout & Nose
        draw.ellipse([cx - int(r * 0.2), cy + int(r * 0.08), cx + int(r * 0.2), cy + int(r * 0.36)], fill=(255, 255, 255))
        draw.ellipse([cx - int(r * 0.08), cy + int(r * 0.12), cx + int(r * 0.08), cy + int(r * 0.24)], fill=(15, 23, 42))

    elif theme_key == "science":
        # Mint circle
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["secondary"], outline=theme["primary"], width=6)
        # Erlenmeyer Flask
        neck = [
            (cx - 15, cy - int(r * 0.55)), (cx + 15, cy - int(r * 0.55)),
            (cx + 15, cy - int(r * 0.18)), (cx + int(r * 0.55), cy + int(r * 0.48)),
            (cx - int(r * 0.55), cy + int(r * 0.48)), (cx - 15, cy - int(r * 0.18))
        ]
        draw.polygon(neck, fill=(255, 255, 255), outline=theme["primary"], width=5)
        # Liquid
        liquid = [
            (cx - int(r * 0.38), cy + int(r * 0.15)), (cx + int(r * 0.38), cy + int(r * 0.15)),
            (cx + int(r * 0.50), cy + int(r * 0.44)), (cx - int(r * 0.50), cy + int(r * 0.44))
        ]
        draw.polygon(liquid, fill=theme["border"])
        # Bubbles
        for bx, by, brad in [(cx - 12, cy + 28, 6), (cx + 16, cy + 34, 8), (cx, cy - 6, 7)]:
            draw.ellipse([bx - brad, by - brad, bx + brad, by + brad], fill=theme["accent"])

    else:
        # Classic Academic Cap & Laurels
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["primary"], outline=theme["accent"], width=6)
        # Graduation Cap Mortarboard
        cap_poly = [(cx, cy - int(r * 0.45)), (cx + int(r * 0.6), cy - int(r * 0.15)), (cx, cy + int(r * 0.12)), (cx - int(r * 0.6), cy - int(r * 0.15))]
        draw.polygon(cap_poly, fill=theme["accent"], outline=(255, 255, 255), width=3)
        # Skullcap
        draw.polygon([(cx - int(r * 0.32), cy - int(r * 0.1)), (cx + int(r * 0.32), cy - int(r * 0.1)), (cx + int(r * 0.26), cy + int(r * 0.28)), (cx - int(r * 0.26), cy + int(r * 0.28))], fill=(217, 119, 6))
        # Tassel
        draw.line([(cx, cy - int(r * 0.15)), (cx + int(r * 0.55), cy + int(r * 0.18)), (cx + int(r * 0.55), cy + int(r * 0.44))], fill=(255, 255, 255), width=4)
        draw.ellipse([cx + int(r * 0.50), cy + int(r * 0.40), cx + int(r * 0.60), cy + int(r * 0.52)], fill=theme["accent"])


def render_single_label(
    state: PrintMasterState,
    subject: Optional[str] = None,
    width_px: int = CANONICAL_W,
    height_px: int = CANONICAL_H,
) -> Image.Image:
    """
    Renders an individual high-resolution school sticker label on a standard 1039 × 590 canvas,
    resizing to target dimensions with high-fidelity filtering if needed.
    """
    theme_key = state.school_theme if state.school_theme in THEME_CONFIGS else "classic"
    theme = THEME_CONFIGS[theme_key]
    lang = state.language
    is_ar = (lang == "ar")

    # Render on canonical 1039 × 590 px canvas
    label = Image.new("RGBA", (CANONICAL_W, CANONICAL_H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(label)

    # 1. Outer rounded card outline
    corner_r = 34
    draw.rounded_rectangle(
        [4, 4, CANONICAL_W - 5, CANONICAL_H - 5],
        radius=corner_r,
        fill=(255, 255, 255, 255),
        outline=theme["border"],
        width=6,
    )

    # 2. Header Decorative Banner
    header_h = 100
    draw.rounded_rectangle(
        [6, 6, CANONICAL_W - 7, header_h],
        radius=corner_r,
        fill=theme["primary"],
    )
    # Square bottom edges of header
    draw.rectangle([6, header_h - 22, CANONICAL_W - 7, header_h], fill=theme["primary"])

    font_header = _get_font(36, bold=True)
    font_year = _get_font(28, bold=True)
    header_title = t("school_label_header", lang)
    year_text = state.school_year or "2026 / 2027"

    if is_ar:
        # Arabic: Title on Right, Year Badge on Left
        # Year pill on left
        pill_w = 210
        draw.rounded_rectangle([25, 20, 25 + pill_w, 80], radius=18, fill=(255, 255, 255), outline=theme["accent"], width=3)
        draw.text((45, 28), year_text, fill=theme["primary"], font=font_year)
        # Title on right
        bbox = draw.textbbox((0, 0), header_title, font=font_header)
        tw = bbox[2] - bbox[0]
        draw.text((CANONICAL_W - 40 - tw, 26), header_title, fill=(255, 255, 255), font=font_header)
    else:
        # LTR: Title on Left, Year Badge on Right
        draw.text((36, 26), header_title, fill=(255, 255, 255), font=font_header)
        pill_w = 210
        pill_x = CANONICAL_W - pill_w - 28
        draw.rounded_rectangle([pill_x, 20, pill_x + pill_w, 80], radius=18, fill=(255, 255, 255), outline=theme["accent"], width=3)
        draw.text((pill_x + 20, 28), year_text, fill=theme["primary"], font=font_year)

    # 3. Avatar Badge (Left side for LTR, Right side for RTL)
    avatar_radius = 115
    if is_ar:
        cx = CANONICAL_W - 165
        cy = 280
    else:
        cx = 165
        cy = 280

    placed_photo = False
    if state.school_custom_avatar and state.image_path and Path(state.image_path).exists():
        try:
            with Image.open(state.image_path).convert("RGBA") as user_img:
                diam = avatar_radius * 2
                user_img = ImageOps.fit(user_img, (diam, diam), Image.Resampling.LANCZOS)
                mask = Image.new("L", (diam, diam), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, diam, diam], fill=255)

                label.paste(user_img, (cx - avatar_radius, cy - avatar_radius), mask)
                # Outer decorative double ring
                draw.ellipse(
                    [cx - avatar_radius - 4, cy - avatar_radius - 4, cx + avatar_radius + 4, cy + avatar_radius + 4],
                    outline=theme["accent"],
                    width=6,
                )
                placed_photo = True
        except Exception:
            placed_photo = False

    if not placed_photo:
        _draw_theme_emblem(draw, theme_key, cx, cy, avatar_radius, theme)

    # 4. Text Fields (Name, Class, Subject)
    # LTR fields take x: 325 -> 1005 (width: 680 px)
    # RTL fields take x: 35 -> 715 (width: 680 px)
    fw = 680
    fx = 35 if is_ar else 325
    fy = 120

    lbl_name = t("school_field_name", lang)
    student_name = state.school_student_name.strip() or t("school_sample_student", lang)

    lbl_class = t("school_field_class", lang)
    grade_val = state.school_grade.strip() or t("school_sample_grade", lang)

    lbl_subject = t("school_field_subject", lang)

    font_tag = _get_font(26, bold=True)
    font_val = _get_font(34, bold=True)
    font_subject_val = _get_font(36, bold=True)
    font_dots = _get_font(28)

    # --- Ribbon 1: Student Name ---
    r1_y = fy
    draw.rounded_rectangle([fx, r1_y, fx + fw, r1_y + 92], radius=18, fill=theme["secondary"], outline=theme["border"], width=3)
    if is_ar:
        draw.text((fx + fw - 150, r1_y + 24), f"{lbl_name}:", fill=theme["text_muted"], font=font_tag)
        # Value left-aligned inside ribbon
        draw.text((fx + 25, r1_y + 20), student_name, fill=theme["text_dark"], font=font_val)
    else:
        draw.text((fx + 24, r1_y + 24), f"{lbl_name}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 175, r1_y + 20), student_name, fill=theme["text_dark"], font=font_val)

    # --- Ribbon 2: Class / Grade ---
    r2_y = fy + 106
    draw.rounded_rectangle([fx, r2_y, fx + fw, r2_y + 92], radius=18, fill=theme["secondary"], outline=theme["border"], width=3)
    if is_ar:
        draw.text((fx + fw - 150, r2_y + 24), f"{lbl_class}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 25, r2_y + 20), grade_val, fill=theme["text_dark"], font=font_val)
    else:
        draw.text((fx + 24, r2_y + 24), f"{lbl_class}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 175, r2_y + 20), grade_val, fill=theme["text_dark"], font=font_val)

    # --- Ribbon 3: Subject ---
    r3_y = fy + 212
    draw.rounded_rectangle([fx, r3_y, fx + fw, r3_y + 96], radius=18, fill=(255, 255, 255), outline=theme["primary"], width=4)
    if is_ar:
        draw.text((fx + fw - 150, r3_y + 26), f"{lbl_subject}:", fill=theme["text_muted"], font=font_tag)
        if subject:
            draw.text((fx + 25, r3_y + 20), subject, fill=theme["primary"], font=font_subject_val)
        else:
            draw.text((fx + 25, r3_y + 26), "•  •  •  •  •  •  •  •  •  •  •  •  •  •  •", fill=(148, 163, 184), font=font_dots)
    else:
        draw.text((fx + 24, r3_y + 26), f"{lbl_subject}:", fill=theme["text_muted"], font=font_tag)
        if subject:
            draw.text((fx + 175, r3_y + 20), subject, fill=theme["primary"], font=font_subject_val)
        else:
            draw.text((fx + 175, r3_y + 26), "•  •  •  •  •  •  •  •  •  •  •  •  •  •  •", fill=(148, 163, 184), font=font_dots)

    # 5. Bottom Motivational Ribbon (Fills the lower card gracefully)
    motto_y = 458
    motto_h = 76
    draw.rounded_rectangle(
        [28, motto_y, CANONICAL_W - 28, motto_y + motto_h],
        radius=16,
        fill=theme["secondary"],
        outline=theme["border"],
        width=2,
    )
    font_motto = _get_font(26, bold=True)
    motto_str = MOTTOES.get(lang, MOTTOES["en"])
    bbox = draw.textbbox((0, 0), motto_str, font=font_motto)
    mw = bbox[2] - bbox[0]
    draw.text(((CANONICAL_W - mw) // 2, motto_y + 18), motto_str, fill=theme["primary"], font=font_motto)

    # 6. Bottom Edge Color Accent Stripe
    draw.rectangle([8, CANONICAL_H - 18, CANONICAL_W - 8, CANONICAL_H - 8], fill=theme["accent"])

    # If target dimensions match canonical, return directly; otherwise, scale with high quality
    if (width_px, height_px) != (CANONICAL_W, CANONICAL_H):
        return label.resize((width_px, height_px), Image.Resampling.LANCZOS)

    return label


def render_school_labels_sheet(state: PrintMasterState, preview: bool = False) -> io.BytesIO:
    """
    Renders the complete A4 printable sheet containing 10 school stickers (2 cols × 5 rows).
    Preview mode generates 96 DPI for fast chat display, while full mode renders at 300 DPI for printing.
    Both modes use high-fidelity Lanczos sampling from the master 1039 × 590 px template.
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
    tick_len = int(round(3.5 * mm_to_px))

    for r in range(rows):
        for c in range(cols):
            x_mm = margin_x_mm + c * (label_w_mm + gap_x_mm)
            y_mm = margin_y_mm + r * (label_h_mm + gap_y_mm)

            x = int(round(x_mm * mm_to_px))
            y = int(round(y_mm * mm_to_px))

            subject_text = subjects_list[idx % len(subjects_list)] if use_auto_subjects else None
            single_img = render_single_label(state, subject=subject_text, width_px=label_w_px, height_px=label_h_px)

            sheet.paste(single_img, (x, y))

            # Corner cut ticks for precise cutting
            draw.line([(x - tick_len, y), (x, y)], fill=(148, 163, 184), width=1)
            draw.line([(x, y - tick_len), (x, y)], fill=(148, 163, 184), width=1)
            draw.line([(x + label_w_px, y), (x + label_w_px + tick_len, y)], fill=(148, 163, 184), width=1)
            draw.line([(x + label_w_px, y - tick_len), (x + label_w_px, y)], fill=(148, 163, 184), width=1)
            draw.line([(x - tick_len, y + label_h_px), (x, y + label_h_px)], fill=(148, 163, 184), width=1)
            draw.line([(x, y + label_h_px), (x, y + label_h_px + tick_len)], fill=(148, 163, 184), width=1)
            draw.line([(x + label_w_px, y + label_h_px), (x + label_w_px + tick_len, y + label_h_px)], fill=(148, 163, 184), width=1)
            draw.line([(x + label_w_px, y + label_h_px), (x + label_w_px, y + label_h_px + tick_len)], fill=(148, 163, 184), width=1)

            idx += 1

    # Bottom Sheet Footer Note
    font_footer = _get_font(int(round(9.0 * (dpi / 72.0))))
    footer_text = "PrintMaster A4 • School Notebook Labels • 10 Stickers (88×50 mm) • Print at 100% Scale / Actual Size"
    draw.text((int(round(margin_x_mm * mm_to_px)), page_h_px - int(round(12.0 * mm_to_px))), footer_text, fill=(148, 163, 184), font=font_footer)

    buf = io.BytesIO()
    if preview:
        # Wrap preview on a subtle dark background mockup with shadow
        pad = 32
        mockup = Image.new("RGB", (page_w_px + pad * 2, page_h_px + pad * 2), (15, 23, 42))
        mockup.paste(sheet, (pad, pad))
        mockup.save(buf, format="JPEG", quality=92)
    else:
        sheet.save(buf, format="PNG", dpi=(300, 300))

    buf.seek(0)
    return buf

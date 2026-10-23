"""
PrintMaster A4 - School Notebook Label Generator Engine
Generates professional, beautiful printable sheets of adhesive student notebook labels.
Supports 5 visual themes, auto-subject lists, custom student photo avatars, and tri-lingual text.
Proportionally engineered at 300 DPI (88 × 50 mm = 1039 × 590 px per label) with massive, high-contrast, ultra-legible typography.
"""

import io
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

from .models import PrintMasterState
from .i18n import t

# Canonical dimensions for 88 × 50 mm at 300 DPI
CANONICAL_W = 1039
CANONICAL_H = 590

# Theme Color Schemes & Accents (5 Boys + 5 Girls + Classic)
THEMES_ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "themes"

THEME_CONFIGS = {
    # --- 👦 Boys Themes (5) ---
    "boy_football": {
        "primary": (4, 120, 87),       # Champion Emerald Green
        "secondary": (236, 253, 245),  # Mint Soft
        "border": (16, 185, 129),
        "text_dark": (6, 78, 59),
        "text_muted": (55, 65, 81),
        "accent": (234, 88, 12),       # Bright Orange
    },
    "boy_superhero": {
        "primary": (29, 78, 216),      # Hero Blue
        "secondary": (239, 246, 255),  # Soft Ice Blue
        "border": (59, 130, 246),
        "text_dark": (30, 58, 138),
        "text_muted": (71, 85, 105),
        "accent": (220, 38, 38),       # Crimson Red
    },
    "boy_space": {
        "primary": (76, 29, 149),      # Cosmic Purple
        "secondary": (245, 243, 255),  # Lavender Tint
        "border": (139, 92, 246),
        "text_dark": (46, 16, 101),
        "text_muted": (75, 85, 99),
        "accent": (250, 204, 21),      # Starlight Yellow
    },
    "boy_cars": {
        "primary": (185, 28, 28),      # Racing Crimson Red
        "secondary": (254, 242, 242),  # Soft Rose Red
        "border": (239, 68, 68),
        "text_dark": (127, 29, 29),
        "text_muted": (75, 85, 99),
        "accent": (245, 158, 11),      # Speed Gold
    },
    "boy_gamer": {
        "primary": (67, 56, 202),      # Cyber Indigo
        "secondary": (238, 242, 255),  # Soft Neon Blue
        "border": (99, 102, 241),
        "text_dark": (49, 46, 129),
        "text_muted": (75, 85, 99),
        "accent": (6, 182, 212),       # Electric Cyan
    },

    # --- 👧 Girls Themes (5) ---
    "girl_unicorn": {
        "primary": (126, 34, 206),     # Magical Violet
        "secondary": (250, 245, 255),  # Pastel Dream
        "border": (192, 132, 252),
        "text_dark": (88, 28, 135),
        "text_muted": (107, 114, 128),
        "accent": (236, 72, 153),      # Sparkle Pink
    },
    "girl_princess": {
        "primary": (190, 24, 93),      # Royal Rose
        "secondary": (253, 242, 248),  # Soft Pink
        "border": (244, 114, 182),
        "text_dark": (131, 24, 67),
        "text_muted": (107, 114, 128),
        "accent": (245, 158, 11),      # Golden Tiara
    },
    "girl_kitty": {
        "primary": (225, 29, 72),      # Strawberry Rose
        "secondary": (255, 241, 242),  # Soft Blush
        "border": (251, 113, 133),
        "text_dark": (136, 19, 55),
        "text_muted": (107, 114, 128),
        "accent": (16, 185, 129),      # Pastel Mint
    },
    "girl_butterfly": {
        "primary": (13, 148, 136),     # Enchanted Teal
        "secondary": (240, 253, 250),  # Mint Soft
        "border": (45, 212, 191),
        "text_dark": (19, 78, 74),
        "text_muted": (71, 85, 105),
        "accent": (244, 63, 94),       # Coral Pink
    },
    "girl_artist": {
        "primary": (109, 40, 217),     # Creative Plum
        "secondary": (245, 243, 255),  # Soft Lilac
        "border": (167, 139, 250),
        "text_dark": (76, 29, 149),
        "text_muted": (75, 85, 99),
        "accent": (245, 158, 11),      # Palette Amber
    },

    # --- Classic Minimalist ---
    "classic": {
        "primary": (30, 58, 138),      # Deep Navy
        "secondary": (239, 246, 255),  # Soft Blue Tint
        "border": (59, 130, 246),      # Royal Blue
        "text_dark": (15, 23, 42),
        "text_muted": (71, 85, 105),
        "accent": (245, 158, 11),      # Gold
    },
    # Backwards compatibility aliases
    "football": {
        "primary": (4, 120, 87),
        "secondary": (236, 253, 245),
        "border": (16, 185, 129),
        "text_dark": (6, 78, 59),
        "text_muted": (55, 65, 81),
        "accent": (234, 88, 12),
    },
    "space": {
        "primary": (76, 29, 149),
        "secondary": (245, 243, 255),
        "border": (139, 92, 246),
        "text_dark": (46, 16, 101),
        "text_muted": (75, 85, 99),
        "accent": (250, 204, 21),
    },
    "cute": {
        "primary": (225, 29, 72),
        "secondary": (255, 241, 242),
        "border": (251, 113, 133),
        "text_dark": (136, 19, 55),
        "text_muted": (107, 114, 128),
        "accent": (245, 158, 11),
    },
    "science": {
        "primary": (13, 148, 136),
        "secondary": (240, 253, 250),
        "border": (20, 184, 166),
        "text_dark": (19, 78, 74),
        "text_muted": (71, 85, 105),
        "accent": (249, 115, 22),
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
    "ar": "★ طريقي نحو النجاح والتفوق المدرسي ★",
    "fr": "★ Année Scolaire de Réussite & d'Excellence ★",
    "en": "★ Knowledge is Power  •  Strive for Excellence ★",
}

BUNDLED_FONTS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"


def _get_font(size: int, bold: bool = False, is_ar: bool = False) -> ImageFont.ImageFont:
    """Safely retrieves TrueType font supporting Latin and Arabic characters across all OS platforms."""
    # 1. Bundled Tahoma in repository (guaranteed cross-platform on Render Linux, Docker, Windows)
    bundled = BUNDLED_FONTS_DIR / ("tahomabd.ttf" if bold else "tahoma.ttf")
    if bundled.exists():
        try:
            return ImageFont.truetype(str(bundled), size)
        except Exception:
            pass

    # 2. Linux server system fonts (Render Ubuntu/Debian)
    linux_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for lp in linux_paths:
        if Path(lp).exists():
            try:
                return ImageFont.truetype(lp, size)
            except Exception:
                continue

    # 3. Windows system fonts
    font_names = ["tahomabd.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["tahoma.ttf", "segoeui.ttf", "arial.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue

    # 4. Scaled default fallback (Pillow 10+)
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _draw_theme_emblem(draw: ImageDraw.Draw, theme_key: str, cx: int, cy: int, r: int, theme: Dict[str, Any]):
    """Draws a colorful, vector-styled decorative emblem badge for the selected theme."""
    if theme_key == "football":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["secondary"], outline=theme["primary"], width=6)
        br = int(r * 0.72)
        draw.ellipse([cx - br, cy - br, cx + br, cy + br], fill=(255, 255, 255), outline=(15, 23, 42), width=5)
        pent = []
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            pent.append((cx + int(br * 0.38 * math.cos(angle)), cy + int(br * 0.38 * math.sin(angle))))
        draw.polygon(pent, fill=(15, 23, 42))
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            p1 = (cx + int(br * 0.38 * math.cos(angle)), cy + int(br * 0.38 * math.sin(angle)))
            p_out = (cx + int(br * math.cos(angle)), cy + int(br * math.sin(angle)))
            draw.line([p1, p_out], fill=(15, 23, 42), width=4)

    elif theme_key == "space":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["primary"], outline=theme["accent"], width=6)
        pr = int(r * 0.44)
        draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=theme["border"], outline=(255, 255, 255), width=3)
        draw.arc([cx - int(r * 0.8), cy - int(r * 0.28), cx + int(r * 0.8), cy + int(r * 0.28)], start=0, end=360, fill=theme["accent"], width=8)
        f_star = _get_font(26, bold=True)
        for sx, sy in [(cx - int(r * 0.5), cy - int(r * 0.5)), (cx + int(r * 0.5), cy - int(r * 0.4)), (cx - int(r * 0.4), cy + int(r * 0.5))]:
            draw.text((sx, sy), "✦", fill=theme["accent"], font=f_star)

    elif theme_key == "cute":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["secondary"], outline=theme["primary"], width=6)
        draw.ellipse([cx - int(r * 0.65), cy - int(r * 0.72), cx - int(r * 0.25), cy - int(r * 0.32)], fill=(244, 114, 182), outline=(190, 24, 93), width=4)
        draw.ellipse([cx + int(r * 0.25), cy - int(r * 0.72), cx + int(r * 0.65), cy - int(r * 0.32)], fill=(244, 114, 182), outline=(190, 24, 93), width=4)
        draw.ellipse([cx - int(r * 0.55), cy - int(r * 0.45), cx + int(r * 0.55), cy + int(r * 0.55)], fill=(251, 207, 232), outline=(190, 24, 93), width=5)
        draw.ellipse([cx - int(r * 0.45), cy + int(r * 0.1), cx - int(r * 0.25), cy + int(r * 0.28)], fill=(244, 63, 94))
        draw.ellipse([cx + int(r * 0.25), cy + int(r * 0.1), cx + int(r * 0.45), cy + int(r * 0.28)], fill=(244, 63, 94))
        draw.ellipse([cx - int(r * 0.25), cy - int(r * 0.1), cx - int(r * 0.15), cy + int(r * 0.02)], fill=(15, 23, 42))
        draw.ellipse([cx + int(r * 0.15), cy - int(r * 0.1), cx + int(r * 0.25), cy + int(r * 0.02)], fill=(15, 23, 42))
        draw.ellipse([cx - int(r * 0.2), cy + int(r * 0.08), cx + int(r * 0.2), cy + int(r * 0.36)], fill=(255, 255, 255))
        draw.ellipse([cx - int(r * 0.08), cy + int(r * 0.12), cx + int(r * 0.08), cy + int(r * 0.24)], fill=(15, 23, 42))

    elif theme_key == "science":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["secondary"], outline=theme["primary"], width=6)
        neck = [
            (cx - 15, cy - int(r * 0.55)), (cx + 15, cy - int(r * 0.55)),
            (cx + 15, cy - int(r * 0.18)), (cx + int(r * 0.55), cy + int(r * 0.48)),
            (cx - int(r * 0.55), cy + int(r * 0.48)), (cx - 15, cy - int(r * 0.18))
        ]
        draw.polygon(neck, fill=(255, 255, 255), outline=theme["primary"], width=5)
        liquid = [
            (cx - int(r * 0.38), cy + int(r * 0.15)), (cx + int(r * 0.38), cy + int(r * 0.15)),
            (cx + int(r * 0.50), cy + int(r * 0.44)), (cx - int(r * 0.50), cy + int(r * 0.44))
        ]
        draw.polygon(liquid, fill=theme["border"])
        for bx, by, brad in [(cx - 12, cy + 28, 6), (cx + 16, cy + 34, 8), (cx, cy - 6, 7)]:
            draw.ellipse([bx - brad, by - brad, bx + brad, by + brad], fill=theme["accent"])

    else:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["primary"], outline=theme["accent"], width=6)
        cap_poly = [(cx, cy - int(r * 0.45)), (cx + int(r * 0.6), cy - int(r * 0.15)), (cx, cy + int(r * 0.12)), (cx - int(r * 0.6), cy - int(r * 0.15))]
        draw.polygon(cap_poly, fill=theme["accent"], outline=(255, 255, 255), width=3)
        draw.polygon([(cx - int(r * 0.32), cy - int(r * 0.1)), (cx + int(r * 0.32), cy - int(r * 0.1)), (cx + int(r * 0.26), cy + int(r * 0.28)), (cx - int(r * 0.26), cy + int(r * 0.28))], fill=(217, 119, 6))
        draw.line([(cx, cy - int(r * 0.15)), (cx + int(r * 0.55), cy + int(r * 0.18)), (cx + int(r * 0.55), cy + int(r * 0.44))], fill=(255, 255, 255), width=4)
        draw.ellipse([cx + int(r * 0.50), cy + int(r * 0.40), cx + int(r * 0.60), cy + int(r * 0.52)], fill=theme["accent"])


def render_single_label(
    state: PrintMasterState,
    subject: Optional[str] = None,
    width_px: int = CANONICAL_W,
    height_px: int = CANONICAL_H,
) -> Image.Image:
    """
    Renders an individual high-resolution school sticker label on a standard 1039 × 590 canvas
    with massive, ultra-clear fonts and crisp contrast.
    """
    theme_key = state.school_theme if state.school_theme in THEME_CONFIGS else "classic"
    theme = THEME_CONFIGS[theme_key]
    lang = state.language
    is_ar = (lang == "ar")

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
    header_h = 108
    draw.rounded_rectangle(
        [6, 6, CANONICAL_W - 7, header_h],
        radius=corner_r,
        fill=theme["primary"],
    )
    draw.rectangle([6, header_h - 22, CANONICAL_W - 7, header_h], fill=theme["primary"])

    font_header = _get_font(48, bold=True, is_ar=is_ar)
    font_year = _get_font(38, bold=True, is_ar=is_ar)
    header_title = t("school_label_header", lang)
    year_text = state.school_year or "2026 / 2027"

    if is_ar:
        # Arabic: Year Pill Left, Title Right
        pill_w = 230
        draw.rounded_rectangle([25, 18, 25 + pill_w, 88], radius=20, fill=(255, 255, 255), outline=theme["accent"], width=3)
        bbox_y = draw.textbbox((0, 0), year_text, font=font_year)
        yw = bbox_y[2] - bbox_y[0]
        yh = bbox_y[3] - bbox_y[1]
        draw.text((25 + (pill_w - yw) // 2, 18 + (70 - yh) // 2 - 4), year_text, fill=theme["primary"], font=font_year)

        bbox = draw.textbbox((0, 0), header_title, font=font_header)
        tw = bbox[2] - bbox[0]
        draw.text((CANONICAL_W - 40 - tw, 22), header_title, fill=(255, 255, 255), font=font_header)
    else:
        # LTR: Title Left, Year Pill Right
        draw.text((36, 22), header_title, fill=(255, 255, 255), font=font_header)
        pill_w = 230
        pill_x = CANONICAL_W - pill_w - 28
        draw.rounded_rectangle([pill_x, 18, pill_x + pill_w, 88], radius=20, fill=(255, 255, 255), outline=theme["accent"], width=3)
        bbox_y = draw.textbbox((0, 0), year_text, font=font_year)
        yw = bbox_y[2] - bbox_y[0]
        yh = bbox_y[3] - bbox_y[1]
        draw.text((pill_x + (pill_w - yw) // 2, 18 + (70 - yh) // 2 - 4), year_text, fill=theme["primary"], font=font_year)

    # 3. Avatar Badge
    avatar_radius = 120
    if is_ar:
        cx = CANONICAL_W - 165
        cy = 285
    else:
        cx = 165
        cy = 285

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
                draw.ellipse(
                    [cx - avatar_radius - 4, cy - avatar_radius - 4, cx + avatar_radius + 4, cy + avatar_radius + 4],
                    outline=theme["accent"],
                    width=6,
                )
                placed_photo = True
        except Exception:
            placed_photo = False

    if not placed_photo:
        mascot_file = THEMES_ASSETS_DIR / f"{theme_key}.png"
        if mascot_file.exists():
            try:
                with Image.open(mascot_file).convert("RGBA") as mascot_img:
                    diam = avatar_radius * 2
                    mascot_img = ImageOps.fit(mascot_img, (diam, diam), Image.Resampling.LANCZOS)
                    mask = Image.new("L", (diam, diam), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse([0, 0, diam, diam], fill=255)

                    label.paste(mascot_img, (cx - avatar_radius, cy - avatar_radius), mask)
                    draw.ellipse(
                        [cx - avatar_radius - 4, cy - avatar_radius - 4, cx + avatar_radius + 4, cy + avatar_radius + 4],
                        outline=theme["accent"],
                        width=6,
                    )
                    draw.ellipse(
                        [cx - avatar_radius - 8, cy - avatar_radius - 8, cx + avatar_radius + 8, cy + avatar_radius + 8],
                        outline=theme["border"],
                        width=3,
                    )
                    placed_photo = True
            except Exception:
                placed_photo = False

    if not placed_photo:
        _draw_theme_emblem(draw, theme_key, cx, cy, avatar_radius, theme)

    # 4. Text Fields (Name, Class, Subject) with Large High-Legibility Fonts
    fw = 695
    fx = 30 if is_ar else 315
    fy = 122

    lbl_name = t("school_field_name", lang)
    student_name = state.school_student_name.strip() or t("school_sample_student", lang)

    lbl_class = t("school_field_class", lang)
    grade_val = state.school_grade.strip() or t("school_sample_grade", lang)

    lbl_subject = t("school_field_subject", lang)

    font_tag = _get_font(38, bold=True, is_ar=is_ar)
    font_class_val = _get_font(52, bold=True, is_ar=is_ar)
    font_subject_val = _get_font(58, bold=True, is_ar=is_ar)
    font_dots = _get_font(36, bold=True)

    # Dynamic font sizing for student name to ensure maximum boldness without truncation
    name_font_size = 62
    if len(student_name) > 22:
        name_font_size = 46
    elif len(student_name) > 16:
        name_font_size = 54
    font_name_val = _get_font(name_font_size, bold=True, is_ar=is_ar)

    # --- Ribbon 1: Student Name ---
    r1_y = fy
    draw.rounded_rectangle([fx, r1_y, fx + fw, r1_y + 104], radius=20, fill=theme["secondary"], outline=theme["border"], width=3)
    if is_ar:
        draw.text((fx + fw - 165, r1_y + 26), f"{lbl_name}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 25, r1_y + 18), student_name, fill=theme["text_dark"], font=font_name_val)
    else:
        draw.text((fx + 24, r1_y + 26), f"{lbl_name}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 185, r1_y + 18), student_name, fill=theme["text_dark"], font=font_name_val)

    # --- Ribbon 2: Class / Grade ---
    r2_y = fy + 116
    draw.rounded_rectangle([fx, r2_y, fx + fw, r2_y + 98], radius=20, fill=theme["secondary"], outline=theme["border"], width=3)
    if is_ar:
        draw.text((fx + fw - 165, r2_y + 24), f"{lbl_class}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 25, r2_y + 18), grade_val, fill=theme["text_dark"], font=font_class_val)
    else:
        draw.text((fx + 24, r2_y + 24), f"{lbl_class}:", fill=theme["text_muted"], font=font_tag)
        draw.text((fx + 185, r2_y + 18), grade_val, fill=theme["text_dark"], font=font_class_val)

    # --- Ribbon 3: Subject ---
    r3_y = fy + 226
    draw.rounded_rectangle([fx, r3_y, fx + fw, r3_y + 105], radius=20, fill=(255, 255, 255), outline=theme["primary"], width=4)
    if is_ar:
        draw.text((fx + fw - 165, r3_y + 26), f"{lbl_subject}:", fill=theme["text_muted"], font=font_tag)
        if subject:
            draw.text((fx + 25, r3_y + 16), subject, fill=theme["primary"], font=font_subject_val)
        else:
            dash_y = r3_y + 58
            curr_x = fx + 25
            dash_end = fx + fw - 180
            while curr_x < dash_end:
                draw.line([(curr_x, dash_y), (min(curr_x + 18, dash_end), dash_y)], fill=(156, 163, 175), width=3)
                curr_x += 28
    else:
        draw.text((fx + 24, r3_y + 26), f"{lbl_subject}:", fill=theme["text_muted"], font=font_tag)
        if subject:
            draw.text((fx + 215, r3_y + 16), subject, fill=theme["primary"], font=font_subject_val)
        else:
            dash_y = r3_y + 58
            curr_x = fx + 215
            dash_end = fx + fw - 30
            while curr_x < dash_end:
                draw.line([(curr_x, dash_y), (min(curr_x + 18, dash_end), dash_y)], fill=(156, 163, 175), width=3)
                curr_x += 28

    # 5. Bottom Motivational Ribbon
    motto_y = 472
    motto_h = 76
    draw.rounded_rectangle(
        [28, motto_y, CANONICAL_W - 28, motto_y + motto_h],
        radius=16,
        fill=theme["secondary"],
        outline=theme["border"],
        width=2,
    )
    font_motto = _get_font(34, bold=True, is_ar=is_ar)
    motto_str = MOTTOES.get(lang, MOTTOES["en"])
    bbox = draw.textbbox((0, 0), motto_str, font=font_motto)
    mw = bbox[2] - bbox[0]
    draw.text(((CANONICAL_W - mw) // 2, motto_y + 14), motto_str, fill=theme["primary"], font=font_motto)

    # 6. Bottom Edge Color Accent Stripe
    draw.rectangle([8, CANONICAL_H - 16, CANONICAL_W - 8, CANONICAL_H - 8], fill=theme["accent"])

    if (width_px, height_px) != (CANONICAL_W, CANONICAL_H):
        return label.resize((width_px, height_px), Image.Resampling.LANCZOS)

    return label


def render_single_label_preview(state: PrintMasterState) -> io.BytesIO:
    """
    Renders a high-resolution, wide landscape hero preview of a single school sticker.
    Framed with modern drop-shadow on dark slate background so that on Telegram (mobile/desktop),
    the sticker expands to full chat width and all typography is instantly legible.
    """
    lang = state.language
    use_auto = (state.school_subject_mode == "auto")
    subj_list = CORE_SUBJECTS.get(lang, CORE_SUBJECTS["en"])
    sample_subj = subj_list[0] if use_auto else None

    # Render master high-res sticker
    sticker = render_single_label(state, subject=sample_subj)

    pad_x = 40
    pad_y = 48
    header_bar_h = 36
    total_w = CANONICAL_W + (pad_x * 2)
    total_h = CANONICAL_H + (pad_y * 2) + header_bar_h

    canvas = Image.new("RGBA", (total_w, total_h), (15, 23, 42, 255))
    draw = ImageDraw.Draw(canvas)

    # Top indicator
    f_info = _get_font(20, bold=True)
    status_text = "PrintMaster A4  |  Notebook Sticker Preview (88 x 50 mm)  |  10x per A4 Sheet"
    draw.text((pad_x, 14), status_text, fill=(226, 232, 240), font=f_info)

    # Soft drop shadow
    shadow = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    sx0 = pad_x
    sy0 = pad_y + header_bar_h
    s_draw.rounded_rectangle([sx0 + 4, sy0 + 10, sx0 + CANONICAL_W + 4, sy0 + CANONICAL_H + 10], radius=34, fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.paste(shadow, (0, 0), shadow)

    # Paste sticker
    canvas.paste(sticker, (pad_x, pad_y + header_bar_h), sticker)

    buf = io.BytesIO()
    # Save as JPEG high quality
    canvas.convert("RGB").save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


def render_school_labels_sheet(state: PrintMasterState, preview: bool = False) -> io.BytesIO:
    """
    Renders the complete A4 printable sheet containing 10 school stickers (2 cols × 5 rows).
    Preview mode generates 96 DPI for chat overview, while full mode renders at 300 DPI for printing.
    """
    dpi = 96.0 if preview else 300.0
    mm_to_px = dpi / 25.4

    page_w_px = int(round(210.0 * mm_to_px))
    page_h_px = int(round(297.0 * mm_to_px))

    sheet = Image.new("RGB", (page_w_px, page_h_px), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

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

    lang = state.language
    subjects_list = CORE_SUBJECTS.get(lang, CORE_SUBJECTS["en"])
    use_auto_subjects = (state.school_subject_mode == "auto")

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
        pad = 32
        mockup = Image.new("RGB", (page_w_px + pad * 2, page_h_px + pad * 2), (15, 23, 42))
        mockup.paste(sheet, (pad, pad))
        mockup.save(buf, format="JPEG", quality=92)
    else:
        sheet.save(buf, format="PNG", dpi=(300, 300))

    buf.seek(0)
    return buf

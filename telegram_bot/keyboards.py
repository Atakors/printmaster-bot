"""
PrintMaster A4 - Telegram Inline Keyboard Builder
Constructs sleek, touch-friendly interactive menus matching all desktop capabilities in English & Arabic.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .models import PrintMasterState
from .layout_engine import STANDARD_PRESETS, GRID_PRESETS, POSTER_PRESETS, MARGIN_PRESETS, BATCH_PRESETS
from .i18n import t


PRESET_TRANS_KEYS = {
    "passport": "preset_passport",
    "us_visa": "preset_us_visa",
    "business_card": "preset_business_card",
    "wallet": "preset_wallet",
    "polaroid": "preset_polaroid",
    "sticker_small": "preset_small_sticker",
    "photo_10x15": "preset_photo_10x15",
    "mini_id": "preset_mini_id",
}


def build_keyboard(state: PrintMasterState) -> InlineKeyboardMarkup:
    """Builds the inline keyboard corresponding to the active menu state."""
    menu = state.current_menu

    if state.mode == "school_labels":
        if menu == "school_themes":
            return build_school_themes_menu(state)
        elif menu == "language":
            return build_language_menu(state)
        elif menu == "about":
            return build_about_menu(state)
        return build_school_labels_menu(state)

    if menu == "presets_size":
        return build_presets_size_menu(state)
    elif menu == "presets_grid":
        return build_presets_grid_menu(state)
    elif menu == "custom_size":
        return build_custom_size_menu(state)
    elif menu == "spacing":
        return build_spacing_menu(state)
    elif menu == "page_margins":
        return build_page_margins_menu(state)
    elif menu == "trimming":
        return build_trimming_menu(state)
    elif menu == "batch_copies":
        return build_batch_menu(state)
    elif menu == "poster_grid":
        return build_poster_grid_menu(state)
    elif menu == "poster_overlap":
        return build_poster_overlap_menu(state)
    elif menu == "language":
        return build_language_menu(state)
    elif menu == "about":
        return build_about_menu(state)
    else:
        return build_main_menu(state)


def build_school_labels_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    """Builds the control keyboard for the School Notebook Labels mode."""
    lang = state.language
    rows = []

    # Mode Selector
    mode_btn = InlineKeyboardButton(t("mode_school_btn", lang), callback_data="toggle_mode")
    rows.append([mode_btn])

    # Name and Class
    name_display = state.school_student_name.strip() or t("school_sample_student", lang)
    grade_display = state.school_grade.strip() or t("school_sample_grade", lang)
    if len(name_display) > 16:
        name_display = name_display[:14] + ".."
    if len(grade_display) > 14:
        grade_display = grade_display[:12] + ".."

    rows.append([
        InlineKeyboardButton(t("btn_school_name", lang, name=name_display), callback_data="input:school_name"),
        InlineKeyboardButton(t("btn_school_grade", lang, grade=grade_display), callback_data="input:school_grade"),
    ])

    # Theme and Subjects Mode
    theme_key = state.school_theme if state.school_theme in ("classic", "football", "space", "cute", "science") else "classic"
    theme_name = t(f"theme_{theme_key}", lang)
    subj_label = t("school_subj_auto", lang) if state.school_subject_mode == "auto" else t("school_subj_blank", lang)

    rows.append([
        InlineKeyboardButton(t("btn_school_theme", lang, theme=theme_name), callback_data="menu:school_themes"),
        InlineKeyboardButton(t("btn_school_subjects", lang, mode=subj_label), callback_data="toggle_school_subjects"),
    ])

    # Student Photo Avatar toggle
    photo_status = t("on", lang) if state.school_custom_avatar else t("off", lang)
    rows.append([
        InlineKeyboardButton(t("btn_school_avatar", lang, status=photo_status), callback_data="toggle_school_avatar"),
    ])

    # Export Buttons
    rows.append([
        InlineKeyboardButton(t("btn_export_pdf", lang), callback_data="export:pdf"),
        InlineKeyboardButton(t("btn_export_image300", lang), callback_data="export:image300"),
    ])

    # Language & Refresh
    rows.append([
        InlineKeyboardButton(t("btn_language", lang), callback_data="menu:language"),
        InlineKeyboardButton(t("btn_refresh", lang), callback_data="refresh_preview"),
    ])

    # Back to Duplicator
    rows.append([
        InlineKeyboardButton("« " + t("mode_duplicator", lang), callback_data="switch_mode:duplicator"),
    ])

    return InlineKeyboardMarkup(rows)


def build_school_themes_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    """Builds interactive theme selector for School Labels."""
    lang = state.language
    themes = ["classic", "football", "space", "cute", "science"]
    rows = []
    for th in themes:
        active = "✓ " if state.school_theme == th else ""
        label = t(f"theme_{th}", lang)
        rows.append([InlineKeyboardButton(f"{active}{label}", callback_data=f"set_school_theme:{th}")])

    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)



def build_main_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    rows = []

    # Mode Selector
    if state.mode == "duplicator":
        mode_btn = InlineKeyboardButton(t("mode_duplicator_btn", lang), callback_data="toggle_mode")
        rows.append([mode_btn])

        # Presets row
        rows.append([
            InlineKeyboardButton(t("btn_size_presets", lang), callback_data="menu:presets_size"),
            InlineKeyboardButton(t("btn_quick_grids", lang), callback_data="menu:presets_grid"),
        ])

        # Custom dimensions & gap
        w_cm = state.image_width_mm / 10.0
        h_cm = state.image_height_mm / 10.0
        rows.append([
            InlineKeyboardButton(t("btn_custom_size", lang, w=w_cm, h=h_cm), callback_data="menu:custom_size"),
            InlineKeyboardButton(t("btn_gap", lang, gap=state.gap_mm), callback_data="menu:spacing"),
        ])

        # Page setup and Trimming
        orient_icon = "📄" if state.is_portrait else "📃"
        rows.append([
            InlineKeyboardButton(t("btn_page_margins", lang, icon=orient_icon), callback_data="menu:page_margins"),
            InlineKeyboardButton(t("btn_trimming", lang), callback_data="menu:trimming"),
        ])

        # Batch copies
        batch_txt = t("batch_copies_option", lang, n=state.total_batch_copies) if state.total_batch_copies > 0 else t("batch_single_option", lang)
        rows.append([
            InlineKeyboardButton(t("btn_batch", lang, text=batch_txt), callback_data="menu:batch_copies"),
        ])

    else:
        # Poster Mode
        mode_btn = InlineKeyboardButton(t("mode_poster_btn", lang), callback_data="toggle_mode")
        rows.append([mode_btn])

        rows.append([
            InlineKeyboardButton(t("btn_poster_grid", lang, cols=state.poster_cols, rows=state.poster_rows), callback_data="menu:poster_grid"),
            InlineKeyboardButton(t("btn_poster_overlap", lang, overlap=state.poster_overlap_mm), callback_data="menu:poster_overlap"),
        ])

        orient_icon = "📄" if state.is_portrait else "📃"
        guide_status = t("on", lang) if state.poster_guides else t("off", lang)
        rows.append([
            InlineKeyboardButton(t("btn_page_margins", lang, icon=orient_icon), callback_data="menu:page_margins"),
            InlineKeyboardButton(t("btn_glue_guides", lang, status=guide_status), callback_data="toggle_poster_guides"),
        ])

    # Export Buttons
    rows.append([
        InlineKeyboardButton(t("btn_export_pdf", lang), callback_data="export:pdf"),
        InlineKeyboardButton(t("btn_export_image300", lang), callback_data="export:image300"),
    ])

    # School Labels Quick Switch
    rows.append([
        InlineKeyboardButton(t("btn_switch_school", lang), callback_data="switch_mode:school_labels"),
    ])

    # Tutorial & Language
    rows.append([
        InlineKeyboardButton(t("btn_tutorial", lang), callback_data="tutorial:step_1"),
        InlineKeyboardButton(t("btn_language", lang), callback_data="menu:language"),
    ])

    # About & Refresh
    rows.append([
        InlineKeyboardButton(t("btn_about", lang), callback_data="menu:about"),
        InlineKeyboardButton(t("btn_refresh", lang), callback_data="refresh_preview"),
    ])

    return InlineKeyboardMarkup(rows)


def build_presets_size_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    rows = []
    for p in STANDARD_PRESETS:
        trans_key = PRESET_TRANS_KEYS.get(p["id"])
        btn_txt = t(trans_key, lang) if trans_key else p["name"]
        rows.append([InlineKeyboardButton(btn_txt, callback_data=f"set_size_preset:{p['id']}")])

    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_presets_grid_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    rows = []
    current_row = []
    for g in GRID_PRESETS:
        current_row.append(InlineKeyboardButton(g["label"], callback_data=f"set_grid_preset:{g['rows']}_{g['cols']}"))
        if len(current_row) == 3:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)

    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_custom_size_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    w_cm = state.image_width_mm / 10.0
    h_cm = state.image_height_mm / 10.0
    ratio_status = t("locked", lang) if state.lock_ratio else t("unlocked", lang)

    rows = [
        [
            InlineKeyboardButton(t("btn_width", lang, w=w_cm), callback_data="input:custom_width"),
            InlineKeyboardButton(t("btn_height", lang, h=h_cm), callback_data="input:custom_height"),
        ],
        [
            InlineKeyboardButton(t("btn_ratio", lang, status=ratio_status), callback_data="toggle_lock_ratio"),
        ],
        [
            InlineKeyboardButton(t("btn_step_w_plus", lang), callback_data="step_w:5"),
            InlineKeyboardButton(t("btn_step_w_minus", lang), callback_data="step_w:-5"),
        ],
        [
            InlineKeyboardButton(t("btn_step_h_plus", lang), callback_data="step_h:5"),
            InlineKeyboardButton(t("btn_step_h_minus", lang), callback_data="step_h:-5"),
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_spacing_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    preset_gaps = [0.0, 1.0, 2.0, 3.0, 5.0, 10.0]
    rows = []
    row = []
    for g in preset_gaps:
        active = "✓ " if abs(state.gap_mm - g) < 0.01 else ""
        label = f"{active}{g:.0f} mm" if g == int(g) else f"{active}{g:.1f} mm"
        row.append(InlineKeyboardButton(label, callback_data=f"set_gap:{g}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton(t("btn_step_gap_plus", lang), callback_data="step_gap:0.5"),
        InlineKeyboardButton(t("btn_step_gap_minus", lang), callback_data="step_gap:-0.5"),
    ])
    rows.append([InlineKeyboardButton(t("btn_enter_custom_gap", lang), callback_data="input:custom_gap")])
    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_page_margins_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    orient_str = t("portrait", lang) if state.is_portrait else t("landscape", lang)
    guide_status = t("on", lang) if state.show_margin_guide else t("off", lang)

    rows = [
        [
            InlineKeyboardButton(t("btn_toggle_orient", lang, status=orient_str), callback_data="toggle_orientation"),
        ],
        [
            InlineKeyboardButton(t("margin_standard", lang), callback_data="set_margin:10"),
            InlineKeyboardButton(t("margin_narrow", lang), callback_data="set_margin:5"),
        ],
        [
            InlineKeyboardButton(t("margin_borderless", lang), callback_data="set_margin:0"),
            InlineKeyboardButton(t("margin_wide", lang), callback_data="set_margin:20"),
        ],
        [
            InlineKeyboardButton(t("btn_margin_guide_toggle", lang, status=guide_status), callback_data="toggle_margin_guide"),
        ],
        [
            InlineKeyboardButton(t("btn_enter_custom_margin", lang), callback_data="input:custom_margin"),
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_trimming_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    cut_status = t("on", lang) if state.show_cut_marks else t("off", lang)
    border_status = t("on", lang) if state.show_border else t("off", lang)
    rot_status = t("on", lang) if state.auto_rotate else t("off", lang)
    align_status = t("center", lang) if state.alignment == "center" else t("top_left", lang)

    rows = [
        [
            InlineKeyboardButton(t("btn_cut_marks_toggle", lang, status=cut_status), callback_data="toggle_cut_marks"),
            InlineKeyboardButton(t("btn_border_toggle", lang, status=border_status), callback_data="toggle_border"),
        ],
        [
            InlineKeyboardButton(t("btn_border_color", lang, color=state.border_color.title()), callback_data="cycle_border_color"),
            InlineKeyboardButton(t("btn_border_thick", lang, thick=state.border_thickness_mm), callback_data="cycle_border_thick"),
        ],
        [
            InlineKeyboardButton(t("btn_auto_rotate_toggle", lang, status=rot_status), callback_data="toggle_auto_rotate"),
        ],
        [
            InlineKeyboardButton(t("btn_alignment_toggle", lang, align=align_status), callback_data="toggle_alignment"),
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_batch_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    rows = []
    row = []
    for b in BATCH_PRESETS:
        label = t("batch_single_option", lang) if b == 0 else t("batch_copies_option", lang, n=b)
        active = "✓ " if state.total_batch_copies == b else ""
        row.append(InlineKeyboardButton(f"{active}{label}", callback_data=f"set_batch:{b}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    limit_status = str(state.max_copies) if state.limit_copies else t("off", lang)
    rows.append([InlineKeyboardButton(t("btn_limit_copies_toggle", lang, status=limit_status), callback_data="toggle_limit_copies")])
    rows.append([InlineKeyboardButton(t("btn_enter_custom_batch", lang), callback_data="input:custom_batch")])
    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_poster_grid_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    rows = []
    for p in POSTER_PRESETS:
        rows.append([
            InlineKeyboardButton(
                f"{p['label']} ({p['approx']})",
                callback_data=f"set_poster_preset:{p['cols']}_{p['rows']}",
            )
        ])

    rows.append([
        InlineKeyboardButton(t("btn_step_col_plus", lang), callback_data="step_poster_col:1"),
        InlineKeyboardButton(t("btn_step_col_minus", lang), callback_data="step_poster_col:-1"),
        InlineKeyboardButton(t("btn_step_row_plus", lang), callback_data="step_poster_row:1"),
        InlineKeyboardButton(t("btn_step_row_minus", lang), callback_data="step_poster_row:-1"),
    ])
    rows.append([InlineKeyboardButton(t("btn_enter_custom_poster_grid", lang), callback_data="input:custom_poster_grid")])
    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_poster_overlap_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    overlaps = [0.0, 5.0, 10.0, 15.0, 20.0]
    rows = []
    row = []
    for ov in overlaps:
        label = t("overlap_edge", lang) if ov == 0 else f"{ov:.0f} mm"
        active = "✓ " if abs(state.poster_overlap_mm - ov) < 0.01 else ""
        row.append(InlineKeyboardButton(f"{active}{label}", callback_data=f"set_overlap:{ov}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    guide_status = t("on", lang) if state.poster_guides else t("off", lang)
    rows.append([
        InlineKeyboardButton(
            t("btn_glue_lines_toggle", lang, status=guide_status),
            callback_data="toggle_poster_guides",
        )
    ])
    rows.append([InlineKeyboardButton(t("btn_enter_custom_overlap", lang), callback_data="input:custom_overlap")])
    rows.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_language_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    """Builds interactive language selector (English / العربية / Français)."""
    lang = state.language
    en_mark = "✅ " if lang == "en" else ""
    ar_mark = "✅ " if lang == "ar" else ""
    fr_mark = "✅ " if lang == "fr" else ""

    rows = [
        [
            InlineKeyboardButton(f"{en_mark}🇬🇧 English", callback_data="set_lang:en"),
            InlineKeyboardButton(f"{ar_mark}🇸🇦 العربية", callback_data="set_lang:ar"),
        ],
        [
            InlineKeyboardButton(f"{fr_mark}🇫🇷 Français", callback_data="set_lang:fr"),
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_about_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    lang = state.language
    rows = [
        [
            InlineKeyboardButton(t("btn_tutorial", lang), callback_data="tutorial:step_1"),
            InlineKeyboardButton(t("btn_language", lang), callback_data="menu:language"),
        ],
        [
            InlineKeyboardButton(t("btn_dev_telegram", lang), url="https://t.me/aitadz"),
            InlineKeyboardButton(t("btn_facebook", lang), url="https://www.facebook.com/aitadz.pro"),
        ],
        [
            InlineKeyboardButton(t("btn_whatsapp", lang), url="https://wa.me/213558655085"),
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)

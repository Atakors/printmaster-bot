"""
PrintMaster A4 - Telegram Inline Keyboard Builder
Constructs sleek, touch-friendly interactive menus matching all desktop capabilities.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .models import PrintMasterState
from .layout_engine import STANDARD_PRESETS, GRID_PRESETS, POSTER_PRESETS, MARGIN_PRESETS, BATCH_PRESETS


def build_keyboard(state: PrintMasterState) -> InlineKeyboardMarkup:
    """Builds the inline keyboard corresponding to the active menu state."""
    menu = state.current_menu

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
    elif menu == "about":
        return build_about_menu(state)
    else:
        return build_main_menu(state)


def build_main_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    rows = []

    # Mode Selector
    if state.mode == "duplicator":
        mode_btn = InlineKeyboardButton("🔀 Mode: 🖨 Duplicator (Grid)", callback_data="toggle_mode")
        rows.append([mode_btn])

        # Presets row
        rows.append([
            InlineKeyboardButton("📐 Size Presets", callback_data="menu:presets_size"),
            InlineKeyboardButton("📊 Quick Grids", callback_data="menu:presets_grid"),
        ])

        # Custom dimensions & gap
        w_cm = state.image_width_mm / 10.0
        h_cm = state.image_height_mm / 10.0
        rows.append([
            InlineKeyboardButton(f"📏 Size: {w_cm:.1f}×{h_cm:.1f} cm", callback_data="menu:custom_size"),
            InlineKeyboardButton(f"↔️ Gap: {state.gap_mm:.1f} mm", callback_data="menu:spacing"),
        ])

        # Page setup and Trimming
        orient_icon = "📄" if state.is_portrait else "📃"
        orient_txt = "Portrait" if state.is_portrait else "Landscape"
        rows.append([
            InlineKeyboardButton(f"{orient_icon} Page & Margins", callback_data="menu:page_margins"),
            InlineKeyboardButton("✂️ Cuts & Borders", callback_data="menu:trimming"),
        ])

        # Batch copies
        batch_txt = f"{state.total_batch_copies} Copies" if state.total_batch_copies > 0 else "1 Page (Auto)"
        rows.append([
            InlineKeyboardButton(f"📦 Batch Export: {batch_txt}", callback_data="menu:batch_copies"),
        ])

    else:
        # Poster Mode
        mode_btn = InlineKeyboardButton("🔀 Mode: 🧩 Poster Maker", callback_data="toggle_mode")
        rows.append([mode_btn])

        rows.append([
            InlineKeyboardButton(f"🧩 Poster Grid ({state.poster_cols}×{state.poster_rows})", callback_data="menu:poster_grid"),
            InlineKeyboardButton(f"📏 Overlap ({state.poster_overlap_mm:.0f} mm)", callback_data="menu:poster_overlap"),
        ])

        orient_icon = "📄" if state.is_portrait else "📃"
        rows.append([
            InlineKeyboardButton(f"{orient_icon} Orientation & Margins", callback_data="menu:page_margins"),
            InlineKeyboardButton(f"🏷 Glue Guides: {'ON' if state.poster_guides else 'OFF'}", callback_data="toggle_poster_guides"),
        ])

    # Export Buttons
    rows.append([
        InlineKeyboardButton("📄 Export PDF (Vector)", callback_data="export:pdf"),
        InlineKeyboardButton("🖼 Export 300 DPI", callback_data="export:image300"),
    ])

    # Tutorial & About
    rows.append([
        InlineKeyboardButton("📚 Beginner Tutorial", callback_data="tutorial:step_1"),
        InlineKeyboardButton("ℹ️ About & Support", callback_data="menu:about"),
    ])

    # Utility row
    rows.append([
        InlineKeyboardButton("🔄 Refresh Preview", callback_data="refresh_preview"),
    ])

    return InlineKeyboardMarkup(rows)


def build_presets_size_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    rows = []
    for p in STANDARD_PRESETS:
        btn_txt = p["name"]
        rows.append([InlineKeyboardButton(btn_txt, callback_data=f"set_size_preset:{p['id']}")])

    rows.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_presets_grid_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    rows = []
    # 3x3 layout of preset grid buttons
    current_row = []
    for g in GRID_PRESETS:
        current_row.append(InlineKeyboardButton(g["label"], callback_data=f"set_grid_preset:{g['rows']}_{g['cols']}"))
        if len(current_row) == 3:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)

    rows.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_custom_size_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    w_cm = state.image_width_mm / 10.0
    h_cm = state.image_height_mm / 10.0
    ratio_icon = "🔒 Locked" if state.lock_ratio else "🔓 Unlocked"

    rows = [
        [
            InlineKeyboardButton(f"Width: {w_cm:.1f} cm", callback_data="input:custom_width"),
            InlineKeyboardButton(f"Height: {h_cm:.1f} cm", callback_data="input:custom_height"),
        ],
        [
            InlineKeyboardButton(f"Aspect Ratio: {ratio_icon}", callback_data="toggle_lock_ratio"),
        ],
        [
            InlineKeyboardButton("➕ Width +5mm", callback_data="step_w:5"),
            InlineKeyboardButton("➖ Width -5mm", callback_data="step_w:-5"),
        ],
        [
            InlineKeyboardButton("➕ Height +5mm", callback_data="step_h:5"),
            InlineKeyboardButton("➖ Height -5mm", callback_data="step_h:-5"),
        ],
        [
            InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_spacing_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
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
        InlineKeyboardButton("➕ Gap +0.5mm", callback_data="step_gap:0.5"),
        InlineKeyboardButton("➖ Gap -0.5mm", callback_data="step_gap:-0.5"),
    ])
    rows.append([InlineKeyboardButton("✏️ Enter Custom Gap", callback_data="input:custom_gap")])
    rows.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_page_margins_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    orient_str = "🔄 Portrait" if state.is_portrait else "🔄 Landscape"
    guide_str = "👁 Margin Guide: ON" if state.show_margin_guide else "👁 Margin Guide: OFF"

    rows = [
        [
            InlineKeyboardButton(f"Orientation: {orient_str}", callback_data="toggle_orientation"),
        ],
        [
            InlineKeyboardButton("Standard (10mm)", callback_data="set_margin:10"),
            InlineKeyboardButton("Narrow (5mm)", callback_data="set_margin:5"),
        ],
        [
            InlineKeyboardButton("Borderless (0mm)", callback_data="set_margin:0"),
            InlineKeyboardButton("Wide (20mm)", callback_data="set_margin:20"),
        ],
        [
            InlineKeyboardButton(guide_str, callback_data="toggle_margin_guide"),
        ],
        [
            InlineKeyboardButton("✏️ Enter Custom Margin (mm)", callback_data="input:custom_margin"),
        ],
        [
            InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_trimming_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    cut_str = "✂️ Cut Marks: ON" if state.show_cut_marks else "✂️ Cut Marks: OFF"
    border_str = "🔲 Border: ON" if state.show_border else "🔲 Border: OFF"
    rot_str = "🔄 Auto-Rotate 90°: ON" if state.auto_rotate else "🔄 Auto-Rotate 90°: OFF"
    align_str = "🎯 Alignment: Center" if state.alignment == "center" else "📐 Alignment: Top-Left"

    rows = [
        [
            InlineKeyboardButton(cut_str, callback_data="toggle_cut_marks"),
            InlineKeyboardButton(border_str, callback_data="toggle_border"),
        ],
        [
            InlineKeyboardButton(f"Color: {state.border_color.title()}", callback_data="cycle_border_color"),
            InlineKeyboardButton(f"Thick: {state.border_thickness_mm:.1f}mm", callback_data="cycle_border_thick"),
        ],
        [
            InlineKeyboardButton(rot_str, callback_data="toggle_auto_rotate"),
        ],
        [
            InlineKeyboardButton(align_str, callback_data="toggle_alignment"),
        ],
        [
            InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def build_batch_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for b in BATCH_PRESETS:
        label = "1 Page (Auto)" if b == 0 else f"{b} Copies"
        active = "✓ " if state.total_batch_copies == b else ""
        row.append(InlineKeyboardButton(f"{active}{label}", callback_data=f"set_batch:{b}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    limit_str = f"Limit per sheet: {state.max_copies}" if state.limit_copies else "Limit per sheet: OFF"
    rows.append([InlineKeyboardButton(limit_str, callback_data="toggle_limit_copies")])
    rows.append([InlineKeyboardButton("✏️ Enter Custom Total Batch", callback_data="input:custom_batch")])
    rows.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_poster_grid_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    rows = []
    for p in POSTER_PRESETS:
        rows.append([
            InlineKeyboardButton(
                f"{p['label']} ({p['approx']})",
                callback_data=f"set_poster_preset:{p['cols']}_{p['rows']}",
            )
        ])

    rows.append([
        InlineKeyboardButton("➕ Col", callback_data="step_poster_col:1"),
        InlineKeyboardButton("➖ Col", callback_data="step_poster_col:-1"),
        InlineKeyboardButton("➕ Row", callback_data="step_poster_row:1"),
        InlineKeyboardButton("➖ Row", callback_data="step_poster_row:-1"),
    ])
    rows.append([InlineKeyboardButton("✏️ Enter Custom Grid (e.g. 3x4)", callback_data="input:custom_poster_grid")])
    rows.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_poster_overlap_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    overlaps = [0.0, 5.0, 10.0, 15.0, 20.0]
    rows = []
    row = []
    for ov in overlaps:
        label = "0 mm (Edge)" if ov == 0 else f"{ov:.0f} mm"
        active = "✓ " if abs(state.poster_overlap_mm - ov) < 0.01 else ""
        row.append(InlineKeyboardButton(f"{active}{label}", callback_data=f"set_overlap:{ov}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton(
            f"Glue Lines & Labels: {'✅ ON' if state.poster_guides else '❌ OFF'}",
            callback_data="toggle_poster_guides",
        )
    ])
    rows.append([InlineKeyboardButton("✏️ Enter Custom Overlap (mm)", callback_data="input:custom_overlap")])
    rows.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def build_about_menu(state: PrintMasterState) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("📚 Beginner Tutorial", callback_data="tutorial:step_1"),
        ],
        [
            InlineKeyboardButton("✈️ Developer Telegram", url="https://t.me/aitadz"),
            InlineKeyboardButton("📘 Facebook", url="https://www.facebook.com/aitadz.pro"),
        ],
        [
            InlineKeyboardButton("💬 WhatsApp Support", url="https://wa.me/213558655085"),
        ],
        [
            InlineKeyboardButton("« Back to Main Menu", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)

"""
PrintMaster A4 - Layout Math and Geometry Calculation Engine
Provides exact millimeter calculations, yield optimization, and grid layouts.
"""

import math
from typing import Dict, Any, List, Tuple
from .models import PrintMasterState

STANDARD_PRESETS = [
    {"id": "passport", "name": "Passport / ID Photo (3.5 × 4.5 cm)", "w": 35.0, "h": 45.0},
    {"id": "us_visa", "name": "US Visa / Square (5.1 × 5.1 cm)", "w": 51.0, "h": 51.0},
    {"id": "business_card", "name": "Standard Business Card (8.5 × 5.5 cm)", "w": 85.0, "h": 55.0},
    {"id": "id_badge", "name": "Credit Card / ID Badge (8.5 × 5.4 cm)", "w": 85.6, "h": 54.0},
    {"id": "a6", "name": "A6 Postcard (10.5 × 14.8 cm)", "w": 105.0, "h": 148.0},
    {"id": "a5", "name": "A5 Flyer (14.8 × 21.0 cm)", "w": 148.0, "h": 210.0},
    {"id": "polaroid", "name": "Polaroid Sticker (7.0 × 7.0 cm)", "w": 70.0, "h": 70.0},
]

GRID_PRESETS = [
    {"rows": 1, "cols": 1, "label": "1-Up (1×1)"},
    {"rows": 2, "cols": 1, "label": "2-Up (2×1)"},
    {"rows": 2, "cols": 2, "label": "4-Up (2×2)"},
    {"rows": 3, "cols": 2, "label": "6-Up (3×2)"},
    {"rows": 4, "cols": 2, "label": "8-Up (4×2)"},
    {"rows": 3, "cols": 3, "label": "9-Up (3×3)"},
    {"rows": 4, "cols": 3, "label": "12-Up (4×3)"},
    {"rows": 4, "cols": 4, "label": "16-Up (4×4)"},
    {"rows": 6, "cols": 4, "label": "24-Up (6×4)"},
]

POSTER_PRESETS = [
    {"cols": 2, "rows": 2, "label": "2 × 2 (~A2, 4 sheets)", "approx": "42 × 60 cm"},
    {"cols": 3, "rows": 3, "label": "3 × 3 (~A0, 9 sheets)", "approx": "63 × 89 cm"},
    {"cols": 2, "rows": 1, "label": "2 × 1 (Wide, 2 sheets)", "approx": "42 × 30 cm"},
    {"cols": 3, "rows": 2, "label": "3 × 2 (Poster, 6 sheets)", "approx": "63 × 60 cm"},
    {"cols": 4, "rows": 4, "label": "4 × 4 (Giant, 16 sheets)", "approx": "84 × 118 cm"},
]

MARGIN_PRESETS = [
    {"name": "Standard / Normal (10 mm)", "val": 10.0},
    {"name": "Narrow (5 mm)", "val": 5.0},
    {"name": "Borderless (0 mm)", "val": 0.0},
    {"name": "Wide (20 mm)", "val": 20.0},
]

BATCH_PRESETS = [0, 20, 50, 100, 200, 500]


def apply_grid_fit(state: PrintMasterState, rows: int, cols: int):
    """Calculates image dimensions to fit exactly in rows x cols on the page."""
    usable_w = state.usable_width_mm
    usable_h = state.usable_height_mm
    gap = state.gap_mm

    if usable_w <= 0 or usable_h <= 0 or rows <= 0 or cols <= 0:
        return

    cell_w = (usable_w - ((cols - 1) * gap)) / cols
    cell_h = (usable_h - ((rows - 1) * gap)) / rows

    if cell_w <= 0 or cell_h <= 0:
        return

    if state.lock_ratio and state.aspect_ratio > 0:
        w = min(cell_w, cell_h * state.aspect_ratio)
        h = w / state.aspect_ratio
    else:
        w = cell_w
        h = cell_h

    state.image_width_mm = round(w, 1)
    state.image_height_mm = round(h, 1)


def calculate_duplicator_layout(state: PrintMasterState) -> Dict[str, Any]:
    """Computes placement coordinates and metrics for Duplicator mode."""
    usable_w = state.usable_width_mm
    usable_h = state.usable_height_mm
    gap = state.gap_mm

    w_mm = max(1.0, state.image_width_mm)
    h_mm = max(1.0, state.image_height_mm)

    render_w = w_mm
    render_h = h_mm
    should_rotate = False

    # Auto-rotate 90° check for max yield
    if state.auto_rotate:
        normal_cols = int((usable_w + gap) // (w_mm + gap))
        normal_rows = int((usable_h + gap) // (h_mm + gap))
        normal_yield = max(0, normal_cols) * max(0, normal_rows)

        rot_cols = int((usable_w + gap) // (h_mm + gap))
        rot_rows = int((usable_h + gap) // (w_mm + gap))
        rot_yield = max(0, rot_cols) * max(0, rot_rows)

        if rot_yield > normal_yield:
            should_rotate = True
            render_w = h_mm
            render_h = w_mm

    cols = max(1, int((usable_w + gap) // (render_w + gap)))
    rows = max(1, int((usable_h + gap) // (render_h + gap)))
    capacity_per_page = cols * rows

    # Limit copies
    if state.limit_copies and state.max_copies > 0:
        drawn_per_page = min(capacity_per_page, state.max_copies)
    else:
        drawn_per_page = capacity_per_page

    # Batch copies
    total_batch = state.total_batch_copies
    if total_batch > 0:
        total_sheets = int(math.ceil(total_batch / capacity_per_page))
        total_copies_to_print = total_batch
    else:
        total_sheets = 1
        total_copies_to_print = drawn_per_page

    total_block_w = (cols * render_w) + ((cols - 1) * gap)
    total_block_h = (rows * render_h) + ((rows - 1) * gap)

    if state.alignment == "center":
        start_x = state.margin_left_mm + max(0.0, (usable_w - total_block_w) / 2.0)
        start_y = state.margin_top_mm + max(0.0, (usable_h - total_block_h) / 2.0)
    else:
        start_x = state.margin_left_mm
        start_y = state.margin_top_mm

    # Generate item coordinate slots
    positions: List[Tuple[float, float, float, float, bool]] = []
    drawn = 0
    for r in range(rows):
        for c in range(cols):
            if drawn >= drawn_per_page:
                break
            x = start_x + c * (render_w + gap)
            y = start_y + r * (render_h + gap)
            positions.append((x, y, render_w, render_h, should_rotate))
            drawn += 1
        if drawn >= drawn_per_page:
            break

    return {
        "cols": cols,
        "rows": rows,
        "capacity_per_page": capacity_per_page,
        "drawn_per_page": drawn_per_page,
        "total_sheets": total_sheets,
        "total_copies_to_print": total_copies_to_print,
        "render_w": render_w,
        "render_h": render_h,
        "should_rotate": should_rotate,
        "start_x": start_x,
        "start_y": start_y,
        "total_block_w": total_block_w,
        "total_block_h": total_block_h,
        "positions": positions,
        "gap": gap,
    }


def calculate_poster_layout(state: PrintMasterState) -> Dict[str, Any]:
    """Computes tiling parameters and overall dimensions for Poster mode."""
    cols = max(1, min(12, state.poster_cols))
    rows = max(1, min(12, state.poster_rows))
    overlap = max(0.0, state.poster_overlap_mm)

    page_w = state.page_width_mm
    page_h = state.page_height_mm

    total_w_mm = cols * (page_w - overlap) + overlap
    total_h_mm = rows * (page_h - overlap) + overlap

    tiles = []
    tile_num = 1
    for r in range(rows):
        for c in range(cols):
            has_right_overlap = (c < cols - 1) and (overlap > 0)
            has_bottom_overlap = (r < rows - 1) and (overlap > 0)
            tiles.append({
                "tile_index": tile_num,
                "row": r,
                "col": c,
                "rows": rows,
                "cols": cols,
                "has_right_glue": has_right_overlap,
                "has_bottom_glue": has_bottom_overlap,
                "right_glue_sheet": tile_num + 1 if has_right_overlap else None,
                "bottom_glue_row": r + 2 if has_bottom_overlap else None,
            })
            tile_num += 1

    return {
        "cols": cols,
        "rows": rows,
        "total_sheets": cols * rows,
        "overlap_mm": overlap,
        "total_w_cm": total_w_mm / 10.0,
        "total_h_cm": total_h_mm / 10.0,
        "total_w_mm": total_w_mm,
        "total_h_mm": total_h_mm,
        "tiles": tiles,
    }

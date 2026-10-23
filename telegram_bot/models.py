"""
PrintMaster A4 - Data Models and User Session State
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple
import os
import time

@dataclass
class PrintMasterState:
    user_id: int
    chat_id: int
    
    # Mode: 'duplicator' or 'poster'
    mode: str = "duplicator"
    
    # Page Setup
    is_portrait: bool = True
    margin_top_mm: float = 10.0
    margin_bottom_mm: float = 10.0
    margin_left_mm: float = 10.0
    margin_right_mm: float = 10.0
    show_margin_guide: bool = True
    
    # Duplicator Settings
    image_width_mm: float = 50.0
    image_height_mm: float = 50.0
    gap_mm: float = 3.0
    lock_ratio: bool = True
    auto_rotate: bool = False
    alignment: str = "center"  # 'center' or 'top_left'
    
    # Cutting & Border
    show_cut_marks: bool = True
    show_border: bool = False
    border_color: str = "black"  # 'black', 'gray', 'white', 'red'
    border_thickness_mm: float = 0.5
    
    # Batch / Copies
    limit_copies: bool = False
    max_copies: int = 24
    total_batch_copies: int = 0  # 0 means fill 1 single page
    
    # Poster Mode Settings
    poster_cols: int = 2
    poster_rows: int = 2
    poster_overlap_mm: float = 10.0
    poster_guides: bool = True

    # School Notebook Labels Settings
    school_student_name: str = ""
    school_grade: str = ""
    school_subject_mode: str = "blank"  # 'blank' (pen dotted line) or 'auto' (pre-filled subjects)
    school_theme: str = "classic"       # 'classic', 'football', 'space', 'cute', 'science'
    school_custom_avatar: bool = False  # If True and image_path exists, place student photo on label
    school_year: str = "2026/2027"
    school_preview_view: str = "single"  # 'single' (zoom 1x) or 'sheet' (full A4 sheet 10x)
    
    # Image Source Information
    image_path: Optional[str] = None
    image_orig_width: int = 0
    image_orig_height: int = 0
    aspect_ratio: float = 1.0
    filename: str = "image.png"
    
    # Navigation / Interaction State
    language: str = "en"  # 'en' or 'ar'
    current_menu: str = "main"  # 'main', 'presets_size', 'presets_grid', 'custom_size', 'margins', 'trimming', 'batch', 'poster_size', 'poster_overlap', 'language'
    waiting_for_input: Optional[str] = None  # e.g., 'custom_width', 'custom_height', 'custom_gap', 'custom_batch', 'custom_margin', etc.
    last_preview_message_id: Optional[int] = None
    updated_at: float = field(default_factory=time.time)

    @property
    def page_width_mm(self) -> float:
        return 210.0 if self.is_portrait else 297.0

    @property
    def page_height_mm(self) -> float:
        return 297.0 if self.is_portrait else 210.0

    @property
    def usable_width_mm(self) -> float:
        return max(0.0, self.page_width_mm - (self.margin_left_mm + self.margin_right_mm))

    @property
    def usable_height_mm(self) -> float:
        return max(0.0, self.page_height_mm - (self.margin_top_mm + self.margin_bottom_mm))

    def set_uniform_margin(self, margin_mm: float):
        self.margin_top_mm = margin_mm
        self.margin_bottom_mm = margin_mm
        self.margin_left_mm = margin_mm
        self.margin_right_mm = margin_mm

    def set_dimensions(self, width_mm: float, height_mm: float, lock_ratio: bool = False):
        self.image_width_mm = max(2.0, width_mm)
        self.image_height_mm = max(2.0, height_mm)
        self.lock_ratio = lock_ratio

    def cleanup_file(self):
        if self.image_path and os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
            except Exception:
                pass
            self.image_path = None

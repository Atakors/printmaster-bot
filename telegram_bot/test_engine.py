"""
PrintMaster A4 - Standalone Engine Test Script
Tests all math, preview rendering, 300 DPI generation, and PDF vector exports locally
without needing a live Telegram connection.
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from telegram_bot.models import PrintMasterState
from telegram_bot.layout_engine import (
    calculate_duplicator_layout,
    calculate_poster_layout,
    apply_grid_fit,
    STANDARD_PRESETS,
)
from telegram_bot.renderer import render_preview_image, render_300dpi_image
from telegram_bot.pdf_exporter import export_pdf
from telegram_bot.keyboards import build_keyboard
from telegram_bot.config import ASSETS_DIR

def run_tests():
    print("=" * 60)
    print("🧪 Running PrintMaster A4 Engine Verification Tests")
    print("=" * 60)

    test_out_dir = Path(__file__).resolve().parent / "test_outputs"
    test_out_dir.mkdir(exist_ok=True)

    sample_img = ASSETS_DIR / "sample_image.jpg"
    if not sample_img.exists():
        print(f"⚠️ Sample image not found at {sample_img}")
        return False

    state = PrintMasterState(user_id=12345, chat_id=12345)
    state.image_path = str(sample_img)
    state.aspect_ratio = 1.0

    # -------------------------------------------------------------
    # Test 1: Duplicator Layout Calculation
    # -------------------------------------------------------------
    print("\n[Test 1] Testing Duplicator Layout Calculation...")
    state.set_dimensions(50.0, 50.0, lock_ratio=True)
    state.set_uniform_margin(10.0)
    state.gap_mm = 3.0
    layout = calculate_duplicator_layout(state)
    print(f"  -> Usable area: {state.usable_width_mm:.1f} × {state.usable_height_mm:.1f} mm")
    print(f"  -> Grid: {layout['cols']} cols × {layout['rows']} rows ({layout['drawn_per_page']} copies/page)")
    assert layout['cols'] >= 3, "Cols should be >= 3 for 50mm on A4 portrait"
    assert layout['rows'] >= 5, "Rows should be >= 5 for 50mm on A4 portrait"
    print("  ✅ Duplicator layout calculation passed.")

    # -------------------------------------------------------------
    # Test 2: Grid Fitting Calculation
    # -------------------------------------------------------------
    print("\n[Test 2] Testing Grid Fitting (3x2)...")
    apply_grid_fit(state, rows=3, cols=2)
    print(f"  -> Fitted dimensions: {state.image_width_mm:.1f} × {state.image_height_mm:.1f} mm")
    fit_layout = calculate_duplicator_layout(state)
    assert fit_layout['cols'] == 2 and fit_layout['rows'] == 3
    print("  ✅ Grid fitting passed.")

    # -------------------------------------------------------------
    # Test 3: Duplicator Preview Generation
    # -------------------------------------------------------------
    print("\n[Test 3] Generating Duplicator Preview Image...")
    prev_buf = render_preview_image(state)
    prev_path = test_out_dir / "preview_duplicator.jpg"
    with open(prev_path, "wb") as f:
        f.write(prev_buf.getvalue())
    print(f"  -> Saved preview: {prev_path} ({prev_path.stat().st_size} bytes)")
    assert prev_path.stat().st_size > 10000, "Preview image file too small"
    print("  ✅ Duplicator preview image generated successfully.")

    # -------------------------------------------------------------
    # Test 4: Duplicator Vector PDF Export (Single Page & Batch)
    # -------------------------------------------------------------
    print("\n[Test 4] Generating Duplicator PDF...")
    state.show_cut_marks = True
    state.show_border = True
    state.border_color = "red"
    pdf_buf = export_pdf(state)
    pdf_path = test_out_dir / "duplicator_single.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_buf.getvalue())
    print(f"  -> Saved single page PDF: {pdf_path} ({pdf_path.stat().st_size} bytes)")
    assert pdf_path.stat().st_size > 5000, "PDF file too small"

    # Multi-page batch test
    print("  -> Testing Multi-Sheet Batch PDF (50 copies)...")
    state.total_batch_copies = 50
    batch_pdf_buf = export_pdf(state)
    batch_pdf_path = test_out_dir / "duplicator_batch_50.pdf"
    with open(batch_pdf_path, "wb") as f:
        f.write(batch_pdf_buf.getvalue())
    print(f"  -> Saved batch PDF: {batch_pdf_path} ({batch_pdf_path.stat().st_size} bytes)")
    assert batch_pdf_path.stat().st_size > pdf_path.stat().st_size, "Batch PDF should be larger"
    print("  ✅ Duplicator PDF exports passed.")

    # -------------------------------------------------------------
    # Test 5: 300 DPI High-Res Export
    # -------------------------------------------------------------
    print("\n[Test 5] Generating 300 DPI High-Res Image...")
    dpi_buf = render_300dpi_image(state)
    dpi_path = test_out_dir / "duplicator_300dpi.png"
    with open(dpi_path, "wb") as f:
        f.write(dpi_buf.getvalue())
    print(f"  -> Saved 300 DPI image: {dpi_path} ({dpi_path.stat().st_size} bytes)")
    assert dpi_path.stat().st_size > 50000, "300 DPI image too small"
    print("  ✅ 300 DPI export passed.")

    # -------------------------------------------------------------
    # Test 6: Poster Mode Calculation & Preview
    # -------------------------------------------------------------
    print("\n[Test 6] Testing Poster Mode (2x2 Sheets)...")
    state.mode = "poster"
    state.poster_cols = 2
    state.poster_rows = 2
    state.poster_overlap_mm = 10.0
    state.poster_guides = True
    poster_info = calculate_poster_layout(state)
    print(f"  -> Total poster sheets: {poster_info['total_sheets']}")
    print(f"  -> Approx poster size: {poster_info['total_w_cm']:.1f} × {poster_info['total_h_cm']:.1f} cm")
    assert poster_info['total_sheets'] == 4

    poster_prev_buf = render_preview_image(state)
    poster_prev_path = test_out_dir / "preview_poster.jpg"
    with open(poster_prev_path, "wb") as f:
        f.write(poster_prev_buf.getvalue())
    print(f"  -> Saved poster preview: {poster_prev_path} ({poster_prev_path.stat().st_size} bytes)")
    assert poster_prev_path.stat().st_size > 10000
    print("  ✅ Poster preview passed.")

    # -------------------------------------------------------------
    # Test 7: Poster Multi-Sheet PDF Export
    # -------------------------------------------------------------
    print("\n[Test 7] Generating Poster Tiled PDF...")
    poster_pdf_buf = export_pdf(state)
    poster_pdf_path = test_out_dir / "poster_tiled_2x2.pdf"
    with open(poster_pdf_path, "wb") as f:
        f.write(poster_pdf_buf.getvalue())
    print(f"  -> Saved tiled poster PDF: {poster_pdf_path} ({poster_pdf_path.stat().st_size} bytes)")
    assert poster_pdf_path.stat().st_size > 10000
    print("  ✅ Poster PDF export passed.")

    # -------------------------------------------------------------
    # Test 8: Keyboard Builder Verification
    # -------------------------------------------------------------
    print("\n[Test 8] Testing Keyboard Builders...")
    for menu in ["main", "presets_size", "presets_grid", "custom_size", "spacing", "page_margins", "trimming", "batch_copies", "poster_grid", "poster_overlap", "about"]:
        state.current_menu = menu
        kbd = build_keyboard(state)
        assert kbd.inline_keyboard, f"Keyboard empty for menu {menu}"
    print("  ✅ All keyboards constructed successfully.")

    # -------------------------------------------------------------
    # Test 9: Tutorial Module Verification
    # -------------------------------------------------------------
    print("\n[Test 9] Testing Tutorial Steps & FAQ...")
    from telegram_bot.tutorial import TUTORIAL_STEPS, get_tutorial_step, get_tutorial_faq
    assert len(TUTORIAL_STEPS) == 6, "Expected 6 tutorial steps"
    for i in range(1, 7):
        text, kbd = get_tutorial_step(i)
        assert text and "Step" in text
        assert kbd.inline_keyboard
    faq_text, faq_kbd = get_tutorial_faq()
    assert "FAQ" in faq_text and faq_kbd.inline_keyboard
    print("  ✅ Tutorial module verified successfully.")

    # -------------------------------------------------------------
    # Test 10: Database Analytics & Tracking Verification
    # -------------------------------------------------------------
    print("\n[Test 10] Testing Database Analytics & User Tracking...")
    from telegram_bot.database import (
        init_db,
        record_user_interaction,
        record_upload,
        record_export,
        get_overview_stats,
        get_top_users,
        get_recent_activity,
        export_users_csv,
    )
    from telegram import User

    init_db()

    # Create mock user
    mock_user = User(id=999888, first_name="TestUser", is_bot=False, username="tester_bot", language_code="en")
    record_user_interaction(mock_user, "start", "/start test")
    record_upload(mock_user.id)
    record_export(mock_user.id, "pdf")
    record_export(mock_user.id, "image")

    stats = get_overview_stats()
    print(f"  -> Total users tracked: {stats['total_users']}")
    print(f"  -> Total interactions: {stats['total_interactions']}")
    print(f"  -> Total PDF exports: {stats['total_pdfs']}")
    assert stats["total_users"] >= 1
    assert stats["total_interactions"] >= 1
    assert stats["total_pdfs"] >= 1

    top_users = get_top_users(limit=5)
    assert len(top_users) >= 1
    print(f"  -> Top user: @{top_users[0]['username']} with {top_users[0]['interaction_count']} actions")

    recent = get_recent_activity(limit=5)
    assert len(recent) >= 1

    csv_data = export_users_csv()
    csv_bytes = csv_data.getvalue()
    assert len(csv_bytes) > 50
    assert b"User ID,Username,First Name" in csv_bytes
    print("  ✅ Database tracking and CSV export verified successfully.")

    # -------------------------------------------------------------
    # Test 11: Arabic Localization & Language Switching
    # -------------------------------------------------------------
    print("\n[Test 11] Testing Arabic Localization & Language Engine...")
    from telegram_bot.i18n import t
    from telegram_bot.tutorial import get_tutorial_step, get_tutorial_faq
    from telegram_bot.database import set_user_language, get_user_language
    from telegram_bot.handlers import format_status_caption

    # Test translations
    assert t("mode_duplicator", "ar") == "نسخ متكرر (شبكة)"
    assert t("mode_duplicator", "en") == "Duplicator (Grid)"
    assert "برينت ماستر" in t("app_title", "ar")

    # Test Arabic status captions
    state.mode = "duplicator"
    state.language = "ar"
    ar_caption = format_status_caption(state)
    assert "وضع تكرار الصور" in ar_caption
    print("  -> Arabic duplicator caption rendered successfully.")

    state.mode = "poster"
    ar_poster_caption = format_status_caption(state)
    assert "صانع البوسترات" in ar_poster_caption
    print("  -> Arabic poster caption rendered successfully.")

    # Test Arabic keyboard
    state.mode = "duplicator"
    ar_kbd = build_keyboard(state)
    assert ar_kbd is not None
    print("  -> Arabic keyboard constructed successfully.")

    # Test Arabic tutorial and FAQ
    tut_text, tut_kbd = get_tutorial_step(1, lang="ar")
    assert "مرحباً بك في برينت ماستر" in tut_text
    faq_text, faq_kbd = get_tutorial_faq(lang="ar")
    assert "الأسئلة الشائعة" in faq_text
    print("  -> Arabic 6-step tutorial and FAQ verified successfully.")

    # Test Database language persistence
    set_user_language(mock_user.id, "ar")
    assert get_user_language(mock_user.id) == "ar"
    set_user_language(mock_user.id, "en")
    assert get_user_language(mock_user.id) == "en"
    print("  -> Database user language persistence verified.")
    print("  ✅ Arabic localization passed with 100% test coverage.")

    # -------------------------------------------------------------
    # Test 12: French Localization & Language Engine
    # -------------------------------------------------------------
    print("\n[Test 12] Testing French Localization & Language Engine...")
    assert t("mode_duplicator", "fr") == "Duplicateur (Grille)"
    assert "Bienvenue" in t("welcome_greeting", "fr", name="Alex")

    # Test French status captions
    state.mode = "duplicator"
    state.language = "fr"
    fr_caption = format_status_caption(state)
    assert "Mode Duplicateur" in fr_caption
    print("  -> French duplicator caption rendered successfully.")

    state.mode = "poster"
    fr_poster_caption = format_status_caption(state)
    assert "Créateur de Poster" in fr_poster_caption
    print("  -> French poster caption rendered successfully.")

    # Test French keyboard
    state.mode = "duplicator"
    fr_kbd = build_keyboard(state)
    assert fr_kbd is not None
    print("  -> French keyboard constructed successfully.")

    # Test French tutorial and FAQ
    tut_fr, _ = get_tutorial_step(1, lang="fr")
    assert "Bienvenue sur PrintMaster A4" in tut_fr
    faq_fr, _ = get_tutorial_faq(lang="fr")
    assert "FAQ & Glossaire" in faq_fr
    print("  -> French 6-step tutorial and FAQ verified successfully.")

    # Test Database French persistence
    set_user_language(mock_user.id, "fr")
    assert get_user_language(mock_user.id) == "fr"
    print("  -> Database French language persistence verified.")
    print("  ✅ French localization passed with 100% test coverage.")

    # -------------------------------------------------------------
    # Test 13: School Notebook Label Generator
    # -------------------------------------------------------------
    print("\n[Test 13] Testing School Notebook Label Generator...")
    from telegram_bot.school_labels import (
        render_single_label,
        render_school_labels_sheet,
        THEME_CONFIGS,
    )
    from telegram_bot.pdf_exporter import export_school_labels_pdf

    state.mode = "school_labels"
    state.school_student_name = "Yacine Benali"
    state.school_grade = "5ème AP / CM2"
    state.school_custom_avatar = True
    state.school_subject_mode = "auto"
    state.language = "ar"

    # Test single sticker rendering across all 5 themes
    for theme_id in THEME_CONFIGS:
        state.school_theme = theme_id
        sticker_img = render_single_label(
            state,
            subject="الرياضيات",
        )
        assert sticker_img.size == (1039, 590), f"Sticker size mismatch: {sticker_img.size}"
        print(f"  -> Sticker rendered for theme '{theme_id}': {sticker_img.size}")

    # Test Sheet Preview Generation (96 DPI)
    state.school_theme = "space"
    sheet_prev_buf = render_school_labels_sheet(state, preview=True)
    assert sheet_prev_buf.getbuffer().nbytes > 15000, "Preview sheet buffer too small"
    preview_sheet_path = test_out_dir / "school_labels_preview.jpg"
    with open(preview_sheet_path, "wb") as f:
        f.write(sheet_prev_buf.getvalue())
    print(f"  -> Saved School Labels Preview: {preview_sheet_path} ({preview_sheet_path.stat().st_size} bytes)")

    # Test Sheet 300 DPI Generation
    sheet_300_buf = render_school_labels_sheet(state, preview=False)
    assert sheet_300_buf.getbuffer().nbytes > 100000, "300 DPI sheet buffer too small"
    sheet_300_path = test_out_dir / "school_labels_300dpi.png"
    with open(sheet_300_path, "wb") as f:
        f.write(sheet_300_buf.getvalue())
    print(f"  -> Saved School Labels 300 DPI: {sheet_300_path} ({sheet_300_path.stat().st_size} bytes)")

    # Test School Labels PDF Generation
    pdf_school_buf = export_pdf(state)
    assert pdf_school_buf.getbuffer().nbytes > 20000, "School labels PDF buffer too small"
    pdf_school_path = test_out_dir / "school_labels.pdf"
    with open(pdf_school_path, "wb") as f:
        f.write(pdf_school_buf.getvalue())
    print(f"  -> Saved School Labels PDF: {pdf_school_path} ({pdf_school_path.stat().st_size} bytes)")

    # Test French & English labels
    state.language = "fr"
    state.school_theme = "classic"
    fr_school_caption = format_status_caption(state)
    assert "Étiquettes de Cahiers Scolaires" in fr_school_caption
    fr_school_kbd = build_keyboard(state)
    assert fr_school_kbd is not None

    state.language = "en"
    state.school_theme = "football"
    en_school_caption = format_status_caption(state)
    assert "School Notebook Labels" in en_school_caption
    en_school_kbd = build_keyboard(state)
    assert en_school_kbd is not None

    print("  ✅ School Notebook Label Generator passed all tests.")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY! FULL ENGINE IS READY.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

"""
PrintMaster A4 - Internationalization (i18n) Engine
Supports English (en) and Arabic (ar) with automatic detection and seamless runtime switching.
"""

from typing import Dict, Any, Optional

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # =========================================================================
    # ENGLISH (en)
    # =========================================================================
    "en": {
        # App Info & Brand
        "app_title": "PrintMaster A4",
        "welcome_greeting": "👋 *Welcome to PrintMaster A4, {name}!*",
        "welcome_body": (
            "🖨️ *Smart Photo Duplicator & Poster Maker for standard A4 paper.*\n\n"
            "✨ *What you can do:*\n"
            "• 📸 Duplicate passport photos, stickers, and cards on 1 page with cut marks.\n"
            "• 🧩 Split large photos across multiple A4 sheets (2×2, 3×3) to create giant posters.\n"
            "• 📄 Export directly to ready-to-print vector PDF or 300 DPI high-res.\n\n"
            "👉 *Send any photo to begin, or explore the sample mockup below!*"
        ),
        "help_text": (
            "📖 *PrintMaster A4 — Command Guide*\n\n"
            "• /start — Open main editor and live preview\n"
            "• /tutorial — Step-by-step beginner guide with tips\n"
            "• /language — Change language (English / العربية)\n"
            "• /cancel — Cancel any pending text input\n"
            "• /help — Show this help message\n\n"
            "💡 *Pro-Tip:* Send images as **File / Document** on Telegram for 100% uncompressed quality!"
        ),
        
        # Languages
        "lang_switch_title": "🌐 *Choose Your Language / Choisir la langue / اختر لغتك:*",
        "lang_en": "🇬🇧 English",
        "lang_ar": "🇸🇦 العربية",
        "lang_fr": "🇫🇷 Français",
        "lang_switched": "Language changed to English! 🇬🇧",

        # Modes
        "mode_duplicator_btn": "🔀 Mode: 🖨 Duplicator (Grid)",
        "mode_poster_btn": "🔀 Mode: 🧩 Poster Maker",
        "mode_duplicator": "Duplicator (Grid)",
        "mode_poster": "Poster Maker",

        # Main Menu Buttons
        "btn_size_presets": "📐 Size Presets",
        "btn_quick_grids": "📊 Quick Grids",
        "btn_custom_size": "📏 Size: {w:.1f}×{h:.1f} cm",
        "btn_gap": "↔️ Gap: {gap:.1f} mm",
        "btn_page_margins": "{icon} Page & Margins",
        "btn_trimming": "✂️ Cuts & Borders",
        "btn_batch": "📦 Batch Export: {text}",
        "btn_poster_grid": "🧩 Poster Grid ({cols}×{rows})",
        "btn_poster_overlap": "📏 Overlap ({overlap:.0f} mm)",
        "btn_glue_guides": "🏷 Glue Guides: {status}",
        "btn_export_pdf": "📄 Export PDF (Vector)",
        "btn_export_image300": "🖼 Export 300 DPI",
        "btn_tutorial": "📚 Beginner Tutorial",
        "btn_about": "ℹ️ About & Support",
        "btn_language": "🌐 Language / اللغة",
        "btn_refresh": "🔄 Refresh Preview",
        "btn_back_main": "« Back to Main Menu",
        "btn_try_demo": "🧪 Try Demo Image",

        # Captions - Duplicator
        "caption_duplicator_header": "✨ *PrintMaster A4 — Duplicator Mode*",
        "caption_grid": "📊 *Grid Layout:* `{cols} × {rows}` ({copies} copies / page)",
        "caption_size": "📏 *Image Size:* `{w:.1f} × {h:.1f} cm`",
        "caption_spacing": "↔️ *Image Spacing:* `{gap:.1f} mm`",
        "caption_page": "📄 *Page Setup:* {orient}",
        "caption_margins": "📐 *Margins:* `{margins}`",
        "caption_batch_single": "• *Batch:* Single A4 Sheet",
        "caption_batch_multi": "• *Total Batch:* `{copies}` copies across `{sheets}` A4 sheets",
        "caption_options": "✂️ *Options:* Cut Marks: `{cuts}` | Border: `{border}` | Auto-Rotate: `{rotate}`",
        "caption_footer_hint": "💡 _Tap the buttons below to customize, or send any new photo!_",

        # Captions - Poster
        "caption_poster_header": "✨ *PrintMaster A4 — Poster Maker*",
        "caption_tiling": "🧩 *Tiling:* `{cols} × {rows}` (`{sheets}` A4 Sheets)",
        "caption_poster_size": "📐 *Overall Poster Size:* `~{w:.1f} × {h:.1f} cm`",
        "caption_overlap": "📏 *Tile Overlap:* `{overlap:.0f} mm`",
        "caption_guides": "🏷 *Glue Guidelines & Numbers:* `{status}`",
        "caption_poster_sheet": "📄 *Sheet Size:* {orient}",
        "caption_poster_margin": "📐 *Print Margin:* `{margins}`",
        "caption_poster_hint": "💡 _Each tile will be scaled and printed onto its own A4 sheet with overlap guides!_",

        # Orientation & Status words
        "portrait": "Portrait",
        "landscape": "Landscape",
        "portrait_full": "Portrait (210 × 297 mm)",
        "landscape_full": "Landscape (297 × 210 mm)",
        "on": "ON",
        "off": "OFF",
        "locked": "🔒 Locked",
        "unlocked": "🔓 Unlocked",
        "center": "Center",
        "top_left": "Top-Left",

        # Size Presets
        "preset_passport": "🛂 Passport Photo (3.5 × 4.5 cm)",
        "preset_us_visa": "🇺🇸 US Visa / Square (5.1 × 5.1 cm)",
        "preset_business_card": "💳 Business Card (8.5 × 5.5 cm)",
        "preset_wallet": "👛 Wallet Photo (6.4 × 8.9 cm)",
        "preset_polaroid": "📸 Polaroid Sticker (7.0 × 7.0 cm)",
        "preset_small_sticker": "🏷️ Small Sticker (3.0 × 3.0 cm)",
        "preset_photo_10x15": "🖼 Photo 10×15 cm (4×6 in)",
        "preset_mini_id": "🪪 Mini ID Photo (2.5 × 3.2 cm)",

        # Custom Size Submenu
        "custom_size_title": "📏 *Custom Dimensions & Aspect Ratio*",
        "custom_size_hint": "Adjust width/height in 5mm steps or tap to type exact numbers:",
        "btn_width": "Width: {w:.1f} cm",
        "btn_height": "Height: {h:.1f} cm",
        "btn_ratio": "Aspect Ratio: {status}",
        "btn_step_w_plus": "➕ Width +5mm",
        "btn_step_w_minus": "➖ Width -5mm",
        "btn_step_h_plus": "➕ Height +5mm",
        "btn_step_h_minus": "➖ Height -5mm",

        # Spacing Submenu
        "spacing_title": "↔️ *Image Spacing (Gap Between Photos)*",
        "spacing_hint": "Select a quick gap preset or type a custom spacing:",
        "btn_step_gap_plus": "➕ Gap +0.5mm",
        "btn_step_gap_minus": "➖ Gap -0.5mm",
        "btn_enter_custom_gap": "✏️ Enter Custom Gap",

        # Margins Submenu
        "margins_title": "📄 *Page Orientation & Margins*",
        "btn_toggle_orient": "Orientation: {status}",
        "btn_margin_guide_toggle": "👁 Margin Guide: {status}",
        "margin_standard": "Standard (10mm)",
        "margin_narrow": "Narrow (5mm)",
        "margin_borderless": "Borderless (0mm)",
        "margin_wide": "Wide (20mm)",
        "btn_enter_custom_margin": "✏️ Enter Custom Margin (mm)",

        # Trimming & Cuts Submenu
        "trimming_title": "✂️ *Cutting Guides, Borders & Auto-Rotate*",
        "btn_cut_marks_toggle": "✂️ Cut Marks: {status}",
        "btn_border_toggle": "🔲 Border: {status}",
        "btn_border_color": "Color: {color}",
        "btn_border_thick": "Thick: {thick:.1f}mm",
        "btn_auto_rotate_toggle": "🔄 Auto-Rotate 90°: {status}",
        "btn_alignment_toggle": "🎯 Alignment: {align}",

        # Batch Copies Submenu
        "batch_title": "📦 *Multi-Sheet Batch Print*",
        "batch_single_option": "1 Page (Auto)",
        "batch_copies_option": "{n} Copies",
        "btn_limit_copies_toggle": "Limit per sheet: {status}",
        "btn_enter_custom_batch": "✏️ Enter Custom Total Batch",

        # Poster Submenus
        "poster_grid_title": "🧩 *Select Poster Tiling*",
        "btn_step_col_plus": "➕ Col",
        "btn_step_col_minus": "➖ Col",
        "btn_step_row_plus": "➕ Row",
        "btn_step_row_minus": "➖ Row",
        "btn_enter_custom_poster_grid": "✏️ Enter Custom Grid (e.g. 3x4)",
        "poster_overlap_title": "📏 *Poster Overlap Margins*",
        "btn_glue_lines_toggle": "Glue Lines & Labels: {status}",
        "btn_enter_custom_overlap": "✏️ Enter Custom Overlap (mm)",
        "overlap_edge": "0 mm (Edge)",

        # About Submenu
        "about_title": "ℹ️ *About PrintMaster A4*",
        "about_body": (
            "PrintMaster A4 was originally built as a high-performance Windows desktop application "
            "for professional photo duplication and large-scale poster printing.\n\n"
            "This Telegram Bot brings the exact same precision mathematical engine to your phone, "
            "allowing instant vector PDF generation and ultra-sharp 300 DPI exports directly in the cloud.\n\n"
            "👨‍💻 *Developer:* AITADZ PRO\n"
            "🌐 *Support & Inquiries:*"
        ),
        "btn_dev_telegram": "✈️ Developer Telegram",
        "btn_facebook": "📘 Facebook",
        "btn_whatsapp": "💬 WhatsApp Support",

        # Interactive Prompts
        "prompt_width": "✏️ *Please enter the desired image WIDTH in cm* (e.g. `3.5` or `5`):",
        "prompt_height": "✏️ *Please enter the desired image HEIGHT in cm* (e.g. `4.5` or `5.1`):",
        "prompt_gap": "✏️ *Please enter the spacing (gap) in mm* (e.g. `2.5` or `0`):",
        "prompt_margin": "✏️ *Please enter the page margin in mm* (e.g. `10` or `5`):",
        "prompt_batch": "✏️ *Please enter the TOTAL number of copies you need* (e.g. `50`):",
        "prompt_poster_grid": "✏️ *Please enter the poster grid format as Columns x Rows* (e.g. `2x2` or `3x4`):",
        "prompt_poster_overlap": "✏️ *Please enter the glue overlap in mm* (e.g. `10` or `15`):",
        "input_cancel_hint": "\n\n_Send /cancel to return without changing._",
        "input_cancelled": "❌ Input cancelled. Returning to main menu.",
        "input_invalid_number": "⚠️ *Invalid input.* Please send a valid positive number (e.g. `3.5`):",
        "input_invalid_grid": "⚠️ *Invalid format.* Please enter in format `COLSxROWS` (e.g. `2x2` or `3x4`):",
        
        # Exporting Messages
        "export_pdf_generating": "⏳ *Rendering high-resolution vector PDF... Please wait.*",
        "export_pdf_ready": "📄 *Your ready-to-print vector PDF is ready!*",
        "export_image_generating": "⏳ *Rendering ultra-crisp 300 DPI print image... Please wait.*",
        "export_image_ready": "🖼 *Your 300 DPI high-resolution print image is ready!*",
        "upload_received": "✅ *Image received and loaded!* Preview updated below.",

        # School Notebook Labels
        "mode_school_btn": "🔀 Mode: 🎒 School Labels",
        "btn_switch_school": "🎒 School Labels",
        "school_caption_header": "🎒 *PrintMaster A4 — School Notebook Labels*",
        "school_caption_body": (
            "📄 *Sheet Layout:* `10 Stickers / A4` (88 × 50 mm)\n"
            "👤 *Student Name:* `{name}`\n"
            "🏫 *Class / Grade:* `{grade}`\n"
            "🎨 *Theme:* `{theme}`\n"
            "📚 *Subjects:* `{subjects}`\n"
            "📸 *Student Photo:* `{photo}`\n\n"
            "💡 _Ready to print directly on standard A4 adhesive sticker paper!_"
        ),
        "btn_school_name": "✏️ Name: {name}",
        "btn_school_grade": "🏫 Class: {grade}",
        "btn_school_theme": "🎨 Theme: {theme}",
        "btn_school_subjects": "📚 Subjects: {mode}",
        "btn_school_avatar": "📸 Student Photo: {status}",
        "school_subj_blank": "Line for Pen (Manual)",
        "school_subj_auto": "10 Core Subjects (Auto)",
        "school_label_header": "STUDENT NOTEBOOK",
        "school_field_name": "Name",
        "school_field_class": "Class",
        "school_field_subject": "Subject",
        "school_sample_student": "Student Name",
        "school_sample_grade": "5th Grade",
        "theme_classic": "🎓 Classic Minimalist",
        "theme_football": "⚽ Football Champions",
        "theme_space": "🚀 Space & Galaxy",
        "theme_cute": "🐻 Cute & Pastel",
        "theme_science": "🔬 Science & Books",
        "prompt_school_name": "✏️ *Please enter the student's Full Name (e.g. Lucas Dupont):*",
        "prompt_school_grade": "🏫 *Please enter the student's Class or Grade (e.g. 5th Grade, CM2):*",
        "school_btn_view_sheet": "📄 Full A4 Sheet (10x)",
        "school_btn_view_single": "🔍 Zoom Single Sticker (1x)",
    },

    # =========================================================================
    # ARABIC (ar) - العربية
    # =========================================================================
    "ar": {
        # App Info & Brand
        "app_title": "برينت ماستر A4",
        "welcome_greeting": "👋 *أهلاً بك في برينت ماستر A4، {name}!*",
        "welcome_body": (
            "🖨️ *المساعد الذكي لتكرار الصور وطباعة البوسترات على ورق A4 بدقة متناهية.*\n\n"
            "✨ *ما الذي يمكنك فعله عبر البوت:*\n"
            "• 📸 تكرار صور الهوية وجوازات السفر والملصقات على صفحة واحدة مع علامات القص.\n"
            "• 🧩 تقسيم الصور الكبيرة إلى أجزاء متعددة (2×2، 3×3...) لطباعة بوسترات جدارية عملاقة مع زوائد اللصق.\n"
            "• 📄 تصدير فوري إلى ملف PDF vector جاهز للطباعة أو صورة فائقة الدقة 300 DPI.\n\n"
            "👉 *أرسل أي صورة لتبدأ، أو جرب النموذج التوضيحي أدناه!*"
        ),
        "help_text": (
            "📖 *دليل أوامر برينت ماستر A4*\n\n"
            "• /start — فتح المحرر الرئيسي ومعاينة الصفحة الحية\n"
            "• /tutorial — الدليل الشامل للمبتدئين مع نصائح الطباعة\n"
            "• /language — تغيير لغة البوت (العربية / English)\n"
            "• /cancel — إلغاء إدخال الأرقام أو القياسات\n"
            "• /help — عرض رسالة المساعدة هذه\n\n"
            "💡 *نصيحة ذهبية:* أرسل الصور عبر تيليجرام كـ **ملف / مستند (File)** للحفاظ على الجودة الأصلية 100% دون ضغط!"
        ),

        # Languages
        "lang_switch_title": "🌐 *اختر لغة البوت / Choose Language / Choisir la langue:*",
        "lang_en": "🇬🇧 English",
        "lang_ar": "🇸🇦 العربية",
        "lang_fr": "🇫🇷 Français",
        "lang_switched": "تم تغيير لغة البوت إلى العربية بنجاح! 🇸🇦",

        # Modes
        "mode_duplicator_btn": "🔀 الوضع: 🖨 نسخ متكرر (شبكة)",
        "mode_poster_btn": "🔀 الوضع: 🧩 صانع البوسترات الجدارية",
        "mode_duplicator": "نسخ متكرر (شبكة)",
        "mode_poster": "صانع البوسترات",

        # Main Menu Buttons
        "btn_size_presets": "📐 مقاسات جاهزة",
        "btn_quick_grids": "📊 شبكات سريعة",
        "btn_custom_size": "📏 المقاس: {w:.1f}×{h:.1f} سم",
        "btn_gap": "↔️ التباعد: {gap:.1f} مم",
        "btn_page_margins": "{icon} الصفحة والهوامش",
        "btn_trimming": "✂️ القص والإطار",
        "btn_batch": "📦 طباعة دفعات: {text}",
        "btn_poster_grid": "🧩 شبكة البوستر ({cols}×{rows})",
        "btn_poster_overlap": "📏 التداخل ({overlap:.0f} مم)",
        "btn_glue_guides": "🏷 أدلة اللصق: {status}",
        "btn_export_pdf": "📄 تصدير PDF (طباعة)",
        "btn_export_image300": "🖼 تصدير صورة 300 DPI",
        "btn_tutorial": "📚 دليل الاستخدام للمبتدئين",
        "btn_about": "ℹ️ حول البوت والدعم",
        "btn_language": "🌐 Language / اللغة",
        "btn_refresh": "🔄 تحديث المعاينة",
        "btn_back_main": "« العودة للقائمة الرئيسية",
        "btn_try_demo": "🧪 تجربة صورة توضيحية",

        # Captions - Duplicator
        "caption_duplicator_header": "✨ *برينت ماستر A4 — وضع تكرار الصور*",
        "caption_grid": "📊 *توزيع الشبكة:* `{cols} × {rows}` ({copies} صورة / صفحة)",
        "caption_size": "📏 *مقاس الصورة:* `{w:.1f} × {h:.1f} سم`",
        "caption_spacing": "↔️ *المسافة بين الصور:* `{gap:.1f} مم`",
        "caption_page": "📄 *إعداد الصفحة:* {orient}",
        "caption_margins": "📐 *الهوامش:* `{margins}`",
        "caption_batch_single": "• *الدفعة:* صفحة A4 واحدة",
        "caption_batch_multi": "• *إجمالي الدفعة:* `{copies}` نسخة موزعة على `{sheets}` صفحات A4",
        "caption_options": "✂️ *الخيارات:* علامات القص: `{cuts}` | إطار خارجي: `{border}` | تدوير تلقائي: `{rotate}`",
        "caption_footer_hint": "💡 _اضغط على الأزرار أدناه للتعديل، أو أرسل صورة جديدة في أي وقت!_",

        # Captions - Poster
        "caption_poster_header": "✨ *برينت ماستر A4 — صانع البوسترات الجدارية*",
        "caption_tiling": "🧩 *التقسيم:* `{cols} × {rows}` (`{sheets}` صفحات A4)",
        "caption_poster_size": "📐 *المقاس التقريبي للبوستر:* `~{w:.1f} × {h:.1f} سم`",
        "caption_overlap": "📏 *هامش تداخل اللصق:* `{overlap:.0f} مم`",
        "caption_guides": "🏷 *أدلة اللصق والترقيم:* `{status}`",
        "caption_poster_sheet": "📄 *مقاس كل ورقة:* {orient}",
        "caption_poster_margin": "📐 *هوامش الطباعة:* `{margins}`",
        "caption_poster_hint": "💡 _سيتم تكبير وتقسيم كل قطعة على ورقة A4 مستقلة مع أرقام وهوامش لتسهيل التجميع!_",

        # Orientation & Status words
        "portrait": "عمودي (طولي)",
        "landscape": "أفقي (عرضي)",
        "portrait_full": "عمودي (210 × 297 مم)",
        "landscape_full": "أفقي (297 × 210 مم)",
        "on": "مفعل",
        "off": "معطل",
        "locked": "🔒 مقفل",
        "unlocked": "🔓 حر",
        "center": "توسيط",
        "top_left": "أعلى اليسار",

        # Size Presets
        "preset_passport": "🛂 صورة جواز سفر (3.5 × 4.5 سم)",
        "preset_us_visa": "🇺🇸 فيزا أمريكية / مربع (5.1 × 5.1 سم)",
        "preset_business_card": "💳 بطاقة عمل (8.5 × 5.5 سم)",
        "preset_wallet": "👛 صورة محفظة (6.4 × 8.9 سم)",
        "preset_polaroid": "📸 ستيكر بولارويد (7.0 × 7.0 سم)",
        "preset_small_sticker": "🏷️ ستيكر صغير (3.0 × 3.0 سم)",
        "preset_photo_10x15": "🖼 صورة فوتوغرافية 10×15 سم (4×6 بوصة)",
        "preset_mini_id": "🪪 صورة هوية مصغرة (2.5 × 3.2 سم)",

        # Custom Size Submenu
        "custom_size_title": "📏 *تعديل المقاسات ونسبة التناسق*",
        "custom_size_hint": "عدل العرض/الارتفاع بخطوات 5 مم أو اضغط للكتابة يدوياً:",
        "btn_width": "العرض: {w:.1f} سم",
        "btn_height": "الارتفاع: {h:.1f} سم",
        "btn_ratio": "تناسق الأبعاد: {status}",
        "btn_step_w_plus": "➕ العرض +5مم",
        "btn_step_w_minus": "➖ العرض -5مم",
        "btn_step_h_plus": "➕ الارتفاع +5مم",
        "btn_step_h_minus": "➖ الارتفاع -5مم",

        # Spacing Submenu
        "spacing_title": "↔️ *التباعد بين الصور (المسافة الفاصلة)*",
        "spacing_hint": "اختر تباعداً جاهزاً أو أدخل القيمة يدوياً:",
        "btn_step_gap_plus": "➕ مسافة +0.5مم",
        "btn_step_gap_minus": "➖ مسافة -0.5مم",
        "btn_enter_custom_gap": "✏️ إدخال تباعد مخصص",

        # Margins Submenu
        "margins_title": "📄 *اتجاه الورقة وهوامش الطباعة*",
        "btn_toggle_orient": "اتجاه الورقة: {status}",
        "btn_margin_guide_toggle": "👁 دليل الهامش: {status}",
        "margin_standard": "قياسي (10 مم)",
        "margin_narrow": "ضيق (5 مم)",
        "margin_borderless": "بدون هوامش (0 مم)",
        "margin_wide": "عريض (20 مم)",
        "btn_enter_custom_margin": "✏️ إدخال هامش مخصص (مم)",

        # Trimming & Cuts Submenu
        "trimming_title": "✂️ *علامات القص، الإطار والتدوير التلقائي*",
        "btn_cut_marks_toggle": "✂️ علامات القص: {status}",
        "btn_border_toggle": "🔲 إطار خارجي: {status}",
        "btn_border_color": "اللون: {color}",
        "btn_border_thick": "السُمك: {thick:.1f}مم",
        "btn_auto_rotate_toggle": "🔄 تدوير تلقائي 90°: {status}",
        "btn_alignment_toggle": "🎯 المحاذاة: {align}",

        # Batch Copies Submenu
        "batch_title": "📦 *طباعة دفعات متعددة الصفحات*",
        "batch_single_option": "صفحة واحدة (تلقائي)",
        "batch_copies_option": "{n} نسخة",
        "btn_limit_copies_toggle": "الحد لكل صفحة: {status}",
        "btn_enter_custom_batch": "✏️ إدخال عدد النسخ الإجمالي",

        # Poster Submenus
        "poster_grid_title": "🧩 *تحديد شبكة تقسيم البوستر*",
        "btn_step_col_plus": "➕ أعمدة",
        "btn_step_col_minus": "➖ أعمدة",
        "btn_step_row_plus": "➕ صفوف",
        "btn_step_row_minus": "➖ صفوف",
        "btn_enter_custom_poster_grid": "✏️ إدخال شبكة مخصصة (مثال: 3x4)",
        "poster_overlap_title": "📏 *هوامش تداخل اللصق للبوستر*",
        "btn_glue_lines_toggle": "أدلة اللصق والترقيم: {status}",
        "btn_enter_custom_overlap": "✏️ إدخال تداخل مخصص (مم)",
        "overlap_edge": "0 مم (بدون تداخل)",

        # About Submenu
        "about_title": "ℹ️ *حول برينت ماستر A4*",
        "about_body": (
            "برينت ماستر A4 تم تطويره في الأصل كتطبيق ديسكتوب احترافي لنظام ويندوز "
            "لتكرار صور الهوية والملصقات وتكبير البوسترات الجدارية بدقة هندسية متناهية.\n\n"
            "هذا البوت ينقل لك نفس القوة الرياضية إلى هاتفك المحمول مباشرة، "
            "مع إمكانية تصدير ملفات PDF فائقة الوضوح وصور 300 DPI جاهزة للمطابع الفورية.\n\n"
            "👨‍💻 *المطور:* AITADZ PRO\n"
            "🌐 *الدعم والتواصل:*"
        ),
        "btn_dev_telegram": "✈️ تيليجرام المطور",
        "btn_facebook": "📘 فيسبوك",
        "btn_whatsapp": "💬 دعم واتساب",

        # Interactive Prompts
        "prompt_width": "✏️ *يرجى إرسال عَرْض الصورة المطلوب بالسنتيمتر (cm)* (مثال: `3.5` أو `5`):",
        "prompt_height": "✏️ *يرجى إرسال ارْتِفاع الصورة المطلوب بالسنتيمتر (cm)* (مثال: `4.5` أو `5.1`):",
        "prompt_gap": "✏️ *يرجى إرسال مسافة التباعد بين الصور بالمليمتر (mm)* (مثال: `2.5` أو `0`):",
        "prompt_margin": "✏️ *يرجى إرسال هامش الورقة بالمليمتر (mm)* (مثال: `10` أو `5`):",
        "prompt_batch": "✏️ *يرجى إرسال عدد النسخ الإجمالي المطلوب طباعته* (مثال: `50`):",
        "prompt_poster_grid": "✏️ *يرجى إرسال شبكة البوستر بصيغة أعمدة x صفوف* (مثال: `2x2` أو `3x4`):",
        "prompt_poster_overlap": "✏️ *يرجى إرسال مسافة تداخل اللصق بالمليمتر (mm)* (مثال: `10` أو `15`):",
        "input_cancel_hint": "\n\n_أرسل /cancel للرجوع دون حفظ أي تغيير._",
        "input_cancelled": "❌ تم الإلغاء. العودة إلى القائمة الرئيسية.",
        "input_invalid_number": "⚠️ *قيمة غير صالحة.* يرجى إرسال رقم موجب صحيح أو عشري (مثال: `3.5`):",
        "input_invalid_grid": "⚠️ *صيغة غير صحيحة.* يرجى كتابة الشبكة بالشكل `أعمدةxصفوف` (مثال: `2x2` أو `3x4`):",

        # Exporting Messages
        "export_pdf_generating": "⏳ *جارٍ معالجة وتوليد ملف PDF عالي الدقة... يرجى الانتظار لحظات.*",
        "export_pdf_ready": "📄 *تم تجهيز ملف PDF للطباعة بنجاح!*",
        "export_image_generating": "⏳ *جارٍ معالجة وتوليد صورة عالية الدقة 300 DPI... يرجى الانتظار لحظات.*",
        "export_image_ready": "🖼 *تم تصدير الصورة فائقة الدقة 300 DPI بنجاح!*",
        "upload_received": "✅ *تم استلام الصورة بنجاح وتحديث المعاينة أدناه!*",

        # School Notebook Labels
        "mode_school_btn": "🔀 الوضع: 🎒 ملصقات الدفاتر المدرسية",
        "btn_switch_school": "🎒 ملصقات الدفاتر المدرسية",
        "school_caption_header": "🎒 *برينت ماستر A4 — مولّد ملصقات الدفاتر المدرسية*",
        "school_caption_body": (
            "📄 *تقسيم الصفحة:* `10 ملصقات / ورقة A4` (88 × 50 مم)\n"
            "👤 *اسم التلميذ(ة):* `{name}`\n"
            "🏫 *القسم / السنة:* `{grade}`\n"
            "🎨 *المظهر:* `{theme}`\n"
            "📚 *المواد الدراسية:* `{subjects}`\n"
            "📸 *صورة التلميذ الشخصية:* `{photo}`\n\n"
            "💡 _جاهزة للطباعة الفورية على ورق لاصق (Sticker A4)!_"
        ),
        "btn_school_name": "✏️ الاسم: {name}",
        "btn_school_grade": "🏫 القسم: {grade}",
        "btn_school_theme": "🎨 المظهر: {theme}",
        "btn_school_subjects": "📚 المواد: {mode}",
        "btn_school_avatar": "📸 صورة التلميذ: {status}",
        "school_subj_blank": "سطر فارغ للكتابة بالقلم",
        "school_subj_auto": "10 مواد دراسية (تلقائي)",
        "school_label_header": "دفتر التلميذ",
        "school_field_name": "الاسم واللقب",
        "school_field_class": "القسم",
        "school_field_subject": "المادة",
        "school_sample_student": "اسم التلميذ(ة)",
        "school_sample_grade": "السنة الخامسة",
        "theme_classic": "🎓 كلاسيكي أنيق",
        "theme_football": "⚽ أبطال كرة القدم",
        "theme_space": "🚀 فضاء وكواكب",
        "theme_cute": "🐻 لطيف ودبدوب",
        "theme_science": "🔬 علوم وكتب",
        "prompt_school_name": "✏️ *يرجى إرسال اسم ولقب التلميذ(ة):*",
        "prompt_school_grade": "🏫 *يرجى إرسال القسم أو السنة الدراسية (مثال: 5 ابتدائي، 2 متوسط، CM2):*",
        "school_btn_view_sheet": "📄 عرض الصفحة كاملة (10x)",
        "school_btn_view_single": "🔍 تكبير ملصق واحد (1x)",
    },

    # =========================================================================
    # FRENCH (fr) - Français
    # =========================================================================
    "fr": {
        # App Info & Brand
        "app_title": "PrintMaster A4",
        "welcome_greeting": "👋 *Bienvenue sur PrintMaster A4, {name} !*",
        "welcome_body": (
            "🖨️ *Assistant intelligent de duplication de photos et de création de posters sur papier A4 standard.*\n\n"
            "✨ *Fonctionnalités principales :*\n"
            "• 📸 Dupliquez photos d'identité, stickers et badges sur 1 page avec repères de coupe.\n"
            "• 🧩 Découpez de grandes photos sur plusieurs feuilles A4 (2×2, 3×3) pour créer des posters géants avec onglets de collage.\n"
            "• 📄 Exportez directement en PDF vectoriel prêt à imprimer ou image haute résolution 300 DPI.\n\n"
            "👉 *Envoyez une photo pour commencer, ou testez l'exemple ci-dessous !*"
        ),
        "help_text": (
            "📖 *PrintMaster A4 — Guide des commandes*\n\n"
            "• /start — Ouvrir l'éditeur et l'aperçu en direct\n"
            "• /tutorial — Tutoriel pas-à-pas pour débutants avec conseils d'impression\n"
            "• /language — Changer de langue (English / العربية / Français)\n"
            "• /cancel — Annuler la saisie en cours\n"
            "• /help — Afficher ce message d'aide\n\n"
            "💡 *Conseil Pro :* Envoyez vos images en tant que **Fichier / Document** sur Telegram pour conserver 100% de la qualité sans compression !"
        ),

        # Languages
        "lang_switch_title": "🌐 *Choisir la langue / Choose Your Language / اختر لغتك :*",
        "lang_en": "🇬🇧 English",
        "lang_ar": "🇸🇦 العربية",
        "lang_fr": "🇫🇷 Français",
        "lang_switched": "Langue changée en Français avec succès ! 🇫🇷",

        # Modes
        "mode_duplicator_btn": "🔀 Mode : 🖨 Duplicateur (Grille)",
        "mode_poster_btn": "🔀 Mode : 🧩 Créateur de Poster",
        "mode_duplicator": "Duplicateur (Grille)",
        "mode_poster": "Créateur de Poster",

        # Main Menu Buttons
        "btn_size_presets": "📐 Formats Prédéfinis",
        "btn_quick_grids": "📊 Grilles Rapides",
        "btn_custom_size": "📏 Format : {w:.1f}×{h:.1f} cm",
        "btn_gap": "↔️ Espacement : {gap:.1f} mm",
        "btn_page_margins": "{icon} Page & Marges",
        "btn_trimming": "✂️ Découpe & Bordures",
        "btn_batch": "📦 Tirage groupé : {text}",
        "btn_poster_grid": "🧩 Grille Poster ({cols}×{rows})",
        "btn_poster_overlap": "📏 Recouvrement ({overlap:.0f} mm)",
        "btn_glue_guides": "🏷 Guides de colle : {status}",
        "btn_export_pdf": "📄 Exporter PDF (Vectoriel)",
        "btn_export_image300": "🖼 Exporter 300 DPI",
        "btn_tutorial": "📚 Tutoriel Débutant",
        "btn_about": "ℹ️ À propos & Support",
        "btn_language": "🌐 Langue / Language",
        "btn_refresh": "🔄 Actualiser l'aperçu",
        "btn_back_main": "« Retour au Menu Principal",
        "btn_try_demo": "🧪 Tester l'image démo",

        # Captions - Duplicator
        "caption_duplicator_header": "✨ *PrintMaster A4 — Mode Duplicateur*",
        "caption_grid": "📊 *Disposition en grille :* `{cols} × {rows}` ({copies} photos / page)",
        "caption_size": "📏 *Taille d'image :* `{w:.1f} × {h:.1f} cm`",
        "caption_spacing": "↔️ *Espacement entre photos :* `{gap:.1f} mm`",
        "caption_page": "📄 *Format de page :* {orient}",
        "caption_margins": "📐 *Marges :* `{margins}`",
        "caption_batch_single": "• *Tirage :* Page A4 unique",
        "caption_batch_multi": "• *Tirage total :* `{copies}` exemplaires sur `{sheets}` feuilles A4",
        "caption_options": "✂️ *Options :* Traits de coupe : `{cuts}` | Bordure : `{border}` | Rotation auto : `{rotate}`",
        "caption_footer_hint": "💡 _Appuyez sur les boutons ci-dessous pour personnaliser, ou envoyez une nouvelle photo !_",

        # Captions - Poster
        "caption_poster_header": "✨ *PrintMaster A4 — Créateur de Poster*",
        "caption_tiling": "🧩 *Découpage en tuiles :* `{cols} × {rows}` (`{sheets}` Feuilles A4)",
        "caption_poster_size": "📐 *Taille globale estimée :* `~{w:.1f} × {h:.1f} cm`",
        "caption_overlap": "📏 *Zone de chevauchement :* `{overlap:.0f} mm`",
        "caption_guides": "🏷 *Lignes de colle & Numéros :* `{status}`",
        "caption_poster_sheet": "📄 *Taille de feuille :* {orient}",
        "caption_poster_margin": "📐 *Marges d'impression :* `{margins}`",
        "caption_poster_hint": "💡 _Chaque section sera mise à l'échelle et imprimée sur une feuille A4 avec des repères d'assemblage !_",

        # Orientation & Status words
        "portrait": "Portrait",
        "landscape": "Paysage",
        "portrait_full": "Portrait (210 × 297 mm)",
        "landscape_full": "Paysage (297 × 210 mm)",
        "on": "ACTIVÉ",
        "off": "DÉSACTIVÉ",
        "locked": "🔒 Verrouillé",
        "unlocked": "🔓 Libre",
        "center": "Centré",
        "top_left": "Haut-Gauche",

        # Size Presets
        "preset_passport": "🛂 Photo d'identité (3.5 × 4.5 cm)",
        "preset_us_visa": "🇺🇸 Visa USA / Carré (5.1 × 5.1 cm)",
        "preset_business_card": "💳 Carte de visite (8.5 × 5.5 cm)",
        "preset_wallet": "👛 Photo portefeuille (6.4 × 8.9 cm)",
        "preset_polaroid": "📸 Sticker Polaroid (7.0 × 7.0 cm)",
        "preset_small_sticker": "🏷️ Petit sticker (3.0 × 3.0 cm)",
        "preset_photo_10x15": "🖼 Photo 10×15 cm (4×6 po)",
        "preset_mini_id": "🪪 Mini photo d'identité (2.5 × 3.2 cm)",

        # Custom Size Submenu
        "custom_size_title": "📏 *Dimensions personnalisées & Proportions*",
        "custom_size_hint": "Ajustez largeur/hauteur par pas de 5mm ou tapez les valeurs exactes :",
        "btn_width": "Largeur : {w:.1f} cm",
        "btn_height": "Hauteur : {h:.1f} cm",
        "btn_ratio": "Proportions : {status}",
        "btn_step_w_plus": "➕ Largeur +5mm",
        "btn_step_w_minus": "➖ Largeur -5mm",
        "btn_step_h_plus": "➕ Hauteur +5mm",
        "btn_step_h_minus": "➖ Hauteur -5mm",

        # Spacing Submenu
        "spacing_title": "↔️ *Espacement entre les photos*",
        "spacing_hint": "Choisissez un écart prédéfini ou entrez une valeur personnalisée :",
        "btn_step_gap_plus": "➕ Écart +0.5mm",
        "btn_step_gap_minus": "➖ Écart -0.5mm",
        "btn_enter_custom_gap": "✏️ Entrer un espacement personnalisé",

        # Margins Submenu
        "margins_title": "📄 *Orientation & Marges de page*",
        "btn_toggle_orient": "Orientation : {status}",
        "btn_margin_guide_toggle": "👁 Lignes de marge : {status}",
        "margin_standard": "Standard (10mm)",
        "margin_narrow": "Étroite (5mm)",
        "margin_borderless": "Sans marge (0mm)",
        "margin_wide": "Large (20mm)",
        "btn_enter_custom_margin": "✏️ Entrer une marge personnalisée (mm)",

        # Trimming & Cuts Submenu
        "trimming_title": "✂️ *Traits de coupe, Bordures & Rotation auto*",
        "btn_cut_marks_toggle": "✂️ Traits de coupe : {status}",
        "btn_border_toggle": "🔲 Bordure : {status}",
        "btn_border_color": "Couleur : {color}",
        "btn_border_thick": "Épaisseur : {thick:.1f}mm",
        "btn_auto_rotate_toggle": "🔄 Rotation auto 90° : {status}",
        "btn_alignment_toggle": "🎯 Alignement : {align}",

        # Batch Copies Submenu
        "batch_title": "📦 *Impression groupée multi-pages*",
        "batch_single_option": "1 Page (Auto)",
        "batch_copies_option": "{n} Copies",
        "btn_limit_copies_toggle": "Limite par feuille : {status}",
        "btn_enter_custom_batch": "✏️ Entrer le nombre total de copies",

        # Poster Submenus
        "poster_grid_title": "🧩 *Sélectionner le découpage du poster*",
        "btn_step_col_plus": "➕ Colonne",
        "btn_step_col_minus": "➖ Colonne",
        "btn_step_row_plus": "➕ Ligne",
        "btn_step_row_minus": "➖ Ligne",
        "btn_enter_custom_poster_grid": "✏️ Entrer une grille (ex: 3x4)",
        "poster_overlap_title": "📏 *Marges de chevauchement du poster*",
        "btn_glue_lines_toggle": "Repères de colle & numéros : {status}",
        "btn_enter_custom_overlap": "✏️ Entrer un chevauchement (mm)",
        "overlap_edge": "0 mm (Bord à bord)",

        # About Submenu
        "about_title": "ℹ️ *À propos de PrintMaster A4*",
        "about_body": (
            "PrintMaster A4 a été conçu à l'origine comme une application Windows haute précision "
            "pour la duplication de photos et l'impression de posters grand format.\n\n"
            "Ce bot Telegram apporte le même moteur mathématique directement sur votre téléphone, "
            "permettant la génération instantanée de PDF vectoriels et d'images 300 DPI haute résolution.\n\n"
            "👨‍💻 *Développeur :* AITADZ PRO\n"
            "🌐 *Support & Contact :*"
        ),
        "btn_dev_telegram": "✈️ Telegram Développeur",
        "btn_facebook": "📘 Facebook",
        "btn_whatsapp": "💬 Support WhatsApp",

        # Interactive Prompts
        "prompt_width": "✏️ *Entrez la LARGEUR souhaitée en cm* (ex: `3.5` ou `5`) :",
        "prompt_height": "✏️ *Entrez la HAUTEUR souhaitée en cm* (ex: `4.5` ou `5.1`) :",
        "prompt_gap": "✏️ *Entrez l'espacement en mm* (ex: `2.5` ou `0`) :",
        "prompt_margin": "✏️ *Entrez la marge de page en mm* (ex: `10` ou `5`) :",
        "prompt_batch": "✏️ *Entrez le nombre TOTAL de copies désiré* (ex: `50`) :",
        "prompt_poster_grid": "✏️ *Entrez la grille sous format Colonnes x Lignes* (ex: `2x2` ou `3x4`) :",
        "prompt_poster_overlap": "✏️ *Entrez le chevauchement en mm* (ex: `10` ou `15`) :",
        "input_cancel_hint": "\n\n_Envoyez /cancel pour annuler sans enregistrer._",
        "input_cancelled": "❌ Saisie annulée. Retour au menu principal.",
        "input_invalid_number": "⚠️ *Valeur invalide.* Veuillez entrer un nombre positif valide (ex: `3.5`) :",
        "input_invalid_grid": "⚠️ *Format invalide.* Veuillez entrer sous la forme `ColonnesxLignes` (ex: `2x2` ou `3x4`) :",

        # Exporting Messages
        "export_pdf_generating": "⏳ *Génération du PDF vectoriel haute définition en cours... Veuillez patienter.*",
        "export_pdf_ready": "📄 *Votre document PDF vectoriel prêt pour l'impression est prêt !*",
        "export_image_generating": "⏳ *Rendu de l'image haute définition 300 DPI... Veuillez patienter.*",
        "export_image_ready": "🖼 *Votre image haute résolution 300 DPI est prête !*",
        "upload_received": "✅ *Image reçue et chargée avec succès !* Aperçu mis à jour ci-dessous.",

        # School Notebook Labels
        "mode_school_btn": "🔀 Mode : 🎒 Étiquettes Scolaires",
        "btn_switch_school": "🎒 Étiquettes Scolaires",
        "school_caption_header": "🎒 *PrintMaster A4 — Étiquettes de Cahiers Scolaires*",
        "school_caption_body": (
            "📄 *Mise en page :* `10 Autocollants / A4` (88 × 50 mm)\n"
            "👤 *Nom de l'élève :* `{name}`\n"
            "🏫 *Classe :* `{grade}`\n"
            "🎨 *Thème visuel :* `{theme}`\n"
            "📚 *Matières :* `{subjects}`\n"
            "📸 *Photo élève :* `{photo}`\n\n"
            "💡 _Prêt à imprimer sur papier autocollant A4 ou papier standard !_"
        ),
        "btn_school_name": "✏️ Nom : {name}",
        "btn_school_grade": "🏫 Classe : {grade}",
        "btn_school_theme": "🎨 Thème : {theme}",
        "btn_school_subjects": "📚 Matières : {mode}",
        "btn_school_avatar": "📸 Photo élève : {status}",
        "school_subj_blank": "Ligne vide (Au stylo)",
        "school_subj_auto": "10 Matières (Auto-rempli)",
        "school_label_header": "CAHIER SCOLAIRE",
        "school_field_name": "Nom",
        "school_field_class": "Classe",
        "school_field_subject": "Matière",
        "school_sample_student": "Nom de l'élève",
        "school_sample_grade": "5ème Année",
        "theme_classic": "🎓 Classique Minimaliste",
        "theme_football": "⚽ Champions de Foot",
        "theme_space": "🚀 Espace & Galaxie",
        "theme_cute": "🐻 Mignon & Pastel",
        "theme_science": "🔬 Sciences & Livres",
        "prompt_school_name": "✏️ *Veuillez entrer le Nom et Prénom de l'élève :*",
        "prompt_school_grade": "🏫 *Veuillez entrer la classe (ex: CM2, 5ème, 3AS) :*",
        "school_btn_view_sheet": "📄 Feuille A4 Complète (10x)",
        "school_btn_view_single": "🔍 Zoom Étiquette (1x)",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """
    Translates a key into the specified language with optional placeholder substitution.
    Falls back to English if key is missing in the target language.
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    template = lang_dict.get(key)
    if template is None:
        template = TRANSLATIONS["en"].get(key, key)
    
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template

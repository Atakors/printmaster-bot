"""
PrintMaster A4 - Telegram Bot Handlers
Processes commands, media uploads, interactive inline buttons, and custom inputs.
"""

import os
import io
import re
import shutil
import logging
from typing import Dict, Any, Optional
from PIL import Image

from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .models import PrintMasterState
from .layout_engine import (
    STANDARD_PRESETS,
    apply_grid_fit,
    calculate_duplicator_layout,
    calculate_poster_layout,
)
from .renderer import render_preview_image, render_300dpi_image
from .pdf_exporter import export_pdf
from .keyboards import build_keyboard
from .config import TEMP_DIR, DEFAULT_SAMPLE_IMAGE, ADMIN_ID
from .tutorial import get_tutorial_step, get_tutorial_faq
from .i18n import t
from .database import (
    init_db,
    record_user_interaction,
    record_upload,
    record_export,
    get_overview_stats,
    get_top_users,
    get_recent_activity,
    export_users_csv,
    set_user_language,
    get_user_language,
)

logger = logging.getLogger(__name__)

# Initialize database tables
init_db()

# In-memory dictionary of user states: user_id -> PrintMasterState
USER_SESSIONS: Dict[int, PrintMasterState] = {}


def get_user_state(user_id: int, chat_id: int, user: Optional[Any] = None) -> PrintMasterState:
    """Retrieves or initializes session state for a user, maintaining language preference."""
    if user_id not in USER_SESSIONS:
        state = PrintMasterState(user_id=user_id, chat_id=chat_id)
        # Determine language from DB or Telegram user locale
        db_lang = get_user_language(user_id)
        if db_lang:
            state.language = db_lang
        elif user and getattr(user, "language_code", None):
            code = str(user.language_code).lower()
            if code.startswith("ar"):
                state.language = "ar"
                set_user_language(user_id, "ar")
            elif code.startswith("fr"):
                state.language = "fr"
                set_user_language(user_id, "fr")

        # Initialize with sample image if available
        if DEFAULT_SAMPLE_IMAGE.exists():
            dest = TEMP_DIR / f"init_{user_id}.jpg"
            shutil.copy(DEFAULT_SAMPLE_IMAGE, dest)
            state.image_path = str(dest)
            try:
                with Image.open(dest) as img:
                    state.image_orig_width, state.image_orig_height = img.size
                    state.aspect_ratio = float(state.image_orig_width) / max(1, state.image_orig_height)
                    state.image_height_mm = state.image_width_mm / max(0.01, state.aspect_ratio)
            except Exception:
                pass
        USER_SESSIONS[user_id] = state
    return USER_SESSIONS[user_id]


def render_current_preview(state: PrintMasterState) -> io.BytesIO:
    """Renders the appropriate live preview buffer depending on active mode."""
    if state.mode == "school_labels":
        from .school_labels import render_school_labels_sheet, render_single_label_preview
        if getattr(state, "school_preview_view", "single") == "sheet":
            return render_school_labels_sheet(state, preview=True)
        return render_single_label_preview(state)
    return render_preview_image(state)


def render_current_300dpi(state: PrintMasterState) -> io.BytesIO:
    """Renders the appropriate 300 DPI high-resolution image buffer depending on active mode."""
    if state.mode == "school_labels":
        from .school_labels import render_school_labels_sheet
        return render_school_labels_sheet(state, preview=False)
    return render_300dpi_image(state)


def format_status_caption(state: PrintMasterState) -> str:
    """Generates an informative, polished Markdown caption for the preview message in active language."""
    lang = state.language
    orient = t("portrait_full", lang) if state.is_portrait else t("landscape_full", lang)
    margins = f"T:{state.margin_top_mm:.0f} B:{state.margin_bottom_mm:.0f} L:{state.margin_left_mm:.0f} R:{state.margin_right_mm:.0f} mm"

    if state.mode == "school_labels":
        name = state.school_student_name.strip() or t("school_sample_student", lang)
        grade = state.school_grade.strip() or t("school_sample_grade", lang)
        theme_key = state.school_theme if state.school_theme in ("classic", "football", "space", "cute", "science") else "classic"
        theme_name = t(f"theme_{theme_key}", lang)
        subjects = t("school_subj_auto", lang) if state.school_subject_mode == "auto" else t("school_subj_blank", lang)
        photo_status = t("on", lang) if state.school_custom_avatar else t("off", lang)

        caption = (
            f"{t('school_caption_header', lang)}\n\n"
            f"{t('school_caption_body', lang, name=name, grade=grade, theme=theme_name, subjects=subjects, photo=photo_status)}"
        )
    elif state.mode == "duplicator":
        layout = calculate_duplicator_layout(state)
        w_cm = state.image_width_mm / 10.0
        h_cm = state.image_height_mm / 10.0

        batch_info = (
            t("caption_batch_multi", lang, copies=state.total_batch_copies, sheets=layout["total_sheets"])
            if state.total_batch_copies > 0
            else t("caption_batch_single", lang)
        )

        cuts_str = t("on", lang) if state.show_cut_marks else t("off", lang)
        border_str = t("on", lang) if state.show_border else t("off", lang)
        rot_str = t("on", lang) if state.auto_rotate else t("off", lang)

        caption = (
            f"{t('caption_duplicator_header', lang)}\n\n"
            f"{t('caption_grid', lang, cols=layout['cols'], rows=layout['rows'], copies=layout['drawn_per_page'])}\n"
            f"{t('caption_size', lang, w=w_cm, h=h_cm)}\n"
            f"{t('caption_spacing', lang, gap=state.gap_mm)}\n"
            f"{t('caption_page', lang, orient=orient)}\n"
            f"{t('caption_margins', lang, margins=margins)}\n"
            f"{batch_info}\n"
            f"{t('caption_options', lang, cuts=cuts_str, border=border_str, rotate=rot_str)}\n\n"
            f"{t('caption_footer_hint', lang)}"
        )
    else:
        poster = calculate_poster_layout(state)
        guides_str = t("on", lang) if state.poster_guides else t("off", lang)
        caption = (
            f"{t('caption_poster_header', lang)}\n\n"
            f"{t('caption_tiling', lang, cols=poster['cols'], rows=poster['rows'], sheets=poster['total_sheets'])}\n"
            f"{t('caption_poster_size', lang, w=poster['total_w_cm'], h=poster['total_h_cm'])}\n"
            f"{t('caption_overlap', lang, overlap=state.poster_overlap_mm)}\n"
            f"{t('caption_guides', lang, status=guides_str)}\n"
            f"{t('caption_poster_sheet', lang, orient=orient)}\n"
            f"{t('caption_poster_margin', lang, margins=margins)}\n\n"
            f"{t('caption_poster_hint', lang)}"
        )

    return caption


# =========================================================================
# ADMIN & ANALYTICS DASHBOARD
# =========================================================================
def is_admin(user_id: int) -> bool:
    """Checks whether the user is authorized to access the /admin dashboard."""
    if not ADMIN_ID:
        return True  # Open until configured, with guidance banner
    return str(user_id) == str(ADMIN_ID)


def build_admin_keyboard(active_tab: str = "main"):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    if active_tab in ("top_users", "recent"):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 Top Users", callback_data="admin:top_users"), InlineKeyboardButton("📜 Recent Stream", callback_data="admin:recent")],
            [InlineKeyboardButton("📥 Export Users CSV", callback_data="admin:csv")],
            [InlineKeyboardButton("« Back to Overview", callback_data="admin:main")],
        ])
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Top Users (Ranking)", callback_data="admin:top_users"),
            InlineKeyboardButton("📜 Recent Activity", callback_data="admin:recent"),
        ],
        [
            InlineKeyboardButton("📥 Export Full CSV", callback_data="admin:csv"),
            InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin:refresh"),
        ],
        [
            InlineKeyboardButton("« Back to Editor", callback_data="menu:main"),
        ],
    ])


def format_admin_overview(user_id: int) -> str:
    stats = get_overview_stats()
    warning_note = ""
    if not ADMIN_ID:
        warning_note = (
            f"\n\n💡 *Owner Notice:* `ADMIN_ID` is not yet set in `.env`.\n"
            f"Your Telegram User ID is `{user_id}`.\n"
            f"Add `ADMIN_ID={user_id}` in `.env` to restrict this dashboard to yourself only!"
        )

    return (
        f"👑 *PrintMaster A4 — Admin Analytics Dashboard*\n\n"
        f"👥 *Total Registered Users:* `{stats['total_users']}`\n"
        f"📊 *Total User Actions:* `{stats['total_interactions']}`\n"
        f"⚡ *Active Users:* `{stats['active_24h']}` in 24h • `{stats['active_7d']}` in 7 days\n\n"
        f"📁 *Feature Usage Breakdown:*\n"
        f"• 🖼 *Images Uploaded:* `{stats['total_uploads']}`\n"
        f"• 📄 *PDF Documents Generated:* `{stats['total_pdfs']}`\n"
        f"• 🎨 *300 DPI Images Exported:* `{stats['total_images']}`"
        f"{warning_note}\n\n"
        f"_Tap a button below to inspect user rankings, view live activity, or download the CSV report:_"
    )


def format_top_users_view() -> str:
    top = get_top_users(limit=15)
    if not top:
        return "👥 *User Analytics — Top Users*\n\nNo user activity recorded yet."

    lines = ["👥 *User Analytics — Most Active Users:*\n"]
    for idx, u in enumerate(top, 1):
        uname = f"@{u['username']}" if u["username"] else f"ID: `{u['user_id']}`"
        name = u["first_name"] or "User"
        last_seen = u["last_seen"][:16] if u["last_seen"] else "N/A"
        lines.append(
            f"*{idx}. {name}* ({uname})\n"
            f"   └ ⚡ `{u['interaction_count']}` actions | 🖼 `{u['images_uploaded']}` uploads | 📄 `{u['pdf_exports']}` PDFs\n"
            f"   └ 🕒 Last seen: `{last_seen}`"
        )

    return "\n".join(lines)


def format_recent_activity_view() -> str:
    recent = get_recent_activity(limit=12)
    if not recent:
        return "📜 *Recent Activity Stream*\n\nNo recent activity logged yet."

    lines = ["📜 *Recent Activity Stream (Last 12 events):*\n"]
    for ev in recent:
        uname = f"@{ev['username']}" if ev.get("username") else f"`{ev['user_id']}`"
        time_str = ev["created_at"][11:19] if ev.get("created_at") else ""
        date_str = ev["created_at"][5:10] if ev.get("created_at") else ""
        event_name = ev["event_type"].replace("_", " ").title()
        details = f" ({ev['details']})" if ev.get("details") else ""
        lines.append(f"• `{date_str} {time_str}` — *{uname}*: `{event_name}`{details}")

    return "\n".join(lines)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /admin and /stats command."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ *Access Denied:* This command is restricted to the bot owner.", parse_mode=ParseMode.MARKDOWN)
        return

    record_user_interaction(user, "admin_view", "/admin")
    text = format_admin_overview(user.id)
    kbd = build_admin_keyboard("main")
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)


# =========================================================================
# STANDARD USER COMMANDS
# =========================================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    record_user_interaction(user, "start", "/start command")

    state = get_user_state(user.id, chat_id, user)
    state.current_menu = "main"
    state.waiting_for_input = None
    lang = state.language

    welcome_text = (
        f"{t('welcome_greeting', lang, name=user.first_name)}\n\n"
        f"{t('welcome_body', lang)}"
    )

    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    # Render initial preview
    preview_buf = render_current_preview(state)
    caption = format_status_caption(state)
    kbd = build_keyboard(state)

    sent_msg = await update.message.reply_photo(photo=preview_buf, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
    state.last_preview_message_id = sent_msg.message_id


async def school_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /school or /labels command to switch straight to School Notebook Labels."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    record_user_interaction(user, "school_labels", "/school command")

    state = get_user_state(user.id, chat_id, user)
    state.mode = "school_labels"
    state.current_menu = "main"
    state.waiting_for_input = None

    preview_buf = render_current_preview(state)
    caption = format_status_caption(state)
    kbd = build_keyboard(state)

    sent_msg = await update.message.reply_photo(photo=preview_buf, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
    state.last_preview_message_id = sent_msg.message_id


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /language or /lang command to show language switcher."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id, user)
    state.current_menu = "language"
    kbd = build_keyboard(state)
    await update.message.reply_text(t("lang_switch_title", state.language), parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)


async def tutorial_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /tutorial command to launch the interactive beginner guide."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id, user)
    record_user_interaction(user, "tutorial", "/tutorial command")
    text, kbd = get_tutorial_step(1, lang=state.language)
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id, user)
    record_user_interaction(user, "help", "/help command")
    await update.message.reply_text(t("help_text", state.language), parse_mode=ParseMode.MARKDOWN)


async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming photos and uncompressed image documents."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id)

    # Determine photo file
    if update.message.photo:
        # Highest resolution photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        ext = ".jpg"
    elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
        file_id = update.message.document.file_id
        doc_name = update.message.document.file_name or "uploaded_image.png"
        ext = os.path.splitext(doc_name)[1] or ".png"
    else:
        return

    status_msg = await update.message.reply_text("⏳ *Loading and processing image...*", parse_mode=ParseMode.MARKDOWN)

    try:
        tg_file = await context.bot.get_file(file_id)
        save_path = TEMP_DIR / f"{user.id}_{int(os.times()[4])}{ext}"
        await tg_file.download_to_drive(custom_path=save_path)

        state.cleanup_file()
        state.image_path = str(save_path)

        with Image.open(save_path) as img:
            state.image_orig_width, state.image_orig_height = img.size
            state.aspect_ratio = float(state.image_orig_width) / max(1, state.image_orig_height)
            if state.lock_ratio:
                state.image_height_mm = round(state.image_width_mm / max(0.01, state.aspect_ratio), 1)

        # Record analytics
        record_user_interaction(user, "upload_image", f"{img.size[0]}x{img.size[1]} {ext}")
        record_upload(user.id)

        await status_msg.delete()

        # Render preview and send new control center
        preview_buf = render_current_preview(state)
        caption = format_status_caption(state)
        kbd = build_keyboard(state)

        sent_msg = await update.message.reply_photo(
            photo=preview_buf,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kbd,
        )
        state.last_preview_message_id = sent_msg.message_id

    except Exception as e:
        logger.exception("Error processing uploaded image: %s", e)
        await status_msg.edit_text(f"❌ Failed to process image: {str(e)}")


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes interactive inline button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id)

    # Record user button click
    record_user_interaction(user, "button_click", data[:40])

    # Admin Dashboard Callbacks
    if data.startswith("admin:"):
        action = data.split(":", 1)[1]
        if not is_admin(user.id):
            await query.answer("Access denied.", show_alert=True)
            return

        if action in ("main", "refresh"):
            text = format_admin_overview(user.id)
            kbd = build_admin_keyboard("main")
            if query.message and query.message.text:
                await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            else:
                await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            return

        elif action == "top_users":
            text = format_top_users_view()
            kbd = build_admin_keyboard("top_users")
            if query.message and query.message.text:
                await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            else:
                await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            return

        elif action == "recent":
            text = format_recent_activity_view()
            kbd = build_admin_keyboard("recent")
            if query.message and query.message.text:
                await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            else:
                await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            return

        elif action == "csv":
            await query.message.reply_chat_action("upload_document")
            csv_buf = export_users_csv()
            await query.message.reply_document(
                document=csv_buf,
                filename="PrintMaster_Users_Analytics.csv",
                caption="📊 *Here is the complete CSV report of all users and usage counts.*",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

    # 0. Tutorial Actions
    if data.startswith("tutorial:"):
        action = data.split(":", 1)[1]
        if action.startswith("step_"):
            step_idx = int(action.split("_")[1])
            text, kbd = get_tutorial_step(step_idx, lang=state.language)
            if query.message and query.message.text:
                await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            else:
                await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            return

        elif action == "faq":
            text, kbd = get_tutorial_faq(lang=state.language)
            if query.message and query.message.text:
                await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            else:
                await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            return

        elif action == "demo":
            if DEFAULT_SAMPLE_IMAGE.exists():
                dest = TEMP_DIR / f"demo_{user.id}.jpg"
                shutil.copy(DEFAULT_SAMPLE_IMAGE, dest)
                state.cleanup_file()
                state.image_path = str(dest)
                with Image.open(dest) as img:
                    state.image_orig_width, state.image_orig_height = img.size
                    state.aspect_ratio = float(state.image_orig_width) / max(1, state.image_orig_height)
                state.mode = "duplicator"
                state.set_dimensions(50.0, 50.0, lock_ratio=True)
                state.gap_mm = 3.0
                state.show_cut_marks = True
                state.current_menu = "main"

                preview_buf = render_current_preview(state)
                caption = format_status_caption(state)
                kbd = build_keyboard(state)

                sent_msg = await query.message.reply_photo(
                    photo=preview_buf,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kbd,
                )
                state.last_preview_message_id = sent_msg.message_id
            else:
                await query.message.reply_text("Sample image not found on server.")
            return

    # Language Switcher
    if data.startswith("set_lang:"):
        new_lang = data.split(":", 1)[1]
        state.language = new_lang
        set_user_language(user.id, new_lang)
        record_user_interaction(user, "set_language", new_lang)
        await query.answer(t("lang_switched", new_lang), show_alert=True)
        state.current_menu = "main"
        await _update_view(query, state)
        return

    # 1. Navigation Menus
    if data.startswith("menu:"):
        state.current_menu = data.split(":", 1)[1]
        state.waiting_for_input = None
        await _update_view(query, state)
        return

    # 2. Toggle Mode
    if data == "toggle_mode":
        if state.mode == "duplicator":
            state.mode = "poster"
        elif state.mode == "poster":
            state.mode = "school_labels"
        else:
            state.mode = "duplicator"
        state.current_menu = "main"
        await _update_view(query, state)
        return

    # Mode Switch Direct
    if data.startswith("switch_mode:"):
        new_mode = data.split(":", 1)[1]
        if new_mode in ("duplicator", "poster", "school_labels"):
            state.mode = new_mode
            state.current_menu = "main"
            state.waiting_for_input = None
            await _update_view(query, state)
        return

    # School Labels callbacks
    if data == "toggle_school_subjects":
        state.school_subject_mode = "blank" if state.school_subject_mode == "auto" else "auto"
        await _update_view(query, state)
        return

    if data == "toggle_school_avatar":
        state.school_custom_avatar = not state.school_custom_avatar
        await _update_view(query, state)
        return

    if data == "toggle_school_view":
        state.school_preview_view = "sheet" if getattr(state, "school_preview_view", "single") == "single" else "single"
        await _update_view(query, state)
        return

    if data.startswith("set_school_theme:"):
        state.school_theme = data.split(":", 1)[1]
        state.current_menu = "main"
        await _update_view(query, state)
        return

    # 3. Presets - Sizes
    if data.startswith("set_size_preset:"):
        preset_id = data.split(":", 1)[1]
        for p in STANDARD_PRESETS:
            if p["id"] == preset_id:
                state.set_dimensions(p["w"], p["h"], lock_ratio=False)
                break
        state.current_menu = "main"
        await _update_view(query, state)
        return

    # 4. Presets - Quick Grids
    if data.startswith("set_grid_preset:"):
        parts = data.split(":", 1)[1].split("_")
        rows, cols = int(parts[0]), int(parts[1])
        apply_grid_fit(state, rows, cols)
        state.current_menu = "main"
        await _update_view(query, state)
        return

    # 5. Lock Aspect Ratio
    if data == "toggle_lock_ratio":
        state.lock_ratio = not state.lock_ratio
        if state.lock_ratio and state.aspect_ratio > 0:
            state.image_height_mm = round(state.image_width_mm / state.aspect_ratio, 1)
        await _update_view(query, state)
        return

    # 6. Step Size
    if data.startswith("step_w:"):
        step = float(data.split(":", 1)[1])
        state.image_width_mm = max(5.0, round(state.image_width_mm + step, 1))
        if state.lock_ratio and state.aspect_ratio > 0:
            state.image_height_mm = round(state.image_width_mm / state.aspect_ratio, 1)
        await _update_view(query, state)
        return

    if data.startswith("step_h:"):
        step = float(data.split(":", 1)[1])
        state.image_height_mm = max(5.0, round(state.image_height_mm + step, 1))
        if state.lock_ratio and state.aspect_ratio > 0:
            state.image_width_mm = round(state.image_height_mm * state.aspect_ratio, 1)
        await _update_view(query, state)
        return

    # 7. Spacing / Gap
    if data.startswith("set_gap:"):
        state.gap_mm = float(data.split(":", 1)[1])
        await _update_view(query, state)
        return

    if data.startswith("step_gap:"):
        step = float(data.split(":", 1)[1])
        state.gap_mm = max(0.0, round(state.gap_mm + step, 1))
        await _update_view(query, state)
        return

    # 8. Page Orientation & Margins
    if data == "toggle_orientation":
        state.is_portrait = not state.is_portrait
        await _update_view(query, state)
        return

    if data.startswith("set_margin:"):
        m = float(data.split(":", 1)[1])
        state.set_uniform_margin(m)
        await _update_view(query, state)
        return

    if data == "toggle_margin_guide":
        state.show_margin_guide = not state.show_margin_guide
        await _update_view(query, state)
        return

    # 9. Cut marks & Border
    if data == "toggle_cut_marks":
        state.show_cut_marks = not state.show_cut_marks
        await _update_view(query, state)
        return

    if data == "toggle_border":
        state.show_border = not state.show_border
        await _update_view(query, state)
        return

    if data == "cycle_border_color":
        colors = ["black", "gray", "white", "red"]
        curr_idx = colors.index(state.border_color.lower()) if state.border_color.lower() in colors else 0
        state.border_color = colors[(curr_idx + 1) % len(colors)]
        await _update_view(query, state)
        return

    if data == "cycle_border_thick":
        thicks = [0.2, 0.5, 1.0, 2.0]
        curr_idx = thicks.index(state.border_thickness_mm) if state.border_thickness_mm in thicks else 1
        state.border_thickness_mm = thicks[(curr_idx + 1) % len(thicks)]
        await _update_view(query, state)
        return

    if data == "toggle_auto_rotate":
        state.auto_rotate = not state.auto_rotate
        await _update_view(query, state)
        return

    if data == "toggle_alignment":
        state.alignment = "top_left" if state.alignment == "center" else "center"
        await _update_view(query, state)
        return

    # 10. Batch Copies
    if data.startswith("set_batch:"):
        state.total_batch_copies = int(data.split(":", 1)[1])
        await _update_view(query, state)
        return

    if data == "toggle_limit_copies":
        state.limit_copies = not state.limit_copies
        await _update_view(query, state)
        return

    # 11. Poster Settings
    if data.startswith("set_poster_preset:"):
        parts = data.split(":", 1)[1].split("_")
        state.poster_cols = int(parts[0])
        state.poster_rows = int(parts[1])
        state.current_menu = "main"
        await _update_view(query, state)
        return

    if data.startswith("step_poster_col:"):
        step = int(data.split(":", 1)[1])
        state.poster_cols = max(1, min(12, state.poster_cols + step))
        await _update_view(query, state)
        return

    if data.startswith("step_poster_row:"):
        step = int(data.split(":", 1)[1])
        state.poster_rows = max(1, min(12, state.poster_rows + step))
        await _update_view(query, state)
        return

    if data.startswith("set_overlap:"):
        state.poster_overlap_mm = float(data.split(":", 1)[1])
        await _update_view(query, state)
        return

    if data == "toggle_poster_guides":
        state.poster_guides = not state.poster_guides
        await _update_view(query, state)
        return

    # 12. Manual Text Inputs Prompt
    if data.startswith("input:"):
        input_type = data.split(":", 1)[1]
        state.waiting_for_input = input_type
        prompt_map = {
            "custom_width": t("prompt_width", state.language),
            "custom_height": t("prompt_height", state.language),
            "custom_gap": t("prompt_gap", state.language),
            "custom_margin": t("prompt_margin", state.language),
            "custom_batch": t("prompt_batch", state.language),
            "custom_poster_grid": t("prompt_poster_grid", state.language),
            "custom_overlap": t("prompt_poster_overlap", state.language),
            "school_name": t("prompt_school_name", state.language),
            "school_grade": t("prompt_school_grade", state.language),
        }
        msg = prompt_map.get(input_type, "Please type the value:")
        cancel_hint = t("input_cancel_hint", state.language)
        await query.message.reply_text(f"{msg}{cancel_hint}", parse_mode=ParseMode.MARKDOWN)
        return

    # 13. Refresh Preview
    if data == "refresh_preview":
        await _update_view(query, state)
        return

    # 14. Export Actions
    if data == "export:pdf":
        await query.message.reply_chat_action("upload_document")
        record_export(user.id, "pdf")
        record_user_interaction(user, "export_pdf", state.mode)
        pdf_buf = export_pdf(state)
        if state.mode == "school_labels":
            fname = "School_Notebook_Labels_A4.pdf"
        elif state.mode == "poster":
            fname = "Poster_A4_Tiles.pdf"
        else:
            fname = f"Batch_{state.total_batch_copies}_Copies.pdf" if state.total_batch_copies > 0 else "Duplicated_A4_Output.pdf"

        await query.message.reply_document(
            document=pdf_buf,
            filename=fname,
            caption=t("export_pdf_ready", state.language),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "export:image300":
        await query.message.reply_chat_action("upload_document")
        record_export(user.id, "image")
        record_user_interaction(user, "export_image300", state.mode)
        img_buf = render_current_300dpi(state)
        if state.mode == "school_labels":
            fname = "School_Notebook_Labels_A4_300DPI.png"
        elif state.mode == "poster":
            fname = "Poster_A4_300DPI.png"
        else:
            fname = "Duplicated_A4_300DPI.png"

        await query.message.reply_document(
            document=img_buf,
            filename=fname,
            caption=t("export_image_ready", state.language),
            parse_mode=ParseMode.MARKDOWN,
        )
        return


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text replies when waiting for custom dimensions or numbers."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id, user)

    text = update.message.text.strip()

    if text.startswith("/"):
        if text == "/cancel":
            state.waiting_for_input = None
            await update.message.reply_text(t("input_cancelled", state.language))
            return

    if not state.waiting_for_input:
        return

    input_type = state.waiting_for_input
    state.waiting_for_input = None

    record_user_interaction(user, "custom_input", f"{input_type}: {text[:30]}")

    try:
        if input_type in ("custom_width", "custom_height"):
            val_mm = _parse_dimension_to_mm(text)
            if val_mm and val_mm > 0:
                if input_type == "custom_width":
                    state.image_width_mm = val_mm
                    if state.lock_ratio and state.aspect_ratio > 0:
                        state.image_height_mm = round(state.image_width_mm / state.aspect_ratio, 1)
                else:
                    state.image_height_mm = val_mm
                    if state.lock_ratio and state.aspect_ratio > 0:
                        state.image_width_mm = round(state.image_height_mm * state.aspect_ratio, 1)
                await update.message.reply_text(f"✅ `{val_mm/10:.1f} cm` (`{val_mm:.1f} mm`)", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(t("input_invalid_number", state.language), parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_gap":
            val_mm = _parse_dimension_to_mm(text)
            if val_mm is not None and val_mm >= 0:
                state.gap_mm = val_mm
                await update.message.reply_text(f"✅ `{val_mm:.1f} mm`", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(t("input_invalid_number", state.language), parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_margin":
            val_mm = _parse_dimension_to_mm(text)
            if val_mm is not None and val_mm >= 0:
                state.set_uniform_margin(val_mm)
                await update.message.reply_text(f"✅ `{val_mm:.1f} mm`", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(t("input_invalid_number", state.language), parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_batch":
            nums = re.findall(r"\d+", text)
            if nums:
                state.total_batch_copies = int(nums[0])
                batch_label = t("batch_copies_option", state.language, n=state.total_batch_copies)
                await update.message.reply_text(f"✅ {batch_label}", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(t("input_invalid_number", state.language), parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_poster_grid":
            match = re.search(r"(\d+)\s*[xX×*]\s*(\d+)", text)
            if match:
                c, r = int(match.group(1)), int(match.group(2))
                state.poster_cols = max(1, min(12, c))
                state.poster_rows = max(1, min(12, r))
                await update.message.reply_text(f"✅ `{state.poster_cols} × {state.poster_rows}`", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(t("input_invalid_grid", state.language), parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_overlap":
            val_mm = _parse_dimension_to_mm(text)
            if val_mm is not None and val_mm >= 0:
                state.poster_overlap_mm = val_mm
                await update.message.reply_text(f"✅ `{val_mm:.1f} mm`", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(t("input_invalid_number", state.language), parse_mode=ParseMode.MARKDOWN)

        elif input_type == "school_name":
            state.school_student_name = text.strip()[:60]
            await update.message.reply_text(f"✅ *{state.school_student_name}*", parse_mode=ParseMode.MARKDOWN)

        elif input_type == "school_grade":
            state.school_grade = text.strip()[:50]
            await update.message.reply_text(f"✅ *{state.school_grade}*", parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.exception("Error parsing text input: %s", e)
        await update.message.reply_text("❌ An error occurred processing the input.")

    # Re-send or refresh control center
    preview_buf = render_current_preview(state)
    caption = format_status_caption(state)
    kbd = build_keyboard(state)

    sent = await update.message.reply_photo(
        photo=preview_buf,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kbd,
    )
    state.last_preview_message_id = sent.message_id


async def _update_view(query, state: PrintMasterState):
    """Updates the preview photo, caption, and inline keyboard in-place or re-sends photo if transitioning from text."""
    try:
        preview_buf = render_current_preview(state)
        caption = format_status_caption(state)
        kbd = build_keyboard(state)

        if query.message and query.message.photo:
            # Update message media and caption seamlessly
            media = InputMediaPhoto(media=preview_buf, caption=caption, parse_mode=ParseMode.MARKDOWN)
            await query.message.edit_media(media=media, reply_markup=kbd)
        else:
            # Transitioning from a text message (e.g. tutorial or FAQ), send new photo preview
            sent = await query.message.reply_photo(photo=preview_buf, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            state.last_preview_message_id = sent.message_id

    except Exception as e:
        logger.exception("Error updating view: %s", e)
        try:
            kbd = build_keyboard(state)
            caption = format_status_caption(state)
            if query.message and query.message.photo:
                await query.message.edit_caption(caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            elif query.message:
                await query.message.edit_text(text=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
        except Exception:
            pass


def _parse_dimension_to_mm(text: str) -> float:
    """Parses user input strings like '5 cm', '5.5cm', '50mm', '50', '2.5' to millimeters."""
    text = text.lower().strip()
    if "cm" in text:
        clean = text.replace("cm", "").strip()
        val = float(clean)
        return val * 10.0
    elif "mm" in text:
        clean = text.replace("mm", "").strip()
        return float(clean)
    else:
        # If raw number: if < 15 assume cm, else mm
        val = float(text)
        return val * 10.0 if val <= 15.0 else val

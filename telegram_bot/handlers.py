"""
PrintMaster A4 - Telegram Bot Handlers
Processes commands, media uploads, interactive inline buttons, and custom inputs.
"""

import os
import io
import re
import shutil
import logging
from typing import Dict
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
from .database import (
    init_db,
    record_user_interaction,
    record_upload,
    record_export,
    get_overview_stats,
    get_top_users,
    get_recent_activity,
    export_users_csv,
)

logger = logging.getLogger(__name__)

# Initialize database tables
init_db()

# In-memory dictionary of user states: user_id -> PrintMasterState
USER_SESSIONS: Dict[int, PrintMasterState] = {}


def get_user_state(user_id: int, chat_id: int) -> PrintMasterState:
    """Retrieves or initializes session state for a user."""
    if user_id not in USER_SESSIONS:
        state = PrintMasterState(user_id=user_id, chat_id=chat_id)
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


def format_status_caption(state: PrintMasterState) -> str:
    """Generates an informative, polished Markdown caption for the preview message."""
    orient = "Portrait (210 × 297 mm)" if state.is_portrait else "Landscape (297 × 210 mm)"
    margins = f"T:{state.margin_top_mm:.0f} B:{state.margin_bottom_mm:.0f} L:{state.margin_left_mm:.0f} R:{state.margin_right_mm:.0f} mm"

    if state.mode == "duplicator":
        layout = calculate_duplicator_layout(state)
        w_cm = state.image_width_mm / 10.0
        h_cm = state.image_height_mm / 10.0

        batch_info = (
            f"• *Total Batch:* `{state.total_batch_copies}` copies across `{layout['total_sheets']}` A4 sheets"
            if state.total_batch_copies > 0
            else "• *Batch:* Single A4 Sheet"
        )

        caption = (
            f"✨ *PrintMaster A4 — Duplicator Mode*\n\n"
            f"📊 *Grid Layout:* `{layout['cols']} × {layout['rows']}` ({layout['drawn_per_page']} copies / page)\n"
            f"📏 *Image Size:* `{w_cm:.1f} × {h_cm:.1f} cm`\n"
            f"↔️ *Image Spacing:* `{state.gap_mm:.1f} mm`\n"
            f"📄 *Page Setup:* {orient}\n"
            f"📐 *Margins:* `{margins}`\n"
            f"{batch_info}\n"
            f"✂️ *Options:* Cut Marks: `{'ON' if state.show_cut_marks else 'OFF'}` | "
            f"Border: `{'ON' if state.show_border else 'OFF'}` | "
            f"Auto-Rotate: `{'ON' if state.auto_rotate else 'OFF'}`\n\n"
            f"💡 _Tap the buttons below to customize, or send any new photo!_"
        )
    else:
        poster = calculate_poster_layout(state)
        caption = (
            f"✨ *PrintMaster A4 — Poster Maker*\n\n"
            f"🧩 *Tiling:* `{poster['cols']} × {poster['rows']}` (`{poster['total_sheets']}` A4 Sheets)\n"
            f"📐 *Overall Poster Size:* `~{poster['total_w_cm']:.1f} × {poster['total_h_cm']:.1f} cm`\n"
            f"📏 *Tile Overlap:* `{state.poster_overlap_mm:.0f} mm`\n"
            f"🏷 *Glue Guidelines & Numbers:* `{'ON' if state.poster_guides else 'OFF'}`\n"
            f"📄 *Sheet Size:* {orient}\n"
            f"📐 *Print Margin:* `{margins}`\n\n"
            f"💡 _Each tile will be scaled and printed onto its own A4 sheet with overlap guides!_"
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

    state = get_user_state(user.id, chat_id)
    state.current_menu = "main"
    state.waiting_for_input = None

    welcome_text = (
        f"👋 *Welcome {user.first_name} to PrintMaster A4 Bot!*\n\n"
        f"🖨 *The complete printing suite in Telegram:*\n"
        f"• *Image Duplicator:* Place multiple copies of photos, stickers, business cards, or passport photos on an A4 sheet with cutting marks.\n"
        f"• *Poster Maker:* Split a large photo across multiple A4 sheets for giant wall posters with overlap glue lines.\n"
        f"• *Vector PDF & 300 DPI Export:* Export print-ready documents with zero quality loss.\n\n"
        f"🐣 *New here?* Type /tutorial or tap *'📚 Beginner Tutorial'* below for a 1-minute visual guide!\n\n"
        f"📸 *Send me any image* to start duplicating or creating a poster, or use the loaded sample image below:"
    )

    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    # Render initial preview
    preview_buf = render_preview_image(state)
    caption = format_status_caption(state)
    kbd = build_keyboard(state)

    sent_msg = await update.message.reply_photo(photo=preview_buf, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
    state.last_preview_message_id = sent_msg.message_id


async def tutorial_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /tutorial command to launch the interactive beginner guide."""
    user = update.effective_user
    record_user_interaction(user, "tutorial", "/tutorial command")
    text, kbd = get_tutorial_step(1)
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    user = update.effective_user
    record_user_interaction(user, "help", "/help command")
    help_text = (
        f"📖 *PrintMaster A4 Help & Instructions*\n\n"
        f"1. *Load an Image:* Simply send any photo or image document directly into this chat.\n"
        f"2. *Duplicator Mode:* Choose standard photo sizes (Passport, Visa, Cards), quick grids (2x2, 3x2, etc.), or adjust width, height, and spacing.\n"
        f"3. *Batch Copies:* Enter total copies (e.g. 50 or 100) to generate a multi-page PDF spanning as many A4 sheets as needed.\n"
        f"4. *Poster Mode:* Choose grid layout (2x2, 3x3, etc.) to print huge posters with glue guides.\n"
        f"5. *Export:* Click *Export PDF* for vector printing or *Export 300 DPI* for ultra high-res image.\n\n"
        f"🐣 *Need a beginner walkthrough?* Send /tutorial to open the interactive step-by-step guide!\n"
        f"👑 *Admin Dashboard:* Send /admin or /stats to view usage stats and user list.\n"
        f"Use /start to reset or reload the menu anytime."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


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
        preview_buf = render_preview_image(state)
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
            text, kbd = get_tutorial_step(step_idx)
            if query.message and query.message.text:
                await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            else:
                await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kbd)
            return

        elif action == "faq":
            text, kbd = get_tutorial_faq()
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

                preview_buf = render_preview_image(state)
                caption = format_status_caption(state)
                kbd = build_keyboard(state)

                sent_msg = await query.message.reply_photo(
                    photo=preview_buf,
                    caption="🎉 *Demo sticker loaded successfully!*\nHere is your live preview. Try customizing it below:\n\n" + caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kbd,
                )
                state.last_preview_message_id = sent_msg.message_id
            else:
                await query.message.reply_text("Sample image not found on server.")
            return

    # 1. Navigation Menus
    if data.startswith("menu:"):
        state.current_menu = data.split(":", 1)[1]
        state.waiting_for_input = None
        await _update_view(query, state)
        return

    # 2. Toggle Mode
    if data == "toggle_mode":
        state.mode = "poster" if state.mode == "duplicator" else "duplicator"
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
            "custom_width": "Enter desired image width in cm or mm (e.g. `5 cm` or `50 mm`):",
            "custom_height": "Enter desired image height in cm or mm (e.g. `5 cm` or `50 mm`):",
            "custom_gap": "Enter spacing/gap in mm (e.g. `2.5 mm`):",
            "custom_margin": "Enter page margin in mm (e.g. `10 mm` or `5 mm`):",
            "custom_batch": "Enter total batch copies (e.g. `100` or `250`):",
            "custom_poster_grid": "Enter columns and rows (e.g. `3x3` or `2x4`):",
            "custom_overlap": "Enter poster overlap in mm (e.g. `15 mm`):",
        }
        msg = prompt_map.get(input_type, "Please type the value:")
        await query.message.reply_text(f"✏️ *Input Required:*\n{msg}\n\n_Type your reply or send /cancel._", parse_mode=ParseMode.MARKDOWN)
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
        fname = (
            "Poster_A4_Tiles.pdf"
            if state.mode == "poster"
            else (f"Batch_{state.total_batch_copies}_Copies.pdf" if state.total_batch_copies > 0 else "Duplicated_A4_Output.pdf")
        )
        await query.message.reply_document(
            document=pdf_buf,
            filename=fname,
            caption="📄 *Here is your print-ready vector PDF document!* Exact scale for A4 paper.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "export:image300":
        await query.message.reply_chat_action("upload_document")
        record_export(user.id, "image")
        record_user_interaction(user, "export_image300", state.mode)
        img_buf = render_300dpi_image(state)
        fname = "Poster_A4_300DPI.png" if state.mode == "poster" else "Duplicated_A4_300DPI.png"
        await query.message.reply_document(
            document=img_buf,
            filename=fname,
            caption="🖼 *Here is your ultra high-resolution 300 DPI image!* Perfect for photo printing.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text replies when waiting for custom dimensions or numbers."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = get_user_state(user.id, chat_id)

    text = update.message.text.strip()

    if text.startswith("/"):
        if text == "/cancel":
            state.waiting_for_input = None
            await update.message.reply_text("✅ Cancelled. Returning to menu.")
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
                await update.message.reply_text(f"✅ Dimension set to `{val_mm/10:.1f} cm` (`{val_mm:.1f} mm`)", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Could not parse dimension. Example: `5 cm` or `45 mm`.")

        elif input_type == "custom_gap":
            val_mm = _parse_dimension_to_mm(text)
            if val_mm is not None and val_mm >= 0:
                state.gap_mm = val_mm
                await update.message.reply_text(f"✅ Gap set to `{val_mm:.1f} mm`", parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_margin":
            val_mm = _parse_dimension_to_mm(text)
            if val_mm is not None and val_mm >= 0:
                state.set_uniform_margin(val_mm)
                await update.message.reply_text(f"✅ Margins set to `{val_mm:.1f} mm`", parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_batch":
            nums = re.findall(r"\d+", text)
            if nums:
                state.total_batch_copies = int(nums[0])
                await update.message.reply_text(f"✅ Total batch set to `{state.total_batch_copies}` copies", parse_mode=ParseMode.MARKDOWN)

        elif input_type == "custom_poster_grid":
            match = re.search(r"(\d+)\s*[xX×*]\s*(\d+)", text)
            if match:
                c, r = int(match.group(1)), int(match.group(2))
                state.poster_cols = max(1, min(12, c))
                state.poster_rows = max(1, min(12, r))
                await update.message.reply_text(f"✅ Poster grid set to `{state.poster_cols} × {state.poster_rows}`", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Format should be Cols x Rows (e.g. `3x3` or `2x4`).")

        elif input_type == "custom_overlap":
            val_mm = _parse_dimension_to_mm(text)
            if val_mm is not None and val_mm >= 0:
                state.poster_overlap_mm = val_mm
                await update.message.reply_text(f"✅ Overlap set to `{val_mm:.1f} mm`", parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.exception("Error parsing text input: %s", e)
        await update.message.reply_text("❌ An error occurred processing the input.")

    # Re-send or refresh control center
    preview_buf = render_preview_image(state)
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
        preview_buf = render_preview_image(state)
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

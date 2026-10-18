"""
PrintMaster A4 - Interactive Beginner Tutorial & FAQ
Provides step-by-step guidance, printing advice, and glossary for new users.
"""

from typing import Dict, Any, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TUTORIAL_STEPS = [
    {
        "step": 1,
        "title": "Welcome to PrintMaster A4 🐣",
        "content": (
            "👋 *Welcome to PrintMaster A4!*\n\n"
            "Have you ever tried printing 6 passport photos or 12 cute stickers on an A4 page, "
            "only for Word or Paint to stretch your image or make it the wrong size?\n\n"
            "🎯 *PrintMaster A4 calculates everything down to the exact millimeter!*\n\n"
            "Here are the two superpowers of this bot:\n"
            "1️⃣ *Duplicator Mode (Grid):* Fit multiple copies of any photo, sticker, or card onto one A4 sheet with cutting guides.\n"
            "2️⃣ *Poster Maker Mode:* Turn any ordinary photo into a giant wall poster split across multiple A4 sheets (2×2, 3×3, etc.) with glue tabs!\n\n"
            "Tap *Next ➡️* to see how easy it is to use!"
        ),
    },
    {
        "step": 2,
        "title": "Sending Photos Like a Pro 📸",
        "content": (
            "📸 *Step 1: Sending Your Image*\n\n"
            "You can send any photo, artwork, or sticker directly into this chat.\n\n"
            "💡 *Pro-Tip for Crystal Clear Prints:*\n"
            "When sending an image on Telegram, you have two choices:\n"
            "• *Send as Photo:* Quick and easy, but Telegram slightly compresses the image.\n"
            "• *Send as File / Document:* Keeps *100% original uncompressed quality*! Ideal for crisp text, stickers, and passport photos.\n\n"
            "👉 *Don't have an image ready right now?*\n"
            "No problem! Tap *'🧪 Try Demo Image'* at any time to practice with our cute sample sticker."
        ),
    },
    {
        "step": 3,
        "title": "Duplicator Mode (Multiple Copies) 🖨️",
        "content": (
            "🖨️ *Step 2: Duplicator Mode (Copies & Grids)*\n\n"
            "Want multiple copies on one page?\n\n"
            "• *📐 Size Presets:* One tap sets official dimensions:\n"
            "  - 🛂 *Passport Photo:* 3.5 × 4.5 cm\n"
            "  - 🇺🇸 *US Visa / Square:* 5.1 × 5.1 cm\n"
            "  - 💳 *Business Card:* 8.5 × 5.5 cm\n"
            "  - 📸 *Polaroid Sticker:* 7.0 × 7.0 cm\n\n"
            "• *📊 Quick Grids:* Tap `4-Up`, `6-Up`, or `9-Up` to instantly auto-fit the page.\n"
            "• *↔️ Spacing (Gap):* Keep a 2 mm or 3 mm gap between items so they don't touch.\n"
            "• *🔒 Aspect Ratio:* Keeps your photo natural so it never looks stretched or squished!"
        ),
    },
    {
        "step": 4,
        "title": "Cutting Marks & Scissors Guide ✂️",
        "content": (
            "✂️ *Step 3: Cutting Marks & Straight Lines*\n\n"
            "Ever tried cutting 15 small photos with scissors and ended up with crooked edges?\n\n"
            "• *✂️ Cut Marks (ON):* We automatically draw 3.5 mm tick marks at every corner plus a faint dashed guide around each photo.\n"
            "• *How to use:* Simply line up your ruler or scissors with the corner tick marks and cut straight through!\n"
            "• *🔲 Borders:* You can turn on a clean colored outline (*Black, Gray, White, Red*) with adjustable thickness so your cards look professionally finished."
        ),
    },
    {
        "step": 5,
        "title": "Giant Poster Maker Mode 🧩",
        "content": (
            "🧩 *Step 4: Making Giant Wall Posters*\n\n"
            "Don't have an expensive large-format printer? You can make huge posters using regular A4 paper!\n\n"
            "• Tap *🔀 Mode* to switch to *Poster Maker*.\n"
            "• Pick your poster size:\n"
            "  - *2 × 2:* 4 A4 sheets (~42 × 60 cm, like an A2 poster!)\n"
            "  - *3 × 3:* 9 A4 sheets (~63 × 89 cm, giant A0 poster!)\n"
            "  - *Custom:* Up to 12 × 12 sheets for massive wall murals.\n\n"
            "• *🏷 Glue Guidelines & Labels:*\n"
            "Every sheet prints with a 10 mm overlap line saying *'Glue Sheet #2 Here'* and sheet numbers (*Row 1/2, Col 1/2*). "
            "Assembling your poster with glue or tape is as easy as a simple puzzle!"
        ),
    },
    {
        "step": 6,
        "title": "Printing at Home (The #1 Rule!) 🖨️",
        "content": (
            "🖨️ *Step 5: Printing Your Exported File*\n\n"
            "Once you're happy with the preview, tap *📄 Export PDF*.\n\n"
            "⚠️ *THE #1 MISTAKE BEGINNERS MAKE:*\n"
            "When your computer or phone print window opens, printers often default to *'Fit to Printable Area'* or *'Shrink to Fit'*.\n\n"
            "👉 **ALWAYS select: 'Actual Size' or '100% Scale'** in your printer settings!\n"
            "• This guarantees your passport photos or business cards print at their *exact millimeter dimensions*!\n"
            "• Ensure paper size is set to **A4** (210 × 297 mm).\n"
            "• Use standard photo paper or glossy sticker paper for the brightest, sharpest colors!\n\n"
            "🎉 *You are now ready to print like a pro!*"
        ),
    },
]

TUTORIAL_FAQ_TEXT = (
    "❓ *PrintMaster A4 — Beginner FAQ & Glossary*\n\n"
    "• *What is 'Lock Aspect Ratio'?*\n"
    "It preserves the proportional width-to-height ratio of your photo so people don't look stretched wide or squished tall.\n\n"
    "• *What is 'Auto-Rotate 90° for Max Yield'?*\n"
    "The bot tests whether rotating your photo sideways lets MORE copies fit on the page. If it saves paper, it rotates automatically!\n\n"
    "• *What is 'Batch Export'?*\n"
    "If you need 50 stickers for an event, set Batch to 50. The bot creates a single multi-page PDF spanning all necessary sheets with exactly 50 copies!\n\n"
    "• *PDF vs. 300 DPI Image — Which should I choose?*\n"
    "  - *📄 PDF:* Best for home or office printers. Exact millimeter scale.\n"
    "  - *🖼 300 DPI Image:* Best if taking the file to a photo lab, kiosk, or professional photo printer.\n\n"
    "• *Why is my printer cutting off the edges?*\n"
    "Most home printers cannot print to the very edge of the paper. Set your page margin to *Standard (10 mm)* or *Narrow (5 mm)* to keep everything inside the printable area!"
)


def get_tutorial_step(step_idx: int) -> Tuple[str, InlineKeyboardMarkup]:
    """Returns the formatted text and navigation keyboard for a given step (1-indexed)."""
    step_idx = max(1, min(len(TUTORIAL_STEPS), step_idx))
    step_data = TUTORIAL_STEPS[step_idx - 1]
    total_steps = len(TUTORIAL_STEPS)

    header = f"📚 *Beginner Tutorial* — Step {step_idx} of {total_steps}\n\n"
    body = step_data["content"]
    full_text = header + body

    nav_row = []
    if step_idx > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Back", callback_data=f"tutorial:step_{step_idx - 1}"))
    if step_idx < total_steps:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"tutorial:step_{step_idx + 1}"))

    rows = []
    if nav_row:
        rows.append(nav_row)

    rows.append([
        InlineKeyboardButton("❓ FAQ & Glossary", callback_data="tutorial:faq"),
        InlineKeyboardButton("🧪 Try Demo Image", callback_data="tutorial:demo"),
    ])
    rows.append([
        InlineKeyboardButton("« Exit Tutorial to Editor", callback_data="menu:main"),
    ])

    return full_text, InlineKeyboardMarkup(rows)


def get_tutorial_faq() -> Tuple[str, InlineKeyboardMarkup]:
    """Returns the FAQ text and navigation buttons."""
    rows = [
        [
            InlineKeyboardButton("« Back to Tutorial", callback_data="tutorial:step_1"),
            InlineKeyboardButton("🧪 Try Demo Image", callback_data="tutorial:demo"),
        ],
        [
            InlineKeyboardButton("« Exit to Main Editor", callback_data="menu:main"),
        ],
    ]
    return TUTORIAL_FAQ_TEXT, InlineKeyboardMarkup(rows)

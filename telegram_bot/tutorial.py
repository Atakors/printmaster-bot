"""
PrintMaster A4 - Interactive Beginner Tutorial & FAQ
Provides step-by-step guidance, printing advice, and glossary for new users in English and Arabic.
"""

from typing import Dict, Any, Tuple, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TUTORIAL_STEPS_EN = [
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

TUTORIAL_STEPS_AR = [
    {
        "step": 1,
        "title": "مرحباً بك في برينت ماستر A4 🐣",
        "content": (
            "👋 *مرحباً بك في برينت ماستر A4!*\n\n"
            "هل حاولت يوماً طباعة 6 صور هوية أو ملصقات على ورقة A4، "
            "لكن برامج مثل Word أو الرسام قامت بتشويه أبعاد الصورة وجعلت المقاس خاطئاً؟\n\n"
            "🎯 *برينت ماستر A4 يحسب كل مليمتر بدقة هندسية مطلقة!*\n\n"
            "إليك الميزتين الأساسيتين للبوت:\n"
            "1️⃣ *وضع التكرار (شبكة):* وضع نسخ متعددة من أي صورة أو بطاقة أو ملصق على ورقة A4 واحدة مع علامات قص دقيقة.\n"
            "2️⃣ *صانع البوسترات الجدارية:* تحويل أي صورة عادية إلى بوستر جداري عملاق مقسم على عدة أوراق A4 (2×2 أو 3×3...) مع زوائد لصق وترقيم ذكي!\n\n"
            "اضغط على *التالي ➡️* لتكتشف مدى السهولة والسرعة!"
        ),
    },
    {
        "step": 2,
        "title": "إرسال الصور كالمحترفين 📸",
        "content": (
            "📸 *الخطوة 1: إرسال صورتك*\n\n"
            "يمكنك إرسال أي صورة شخصية أو تصميم أو ستيكر في المحادثة مباشرة.\n\n"
            "💡 *نصيحة ذهبية لجودة طباعة فائقة النقاء:*\n"
            "عند إرسال الصورة في تيليجرام، لديك خياران:\n"
            "• *إرسال كصورة (Photo):* سريع وسهل، لكن تيليجرام يقلل من جودة الصورة قليلاً.\n"
            "• *إرسال كملف / مستند (File / Document):* يحافظ على *الجودة الأصلية 100% دون أي ضغط*! وهو الخيار المثالي لصور الهوية والنصوص والملصقات الدقيقة.\n\n"
            "👉 *ليس لديك صورة جاهزة الآن؟*\n"
            "لا تقلق! اضغط على زر *'🧪 تجربة صورة توضيحية'* في أي وقت لتجربة الخيارات مع نموذج جاهز."
        ),
    },
    {
        "step": 3,
        "title": "وضع التكرار (نسخ متعددة) 🖨️",
        "content": (
            "🖨️ *الخطوة 2: وضع التكرار وضبط الشبكة*\n\n"
            "تريد عدة نسخ على صفحة واحدة؟\n\n"
            "• *📐 مقاسات رسمية جاهزة بضغطة زر:*\n"
            "  - 🛂 *صورة جواز السفر:* 3.5 × 4.5 سم\n"
            "  - 🇺🇸 *فيزا أمريكية / مربع:* 5.1 × 5.1 سم\n"
            "  - 💳 *بطاقة عمل:* 8.5 × 5.5 سم\n"
            "  - 📸 *ستيكر بولارويد:* 7.0 × 7.0 سم\n\n"
            "• *📊 شبكات سريعة:* اختر فوراً 4 صور أو 6 صور أو 9 صور لملء الصفحة تلقائياً.\n"
            "• *↔️ التباعد بين الصور:* حافظ على مسافة 2 أو 3 مم بين الصور لسهولة القص وعدم تداخلها.\n"
            "• *🔒 قفل التناسب:* يحافظ على أبعاد وجهك طبيعية تماماً دون مط أو انكماش!"
        ),
    },
    {
        "step": 4,
        "title": "علامات القص والمقص ✂️",
        "content": (
            "✂️ *الخطوة 3: علامات القص والخطوط المستقيمة*\n\n"
            "هل عانيت من قص صور صغيرة بالمقص وحصلت على حواف متعرجة ومائلة؟\n\n"
            "• *✂️ علامات القص (مفعل):* نقوم تلقائياً برسم علامات زاوية دقيقة 3.5 مم حول كل صورة مع خطوط إرشادية خفيفة.\n"
            "• *طريقة الاستخدام:* ضع المسطرة بمحاذاة علامات الزوايا وقص بخط مستقيم باستخدام الكاتر أو المقص!\n"
            "• *🔲 الإطار الخارجي:* يمكنك إضافة إطار محدد بألوان (*أسود، رمادي، أبيض، أحمر*) وسماكة قابلة للتعديل لمظهر أنيق."
        ),
    },
    {
        "step": 5,
        "title": "صانع البوسترات الجدارية العملاقة 🧩",
        "content": (
            "🧩 *الخطوة 4: صناعة بوستر جداري ضخم*\n\n"
            "لا تملك طابعة ضخمة ومكلفة؟ يمكنك صنع بوستر جداري هائل باستخدام أوراق A4 عادية!\n\n"
            "• اضغط على *🔀 الوضع* للتحويل إلى *صانع البوسترات*.\n"
            "• اختر مقاس البوستر:\n"
            "  - *2 × 2:* 4 ورقات A4 (حوالي 42 × 60 سم، بحجم بوستر A2!)\n"
            "  - *3 × 3:* 9 ورقات A4 (حوالي 63 × 89 سم، بحجم بوستر عملاق A0!)\n"
            "  - *مخصص:* حتى 12 × 12 ورقة لجدارية كاملة.\n\n"
            "• *🏷 أدلة وهوامش اللصق الذكية:*\n"
            "تطبع كل ورقة مع هامش تداخل 10 مم مكتوب عليه *'الصق الورقة رقم 2 هنا'* وترقيم الورقة. "
            "تجميع البوستر يصبح بسيطاً وممتعاً مثل حل بازل سهل!"
        ),
    },
    {
        "step": 6,
        "title": "الطباعة في المنزل (القاعدة الذهبية رقم 1!) 🖨️",
        "content": (
            "🖨️ *الخطوة 5: طباعة الملف المصدر*\n\n"
            "بعد تجهيز المعاينة، اضغط على *📄 تصدير PDF*.\n\n"
            "⚠️ *أكبر خطأ يقع فيه المبتدئون:*\n"
            "عند فتح نافذة الطباعة على الكمبيوتر أو الهاتف، تختار برامج الطباعة تلقائياً خيار *'ملاءمة لمنطقة الطباعة Fit to Page'* مما يغير المقاسات الحقيقية!\n\n"
            "👉 **اختر دائماً: 'الحجم الفعلي Actual Size' أو '100% Scale'** في إعدادات الطابعة!\n"
            "• هذا يضمن طباعة صور جواز السفر وبطاقات العمل بمقاساتها المليمترية الدقيقة بنسبة 100%!\n"
            "• تأكد أن مقاس الورق في الطابعة مضبوط على **A4** (210 × 297 مم).\n"
            "• استخدم ورق صور (Glossy Photo Paper) للحصول على ألوان زاهية وساطعة!\n\n"
            "🎉 *أنت الآن جاهز للطباعة باحترافية تامة!*"
        ),
    },
]

TUTORIAL_FAQ_TEXT_EN = (
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

TUTORIAL_FAQ_TEXT_AR = (
    "❓ *برينت ماستر A4 — الأسئلة الشائعة والمصطلحات*\n\n"
    "• *ما فائدة 'قفل تناسق الأبعاد Aspect Ratio'؟*\n"
    "يحافظ على النسبة الطبيعية بين العرض والارتفاع حتى لا تظهر الوجوه ممتدة بالعرض أو مضغوطة بالطول.\n\n"
    "• *ما هو 'التدوير التلقائي 90° لأقصى استغلال'؟*\n"
    "يقوم البوت باختبار هل تدوير الصورة عرضياً سيتيح وضع عدد صور أكبر على نفس الورقة. إذا كان يقلل الهدر، يتم التدوير تلقائياً!\n\n"
    "• *ما هو 'تصدير الدفعات Batch Export'؟*\n"
    "إذا كنت بحاجة إلى 50 ستيكر لفعالية معينة، حدد الدفعة 50. سيقوم البوت بإنشاء ملف PDF متعدد الصفحات يحتوي بالضبط على 50 صورة دون زيادة أو نقصان!\n\n"
    "• *أيهما أفضل: ملف PDF أم صورة 300 DPI؟*\n"
    "  - *📄 ملف PDF:* الأفضل للطباعة المباشرة من الطابعة المنزلية أو المكتبية بمقاييس دقيقة.\n"
    "  - *🖼 صورة 300 DPI:* الأفضل إذا كنت سترسل الملف إلى استوديو تصوير فوتوغرافي أو مطبعة.\n\n"
    "• *لماذا تقطع طابعتي أطراف الورقة؟*\n"
    "معظم الطابعات المنزلية تحتوي على هامش ميكانيكي لا تستطيع الطباعة عليه. اضبط هامش الصفحة على *قياسي (10 مم)* أو *ضيق (5 مم)* لضمان بقاء كل الصور داخل النطاق القابل للطباعة!"
)

# Backwards compatibility aliases
TUTORIAL_STEPS = TUTORIAL_STEPS_EN
TUTORIAL_FAQ_TEXT = TUTORIAL_FAQ_TEXT_EN



def get_tutorial_step(step_idx: int, lang: str = "en") -> Tuple[str, InlineKeyboardMarkup]:
    """Returns the formatted text and navigation keyboard for a given step (1-indexed)."""
    steps_list = TUTORIAL_STEPS_AR if lang == "ar" else TUTORIAL_STEPS_EN
    step_idx = max(1, min(len(steps_list), step_idx))
    step_data = steps_list[step_idx - 1]
    total_steps = len(steps_list)

    if lang == "ar":
        header = f"📚 *دليل المبتدئين* — الخطوة {step_idx} من {total_steps}\n\n"
        btn_back = "⬅️ السابق"
        btn_next = "التالي ➡️"
        btn_faq = "❓ الأسئلة الشائعة"
        btn_demo = "🧪 تجربة صورة توضيحية"
        btn_exit = "« الخروج إلى المحرر الرئيسي"
    else:
        header = f"📚 *Beginner Tutorial* — Step {step_idx} of {total_steps}\n\n"
        btn_back = "⬅️ Back"
        btn_next = "Next ➡️"
        btn_faq = "❓ FAQ & Glossary"
        btn_demo = "🧪 Try Demo Image"
        btn_exit = "« Exit Tutorial to Editor"

    body = step_data["content"]
    full_text = header + body

    nav_row = []
    if step_idx > 1:
        nav_row.append(InlineKeyboardButton(btn_back, callback_data=f"tutorial:step_{step_idx - 1}"))
    if step_idx < total_steps:
        nav_row.append(InlineKeyboardButton(btn_next, callback_data=f"tutorial:step_{step_idx + 1}"))

    rows = []
    if nav_row:
        rows.append(nav_row)

    rows.append([
        InlineKeyboardButton(btn_faq, callback_data="tutorial:faq"),
        InlineKeyboardButton(btn_demo, callback_data="tutorial:demo"),
    ])
    rows.append([
        InlineKeyboardButton(btn_exit, callback_data="menu:main"),
    ])

    return full_text, InlineKeyboardMarkup(rows)


def get_tutorial_faq(lang: str = "en") -> Tuple[str, InlineKeyboardMarkup]:
    """Returns the FAQ text and navigation buttons."""
    if lang == "ar":
        faq_text = TUTORIAL_FAQ_TEXT_AR
        btn_back = "« العودة للدليل"
        btn_demo = "🧪 تجربة صورة توضيحية"
        btn_exit = "« العودة للمحرر الرئيسي"
    else:
        faq_text = TUTORIAL_FAQ_TEXT_EN
        btn_back = "« Back to Tutorial"
        btn_demo = "🧪 Try Demo Image"
        btn_exit = "« Exit to Main Editor"

    rows = [
        [
            InlineKeyboardButton(btn_back, callback_data="tutorial:step_1"),
            InlineKeyboardButton(btn_demo, callback_data="tutorial:demo"),
        ],
        [
            InlineKeyboardButton(btn_exit, callback_data="menu:main"),
        ],
    ]
    return faq_text, InlineKeyboardMarkup(rows)

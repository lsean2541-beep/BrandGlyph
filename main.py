import os
import io
import asyncio
import logging
from PIL import Image, ImageDraw, ImageFont
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Preset Premium Color Schemes (Background, Text/Accent)
COLOR_THEMES = {
    "theme_dark": ("#121212", "#00E5FF", "Dark Cyber"),       
    "theme_gold": ("#1A1A1A", "#D4AF37", "Luxury Gold"),     
    "theme_clean": ("#F5F5F5", "#2962FF", "Minimal Blue"),    
    "theme_sunset": ("#212121", "#FF6D00", "Sunset Glow")     
}

# Preset Layout Framing Styles
LAYOUT_STYLES = {
    "style_minimal": "Text Only (Ultra Minimalist)",
    "style_circle": "Text inside a Sleek Circle",
    "style_box": "Text Framed in a Square",
    "style_underline": "Text underlined with an Accent Bar"
}

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() # Reset user session data safely
    context.user_data["step"] = "awaiting_name"
    
    msg = (
        "✨ **Welcome to BrandGlyph!** ✨\n\n"
        "Let's craft a beautiful, minimalist logo for your business or project instantly.\n\n"
        "👉 **To start, please type your Brand Name or Initials below:**\n"
        "_(Keep it under 15 characters for the best visual layout)_"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# Handle Text Input safely matching workflow state
async def handle_brand_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure we are actually expecting a name right now
    if context.user_data.get("step") != "awaiting_name":
        await update.message.reply_text("⚠️ Please type /start to generate a fresh logo profile.")
        return

    brand_name = update.message.text.strip()
    
    if len(brand_name) > 20:
        await update.message.reply_text("⚠️ That name is a bit too long for a clean layout. Try a shorter name or initials!")
        return
        
    context.user_data["brand_name"] = brand_name
    context.user_data["step"] = "awaiting_color"
    
    # Render Color Selection Menu
    keyboard = []
    for key, (bg, fg, name) in COLOR_THEMES.items():
        keyboard.append([InlineKeyboardButton(f"🎨 {name}", callback_data=key)])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎨 Excellent. Now choose a **Color Palette** profile for your brand identity:", 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )

# Handle Color Choice
async def handle_color_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if context.user_data.get("step") != "awaiting_color":
        await query.message.reply_text("❌ Configuration sequence out of order. Run /start again.")
        return
        
    context.user_data["color_theme"] = query.data
    context.user_data["step"] = "awaiting_style"
    
    # Render Layout Selection Menu
    keyboard = []
    for key, name in LAYOUT_STYLES.items():
        keyboard.append([InlineKeyboardButton(f"📐 {name}", callback_data=key)])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📐 Next, select the **Geometric Layout Style** structural framework:", reply_markup=reply_markup)

# Generate and Deliver the Logo Graphic Matrix
async def generate_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if context.user_data.get("step") != "awaiting_style":
        await query.message.reply_text("❌ Configuration sequence out of order. Run /start again.")
        return
        
    layout_style = query.data
    brand_name = context.user_data.get("brand_name")
    theme_key = context.user_data.get("color_theme")
    
    if not brand_name or not theme_key:
        await query.message.edit_text("❌ Session expired or invalid inputs. Please restart using /start.")
        return
        
    await query.message.edit_text("⚡ Generating pixels, shapes, and asset parameters... please hold.")
    
    # Get configuration hex codes
    bg_color, fg_color, _ = COLOR_THEMES[theme_key]
    
    # Create clean 800x800 high resolution master canvas
    canvas_size = (800, 800)
    image = Image.new("RGB", canvas_size, fill=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Initialize basic typographic fallback architecture parameters
    font = ImageFont.load_default()
    
    # Process Layout Formations base designs
    if layout_style == "style_circle":
        draw.ellipse([150, 150, 650, 650], outline=fg_color, width=12)
    elif layout_style == "style_box":
        draw.rectangle([160, 160, 640, 640], outline=fg_color, width=12)
    elif layout_style == "style_underline":
        draw.line([200, 480, 600, 480], fill=fg_color, width=12)

    # High quality clean structural centering layer mapping
    text_layer = Image.new("RGBA", (400, 100), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text((200, 50), brand_name, fill=fg_color, font=font, anchor="mm")
    
    # Resize up cleanly using high interpolation to avoid rendering block distortion artifacts
    scaled_text = text_layer.resize((560, 140), Image.Resampling.LANCZOS)
    image.paste(scaled_text, (120, 330), scaled_text)
    
    # Compile directly into output system memory pipes
    out_buffer = io.BytesIO()
    image.save(out_buffer, format="PNG")
    out_buffer.seek(0)
    out_buffer.name = "brand_logo.png"
    
    # Send final image back to chat pipeline
    caption = f"✅ **Logo Generated Successfully!**\n\n🏷️ **Brand:** `{brand_name}`\n🎨 **Palette:** {COLOR_THEMES[theme_key][2]}\n📐 **Layout:** {LAYOUT_STYLES[layout_style]}"
    await query.message.reply_photo(photo=out_buffer, caption=caption, parse_mode="Markdown")
    await query.message.delete()
    
    # Clear user instance session memory profiles clear
    context.user_data.clear()

def main():
    # Explicit loop initialization block ensuring safe runtime under Python 3.14 on Render
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if not TOKEN:
        logger.error("No BOT_TOKEN found in environment config!")
        return

    application = Application.builder().token(TOKEN).build()

    # Dynamic Callback Routing Wireframe Handlers Configuration Map
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_color_choice, pattern="^theme_"))
    application.add_handler(CallbackQueryHandler(generate_logo, pattern="^style_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_brand_name))

    print("🤖 BrandGlyph core engine pipelines active and listening...")
    application.run_polling()

if __name__ == "__main__":
    main()

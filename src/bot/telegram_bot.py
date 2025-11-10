"""
Ethio Bingo Telegram Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from src.core.config import settings
from src.core.database import get_db
from src.models import Player
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class EthioBingoBot:
    """Main Telegram Bot class"""
    
    def __init__(self):
        self.app = None
    
    def setup(self):
        """Setup bot application"""
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        
        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("play", self.play_command))
        self.app.add_handler(CommandHandler("create", self.create_room_command))
        self.app.add_handler(CommandHandler("join", self.join_room_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Register or get player
        with get_db() as db:
            player = db.query(Player).filter(Player.telegram_id == str(user.id)).first()
            if not player:
                player = Player(
                    telegram_id=str(user.id),
                    display_name=user.full_name or user.username or f"Player{user.id}",
                    avatar_url=None
                )
                db.add(player)
                db.commit()
        
        welcome_text = f"""
🎉 *Welcome to Ethio Bingo!* 🎉

Hello {user.first_name}! 

Ethio Bingo is an exciting multiplayer Bingo game where you can:
• Play classic 75-ball or 90-ball Bingo
• Create private rooms with friends
• Join public games
• Win amazing prizes!

*Quick Start:*
• /play - Start playing now
• /create - Create a new game room
• /join [code] - Join a game with room code
• /help - Get help and instructions

Ready to play? Tap the button below!
"""
        
        keyboard = [
            [InlineKeyboardButton("🎮 Play Now", callback_data="play_now")],
            [InlineKeyboardButton("🏠 Create Room", callback_data="create_room")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 *Ethio Bingo - How to Play*

*Game Variants:*
• *75-Ball Bingo*: 5×5 grid with numbers 1-75
• *90-Ball Bingo*: 3×9 grid with numbers 1-90

*Commands:*
• /start - Start the bot
• /play - Quick play
• /create - Create new game room
• /join [code] - Join game with code
• /help - Show this help

*How to Play:*
1. Join or create a room
2. Get your bingo card(s)
3. Numbers are called automatically
4. Mark numbers on your card
5. Complete the pattern first to win!

*Winning Patterns:*
• Line (horizontal, vertical, diagonal)
• Four Corners
• Full House (complete card)

Good luck! 🍀
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def play_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /play command - open mini app"""
        # Create web app button
        web_app_url = f"{settings.telegram_webhook_url}/app"
        
        keyboard = [
            [InlineKeyboardButton(
                "🎮 Open Ethio Bingo",
                web_app=WebAppInfo(url=web_app_url)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎮 *Ready to Play!*\n\nTap the button below to open Ethio Bingo game:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def create_room_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command"""
        keyboard = [
            [InlineKeyboardButton("75-Ball Game", callback_data="create_75")],
            [InlineKeyboardButton("90-Ball Game", callback_data="create_90")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🏠 *Create New Game Room*\n\nSelect game type:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def join_room_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /join [code] command"""
        if context.args and len(context.args) > 0:
            room_code = context.args[0]
            # Open mini app with room code
            web_app_url = f"{settings.telegram_webhook_url}/app?room={room_code}"
            
            keyboard = [
                [InlineKeyboardButton(
                    f"🚪 Join Room {room_code}",
                    web_app=WebAppInfo(url=web_app_url)
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🚪 *Join Game Room*\n\nRoom Code: `{room_code}`\n\nTap to join:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "❌ Please provide a room code.\n\nUsage: /join [room_code]"
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "play_now":
            await self.play_command(query, context)
        elif query.data == "create_room":
            await self.create_room_command(query, context)
        elif query.data == "help":
            await self.help_command(query, context)
        elif query.data.startswith("create_"):
            variant = query.data.replace("create_", "")
            web_app_url = f"{settings.telegram_webhook_url}/app?action=create&variant={variant}"
            
            keyboard = [
                [InlineKeyboardButton(
                    f"🎮 Create {variant.upper()}-Ball Room",
                    web_app=WebAppInfo(url=web_app_url)
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"🏠 *Creating {variant.upper()}-Ball Game*\n\nTap to configure and start:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Ethio Bingo Bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Create bot instance
bot = EthioBingoBot()

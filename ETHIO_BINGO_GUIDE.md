# 🎉 Ethio Bingo - Telegram Bot Game

A scalable, real-time multiplayer Bingo game built as a Telegram Mini App with support for 75-ball and 90-ball variants.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### Core Features
- **Multiple Game Variants**: Support for 75-ball and 90-ball Bingo
- **Real-time Multiplayer**: WebSocket-based real-time game updates
- **Telegram Integration**: Seamless integration as a Telegram Mini App
- **Scalable Architecture**: Redis-based pub/sub for handling hundreds of concurrent players
- **Secure RNG**: Cryptographically secure random number generation with audit trails
- **Pattern Matching**: Multiple winning patterns (lines, diagonals, four corners, full house)
- **Auto-marking**: Automatic number marking on cards
- **Responsive UI**: Mobile-first design optimized for Telegram

### Game Features
- Create private rooms or join public games
- Host controls for game management
- Multiple cards per player support
- Real-time number drawing
- Instant claim verification
- Winner announcements
- Game audit logs

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.9+
- FastAPI for REST API and WebSocket
- SQLAlchemy for ORM
- PostgreSQL for persistent storage
- Redis for caching and pub/sub
- python-telegram-bot for Telegram integration

**Frontend:**
- HTML5/CSS3/JavaScript (Vanilla)
- Telegram Web App SDK
- WebSocket for real-time updates
- Responsive design for mobile

### System Architecture

```
┌─────────────┐
│   Telegram  │
│     Bot     │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
┌──────▼──────┐  ┌───▼────────┐
│  FastAPI    │  │  Mini App  │
│   Server    │◄─┤ (Frontend) │
└──────┬──────┘  └────────────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
┌──────▼──────┐ ┌────▼─────┐  ┌────▼─────┐
│ PostgreSQL  │ │  Redis   │  │WebSocket │
└─────────────┘ └──────────┘  └──────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+
- Redis 6+
- Telegram Bot Token (from @BotFather)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YonasGr/bingo.git
cd bingo
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL database**
```bash
# Create database
createdb ethio_bingo

# Or using psql
psql -U postgres
CREATE DATABASE ethio_bingo;
\q
```

5. **Setup Redis**
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

6. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/ethio_bingo
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

7. **Initialize database**
```bash
python -c "from src.core.database import init_db; init_db()"
```

8. **Run the application**
```bash
# Run both bot and API server
python main.py

# Or run separately:
# Bot only
python main.py bot

# API only
python main.py api
```

## 📱 Telegram Bot Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token

### 2. Configure Mini App

1. Send `/mybots` to BotFather
2. Select your bot
3. Choose "Bot Settings" → "Menu Button"
4. Set the Web App URL: `https://your-domain.com/app`

### 3. Set Bot Commands

Send to BotFather:
```
/setcommands

start - Start the bot
play - Quick play
create - Create new game room
join - Join game with code
help - Get help and instructions
```

## 🎮 How to Play

### Creating a Game

1. Start a chat with your bot in Telegram
2. Send `/create` command
3. Choose game variant (75-ball or 90-ball)
4. Configure game settings in the Mini App
5. Share the room code with friends
6. Start the game when ready

### Joining a Game

1. Receive a room code from a friend
2. Send `/join [room_code]` to the bot
3. Tap to open the game
4. Wait for the host to start

### Playing

1. Watch as numbers are called automatically
2. Numbers are auto-marked on your card
3. Complete the required pattern first
4. Tap "BINGO!" to claim your win
5. Server verifies your claim instantly

## 🔧 Configuration

### Game Settings

Edit `src/core/config.py` or use environment variables:

```python
# Maximum players per room
MAX_PLAYERS_PER_ROOM = 100

# Time between number draws (seconds)
DEFAULT_DRAW_INTERVAL = 5

# Auto-mark numbers on cards
AUTO_MARK_ENABLED = True
```

### Patterns

Available winning patterns (75-ball):
- Horizontal lines
- Vertical lines
- Diagonal lines
- Four corners
- Full house

90-ball patterns:
- One line
- Two lines
- Full house

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest src/tests/test_game_service.py -v
```

## 📊 Performance & Scalability

### Design Considerations

- **Horizontal Scaling**: Stateless API design allows multiple server instances
- **Redis Pub/Sub**: Handles real-time message broadcasting across servers
- **Connection Pooling**: Database connection pooling for efficient resource usage
- **WebSocket Management**: Efficient connection management with automatic cleanup
- **Caching**: Redis caching for frequently accessed data

### Load Testing

The system is designed to handle:
- 100+ concurrent players per room
- 1000+ simultaneous WebSocket connections
- Sub-second claim verification
- Minimal latency for number broadcasting

### Optimization Tips

1. **Database**: Use connection pooling and proper indexing
2. **Redis**: Use Redis Cluster for high availability
3. **API**: Deploy behind a load balancer (nginx, HAProxy)
4. **CDN**: Serve static assets via CDN
5. **Monitoring**: Use application monitoring (Prometheus, Grafana)

## 🔒 Security Features

- **Cryptographic RNG**: Uses Python's `secrets` module for secure randomization
- **Audit Trails**: Complete draw logs with hash chains
- **Claim Verification**: Server-side validation prevents cheating
- **Rate Limiting**: Prevents spam and abuse
- **Input Validation**: All inputs validated with Pydantic
- **JWT Authentication**: Secure token-based authentication

## 📁 Project Structure

```
bingo/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py           # FastAPI application
│   ├── bot/
│   │   ├── __init__.py
│   │   └── telegram_bot.py   # Telegram bot
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── redis.py          # Redis client
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py       # SQLAlchemy models
│   ├── services/
│   │   ├── __init__.py
│   │   └── game_service.py   # Game logic
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Styles
│   │   └── js/
│   │       └── app.js        # Frontend JS
│   ├── templates/
│   │   └── index.html        # Mini App HTML
│   └── tests/
│       ├── __init__.py
│       └── test_game_service.py
├── .env.example              # Example environment file
├── .gitignore
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🛠️ Development

### Code Style

The project follows PEP 8 guidelines. Use the provided formatters:

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes with tests
3. Ensure all tests pass: `pytest`
4. Format code: `black src/`
5. Submit pull request

## 🚀 Deployment

### Production Deployment

1. **Using Docker** (Recommended)
```bash
# Build image
docker build -t ethio-bingo .

# Run with docker-compose
docker-compose up -d
```

2. **Using Systemd**
```bash
# Create systemd service
sudo nano /etc/systemd/system/ethio-bingo.service

# Enable and start
sudo systemctl enable ethio-bingo
sudo systemctl start ethio-bingo
```

3. **Using Supervisor**
```bash
# Install supervisor
sudo apt-get install supervisor

# Configure in /etc/supervisor/conf.d/ethio-bingo.conf
```

### Webhook Setup (Production)

For production, use webhooks instead of polling:

```python
from src.bot.telegram_bot import bot

# Set webhook
bot.app.bot.set_webhook(
    url=f"{settings.telegram_webhook_url}/webhook",
    allowed_updates=Update.ALL_TYPES
)
```

## 📝 API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /api/rooms` - Create game room
- `GET /api/rooms/{room_id}` - Get room details
- `POST /api/rooms/{room_id}/join` - Join room
- `POST /api/rooms/{room_id}/start` - Start game
- `POST /api/rooms/{room_id}/draw` - Draw number
- `POST /api/rooms/{room_id}/claim` - Claim bingo
- `WS /ws/{room_id}` - WebSocket connection

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Telegram Bot API for excellent documentation
- FastAPI for the amazing web framework
- The open-source community

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## 🗺️ Roadmap

### Phase 2 Features
- [ ] User profiles and statistics
- [ ] Leaderboards
- [ ] Prize system
- [ ] Custom card themes
- [ ] Sound effects
- [ ] Multiple simultaneous games
- [ ] Tournament mode
- [ ] Social features (chat, emoji reactions)
- [ ] Payment integration
- [ ] Admin dashboard

### Phase 3 Features
- [ ] Mobile native apps (iOS/Android)
- [ ] Voice announcements
- [ ] Advanced analytics
- [ ] Machine learning for fraud detection
- [ ] Multi-language support
- [ ] Blockchain integration for provably fair games

---

Made with ❤️ for the Bingo community

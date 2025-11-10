# API Reference - Ethio Bingo

## Base URL

Development: `http://localhost:8000`
Production: `https://yourdomain.com`

## Authentication

Currently using Telegram user authentication. Future versions will include JWT tokens.

## REST API Endpoints

### Health Check

#### GET /health
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Room Management

#### POST /api/rooms
Create a new game room.

**Request Body:**
```json
{
  "variant": "75",
  "cards_per_player": 1,
  "pattern": "horizontal_line",
  "auto_draw": true,
  "draw_interval": 5,
  "player_id": "tg_12345"
}
```

**Response:**
```json
{
  "room_id": "uuid-here",
  "room_code": "ABCD1234",
  "variant": "75",
  "state": "lobby",
  "pattern": "horizontal_line",
  "created_at": "2024-01-01T00:00:00.000000"
}
```

#### GET /api/rooms/{room_id}
Get room details.

**Response:**
```json
{
  "id": "uuid-here",
  "host_id": "uuid-here",
  "variant": "75",
  "state": "lobby",
  "pattern": {
    "id": "horizontal_line",
    "variant": "75"
  },
  "called_numbers": [],
  "winners": [],
  "players": [
    {
      "id": "uuid-here",
      "name": "Player Name"
    }
  ],
  "auto_draw": true,
  "draw_interval": 5
}
```

#### POST /api/rooms/{room_id}/join
Join a game room.

**Request Body:**
```json
{
  "player_id": "tg_12345"
}
```

**Response:**
```json
{
  "message": "Joined room successfully",
  "cards": [
    {
      "id": "uuid-here",
      "grid": [
        [
          {"value": 1, "marked": false, "free": false},
          {"value": 16, "marked": false, "free": false},
          ...
        ],
        ...
      ]
    }
  ]
}
```

#### POST /api/rooms/{room_id}/start
Start the game (host only).

**Response:**
```json
{
  "message": "Game started",
  "state": "running"
}
```

#### POST /api/rooms/{room_id}/draw
Manually draw next number (host only, when auto_draw is false).

**Response:**
```json
{
  "number": 42,
  "sequence": 1
}
```

#### POST /api/rooms/{room_id}/claim
Claim bingo.

**Request Body:**
```json
{
  "player_id": "tg_12345",
  "card_id": "uuid-here"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Valid bingo!",
  "status": "accepted"
}
```

## WebSocket API

### Connection

#### WS /ws/{room_id}
Connect to room for real-time updates.

### Client to Server Messages

#### Ping
Keep connection alive.

```json
{
  "type": "ping"
}
```

### Server to Client Messages

#### Game Started
Sent when host starts the game.

```json
{
  "type": "game_started",
  "room_id": "uuid-here"
}
```

#### Number Drawn
Sent when a new number is called.

```json
{
  "type": "number_drawn",
  "number": 42,
  "sequence": 1
}
```

#### Claim Result
Sent after a claim is verified.

```json
{
  "type": "claim_result",
  "player_id": "uuid-here",
  "valid": true,
  "message": "Valid bingo!"
}
```

#### Player Joined
Sent when a player joins the room.

```json
{
  "type": "player_joined",
  "player": {
    "id": "uuid-here",
    "name": "Player Name"
  }
}
```

#### Pong
Response to ping.

```json
{
  "type": "pong"
}
```

## Data Models

### Card Grid Structure (75-ball)

```json
[
  [
    {"value": 1, "marked": false, "free": false},
    {"value": 16, "marked": false, "free": false},
    {"value": 31, "marked": false, "free": false},
    {"value": 46, "marked": false, "free": false},
    {"value": 61, "marked": false, "free": false}
  ],
  [
    {"value": 2, "marked": false, "free": false},
    {"value": 17, "marked": false, "free": false},
    {"value": 32, "marked": false, "free": false},
    {"value": 47, "marked": false, "free": false},
    {"value": 62, "marked": false, "free": false}
  ],
  [
    {"value": 3, "marked": false, "free": false},
    {"value": 18, "marked": false, "free": false},
    {"value": null, "marked": true, "free": true},
    {"value": 48, "marked": false, "free": false},
    {"value": 63, "marked": false, "free": false}
  ],
  [
    {"value": 4, "marked": false, "free": false},
    {"value": 19, "marked": false, "free": false},
    {"value": 34, "marked": false, "free": false},
    {"value": 49, "marked": false, "free": false},
    {"value": 64, "marked": false, "free": false}
  ],
  [
    {"value": 5, "marked": false, "free": false},
    {"value": 20, "marked": false, "free": false},
    {"value": 35, "marked": false, "free": false},
    {"value": 50, "marked": false, "free": false},
    {"value": 65, "marked": false, "free": false}
  ]
]
```

### Card Grid Structure (90-ball)

```json
[
  [
    {"value": 1, "marked": false, "free": false},
    {"value": null, "marked": false, "free": false},
    {"value": 23, "marked": false, "free": false},
    {"value": null, "marked": false, "free": false},
    {"value": 45, "marked": false, "free": false},
    {"value": 56, "marked": false, "free": false},
    {"value": null, "marked": false, "free": false},
    {"value": 78, "marked": false, "free": false},
    {"value": null, "marked": false, "free": false}
  ],
  // ... 2 more rows
]
```

## Winning Patterns

### 75-ball Patterns

- **horizontal_line**: Any horizontal line
- **vertical_line**: Any vertical line
- **diagonal**: Any diagonal line
- **four_corners**: Four corner cells
- **full_house**: All cells marked

### 90-ball Patterns

- **one_line**: Complete one row
- **two_lines**: Complete two rows
- **full_house**: All numbers marked

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently no rate limiting implemented. Will be added in Phase 2.

## Pagination

Currently no pagination. All results returned at once. Will be added in Phase 2.

## Examples

### Create and Start a Game

```bash
# 1. Create room
curl -X POST http://localhost:8000/api/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "variant": "75",
    "cards_per_player": 1,
    "pattern": "horizontal_line",
    "player_id": "tg_12345"
  }'

# Response: {"room_id": "abc123...", "room_code": "ABCD1234", ...}

# 2. Join room
curl -X POST http://localhost:8000/api/rooms/abc123.../join \
  -H "Content-Type: application/json" \
  -d '{"player_id": "tg_12345"}'

# 3. Start game
curl -X POST http://localhost:8000/api/rooms/abc123.../start

# 4. Connect WebSocket
wscat -c ws://localhost:8000/ws/abc123...
```

### JavaScript Example

```javascript
// Create room
const response = await fetch('http://localhost:8000/api/rooms', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    variant: '75',
    cards_per_player: 1,
    pattern: 'horizontal_line',
    player_id: 'tg_12345'
  })
});
const data = await response.json();
console.log('Room created:', data.room_id);

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/${data.room_id}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
  
  if (message.type === 'number_drawn') {
    console.log('Number called:', message.number);
  }
};

// Claim bingo
const claimResponse = await fetch(
  `http://localhost:8000/api/rooms/${data.room_id}/claim`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      player_id: 'tg_12345',
      card_id: cardId
    })
  }
);
```

## Changelog

### Version 1.0.0 (Phase 1)
- Initial release
- Basic game functionality
- REST API endpoints
- WebSocket real-time updates
- 75-ball and 90-ball support
- Pattern verification

### Future Versions
- Version 1.1.0: User authentication, statistics
- Version 1.2.0: Leaderboards, achievements
- Version 2.0.0: Tournament mode, prizes

## Support

For API issues or questions:
- GitHub Issues: https://github.com/YonasGr/bingo/issues
- Documentation: See ETHIO_BINGO_GUIDE.md

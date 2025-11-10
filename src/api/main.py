"""
FastAPI Application for Ethio Bingo
Handles REST API, WebSocket connections, and serves Telegram Mini App
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
import hashlib

from src.core.config import settings
from src.core.database import get_db_session, init_db
from src.core.redis import redis_client
from src.models import GameRoom, Player, Card, Claim
from src.services import CardGenerator, DrawEngine, PatternVerifier

app = FastAPI(title="Ethio Bingo API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for connection in dead_connections:
                self.disconnect(connection, room_id)

manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    init_db()
    await redis_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await redis_client.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Ethio Bingo API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/app", response_class=HTMLResponse)
async def mini_app(request: Request):
    """Serve Telegram Mini App"""
    return templates.TemplateResponse("index.html", {"request": request})


# Room Management Endpoints

@app.post("/api/rooms")
async def create_room(
    variant: str = "75",
    cards_per_player: int = 1,
    pattern: str = "horizontal_line",
    auto_draw: bool = True,
    draw_interval: int = 5,
    player_id: str = None,
    db: Session = Depends(get_db_session)
):
    """Create a new game room"""
    try:
        # Set number range based on variant
        if variant == "90":
            min_num, max_num = 1, 90
        else:
            min_num, max_num = 1, 75
        
        # Initialize draw pool
        draw_pool, seed = DrawEngine.initialize_draw_pool(min_num, max_num)
        
        # Create pattern configuration
        pattern_config = {
            "id": pattern,
            "variant": variant
        }
        
        # Create room
        room = GameRoom(
            host_id=player_id,
            variant=variant,
            number_range_min=min_num,
            number_range_max=max_num,
            cards_per_player=cards_per_player,
            pattern=pattern_config,
            state="lobby",
            called_numbers=[],
            draw_pool=draw_pool,
            winners=[],
            draw_interval=draw_interval,
            auto_draw=auto_draw
        )
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        # Generate room code (short version of UUID)
        room_code = room.id[:8].upper()
        
        return {
            "room_id": room.id,
            "room_code": room_code,
            "variant": variant,
            "state": room.state,
            "pattern": pattern,
            "created_at": room.created_at.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str, db: Session = Depends(get_db_session)):
    """Get room details"""
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get players in room
    cards = db.query(Card).filter(Card.room_id == room_id).all()
    player_ids = list(set([card.owner_id for card in cards]))
    players = db.query(Player).filter(Player.id.in_(player_ids)).all() if player_ids else []
    
    return {
        "id": room.id,
        "host_id": room.host_id,
        "variant": room.variant,
        "state": room.state,
        "pattern": room.pattern,
        "called_numbers": room.called_numbers,
        "winners": room.winners,
        "players": [{"id": p.id, "name": p.display_name} for p in players],
        "auto_draw": room.auto_draw,
        "draw_interval": room.draw_interval
    }


@app.post("/api/rooms/{room_id}/join")
async def join_room(
    room_id: str,
    player_id: str,
    db: Session = Depends(get_db_session)
):
    """Join a game room"""
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.state != "lobby":
        raise HTTPException(status_code=400, detail="Room is not in lobby state")
    
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Generate cards for player
    cards_data = []
    for _ in range(room.cards_per_player):
        card_grid = CardGenerator.generate_card(room.variant)
        card = Card(
            room_id=room_id,
            owner_id=player_id,
            variant=room.variant,
            grid=card_grid
        )
        db.add(card)
        cards_data.append(card)
    
    db.commit()
    
    # Broadcast player joined
    await manager.broadcast(room_id, {
        "type": "player_joined",
        "player": {
            "id": player.id,
            "name": player.display_name
        }
    })
    
    return {
        "message": "Joined room successfully",
        "cards": [{"id": c.id, "grid": c.grid} for c in cards_data]
    }


@app.post("/api/rooms/{room_id}/start")
async def start_game(room_id: str, db: Session = Depends(get_db_session)):
    """Start the game"""
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.state != "lobby":
        raise HTTPException(status_code=400, detail="Game already started")
    
    room.state = "running"
    db.commit()
    
    # Broadcast game started
    await manager.broadcast(room_id, {
        "type": "game_started",
        "room_id": room_id
    })
    
    # Start auto-draw if enabled
    if room.auto_draw:
        asyncio.create_task(auto_draw_task(room_id))
    
    return {"message": "Game started", "state": "running"}


@app.post("/api/rooms/{room_id}/draw")
async def manual_draw(room_id: str, db: Session = Depends(get_db_session)):
    """Manually draw next number"""
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.state != "running":
        raise HTTPException(status_code=400, detail="Game not running")
    
    # Draw number
    draw_pool = room.draw_pool
    number = DrawEngine.draw_number(draw_pool)
    
    if number is None:
        return {"message": "No more numbers to draw"}
    
    # Update room
    called_numbers = room.called_numbers
    called_numbers.append(number)
    room.called_numbers = called_numbers
    room.draw_pool = draw_pool
    db.commit()
    
    # Broadcast number drawn
    await manager.broadcast(room_id, {
        "type": "number_drawn",
        "number": number,
        "sequence": len(called_numbers)
    })
    
    return {"number": number, "sequence": len(called_numbers)}


@app.post("/api/rooms/{room_id}/claim")
async def claim_bingo(
    room_id: str,
    player_id: str,
    card_id: str,
    db: Session = Depends(get_db_session)
):
    """Claim bingo"""
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Verify claim
    pattern_name = room.pattern.get("id", "horizontal_line")
    is_valid, message = PatternVerifier.verify_claim(
        card.grid,
        room.called_numbers,
        pattern_name,
        room.variant
    )
    
    # Create claim record
    claim = Claim(
        room_id=room_id,
        player_id=player_id,
        card_id=card_id,
        claimed_pattern=pattern_name,
        status="accepted" if is_valid else "rejected",
        verification_message=message,
        verified_at=datetime.utcnow() if is_valid else None
    )
    db.add(claim)
    
    if is_valid:
        # Add to winners
        winners = room.winners
        winners.append({
            "player_id": player_id,
            "card_id": card_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        room.winners = winners
        room.state = "finished"
    
    db.commit()
    
    # Broadcast claim result
    await manager.broadcast(room_id, {
        "type": "claim_result",
        "player_id": player_id,
        "valid": is_valid,
        "message": message
    })
    
    return {
        "valid": is_valid,
        "message": message,
        "status": claim.status
    }


# WebSocket endpoint
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket connection for real-time updates"""
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle client messages if needed
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


# Background task for auto-draw
async def auto_draw_task(room_id: str):
    """Background task to automatically draw numbers"""
    while True:
        try:
            with get_db_session() as db:
                room = next(db.query(GameRoom).filter(GameRoom.id == room_id).first())
                
                if not room or room.state != "running":
                    break
                
                # Draw number
                draw_pool = room.draw_pool
                number = DrawEngine.draw_number(draw_pool)
                
                if number is None:
                    break
                
                # Update room
                called_numbers = room.called_numbers
                called_numbers.append(number)
                room.called_numbers = called_numbers
                room.draw_pool = draw_pool
                db.commit()
                
                # Broadcast
                await manager.broadcast(room_id, {
                    "type": "number_drawn",
                    "number": number,
                    "sequence": len(called_numbers)
                })
                
                # Wait for draw interval
                await asyncio.sleep(room.draw_interval)
        
        except Exception as e:
            print(f"Error in auto_draw_task: {e}")
            break


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

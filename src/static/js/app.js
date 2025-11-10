// Ethio Bingo - Main Application JavaScript

// Initialize Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Application State
const state = {
    roomId: null,
    playerId: null,
    cards: [],
    currentCard: null,
    calledNumbers: [],
    isHost: false,
    ws: null
};

// API Base URL
const API_BASE = window.location.origin;

// Initialize Application
async function init() {
    try {
        // Get Telegram user data
        const user = tg.initDataUnsafe.user;
        if (user) {
            state.playerId = `tg_${user.id}`;
        }
        
        // Apply Telegram theme
        if (tg.colorScheme === 'dark') {
            document.body.classList.add('telegram-dark');
        }
        
        // Parse URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const action = urlParams.get('action');
        const roomCode = urlParams.get('room');
        const variant = urlParams.get('variant') || '75';
        
        // Setup event listeners
        setupEventListeners();
        
        // Handle different actions
        if (action === 'create') {
            await createRoom(variant);
        } else if (roomCode) {
            await joinRoomByCode(roomCode);
        } else {
            showScreen('lobby-screen');
        }
        
        hideScreen('loading-screen');
    } catch (error) {
        console.error('Initialization error:', error);
        tg.showAlert('Failed to initialize app. Please try again.');
    }
}

// Screen Management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function hideScreen(screenId) {
    document.getElementById(screenId).classList.remove('active');
}

// Event Listeners Setup
function setupEventListeners() {
    document.getElementById('btn-create').addEventListener('click', () => createRoom('75'));
    document.getElementById('btn-quick-play').addEventListener('click', quickPlay);
    document.getElementById('btn-start').addEventListener('click', startGame);
    document.getElementById('btn-claim').addEventListener('click', claimBingo);
    document.getElementById('btn-new-game').addEventListener('click', () => {
        location.reload();
    });
}

// Room Management
async function createRoom(variant = '75') {
    try {
        const response = await fetch(`${API_BASE}/api/rooms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                variant: variant,
                cards_per_player: 1,
                pattern: 'horizontal_line',
                auto_draw: true,
                draw_interval: 5,
                player_id: state.playerId
            })
        });
        
        const data = await response.json();
        state.roomId = data.room_id;
        state.isHost = true;
        
        // Update UI
        document.getElementById('room-code').textContent = data.room_code;
        document.getElementById('room-variant').textContent = `${variant}-Ball`;
        document.getElementById('room-pattern').textContent = 'Horizontal Line';
        document.getElementById('room-info').style.display = 'block';
        document.getElementById('btn-start').style.display = 'block';
        
        // Join the created room
        await joinRoom(state.roomId);
        
        tg.showAlert(`Room created! Code: ${data.room_code}`);
    } catch (error) {
        console.error('Create room error:', error);
        tg.showAlert('Failed to create room');
    }
}

async function joinRoomByCode(roomCode) {
    try {
        // In a real implementation, you'd have an endpoint to resolve room code to ID
        // For now, we'll use the code as the ID
        await joinRoom(roomCode);
    } catch (error) {
        console.error('Join room error:', error);
        tg.showAlert('Failed to join room');
    }
}

async function joinRoom(roomId) {
    try {
        const response = await fetch(`${API_BASE}/api/rooms/${roomId}/join`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: state.playerId })
        });
        
        const data = await response.json();
        state.cards = data.cards;
        state.currentCard = data.cards[0];
        
        // Connect WebSocket
        connectWebSocket(roomId);
        
        showScreen('lobby-screen');
    } catch (error) {
        console.error('Join room error:', error);
        throw error;
    }
}

async function quickPlay() {
    // Create a room and auto-start
    await createRoom('75');
    setTimeout(() => startGame(), 1000);
}

async function startGame() {
    try {
        const response = await fetch(`${API_BASE}/api/rooms/${state.roomId}/start`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showGameScreen();
        }
    } catch (error) {
        console.error('Start game error:', error);
        tg.showAlert('Failed to start game');
    }
}

// WebSocket Connection
function connectWebSocket(roomId) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/${roomId}`;
    
    state.ws = new WebSocket(wsUrl);
    
    state.ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    state.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    state.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    state.ws.onclose = () => {
        console.log('WebSocket disconnected');
    };
    
    // Keep alive
    setInterval(() => {
        if (state.ws.readyState === WebSocket.OPEN) {
            state.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }, 30000);
}

function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'game_started':
            showGameScreen();
            break;
        
        case 'number_drawn':
            addCalledNumber(message.number);
            updateLastNumber(message.number);
            autoMarkCard(message.number);
            break;
        
        case 'claim_result':
            handleClaimResult(message);
            break;
        
        case 'player_joined':
            addPlayerToList(message.player);
            break;
    }
}

// Game Screen
function showGameScreen() {
    showScreen('game-screen');
    renderCard(state.currentCard);
}

function renderCard(card) {
    const container = document.getElementById('card-container');
    container.innerHTML = '';
    
    const variant = card.variant || '75';
    const cardDiv = document.createElement('div');
    cardDiv.className = 'bingo-card';
    
    // Add column headers for 75-ball
    if (variant === '75') {
        const headerDiv = document.createElement('div');
        headerDiv.className = 'card-header';
        ['B', 'I', 'N', 'G', 'O'].forEach(letter => {
            const label = document.createElement('div');
            label.className = 'card-column-label';
            label.textContent = letter;
            headerDiv.appendChild(label);
        });
        cardDiv.appendChild(headerDiv);
    }
    
    // Add grid
    const gridDiv = document.createElement('div');
    gridDiv.className = `card-grid card-grid-${variant}`;
    
    card.grid.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'card-cell';
            cellDiv.dataset.row = rowIndex;
            cellDiv.dataset.col = colIndex;
            
            if (cell.free) {
                cellDiv.classList.add('free');
                cellDiv.textContent = 'FREE';
            } else if (cell.value === null) {
                cellDiv.classList.add('blank');
            } else {
                cellDiv.textContent = cell.value;
                if (cell.marked) {
                    cellDiv.classList.add('marked');
                }
                
                // Add click handler for manual marking
                cellDiv.addEventListener('click', () => {
                    toggleCellMark(rowIndex, colIndex);
                });
            }
            
            gridDiv.appendChild(cellDiv);
        });
    });
    
    cardDiv.appendChild(gridDiv);
    container.appendChild(cardDiv);
}

function toggleCellMark(row, col) {
    const cell = state.currentCard.grid[row][col];
    if (cell.value !== null && !cell.free) {
        cell.marked = !cell.marked;
        renderCard(state.currentCard);
    }
}

function autoMarkCard(number) {
    let updated = false;
    state.currentCard.grid.forEach(row => {
        row.forEach(cell => {
            if (cell.value === number && !cell.marked) {
                cell.marked = true;
                updated = true;
            }
        });
    });
    
    if (updated) {
        renderCard(state.currentCard);
        // Vibrate for feedback
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('light');
        }
    }
}

function addCalledNumber(number) {
    state.calledNumbers.push(number);
    
    const strip = document.getElementById('called-numbers-strip');
    const chip = document.createElement('div');
    chip.className = 'called-number-chip';
    chip.textContent = number;
    strip.appendChild(chip);
    
    // Scroll to end
    strip.scrollLeft = strip.scrollWidth;
    
    // Update counter
    document.getElementById('numbers-called').textContent = state.calledNumbers.length;
}

function updateLastNumber(number) {
    document.getElementById('last-number').textContent = number;
}

// Claim Bingo
async function claimBingo() {
    try {
        const response = await fetch(`${API_BASE}/api/rooms/${state.roomId}/claim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: state.playerId,
                card_id: state.currentCard.id
            })
        });
        
        const data = await response.json();
        
        if (data.valid) {
            tg.HapticFeedback?.notificationOccurred('success');
        } else {
            tg.HapticFeedback?.notificationOccurred('error');
            tg.showAlert(data.message);
        }
    } catch (error) {
        console.error('Claim error:', error);
        tg.showAlert('Failed to submit claim');
    }
}

function handleClaimResult(message) {
    if (message.valid) {
        document.getElementById('winner-message').textContent = 
            message.player_id === state.playerId ? 
            'Congratulations! You won!' : 
            'Game Over! Another player won.';
        showScreen('winner-screen');
    }
}

// Helper Functions
function addPlayerToList(player) {
    const container = document.getElementById('players-container');
    const playerDiv = document.createElement('div');
    playerDiv.className = 'player-item';
    playerDiv.innerHTML = `
        <div class="player-avatar">${player.name.charAt(0).toUpperCase()}</div>
        <div>${player.name}</div>
    `;
    container.appendChild(playerDiv);
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

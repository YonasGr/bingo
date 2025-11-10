# Bingo Game — Technical Specification & Developer Guide

## 1. Overview

**Purpose:** Provide a clear, implementable specification for a digital Bingo game (web & mobile) supporting common variants (75-ball and 90-ball), multiplayer sessions, customizable rules, and secure/random draws.

**Audience:** Backend & frontend developers, QA engineers, product owner.

**High-level goals:**

* Robust RNG and auditable draws.
* Real-time multiplayer playability and low-latency updates.
* Flexible rule configurator for hosts.
* Clear UI/UX for players on desktop & mobile.
* Accessibility and performance for large rooms.

---

## 2. Supported Variants

1. **75-ball (Standard US)**

   * Card: 5×5 grid. Columns labeled B, I, N, G, O.
   * Numbers: 1–75. Typical column ranges: B(1–15), I(16–30), N(31–45), G(46–60), O(61–75).
   * Center tile: Free (N column, row 3).
2. **90-ball (UK/International)**

   * Card: 3 rows × 9 columns.
   * Numbers: 1–90. Each row has 5 numbers and 4 blanks.
   * Typical winning targets: 1 line, 2 lines, full house.
3. **Custom modes**

   * Grid sizes, number ranges, special symbols (kids), and custom winning patterns (X, four corners, T, etc.).

---

## 3. Game Rules (Configurable)

* **Players per room:** configurable (1..unbounded).
* **Cards per player:** configurable (1..n).
* **Winning patterns:** host picks from preset list or defines custom mask(s).
* **Prize rule:** first valid claim wins, or split if simultaneous. Admin chooses.
* **Claim verification:** strict validation against called numbers.
* **Draw cadence:** time between calls can be automated or manual by host.

---

## 4. Data Models

(Example JSON schema style)

### 4.1 Player

```json
{
  "id": "uuid",
  "displayName": "string",
  "avatarUrl": "string|null",
  "connected": true,
  "cards": ["cardId", ...]
}
```

### 4.2 Card

```json
{
  "id": "uuid",
  "variant": "75|90|custom",
  "grid": [[{ "value": number|null, "marked": bool }]],
  "ownerId": "uuid",
  "createdAt": "iso8601"
}
```

### 4.3 GameRoom / Session

```json
{
  "id": "uuid",
  "hostId": "uuid",
  "variant": "75|90|custom",
  "numberRange": {"min":1, "max":75},
  "cardsPerPlayer": 1,
  "pattern": {"id":"line","mask": [[0/1]] /* matrix mask */},
  "state": "lobby|running|verifying|finished",
  "calledNumbers": [int],
  "drawPool": [int],
  "winners": [{"playerId": "uuid","cardId":"uuid","timestamp":"iso8601"}],
  "createdAt": "iso8601"
}
```

### 4.4 DrawLog (audit)

```json
{
  "gameId":"uuid",
  "sequence": [{"drawNumber":1,"value":42,"source":"serverRNG","hash":"sha256(...)"}],
  "seed": "base64-seed-or-public-key",
  "finalHash":"sha256(...)"
}
```

---

## 5. APIs (HTTP + WebSocket)

Design: REST for setup & queries; WebSocket (or WebRTC/data channels) for real-time events.

### 5.1 REST Endpoints (examples)

* `POST /api/rooms` — Create new room (body: variant, pattern, cardsPerPlayer, host settings). Returns room ID.
* `GET /api/rooms/{roomId}` — Room details & state.
* `POST /api/rooms/{roomId}/join` — Join room (body: player info); returns auth token for WebSocket.
* `POST /api/rooms/{roomId}/cards` — Request/assign card(s) for player.
* `POST /api/rooms/{roomId}/start` — Host starts game.
* `POST /api/rooms/{roomId}/draw` — Host/manual draw (if manual mode).
* `POST /api/rooms/{roomId}/claim` — Player claims Bingo (body: cardId, claimedPattern).
* `GET /api/rooms/{roomId}/audit` — Download draw log / audit trail (for admin).

### 5.2 WebSocket Events

**Server -> Clients**

* `room.update` — broadcast state updates.
* `draw.called` — next number called: `{value, seq}`.
* `player.joined` / `player.left`.
* `card.assigned` — card payload.
* `claim.request` — notify host that a claim was made (includes claim id).
* `claim.result` — verification result (accepted/rejected + reason).

**Client -> Server**

* `claim.submit` — send claim with marked positions, timestamps, clientSignature.
* `ping/pong` — keepalive.

Security: Require auth tokens for socket connections; rate-limit claim actions.

---

## 6. Core Algorithms

### 6.1 Card Generation

* **75-ball algorithm:**

  * For each column (B,I,N,G,O) choose unique numbers from column-specific ranges.
  * Shuffle within column if desired for placement.
  * Set center cell to FREE (null or special marker).
* **90-ball algorithm:**

  * Standard approach: columns map to 1–10, 11–20, ... 81–90. Place 15 numbers across 3 rows with constraints so each row has 5 numbers, column counts vary but total per column is 1..3.
* **Uniqueness:** ensure cards for the same room are not duplicates (optional: allow duplicates if desired).

### 6.2 RNG / Draw Pool

* Approach: Use a secure PRNG seeded per game.

  * Example: generate seed server-side using CSPRNG (e.g., Node `crypto.randomBytes(32)`), keep the seed in DrawLog for audit.
  * Shuffle the array [min..max] using Fisher–Yates with the seed-derived stream.
* For auditability: compute and publish final hash of the seeded shuffle (e.g., hash(seed + concatenated draw order)). Optionally reveal seed after game to let players verify shuffle.

### 6.3 Pattern Verification

* Represent winning patterns as boolean masks (matrix same dimensions as card). For each card:

  * Compute `markedMask` from card state (1 if value called and marked).
  * Check if `(markedMask & patternMask) == patternMask` (i.e., all required positions marked).
* Additional logic for `free` tile: auto-mark as true.

---

## 7. Claim Flow & Verification

1. Player triggers `claim.submit` (client sends their card state and claim metadata with timestamp and client nonce/signature).
2. Server immediately freezes claim processing for that game state to avoid race conditions.
3. Server verifies:

   * All marked numbers are present in `calledNumbers` set.
   * The pattern check passes.
   * No previous accepted claim for same draw (unless rules allow split).
4. If claim accepted: record winner(s) and broadcast `claim.result` accepted.
5. If rejected: broadcast reject with reason (e.g., "Marked number 48 has not been called yet").

**Edge cases:** simultaneous claims that look valid — use server timestamp order or tie-break rules (split prize). Always keep audit log.

---

## 8. UI/UX Design (wireframes & behavior)

(Developer can convert this to visual wireframes)

### 8.1 Lobby Screen

* Room code, round settings, host panel.
* List of players and cards-per-player selector.
* Host controls: Start, Manual Draw button (if manual), Draw cadence slider, Pattern selector.

### 8.2 Player Screen (during game)

* Grid rendering of card(s) with tappable/checkbox cells (auto-mark when number called if auto-mark mode enabled).
* Top bar: Called numbers list (compact), last called number highlighted.
* Claim button: Enabled when player thinks they have winning pattern.
* History area: Past draws, timer to next draw.

### 8.3 Host/Moderator Panel

* Controls to call next number (manual) or start/stop auto-draw.
* View incoming claims queue with thumbnails of card(s) to quickly verify.
* Option to accept/reject and annotate.

### 8.4 Mobile Considerations

* Cards should scale; allow swipe to switch between multiple cards.
* Buttons reachable with thumb (bottom area).
* Offline resilience: temporary local cache of card & called numbers so UI doesn't break on short disconnects.

---

## 9. Security, Fairness & Auditability

* **CSPRNG:** use a cryptographically secure RNG for seed generation and shuffles.
* **Draw logs:** immutable log of draws with hash chaining; provide export for audits.
* **Client trust minimization:** Clients should not be authoritative for wins (server verifies). Client signatures/time nonces help detect replay attacks.
* **Rate-limiting & anti-cheat:** limit claim attempts per minute; suspicious behavior flagged.
* **Data retention & privacy:** store minimal player PII; allow deletion.

---

## 10. Performance & Scalability

* Use WebSocket clusters with sticky sessions or a pub/sub layer (e.g., Redis Pub/Sub) to broadcast draws and events.
* Keep card generation and pattern checks efficient (bitmasks where possible).
* For large rooms (1000s concurrent players), consider sharding rooms across servers.

---

## 11. Testing & QA

* **Unit tests:** card generation, RNG shuffle determinism (given seed), pattern verification.
* **Integration tests:** claims flow, race conditions with simultaneous claims.
* **Load tests:** simulate many concurrent players to verify latency.
* **Security tests:** RNG audit, attempt forged claims.

---

## 12. Logging & Monitoring

* Log important events: room create/start/stop, draws, claims (accepted/rejected), disconnects.
* Monitor metrics: connected clients, draws/sec, average claim verification latency, error rates.

---

## 13. Analytics & Optional Features

* Track player retention, session duration, win rates.
* Add cosmetic themes, sounds, achievements, leaderboards.
* Add social features: chat (moderated), emoticons, gifting cards.

---

## 14. Acceptance Criteria & Milestones

**MVP (2–4 sprints)**

* Create/join room, card generation (75-ball), auto-draw with RNG, realtime update to players, claim and server verification, basic UI for desktop & mobile.

**Phase 2**

* 90-ball support, pattern customizer, host panel, audit logs export.

**Phase 3**

* Load scaling, performance tuning, analytics, cosmetic features, payments/prize handling.

---

## 15. Example Implementation Notes (Tech stack suggestions)

* **Backend:** Node.js + TypeScript (or Go) with WebSocket support; use Redis for pub/sub and short-lived state.
* **DB:** PostgreSQL for persistent data (rooms, player profiles), Redis for ephemeral state.
* **Auth:** JWT for session tokens.
* **RNG:** Node `crypto` or libs with CSPRNG. Store seed securely (and optionally reveal after game for audit).
* **Frontend:** React (web) and React Native (mobile) sharing UI components. Use state management (Redux/Recoil) for local card state.

---

## 16. Deliverables for the Developer

1. API contract (OpenAPI/Swagger) for endpoints described above.
2. Card generation module with unit tests and deterministic seed-based mode for QA.
3. Draw engine with audit logging and hashing.
4. WebSocket event schema & client SDK (small JS lib) to manage realtime events.
5. Frontend components: lobby, card grid, host panel, claim modal.
6. End-to-end tests simulating a full round with 50 concurrent players.

---

## 17. Appendix — Pattern Mask Examples

* **5-in-a-row (75-ball):** mask with row/column/diagonal lines.
* **Four corners:** mask corners true.
* **Full house:** all non-null cells true.

---

If you'd like, I can also:

* Produce an **OpenAPI** spec for the REST endpoints.
* Create **detailed UI mockups** (Figma-ready descriptions) for developer handoff.
* Produce **sample unit tests** (card generation, pattern verifier) in your preferred language.

Tell me which of those you'd like next and I will add them to the document.

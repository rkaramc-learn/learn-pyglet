# Feature Specification: Health & Stamina System (Tag Gameplay)

## 1. Overview
To transform the current "endless chase" into a structured game loop, we will introduce a **Health System** for the Mouse (player) and a **Stamina System** for the Kitten (AI). This creates a "win/loss" condition: the mouse must survive until the kitten runs out of energy.

## 2. Core Mechanics

### 2.1. Mouse Health (Life)
*   **Representation:** A visual bar (100 HP max) floating above the Mouse sprite.
    *   **Colors:** Green when > 30%, Red when < 30%.
*   **Catch Range:** Dynamic calculation: `(MaxDimension(Kitten) + MaxDimension(Mouse)) / 2`.
*   **Drain Logic:** Occurs when the distance between centers is less than `CatchRange`.
    *   **Formula:** `DrainRate = BaseRate * (1 - (Distance / CatchRange))`
    *   **Application:** `mouse_health -= DrainRate * dt`.
*   **Regeneration:** None. (Deferred to later implementation).
*   **Game Over (Loss):** When HP reaches 0, the game halts, displays "Caught!", and resets after a delay or input.

### 2.2. Kitten Stamina (Energy)
*   **Representation:** A visual bar (100 Energy max) floating above the Kitten sprite.
    *   **Colors:** Green when > 30%, Red when < 30%.
*   **Passive Drain:** Drains constantly at 2 units per second.
*   **Regeneration (Vampiric):** Occurs when within `CatchRange` of the mouse.
    *   **Formula:** `RegenRate = BaseRate * (1 - (Distance / CatchRange))`
    *   **Application:** `kitten_stamina += RegenRate * dt`.
    *   **Note:** Use the same calculation formula as Mouse Health but apply it independently to avoid coupling update loops.
*   **Victory Condition (Win):** If Stamina hits 0, the Kitten "falls asleep". The game halts, displays "You Win!!", and resets after a delay or input.

## 3. Visuals (UI)
*   **Health/Stamina Bars:**
    *   Drawn using `pyglet.shapes.Rectangle`.
    *   **Position:** Floating ~20px above the respective sprite.
    *   **Structure:** A dark background rectangle with a colored foreground rectangle scaled by percentage.
    *   **// OPTIMIZE:** Recreating shape instances every frame is expensive. Instantiate once and update `.width` and `.color` properties in `update()`.

## 4. Technical Implementation Steps

### Phase 1: Core State & Logic
1.  **Constants:** Define `MAX_HEALTH = 100`, `MAX_STAMINA = 100`, `BASE_DRAIN_RATE`, `PASSIVE_STAMINA_DRAIN = 2.0`.
2.  **Initialization:** Add `mouse_health` and `kitten_stamina` to the game state.
3.  **Dynamic Range:** Calculate `catch_range` during setup based on sprite dimensions.
4.  **Update Loop:**
    *   Calculate distance `d` between entities.
    *   If `d < catch_range`:
        *   Calculate `factor = 1.0 - (d / catch_range)`.
        *   `mouse_health -= (BASE_DRAIN_RATE * factor) * dt`.
        *   `kitten_stamina += (BASE_DRAIN_RATE * factor) * dt`.
    *   `kitten_stamina -= PASSIVE_STAMINA_DRAIN * dt`.
5.  **Win/Loss Check:**
    *   If `mouse_health <= 0`: Trigger Loss State.
    *   If `kitten_stamina <= 0`: Trigger Win State.

### Phase 2: Visuals & UI
1.  **Shape Setup:** Create background and foreground rectangles for both bars.
2.  **Positioning:** Sync bar positions to sprite `x, y` coordinates in `on_draw` or `update`.
3.  **Labels:** Create "Caught!" and "You Win!!" labels (hidden by default).

## 5. Beads Tasks
*   `pyglet-hlt`: Implement Mouse Health & Kitten Stamina state logic.
*   `pyglet-ui`: Draw Floating UI bars using `pyglet.shapes`.
*   `pyglet-gm`: Implement Win/Loss triggers and "Caught/Win" overlays.
*   `pyglet-opt`: Optimize UI by reusing shape instances. **// NEW**
*   `pyglet-reg`: (Idea) Implement Mouse Health regeneration mechanic. **// IDEA**
*   `pyglet-agr`: (Idea) Implement Kitten "Aggro/Sprint" mode. **// IDEA**
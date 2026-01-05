# Feature Specification: Health & Stamina System (Tag Gameplay)

## 1. Overview
To transform the current "endless chase" into a structured game loop, we will introduce a **Health System** for the Mouse (player) and a **Stamina/Fatigue System** for the Kitten (AI). This creates a dynamic where the player must manage their exposure to danger while the AI has bursts of intensity.

## 2. Core Mechanics

### 2.1. Mouse Health (Life)
*   **Representation:** A visual bar (Green -> Red) floating above the Mouse sprite or fixed in the UI.
*   **Max Value:** 100 HP.
*   **Drain Condition:** Occurs when the Kitten is within "Catch Range" (collision threshold).
    *   *Catch Range:* 64 pixels (sprite width/4, center-to-center).
    *   *Drain Formula:* `Damage = (10 + (20 * ProximityFactor)) * dt`.
        *   `ProximityFactor = 1.0 - (Distance / CatchRange)`. Clamped [0, 1].
        *   Max Drain (Distance ~0): 30 HP/s.
        *   Min Drain (Distance ~64): 10 HP/s.
    *   **// RESOLVED:** Formula defined as Linear Interpolation based on overlap.
*   **Regeneration:** (Optional) Slow regen (1-5 HP/s) if safely away from the Kitten for >3 seconds.
    *   **// OPTIMIZE:** Ensure regen doesn't trivialize the "Vampiric" mechanic. Consider disabling regen if Kitten is in "Aggro" state.
*   **Game Over:** When HP reaches 0, the game halts, displays "Caught!", and resets after a delay or input.

### 2.2. Kitten Stamina (Energy)
*   **Representation:** A visual bar (Yellow/Orange) above the Kitten sprite.
*   **Max Value:** 100 Energy.
*   **Behavior State Machine:**
    *   **Normal (Chase):** Moves at standard speed (`base_speed / 1.5`). Drains Stamina at 2 units/s.
    *   **Sprint (Aggro):** (Future Feature) If Stamina > 50, Kitten can burst at `1.2x` speed for a short duration, draining Stamina (e.g., 5 units/s).
    *   **Vampiric Regeneration:** If mouse is within catch range and losing HP, the drained amount is added to Kitten Stamina.
        *   **// TECH_DEBT:** Logic coupling handled by `run_health_logic()` function that accepts both entities.
    *   **Tired:** If Stamina hits 0, Kitten slows to `0.5x` speed until Stamina recovers to 30%.
        *   **// RESOLVED:** Explicit `kitten_is_tired` boolean flag required. State transition:
            *   Normal -> Tired: When `stamina <= 0`.
            *   Tired -> Normal: When `stamina >= 30`.

## 3. Visuals (UI)
*   **Health Bars:** Simple `pyglet.shapes.Rectangle` drawn in the `on_draw` loop.
    *   Background: Grey/Black (dims).
    *   Foreground: Colored rect based on % fill.
    *   Position: Floating ~20px above the respective sprite.
    *   **// OPTIMIZE:** Recreating `shapes.Rectangle` every frame is expensive. Update properties of existing shape instances instead.

## 4. Technical Implementation Steps

### Phase 1: Core Mechanics (Health & Vampirism)
1.  **State Management:** Add `mouse_health`, `kitten_stamina`, `kitten_is_tired` flags.
2.  **Logic Update:**
    *   Calculate `overlap_factor` (0.0 to 1.0) based on collision distance.
    *   Calculate `damage = (MinDrain + (MaxDrain - MinDrain) * overlap_factor) * dt`.
    *   Apply: `mouse_health -= damage`.
    *   Apply: `kitten_stamina += damage * 0.5` (Vampiric Ratio - 50% efficiency?).
        *   *Update:* 1:1 ratio for now.
    *   Apply: `kitten_stamina -= passive_drain * dt` (Constant decay).
3.  **State Check:**
    *   If `kitten_stamina <= 0`: Set `kitten_is_tired = True`.
    *   If `kitten_is_tired` AND `kitten_stamina >= 30`: Set `kitten_is_tired = False`.
    *   Update speed based on `kitten_is_tired`.
    *   If `mouse_health <= 0`: Trigger **Game Over**.

### Phase 2: Visuals & Polish
1.  **Rendering:** Implement efficient shape updates for health bars.
2.  **Feedback:** Add color flash on damage?
    *   **// TEST:** Verify visual feedback is perceptible at 60FPS.

## 5. Beads Tasks
*   `pyglet-hlt`: Implement Mouse Health Bar & Damage Logic.
*   `pyglet-ui`: Draw Floating Health Bars using `pyglet.shapes`.
*   `pyglet-gm`: Implement Game Over / Reset State.
*   `pyglet-stm`: Implement Kitten Stamina & Vampiric Logic.

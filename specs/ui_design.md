# UI Design Specification: "Playful Chase"

## 1. Design Philosophy

A clean, vibrant, arcade-style aesthetic that prioritizes gameplay visibility and readability. The design uses high-contrast colors and simple geometric shapes manageable with `pyglet.shapes`.

## 2. Color Palette

We will use a flat color palette inspired by modern UI frameworks.

| Usage               | Color Name    | Hex       | RGB               |
| ------------------- | ------------- | --------- | ----------------- |
| **Background**      | `Deep Space`  | `#2C3E50` | `(44, 62, 80)`    |
| **Player (Mouse)**  | `Emerald`     | `#2ECC71` | `(46, 204, 113)`  |
| **Enemy (Kitten)**  | `Alizarin`    | `#E74C3C` | `(231, 76, 60)`   |
| **UI Text**         | `Clouds`      | `#ECF0F1` | `(236, 240, 241)` |
| **UI Accent**       | `Peter River` | `#3498DB` | `(52, 152, 219)`  |
| **Health Good**     | `Emerald`     | `#2ECC71` | `(46, 204, 113)`  |
| **Health Low**      | `Orange`      | `#F39C12` | `(243, 156, 18)`  |
| **Health Critical** | `Alizarin`    | `#E74C3C` | `(231, 76, 60)`   |
| **Button Base**     | `Belize Hole` | `#2980B9` | `(41, 128, 185)`  |
| **Button Hover**    | `Peter River` | `#3498DB` | `(52, 152, 219)`  |

## 3. Typography

- **Font**: Arial (System default), falling back to Sans-Serif.
- **Scale**:
  - **Hero Title**: 72px, Bold.
  - **Section Header**: 36px.
  - **Body Text**: 18px.
  - **Small/UI Labels**: 14px.

## 4. Screens Breakdown

### 4.1. Splash Screen

- **Background**: `Deep Space`.
- **Center**: Giant "Pyglet Chase" title in `Clouds` color.
- **Animation**: Fade in/out (if possible) or specific duration.

### 4.2. Home Screen (Game Start)

- **Layout**: Vertical stack centered.
- **Title**: "CHASER GAME" (72px).
- **Instructions Box**: Semi-transparent dark overlay (`0, 0, 0, 100`) behind text for readability.
- **Controls**:
  - Grid layout of keys.
- **Primary Action**: "Press SPACE to Start" (Pulsing effect optional).

### 4.3. HUD (Game Running)

- **Top Bar**: Semi-transparent bar across top showing:
  - Time Survived (Center).
  - Score/Distance (Right).
- **Entity Bars**:
  - **Health (Mouse)**: Standard green bar above mouse. Border: 2px White.
  - **Stamina (Kitten)**: Blue/Cyan bar above kitten to distinguish from health.

### 4.4. Game End (Results)

- **Conditional Theme**:
  - **Win**: Green background tint or confetti effect.
  - **Loss**: Red background tint.
- **Stats Card**:
  - "Time Survived: XXm YYs"
  - "Distance Run: ZZZ px"
- **Actions**:
  - Review Board: Large "Play Again" button (visual representation of Space key).

## 5. Implementation Strategy

1.  **Config Update**: Migrate hardcoded colors in `config.py` to `GameConfig` palette.
2.  **UI Component Library**: Create reusable visual components in `src/chaser_game/ui/`.
    - `Button`: Text + Rectangle background + Hover state.
    - `Panel`: Rounded rectangle with transparency.
3.  **Screen Refactor**: Apply new components to existing screens.

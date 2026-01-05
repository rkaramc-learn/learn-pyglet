import pyglet
import os
import math

def run_hello_world():
    from pyglet.window import key, mouse

    # Add the current directory to the resource path
    script_dir = os.path.dirname(__file__)
    pyglet.resource.path = [script_dir]
    pyglet.resource.reindex()

    window = pyglet.window.Window()

    label = pyglet.text.Label('Hello, world!', font_size=36, x=window.width // 2, y = window.height // 2, anchor_x = 'center', anchor_y = 'center')
    
    # Kitten Setup
    image = pyglet.resource.image('kitten.png')
    image.width = image.width // 10
    image.height = image.height // 10
    image_x = window.width // 2
    image_y = window.height // 2
    
    # Speed is relative to window size (e.g., cross width in 10 seconds)
    base_speed = window.width / 10.0
    mouse_speed = base_speed
    kitten_speed = base_speed / 1.5
    
    # Mouse Setup
    mouse_sheet = pyglet.resource.image('mouse_sheet.png')
    mouse_grid = pyglet.image.ImageGrid(mouse_sheet, 10, 10)
    mouse_anim = pyglet.image.Animation.from_image_sequence(mouse_grid, 1/12.0) # pyright: ignore[reportPrivateImportUsage]
    mouse_sprite = pyglet.sprite.Sprite(mouse_anim)
    mouse_sprite.scale = 0.25
    # Start at top-left
    mouse_sprite.x = 0
    mouse_sprite.y = window.height - mouse_sprite.height

    # Manual Velocity (Press-to-move)
    mouse_vx = 0.0
    mouse_vy = 0.0
    
    # Load sound
    meow_sound = pyglet.resource.media('meow.wav', streaming=False)
    
    # Load and play background music
    ambience_sound = pyglet.resource.media('ambience.wav')
    music_player = pyglet.media.Player()
    music_player.queue(ambience_sound)
    music_player.loop = True
    music_player.play()

    was_moving = False

    # Key handler for continuous input
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    
    def on_key_press(symbol: int, _modifiers: int):
        nonlocal mouse_speed, image_x, image_y, was_moving
        nonlocal mouse_vx, mouse_vy
        
        if symbol == key.Q:
            window.close()
        elif symbol == key.R:
            # Reset Game State
            mouse_speed = base_speed
            image_x = window.width // 2
            image_y = window.height // 2
            
            mouse_sprite.x = 0
            mouse_sprite.y = window.height - mouse_sprite.height
            
            # Reset mouse movement state
            mouse_vx = 0.0
            mouse_vy = 0.0
            was_moving = False
        
        # Manual Movement Control (Sets Velocity)
        diag_factor = 0.7071 # 1/sqrt(2) to normalize diagonal speed
        
        if symbol == key.UP:
            mouse_vx = 0.0
            mouse_vy = mouse_speed
        elif symbol == key.DOWN:
            mouse_vx = 0.0
            mouse_vy = -mouse_speed
        elif symbol == key.LEFT:
            mouse_vx = -mouse_speed
            mouse_vy = 0.0
        elif symbol == key.RIGHT:
            mouse_vx = mouse_speed
            mouse_vy = 0.0
        # Diagonals
        elif symbol == key.HOME: # Up-Left
            mouse_vx = -mouse_speed * diag_factor
            mouse_vy = mouse_speed * diag_factor
        elif symbol == key.PAGEUP: # Up-Right
            mouse_vx = mouse_speed * diag_factor
            mouse_vy = mouse_speed * diag_factor
        elif symbol == key.END: # Down-Left
            mouse_vx = -mouse_speed * diag_factor
            mouse_vy = -mouse_speed * diag_factor
        elif symbol == key.PAGEDOWN: # Down-Right
            mouse_vx = mouse_speed * diag_factor
            mouse_vy = -mouse_speed * diag_factor
        elif symbol == key.SPACE: # Stop
            mouse_vx = 0.0
            mouse_vy = 0.0
            
    def on_mouse_press(x: int, y: int, button: int, _modifiers: int):
        nonlocal mouse_vx, mouse_vy
        
        if button == mouse.LEFT:
            # Set direction towards click
            # Target center of mouse sprite for vector calculation
            current_x = mouse_sprite.x + (mouse_sprite.width / 2)
            current_y = mouse_sprite.y + (mouse_sprite.height / 2)
            
            dx = float(x) - current_x
            dy = float(y) - current_y
            
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                # Normalize and apply speed
                mouse_vx = (dx / length) * mouse_speed
                mouse_vy = (dy / length) * mouse_speed
            else:
                mouse_vx = 0.0
                mouse_vy = 0.0

    window.push_handlers(on_key_press=on_key_press, on_mouse_press=on_mouse_press)

    def update(dt: float):
        nonlocal image_x, image_y, was_moving
        
        # --- Mouse Movement ---
        # Manual Velocity
        mouse_sprite.x += mouse_vx * dt
        mouse_sprite.y += mouse_vy * dt

        # --- Kitten Movement (AI Only) ---
        # Kitten always chases mouse now
        
        # Target center of mouse sprite
        tx = mouse_sprite.x + (mouse_sprite.width / 2) - (image.width / 2)
        ty = mouse_sprite.y + (mouse_sprite.height / 2) - (image.height / 2)
        
        dx = tx - image_x
        dy = ty - image_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        is_moving = False
        if distance > 2.0: # Threshold to prevent jitter
            travel = min(distance, kitten_speed * dt)
            
            image_x += (dx / distance) * travel
            image_y += (dy / distance) * travel
            is_moving = True

        # Check if kitten stopped moving
        if was_moving and not is_moving:
            meow_sound.play() # pyright: ignore[reportUnusedCallResult]
        
        was_moving = is_moving

    pyglet.clock.schedule_interval(update, 1/60.0) # pyright: ignore[reportUnknownMemberType]

    @window.event # pyright: ignore[reportUnknownMemberType]
    def on_draw(): # pyright: ignore[reportUnusedFunction]
        window.clear()
        label.draw()
        image.blit(int(image_x), int(image_y))
        mouse_sprite.draw()

    pyglet.app.run()

if __name__ == "__main__":
    run_hello_world()

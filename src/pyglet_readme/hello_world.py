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
    
    # Speed is relative to window size (e.g., cross width in 4 seconds)
    base_speed_x = window.width / 4.0
    base_speed_y = window.height / 4.0
    current_speed_x = base_speed_x
    current_speed_y = base_speed_y
    
    # Mouse Setup
    mouse_sheet = pyglet.resource.image('mouse_sheet.png')
    mouse_grid = pyglet.image.ImageGrid(mouse_sheet, 10, 10)
    mouse_anim = pyglet.image.Animation.from_image_sequence(mouse_grid, 1/12.0) # pyright: ignore[reportPrivateImportUsage]
    mouse_sprite = pyglet.sprite.Sprite(mouse_anim)
    mouse_sprite.scale = 0.25
    # Start at top-left
    mouse_sprite.x = 0
    mouse_sprite.y = window.height - mouse_sprite.height

    # Mouse Movement State
    mouse_start_x = mouse_sprite.x
    mouse_start_y = mouse_sprite.y
    mouse_target_x = mouse_sprite.x
    mouse_target_y = mouse_sprite.y
    mouse_move_time = 0.0
    mouse_move_duration = 3.0
    mouse_is_moving = False
    
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
        nonlocal current_speed_x, current_speed_y, image_x, image_y, was_moving
        nonlocal mouse_is_moving, mouse_target_x, mouse_target_y
        
        if symbol == key.Q:
            window.close()
        elif symbol == key.R:
            # Reset Game State
            current_speed_x = base_speed_x
            current_speed_y = base_speed_y
            image_x = window.width // 2
            image_y = window.height // 2
            
            mouse_sprite.x = 0
            mouse_sprite.y = window.height - mouse_sprite.height
            
            # Reset mouse movement state
            mouse_is_moving = False
            mouse_target_x = mouse_sprite.x
            mouse_target_y = mouse_sprite.y
            was_moving = False
            
    def on_mouse_press(x: int, y: int, button: int, _modifiers: int):
        nonlocal mouse_target_x, mouse_target_y, mouse_start_x, mouse_start_y
        nonlocal mouse_move_time, mouse_is_moving
        
        if button == mouse.LEFT:
            # Setup mouse movement
            mouse_target_x = float(x)
            mouse_target_y = float(y)
            mouse_start_x = mouse_sprite.x
            mouse_start_y = mouse_sprite.y
            mouse_move_time = 0.0
            mouse_is_moving = True

    window.push_handlers(on_key_press=on_key_press, on_mouse_press=on_mouse_press)

    def update(dt: float):
        nonlocal image_x, image_y, was_moving
        nonlocal mouse_move_time, mouse_is_moving
        
        # --- Mouse Movement (Tweening vs Manual) ---
        move_dist_x = current_speed_x * dt
        move_dist_y = current_speed_y * dt
        mouse_manual_move = False

        # 1. Keyboard Control (Moves Mouse Sprite)
        # Cardinal movement (Arrows)
        if keys[key.UP]:
            mouse_sprite.y += move_dist_y
            mouse_manual_move = True
        if keys[key.DOWN]:
            mouse_sprite.y -= move_dist_y
            mouse_manual_move = True
        if keys[key.LEFT]:
            mouse_sprite.x -= move_dist_x
            mouse_manual_move = True
        if keys[key.RIGHT]:
            mouse_sprite.x += move_dist_x
            mouse_manual_move = True

        # Diagonal movement
        if keys[key.HOME]: # Up-Left
            mouse_sprite.y += move_dist_y
            mouse_sprite.x -= move_dist_x
            mouse_manual_move = True
        if keys[key.PAGEUP]: # Up-Right
            mouse_sprite.y += move_dist_y
            mouse_sprite.x += move_dist_x
            mouse_manual_move = True
        if keys[key.END]: # Down-Left
            mouse_sprite.y -= move_dist_y
            mouse_sprite.x -= move_dist_x
            mouse_manual_move = True
        if keys[key.PAGEDOWN]: # Down-Right
            mouse_sprite.y -= move_dist_y
            mouse_sprite.x += move_dist_x
            mouse_manual_move = True
            
        if mouse_manual_move:
            # Cancel any active tweening
            mouse_is_moving = False
            # Sync target to current position so it doesn't snap back later
            mouse_target_x = mouse_sprite.x
            mouse_target_y = mouse_sprite.y
            
        elif mouse_is_moving:
            # Handle tweening only if not manually driving
            mouse_move_time += dt
            t = mouse_move_time / mouse_move_duration
            
            if t >= 1.0:
                t = 1.0
                mouse_is_moving = False
            
            # Linear Interpolation (Lerp)
            mouse_sprite.x = mouse_start_x + (mouse_target_x - mouse_start_x) * t
            mouse_sprite.y = mouse_start_y + (mouse_target_y - mouse_start_y) * t

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
            # Kitten uses average speed for chase logic to keep it simple but relative
            avg_speed = (current_speed_x + current_speed_y) / 2.0
            travel = min(distance, avg_speed * dt)
            
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

import pyglet
import os

def run_hello_world():
    from pyglet.window import key

    # Add the current directory to the resource path
    script_dir = os.path.dirname(__file__)
    pyglet.resource.path = [script_dir]
    pyglet.resource.reindex()

    window = pyglet.window.Window()

    label = pyglet.text.Label('Hello, world!', font_size=36, x=window.width // 2, y = window.height // 2, anchor_x = 'center', anchor_y = 'center')
    image = pyglet.resource.image('kitten.png')
    image.width = image.width // 10
    image.height = image.height // 10

    image_x = window.width // 2
    image_y = window.height // 2
    step_size = 100.0  # Pixels per second

    # Key handler for continuous input
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    
    def on_key_press(symbol: int, _modifiers: int):
        nonlocal step_size
        if symbol == key.W:
            step_size += 50
        elif symbol == key.S:
            step_size = max(0, step_size - 50)
        elif symbol == key.Q:
            window.close()

    window.push_handlers(on_key_press=on_key_press)

    def update(dt: float):
        nonlocal image_x, image_y
        
        # Move with step_size (pixels per second)
        move_distance = step_size * dt
        
        if keys[key.J]:
            image_y += move_distance
        if keys[key.K]:
            image_y -= move_distance
        if keys[key.H]:
            image_x -= move_distance
        if keys[key.L]:
            image_x += move_distance

    pyglet.clock.schedule_interval(update, 1/60.0) # pyright: ignore[reportUnknownMemberType]

    @window.event # pyright: ignore[reportUnknownMemberType]
    def on_draw(): # pyright: ignore[reportUnusedFunction]
        window.clear()
        label.draw()
        image.blit(int(image_x), int(image_y))

    pyglet.app.run()

if __name__ == "__main__":
    run_hello_world()

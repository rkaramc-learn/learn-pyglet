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

    image_x = 0
    image_y = 0
    step_size = 10

    # Key handler for continuous input
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    def update(dt: float): # pyright: ignore[reportUnusedParameter]
        nonlocal image_x, image_y
        
        # Move with step_size (treated as pixels per frame here for smooth response)
        if keys[key.J]:
            image_y += step_size
        if keys[key.K]:
            image_y -= step_size
        if keys[key.H]:
            image_x -= step_size
        if keys[key.L]:
            image_x += step_size

    pyglet.clock.schedule_interval(update, 1/60.0) # pyright: ignore[reportUnknownMemberType]

    @window.event  # pyright: ignore[reportUnknownMemberType]
    def on_draw(): # pyright: ignore[reportUnusedFunction]
        window.clear()
        label.draw()
        image.blit(image_x, image_y)
    
    @window.event # pyright: ignore[reportUnknownMemberType]
    def on_key_press(symbol: int, _modifiers: int): # pyright: ignore[reportUnusedFunction]
        nonlocal step_size

        if symbol == key.W:
            step_size += 10
        elif symbol == key.S:
            step_size = max(0, step_size - 10)

    pyglet.app.run()

if __name__ == "__main__":
    run_hello_world()

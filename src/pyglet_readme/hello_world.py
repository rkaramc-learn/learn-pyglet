import pyglet
import os

def run_hello_world():
    # Add the current directory to the resource path
    script_dir = os.path.dirname(__file__)
    pyglet.resource.path = [script_dir]
    pyglet.resource.reindex()

    window = pyglet.window.Window()

    label = pyglet.text.Label('Hello, world!', font_size=36, x=window.width // 2, y = window.height // 2, anchor_x = 'center', anchor_y = 'center')
    image = pyglet.resource.image('kitten.png')
    image.width = image.width // 10
    image.height = image.height // 10

    @window.event  # pyright: ignore[reportUnknownMemberType]
    def on_draw(): # pyright: ignore[reportUnusedFunction]
        window.clear()
        label.draw()
        image.blit(0, 0)

    step_size = 10
    
    @window.event
    def on_key_press(symbol, modifiers):
        # move image...
        # if key is j - up by step_size pixels
        # if key is k - down by step_size pixels
        # if key is h - left by step_size pixels
        # if key is l - right by step_size pixels
        # if key is w - increase step size by 10 pixels
        # if key is s - decrease step size by 10 pixels

    pyglet.app.run()

if __name__ == "__main__":
    run_hello_world()

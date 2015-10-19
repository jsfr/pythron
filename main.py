import sys
import sdl2
import sdl2.ext
import sdl2.keyboard
import random
from enum import Enum


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window, color):
        super(SoftwareRenderer, self).__init__(window)
        self.color = color
        sdl2.ext.fill(self.surface, self.color)

    def render(self, components):
        super(SoftwareRenderer, self).render(components)


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, gridsize):
        super(MovementSystem, self).__init__()
        self.componenttypes = Direction, sdl2.ext.Sprite
        self.gridsize = gridsize

    def process(self, world, componentsets):
        for direction, sprite in componentsets:
            if direction == Direction.up:
                sprite.y -= self.gridsize
            elif direction == Direction.down:
                sprite.y += self.gridsize
            elif direction == Direction.left:
                sprite.x -= self.gridsize
            elif direction == Direction.right:
                sprite.x += self.gridsize

# class BoardSystem(sdl2.ext.Applicator):
#     def __init__(self):
#         super(BoardSystem, self).__init__()


# class Board():
#     def __init__(self, rows, columns):
#         self.grid = [[False for i in range(0, columns)]
#                      for i in range(0, rows)]


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, controls, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.direction = Direction.none
        self.controls = Controls(
            controls[0], controls[1], controls[2], controls[3])


class Controls(object):
    def __init__(self, up, down, left, right):
        super(Controls, self).__init__()
        self.up = sdl2.keyboard.SDL_GetKeyFromName(up)
        self.down = sdl2.keyboard.SDL_GetKeyFromName(down)
        self.left = sdl2.keyboard.SDL_GetKeyFromName(left)
        self.right = sdl2.keyboard.SDL_GetKeyFromName(right)


class Direction(Enum):
    none = 0
    up = 1
    down = 2
    left = 3
    right = 4


def handle_events(players):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                for player in players:
                    if event.key.keysym.sym == player.controls.up:
                        player.direction = Direction.up
                    elif event.key.keysym.sym == player.controls.down:
                        player.direction = Direction.down
                    elif event.key.keysym.sym == player.controls.left:
                        player.direction = Direction.left
                    elif event.key.keysym.sym == player.controls.right:
                        player.direction = Direction.right
            elif event.type == sdl2.SDL_QUIT:
                return False
        return True


def run():
    BG = sdl2.ext.Color(0, 0, 0)
    GRID_SIZE = 7
    ROWS = 120
    COLUMNS = 120
    BOARD_SIZE = GRID_SIZE*COLUMNS, GRID_SIZE*ROWS
    DELAY = 10

    sdl2.ext.init()
    window = sdl2.ext.Window(title="pythron", size=BOARD_SIZE)
    window.show()

    world = sdl2.ext.World()
    movement = MovementSystem(GRID_SIZE)
    spriterenderer = SoftwareRenderer(window, BG)

    world.add_system(movement)
    world.add_system(spriterenderer)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sprite = factory.from_color(
        sdl2.ext.Color(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)),
        size=(GRID_SIZE, GRID_SIZE))

    players = [
        Player(world, sprite, [b'up', b'down', b'left', b'right'], 0, 0)
    ]

    running = True
    while running:
        running = handle_events(players)
        sdl2.SDL_Delay(DELAY)
        world.process()


if __name__ == "__main__":
    sys.exit(run())

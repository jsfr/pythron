import sys
import sdl2
import sdl2.ext
import random
from enum import Enum

BG = sdl2.ext.Color(0, 0, 0)
GRID_SIZE = 5
ROWS = 120
COLUMNS = 40
BOARD_SIZE = GRID_SIZE*COLUMNS, GRID_SIZE*ROWS
DELAY = 10


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window, color):
        super(SoftwareRenderer, self).__init__(window)
        self.color = color
        sdl2.ext.fill(self.surface, self.color)

    def render(self, components):
        super(SoftwareRenderer, self).render(components)


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Direction, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, world, componentsets):
        for direction, sprite in componentsets:
            swidth, sheight = sprite.size

            if direction == Direction.up:
                sprite.y -= GRID_SIZE
            elif direction == Direction.down:
                sprite.y += GRID_SIZE
            elif direction == Direction.left:
                sprite.x -= GRID_SIZE
            elif direction == Direction.right:
                sprite.x += GRID_SIZE

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            pmaxx = sprite.x + swidth
            pmaxy = sprite.y + sheight
            if pmaxx > self.maxx:
                sprite.x = self.maxx - swidth
            if pmaxy > self.maxy:
                sprite.y = self.maxy - sheight


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.direction = Direction.none


class Direction(Enum):
    none = 0
    up = 1
    down = 2
    left = 3
    right = 4


def run():
    sdl2.ext.init()
    window = sdl2.ext.Window(title="pythron", size=BOARD_SIZE)
    window.show()

    world = sdl2.ext.World()

    movement = MovementSystem(0, 0, BOARD_SIZE[0], BOARD_SIZE[1])
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

    player = Player(world, sprite, 0, 0)

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    player.direction = Direction.up
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    player.direction = Direction.down
                elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                    player.direction = Direction.left
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    player.direction = Direction.right
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(DELAY)
        world.process()

if __name__ == "__main__":
    sys.exit(run())

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

class StateSystem(sdl2.ext.Applicator):
    def __init__(self, players):
        super(StateSystem, self).__init__()
        self.componenttypes = [PlayerData]
        self.players = players

    def process(self, world, componentsets):
        alive = 0
        for [playerdata] in componentsets:
            if playerdata.alive:
                alive += 1
            if alive > 1:
                return
        for player in self.players:
            player.reset()


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, gridsize, rows, columns):
        super(MovementSystem, self).__init__()
        self.componenttypes = PlayerData, sdl2.ext.Sprite
        self.gridsize = gridsize
        self.rows = rows
        self.columns = columns
        self.grid = [[False for i in range(0, rows)]
                     for i in range(0, columns)]

    def process(self, world, componentsets):
        for playerdata, sprite in componentsets:
            if not playerdata.alive:
                continue

            posx = sprite.x
            posy = sprite.y

            oldcol = posx // self.gridsize
            oldrow = posy // self.gridsize

            direction = playerdata.direction
            if direction == Direction.up:
                posy -= self.gridsize
            elif direction == Direction.down:
                posy += self.gridsize
            elif direction == Direction.left:
                posx -= self.gridsize
            elif direction == Direction.right:
                posx += self.gridsize

            newcol = posx // self.gridsize
            newrow = posy // self.gridsize
            if newcol >= self.columns or newcol < 0 or \
               newrow >= self.rows or newrow < 0:
                playerdata.alive = False
                continue

            entry = self.grid[newrow][newcol]
            if entry:
                playerdata.alive = False
                continue

            self.grid[oldrow][oldcol] = True
            sprite.x = posx
            sprite.y = posy


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, controls_left, controls_right, posx, posy, direction):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.playerdata = PlayerData(direction, posx, posy)
        self.controls = Controls(controls_left, controls_right)

    def reset(self):
        self.sprite.position = self.playerdata.position
        self.playerdata.direction = self.playerdata.direction
        self.playerdata.alive = True


class PlayerData(object):
    def __init__(self, direction, posx, posy):
        super(PlayerData, self).__init__()
        self.direction = direction
        self.alive = True
        self.direction = direction
        self.position = posx, posy

class SpriteFactory():
    def __init__(self, gridsize):
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        self.gridsize = gridsize

    def sprite(self):
        return self.factory.from_color(
            sdl2.ext.Color(
                random.randint(10, 250),
                random.randint(10, 250),
                random.randint(10, 250)),
            size=(self.gridsize, self.gridsize))


class Controls(object):
    def __init__(self, left, right):
        super(Controls, self).__init__()
        self.left = sdl2.keyboard.SDL_GetKeyFromName(left)
        self.right = sdl2.keyboard.SDL_GetKeyFromName(right)


class Direction(Enum):
    up = 0
    right = 1
    down = 2
    left = 3

    def turn_left(self):
        if self == Direction.up:
            return Direction.left
        elif self == Direction.down:
            return Direction.right
        elif self == Direction.left:
            return Direction.down
        elif self == Direction.right:
            return Direction.up

    def turn_right(self):
        if self == Direction.up:
            return Direction.right
        elif self == Direction.down:
            return Direction.left
        elif self == Direction.left:
            return Direction.up
        elif self == Direction.right:
            return Direction.down


def handle_events(players):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                for player in players:
                    if event.key.keysym.sym == player.controls.left:
                        player.playerdata.direction = player.playerdata.direction.turn_left()
                    elif event.key.keysym.sym == player.controls.right:
                        player.playerdata.direction = player.playerdata.direction.turn_right()
            elif event.type == sdl2.SDL_QUIT:
                return False
        return True


def run():
    BG = sdl2.ext.Color(0, 0, 0)
    GRID_SIZE = 8
    ROWS = 120
    COLUMNS = 120
    BOARD_SIZE = GRID_SIZE*COLUMNS, GRID_SIZE*ROWS
    DELAY = 10

    sdl2.ext.init()
    window = sdl2.ext.Window(title="pythron", size=BOARD_SIZE)
    window.show()

    world = sdl2.ext.World()
    factory = SpriteFactory(GRID_SIZE)
    players = [
        Player(world, factory.sprite(), b'left', b'right', 4*GRID_SIZE, 4*GRID_SIZE, Direction.right),
        Player(world, factory.sprite(), b'a', b'd', (COLUMNS-5)*GRID_SIZE, 4*GRID_SIZE, Direction.down),
        Player(world, factory.sprite(), b'f', b'h', 4*GRID_SIZE, (ROWS-5)*GRID_SIZE, Direction.up),
        Player(world, factory.sprite(), b'j', b'l', (COLUMNS-5)*GRID_SIZE, (ROWS-5)*GRID_SIZE, Direction.left)
    ]

    spriterenderer = SoftwareRenderer(window, BG)
    movement = MovementSystem(GRID_SIZE, ROWS, COLUMNS)
    state = StateSystem(players)

    world.add_system(spriterenderer)
    world.add_system(movement)
    world.add_system(state)

    running = True
    while running:
        running = handle_events(players)
        sdl2.SDL_Delay(DELAY)
        world.process()


if __name__ == "__main__":
    sys.exit(run())

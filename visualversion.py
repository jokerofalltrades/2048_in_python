"""Runs 2048 in pygame window with visual tiles and score display."""
import pygame
import sys
import random
from pygame.locals import *

# Constants
WINDOW_SIZE = 430
TILE_SIZE = 95
SPACING = 10
BOTTOM_ROW_HEIGHT = 80

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

class Game2048:
    def __init__(self):
        self.gamegrid = [" "] * 16
        self.score = 0
        for _ in range(2):
            self.spawn_new_tile()
    
    def spawn_new_tile(self):
        highest_tile = 2
        empty_tiles = [i for i, tile in enumerate(self.gamegrid) if tile == " "]
        if empty_tiles:
            index = random.choice(empty_tiles)
            self.gamegrid[index] = str(2 ** random.randint(1, 2)) if highest_tile >= 4 else "2"

    def row_and_column_splitting(self):
        row_and_column_split = [[[], [], [], []], [[], [], [], []]]
        for i, tile in enumerate(self.gamegrid):
            if tile != " ":
                row_and_column_split[0][i // 4].append(tile)
                row_and_column_split[1][i % 4].append(tile)
        return row_and_column_split

    def construct_new_grid(self, direction, file_split):
        grid = [" " for _ in range(16)]
        if direction == "a":
            for i in range(4):
                for j in range(len(file_split[i])):
                    grid[i * 4 + j] = file_split[i][j]
        elif direction == "d":
            for i in range(4):
                for j in range(len(file_split[i])):
                    grid[i * 4 + (3 - j)] = file_split[i][len(file_split[i]) - j - 1]
        elif direction == "w":
            for i in range(4):
                for j in range(len(file_split[i])):
                    grid[i + j * 4] = file_split[i][j]
        elif direction == "s":
            for i in range(4):
                for j in range(len(file_split[i])):
                    grid[i + (3 - j) * 4] = file_split[i][len(file_split[i]) - j - 1]
        return grid

    def new_merge(self, direction, test=False):
        merged = False
        row_and_column_split = self.row_and_column_splitting()
        is_column = 0 if direction in ["a", "d"] else 1
        for file in row_and_column_split[is_column]:
            file_len = len(file)
            if file_len >= 2:
                for v in range(file_len - 1):
                    if direction in ["a", "w"]:
                        if file[v] == file[v + 1]:
                            merged = True
                            file[v] = str(int(file[v]) * 2) + "m"
                            file[v + 1] = " "
                    elif direction in ["d", "s"]:
                        if file[file_len - v - 2] == file[file_len - v - 1]:
                            merged = True
                            file[file_len - v - 1] = str(int(file[file_len - v - 1]) * 2) + "m"
                            file[file_len - v - 2] = " "
            file[:] = [tile for tile in file if tile != " "]
            for i in range(len(file)):
                if "m" in file[i]:
                    file[i] = file[i].replace("m", "")
                    if test == False:
                        self.score += int(file[i])
        if not test:
            self.gamegrid = self.construct_new_grid(direction, row_and_column_split[is_column])
        if test is None:
            return self.construct_new_grid(direction, row_and_column_split[is_column])
        return merged if test else (self.gamegrid, self.score)

class Renderer:
    colours = { 
        "default": {
            "dfont":(119,110,101),
            "lfont":(249,246,242),
            "gridbg":(184,172,160), 
            "0":(202,192,180), 
            "2":(238,228,218), 
            "4":(237,224,200), 
            "8":(242,177,121), 
            "16":(245,149,99), 
            "32":(246,124,96), 
            "64":(246,94,59), 
            "128":(237,207,115), 
            "256":(237,204,98), 
            "512":(237,200,80), 
            "1024":(237,197,63), 
            "2048":(237,194,45),
            "bg":(252,247,241)
        },
        "sea":{
            "dfont":(43,43,43),
            "lfont":(232,232,232),
            "gridbg":(194, 210, 236),
            "0":(0,0,0),
            "2":(140, 188, 255),
            "4":(84, 155, 255),
            "8":(70, 180, 180),
            "16":(50, 210, 181),
            "32":(100, 210, 100),
            "64":(120, 210, 50),
            "128":(240, 100, 50),
            "256":(240, 100, 150),
            "512":(230, 50, 180),
            "1024":(210, 30, 220),
            "2048":(180, 0, 255),
            "bg":(255,255,255)
        }
    }

    def __init__(self, window_size, theme):
        self.window_size = window_size
        self.theme = theme

    def render_grid(self, gamegrid, window):
        x = SPACING
        y = SPACING
        pygame.draw.rect(window, self.colours[self.theme]["gridbg"], (0, 0, self.window_size, self.window_size))
        for tile in gamegrid:
            if tile != " ":
                inttile = int(tile)
                tilelen = len(str(tile))
                font = pygame.font.SysFont('quicksand', int(40/(tilelen**0.15)), bold=True)
                pygame.draw.rect(window, self.colours[self.theme][str(tile)], (x, y, TILE_SIZE, TILE_SIZE), border_radius=3)
                if inttile > 4:
                    text_surface = font.render(str(tile), False, self.colours[self.theme]["lfont"])
                else:
                    text_surface = font.render(str(tile), False, self.colours[self.theme]["dfont"])
                window.blit(text_surface, (x + 37 - int((tilelen)**2.3), y + 23 + tilelen*2))
            else:
                pygame.draw.rect(window, self.colours[self.theme]["0"], (x, y, TILE_SIZE, TILE_SIZE), border_radius=3)
            x += TILE_SIZE + SPACING
            if x >= self.window_size:
                x = SPACING
                y += TILE_SIZE + SPACING

    def render_score(self, score, window):
        font = pygame.font.SysFont('quicksand', 50)
        text_surface = font.render("Score: "+str(score), False, self.colours[self.theme]["dfont"])
        window.blit(text_surface, (5, self.window_size))

    def render_bottom_row(self, score, window):
        pygame.draw.rect(window, self.colours[self.theme]["bg"], (0, self.window_size, self.window_size, BOTTOM_ROW_HEIGHT))
        self.render_score(score, window)

def main():
    pygame.init()
    theme = "default"
    window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + BOTTOM_ROW_HEIGHT))
    pygame.display.set_caption('2048')

    game = Game2048()
    renderer = Renderer(WINDOW_SIZE, theme)

    while True:
        window.fill((renderer.colours[theme]["bg"]))
        allfull = all(tile != " " for tile in game.gamegrid)
        if allfull:
            if game.new_merge("w", test=True) or game.new_merge("a", test=True) or game.new_merge("s", test=True) or game.new_merge("d", test=True):
                allfull = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not allfull:
                    direction = None
                    if event.key in [pygame.K_w, pygame.K_UP]: direction = "w"
                    if event.key in [pygame.K_a, pygame.K_LEFT]: direction = "a"
                    if event.key in [pygame.K_s, pygame.K_DOWN]: direction = "s"
                    if event.key in [pygame.K_d, pygame.K_RIGHT]: direction = "d"
                    if direction and (game.new_merge(direction, test=True) or game.gamegrid != game.new_merge(direction, test=None)):
                        game.gamegrid, game.score = game.new_merge(direction)
                        game.spawn_new_tile()
        renderer.render_grid(game.gamegrid, window)
        renderer.render_bottom_row(game.score, window)
        pygame.display.update()

if __name__ == "__main__":
    main()

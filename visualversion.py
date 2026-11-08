"""Runs 2048 in pygame display with visual tiles and score display."""
import copy
import math
import random
from typing import Literal

import pygame

# Constants
WINDOW_SIZE = 430
TILE_SIZE = 95
WIN_TILE_SIZE = 125
SPACING = 10
SMALL_SPACING = 5
BOTTOM_ROW_HEIGHT = 80
RANDOM_LIST = random.sample(range(10000), 10000)
AI_DEPTH = 3

class HeuristicAI:
    def __init__(self):
        self.depth = AI_DEPTH
        self.state = False

    def set_state(self, state): self.state = state
    def get_state(self): return self.state

    def calculate_smoothness(self, game: 'Game2048'):
        """Calculate the smoothness of the grid (average log2 difference between adjacent tiles)."""
        smoothness = 0
        total_comparisons = 0
        gamegrid = [[],[],[],[]]
        for i, tile in enumerate(game.gamegrid):
            gamegrid[i // 4].append(tile)
        log_grid = [[math.log2(int(tile)) if tile != "0" else 0 for tile in row] for row in gamegrid]
        for row in range(len(log_grid)):
            for column in range(len(log_grid[row])):
                current_value = log_grid[row][column]
                if column < len(log_grid[row]) - 1:
                    right_value = log_grid[row][column + 1]
                    smoothness -= abs(current_value - right_value)
                    total_comparisons += 1
                if row < len(log_grid) - 1:
                    down_value = log_grid[row + 1][column]
                    smoothness -= abs(current_value - down_value)
                    total_comparisons += 1
        return smoothness / total_comparisons

    def generate_sequences(self):
        self.sequences = {}
        options = ["w", "a", "s", "d"]
        for i in range(4**self.depth):
            sequence = []
            for _ in range(self.depth):
                sequence.append(options[i % 4])
                i //= 4
            self.sequences["".join(sequence)] = 0

    def evaluate_sequences(self, game: 'Game2048'):
        """A Sequences score is defined as:
    The number of points gained from the move * how close the move is to the original position
    The number of valid moves * 25
    A anti-bonus for having the board too full: 4^(6 - number of empty tiles)
    Add the largest tile's value if it is in the corner (after move 10 only)
    Set Score to minus 100000 if the game is over and -1 million if a move is invalid"""
        self.generate_sequences()
        for sequence in self.sequences:
            game_copy = copy.deepcopy(game)
            self.points = 0
            cornerbonus = 0

            for move in sequence:
                if not game_copy.merge(move, mode="can_move"):
                    self.sequences[sequence] = -100000 if game_copy.check_full() else -1000000
                    break

                points_gained = game_copy.merge(move, mode="points")
                points_gained = points_gained if isinstance(points_gained, int) else 0

                game_copy.merge(move, mode="execute")
                game_copy.spawn_new_tile()

                self.intgamemgrid = [int(tile) for tile in game_copy.gamegrid]
                max_tile = max(self.intgamemgrid)

                if max_tile in (self.intgamemgrid[0], self.intgamemgrid[3], self.intgamemgrid[12], self.intgamemgrid[15]) and game_copy.moves > 10:
                    cornerbonus += max_tile / 2

                self.points += points_gained * (game.moves - game_copy.moves + self.depth)
            self.intgamemgrid = [int(tile) for tile in game_copy.gamegrid]
            tilebonus = 4 ** max(6 - self.intgamemgrid.count(0), 0)
            smoothness = round(self.calculate_smoothness(game_copy) * 100, 3)
            valid_moves = sum(1 for direction in ("w", "a", "s", "d") if game_copy.merge(direction, mode="can_move")) * 25
            if self.sequences[sequence] == 0:
                self.sequences[sequence] = self.points - tilebonus + smoothness + cornerbonus + valid_moves
        return max(self.sequences, key=lambda k: self.sequences[k])

    def make_move(self, game: 'Game2048'):
        game.merge(self.evaluate_sequences(game)[0], mode="execute")

class OptionBox:
    def __init__(self, display: pygame.Surface, rect: pygame.Rect | tuple[int, int, int, int], colour: pygame.Color | tuple[int, int, int], highlight_colour: pygame.Color | tuple[int, int, int], font: pygame.font.Font, font_colour: pygame.Color | tuple[int, int, int], option_list: list[str], selected = 0):
        self.colour = colour
        self.highlight_colour = highlight_colour
        self.rect = pygame.Rect(rect) if isinstance(rect, tuple) else rect
        self.font = font
        self.font_colour = font_colour
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.clicked = False
        self.active_option = -1
        self.display = display

    def draw(self):
        pygame.draw.rect(self.display, self.highlight_colour if self.menu_active else self.colour, self.rect)
        pygame.draw.rect(self.display, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, self.font_colour)
        self.display.blit(msg, msg.get_rect(center = self.rect.center))
        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(self.display, self.highlight_colour if i == self.active_option else self.colour, rect)
                msg = self.font.render(text, 1, self.font_colour)
                self.display.blit(msg, msg.get_rect(center = rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(self.display, (0, 0, 0), outer_rect, 2)

    def update(self):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break
        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.clicked = True
            if self.menu_active:
                self.draw_menu = not self.draw_menu
            elif self.draw_menu and self.active_option >= 0:
                self.selected = self.active_option
                self.draw_menu = False
                return self.active_option
        return -1

class Game2048:
    def __init__(self):
        self.gridsize = 16
        self.gamegrid = ["0"] * self.gridsize
        self.score = 0
        self.win = False
        self.winbefore = False
        self.moves = 0
        for _ in range(2):
            self.spawn_new_tile()

    def spawn_new_tile(self):
        highest_tile = max([int(tile) for tile in self.gamegrid if tile != "0"]) if any(tile != "0" for tile in self.gamegrid) else 2
        empty_tiles = [i for i, tile in enumerate(self.gamegrid) if tile == "0"]
        if empty_tiles:
            index = empty_tiles[RANDOM_LIST[self.moves % 10000] % len(empty_tiles)]
            self.gamegrid[index] = str(4 if RANDOM_LIST[self.moves % 10000] % 4 == 0 else 2) if highest_tile >= 4 else "2"

    def construct_merge_array(self, direction: Literal["w", "a", "s", "d"]) -> list[list[str]]:
        merge_array: list[list[str]] = [[self.gamegrid[ ((i * 4) + j) if direction in ("w", "s") else (i + (j * 4)) ] for i in range(4)] for j in range(4)]
        if direction in ("s", "d"):
            merge_array = [merge_array[i][::-1] for i in range(4)]
        return merge_array

    def merge(self, direction: Literal["w", "a", "s", "d"], mode: Literal["execute", "simulate", "can_move", "points"] = "execute"):
        merge_grid: list[list[str]] = self.construct_merge_array(direction)
        new_grid: list[list[str]] = []
        points_gained: int = 0

        for file in merge_grid:
            file_no_empty = [tile for tile in file if tile != "0"]
            if not file_no_empty:
                new_grid.append(file)
                continue

            processed_file = []
            i = 0
            while i < len(file_no_empty):
                if i + 1 < len(file_no_empty) and file_no_empty[i] == file_no_empty[i + 1]:
                    new_value = int(file_no_empty[i]) * 2
                    processed_file.append(str(new_value))
                    points_gained += new_value
                    i += 2
                else:
                    processed_file.append(file_no_empty[i])
                    i += 1
            padded_file = processed_file + ["0"] * (4 - len(processed_file))
            new_grid.append(padded_file)

        resulting_grid = self.construct_new_grid_v2(new_grid, direction)

        if mode == "can_move":
            return self.gamegrid != resulting_grid
        elif mode == "points":
            return points_gained
        elif mode == "simulate":
            return resulting_grid
        elif mode == "execute":
            self.gamegrid = resulting_grid
            self.score += points_gained
            self.moves += 1
            return self.gamegrid, self.score

    def construct_new_grid_v2(self, new_merged_grid: list[list[str]], direction: Literal["w", "a", "s", "d"]) -> list[str]:
        if direction in ("s", "d"):
            new_merged_grid = [new_merged_grid[i][::-1] for i in range(4)]
        return [new_merged_grid[i % 4][i // 4] if direction in ("w", "s") else new_merged_grid[i // 4][i % 4] for i in range(16)]

    def check_win(self):
        self.win = False
        if "2048" in self.gamegrid and self.winbefore == False: self.win,self.winbefore = True, True
        return self.win

    def check_full(self):
        return all(tile != "0" for tile in self.gamegrid) and not any(self.merge(direction, mode="can_move") for direction in ("w", "a", "s", "d"))

COLOURS = {
    "Default": {
        "dfont&buttons":(119,110,101),
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
        "4096+":(50,50,50),
        "bg":(252,247,241),
        "highlight":(255,255,153)
    },
    "Sea":{
        "dfont&buttons":(43,43,43),
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
        "4096+":(50,50,50),
        "bg":(255,255,255),
        "highlight":(255,255,153)
    },
    "Traffic":{
         "dfont&buttons":(10,10,10),
         "lfont":(255,255,255),
         "gridbg":(100,100,100),
         "0":(0,0,0),
         "2":(255,0,0),
         "4":(255, 50, 0),
         "8":(255, 100, 0),
         "16":(255, 150, 0),
         "32":(255,200,0),
         "64":(235,225,0),
         "128":(180,235,0),
         "256":(150,255,0),
         "512":(100,255,0),
         "1024":(50,255,0),
         "2048":(0,255,0),
         "4096+":(50,50,50),
         "bg":(255,255,255),
         "highlight":(255,255,153)
    },
    "Disco":{
         "dfont&buttons":(20,20,10),
         "lfont":(255,255,180),
         "gridbg":(100,100,100),
         "0":(0,0,0),
         "2":(194,10,169),
         "4":(83, 50, 200),
         "8":(206, 166, 66),
         "16":(99, 0, 0),
         "32":(87,222,222),
         "64":(35,225,20),
         "128":(38,235,100),
         "256":(150,77,100),
         "512":(100,255,140),
         "1024":(50,255,222),
         "2048":(20,55,39),
         "4096+":(50,50,50),
         "bg":(204,175,96),
         "highlight":(255,255,153)
    },
    "Blurple":{
         "dfont&buttons":(0,0,0),
         "lfont":(240,240,240),
         "gridbg":(69,69,69),
         "0":(0,0,0),
         "2":(75,150,255),
         "4":(0,125,255),
         "8":(50,0,250),
         "16":(100, 0, 250),
         "32":(75,0,200),
         "64":(75,25,100),
         "128":(50,50,50),
         "256":(75,50,75),
         "512":(100,50,100),
         "1024":(100,0,150),
         "2048":(150,10,250),
         "4096+":(0,0,0),
         "bg":(125,75,200),
         "highlight":(240,240,240)
    }
}

class Button:
    """Creates a pygame.Rect object that can return whether it is pressed."""
    def __init__(self, gui: "Renderer", rect: tuple[int, int, int, int] | pygame.Rect, text: str, font_size: int = 25, border_radius: int = 0, border_size: int = 5) -> None:
        self.gui = gui
        self.rect = pygame.Rect(rect) if isinstance(rect, tuple) else rect
        self.font = pygame.font.SysFont("quicksand", size=font_size)
        self.text_bound_box = self.rect.inflate(-border_size * 2, -border_size * 2)
        self.text = text
        self.border_radius = border_radius
        self.clicked: bool = pygame.mouse.get_pressed()[0]

    def render(self):
        pygame.draw.rect(self.gui.display, COLOURS[self.gui.theme]["lfont"], self.rect, border_radius=self.border_radius)
        pygame.draw.rect(self.gui.display, COLOURS[self.gui.theme]["dfont&buttons"], self.text_bound_box, border_radius=self.border_radius)

        button_text: pygame.Surface = self.font.render(self.text, False, COLOURS[self.gui.theme]["lfont"])
        button_text_rect: pygame.Rect = button_text.get_rect(center=self.text_bound_box.center)

        if self.text_bound_box.contains(button_text_rect):
            self.gui.display.blit(button_text, button_text_rect)
        else:
            self.multiline_text()

    def multiline_text(self, line_padding: int = 4):
        """Renders self.text as two centred lines inside text_bound_box."""
        lines = [self.font.render(word, False, COLOURS[self.gui.theme]["lfont"]) for word in self.text_split(self.text)]
        total_height = sum(text.get_height() for text in lines) + line_padding * (len(lines) - 1)
        top = self.text_bound_box.centery - total_height // 2

        for text in lines:
            text_rect = text.get_rect(centerx=self.text_bound_box.centerx, top=top)
            self.gui.display.blit(text, text_rect)
            top += text.get_height() + line_padding

    def text_split(self, text: str) -> list[str]:
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word]) if current_line else word
            if self.font.size(test_line)[0] <= self.text_bound_box.width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def button_clicked(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] and not self.clicked:
            self.clicked = True
            action = True
        else:
            self.clicked = bool(pygame.mouse.get_pressed()[0])
        return action

class Renderer:
    def __init__(self, theme: str = "Default"):
        self.display = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + BOTTOM_ROW_HEIGHT))
        self.window_size: int = WINDOW_SIZE
        self.theme = theme
        self.clicked: bool = False
        self.themelist = [themename for themename in COLOURS]
        self.create_option_box()

        win_tile_bg_size = WIN_TILE_SIZE + SPACING * 2
        self.element_sizes: dict[str, pygame.Rect] = {
            "background": self.display.get_rect(),
            "bottom_row": pygame.Rect(0, self.window_size, self.window_size, BOTTOM_ROW_HEIGHT),
            "score": pygame.Rect(SPACING, self.window_size + SPACING, self.window_size * 3 // 5 - SPACING, BOTTOM_ROW_HEIGHT - SPACING * 2),
            "bottom_settings_button": pygame.Rect(self.window_size * 3 // 5, self.window_size, self.window_size // 5 + SPACING, BOTTOM_ROW_HEIGHT),
            "menu_button": pygame.Rect(self.window_size * 4 // 5 + SPACING, self.window_size, self.window_size // 5 - SPACING, BOTTOM_ROW_HEIGHT),
            "win_tile_bg": pygame.Rect((self.window_size - win_tile_bg_size) // 2, 50, win_tile_bg_size, win_tile_bg_size),
            "continue_button": pygame.Rect(self.window_size // 4, self.window_size * 2 // 3, self.window_size // 4, self.get_line_height(30) + SPACING * 2),
            "win_restart_button": pygame.Rect(self.window_size // 2, self.window_size * 2 // 3, self.window_size // 4, self.get_line_height(30) + SPACING * 2),
            "lose_restart_button": pygame.Rect(self.window_size // 4, self.display.get_height() // 2 + self.get_line_height(40), self.window_size // 4, self.get_line_height(35) + SPACING * 2),
            "lose_menu_button": pygame.Rect(self.window_size // 2, self.display.get_height() // 2 + self.get_line_height(40), self.window_size // 4, self.get_line_height(35) + SPACING * 2),
            "play_button": pygame.Rect(self.window_size // 4, self.display.get_height() // 2 - 40, self.window_size // 2, self.get_line_height(45) + SPACING * 4),
            "settings_button": pygame.Rect(self.window_size // 4, self.display.get_height() // 2 - 40 + self.get_line_height(45) + SPACING * 4, self.window_size // 2, self.get_line_height(45) + SPACING * 4),
            "quit_button": pygame.Rect(self.window_size // 4, self.display.get_height() // 2 - 40 + self.get_line_height(45) * 2 + SPACING * 8, self.window_size // 2, self.get_line_height(45) + SPACING * 4),
            "ai_enabled_button": pygame.Rect(self.window_size * 3 // 5, (self.display.get_height() - self.get_line_height(30) - SPACING * 2) // 2 + 20, self.window_size // 6, self.get_line_height(30) + SPACING * 2),
            "back_button": pygame.Rect(self.window_size - (self.get_line_height(30) + SPACING * 3), SPACING, self.get_line_height(30) + SPACING * 2, self.get_line_height(30) + SPACING * 2)
        }

        self.buttons: dict[str, list[Button]] = {
            "main_menu": [
                Button(self, self.element_sizes["play_button"], "Play", font_size=45, border_radius=10, border_size=SMALL_SPACING),
                Button(self, self.element_sizes["settings_button"], "Settings", font_size=45, border_radius=10, border_size=SMALL_SPACING),
                Button(self, self.element_sizes["quit_button"], "Quit", font_size=45, border_radius=10, border_size=SMALL_SPACING)
            ],
            "settings": [
                Button(self, self.element_sizes["ai_enabled_button"], "Off", font_size=30, border_radius=10, border_size=SMALL_SPACING),
                Button(self, self.element_sizes["back_button"], "X", font_size=30, border_radius=10, border_size=SMALL_SPACING)
            ],
            "bottom_row": [
                Button(self, self.element_sizes["bottom_settings_button"], "Settings", font_size=25, border_radius=10, border_size=SMALL_SPACING),
                Button(self, self.element_sizes["menu_button"], "Menu", font_size=25, border_radius=10, border_size=SMALL_SPACING)
            ],
            "winscreen": [
                Button(self, self.element_sizes["continue_button"], "Continue", font_size=30, border_radius=10, border_size=SMALL_SPACING),
                Button(self, self.element_sizes["win_restart_button"], "Restart", font_size=30, border_radius=10, border_size=SMALL_SPACING)
            ],
            "losescreen": [
                Button(self, self.element_sizes["lose_restart_button"], "Restart", font_size=35, border_radius=10, border_size=SMALL_SPACING),
                Button(self, self.element_sizes["lose_menu_button"], "Menu", font_size=35, border_radius=10, border_size=SMALL_SPACING)
            ]
        }

    def get_line_height(self, font_size: int) -> int:
        return pygame.font.SysFont('quicksand', font_size).get_linesize()

    def clamp_surface_by_width(self, input_surface: pygame.Surface, clamping_rect: pygame.Rect | tuple[int, int, int, int] | None = None) -> pygame.Surface:
        """Takes a surface and scales it down to a new size based on the display width, if it is larger than the display width.
        Alternatiely, if a pygame.pygame.Rect object is provided, it will clamp it to the width of the rect."""
        if clamping_rect is None:
            scale_factor = min(1.0, (self.display.get_width() - 50) / input_surface.get_width())
        else:
            clamping_rect = pygame.Rect(clamping_rect) if isinstance(clamping_rect, tuple) else clamping_rect
            scale_factor = min(1.0, clamping_rect.width / input_surface.get_width())
        return pygame.transform.scale_by(input_surface, scale_factor) if scale_factor != 1.0 else input_surface

    def render_text_by_centre(self, text: str, centre_point: tuple[int, int], colour: pygame.Color | tuple[int, int, int], font_size: int = 25, bold: bool = False, font: pygame.font.Font | None = None, clamping_rect: pygame.Rect | tuple[int, int, int, int] | None = None) -> None:
        """Creates and blits a text object to the display based on the provided parameters. If a font is not provided, the function defines its own font with the supplied size.
        Additionally, if a clamping_rect is provided, the text is clamped to that size using the clamp_surface_by_width function."""
        if font is None:
            font = pygame.font.SysFont('quicksand', size=font_size, bold=bold)
        if clamping_rect is None:
            text_surface = font.render(text, False, colour)
        else:
            text_surface = self.clamp_surface_by_width(font.render(text, False, colour), clamping_rect)
        self.display.blit(text_surface, text_surface.get_rect(center=centre_point))

    def create_option_box(self, selected=0):
        self.themeoptions = OptionBox(self.display, (115, 175, 200, 250 // len(self.themelist)), COLOURS[self.theme]["bg"], COLOURS[self.theme]["highlight"], pygame.font.SysFont('quicksand', 30, bold=True), COLOURS[self.theme]["dfont&buttons"], self.themelist, selected)

    def render_grid(self, gamegrid: list[str]):
        x = SPACING
        y = SPACING
        self.clear_display()
        pygame.draw.rect(self.display, COLOURS[self.theme]["gridbg"], (0, 0, self.window_size, self.window_size))
        for tile in gamegrid:
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.display, COLOURS[self.theme][tile if int(tile) <= 2048 else "4096+"], tile_rect, border_radius=3)
            if tile != "0":
                self.render_text_by_centre(tile, tile_rect.center, COLOURS[self.theme]["lfont" if int(tile) > 4 else "dfont&buttons"], font_size=40, bold=True, clamping_rect=tile_rect.inflate(-20, -20))
            x += TILE_SIZE + SPACING
            if x >= self.window_size:
                x = SPACING
                y += TILE_SIZE + SPACING

    def render_bottom_row(self, score: int) -> None:
        pygame.draw.rect(self.display, COLOURS[self.theme]["bg"], self.element_sizes["bottom_row"])
        self.render_text_by_centre(f"Score: {score}", self.element_sizes["score"].center, COLOURS[self.theme]["dfont&buttons"], font_size=50, clamping_rect=self.element_sizes["score"])

    def clear_display(self) -> None:
        self.display.fill(COLOURS[self.theme]["bg"])

    def render_winscreen(self) -> None:
        self.render_text_by_centre("You Win!", self.element_sizes["background"].center, COLOURS[self.theme]["dfont&buttons"], font_size=50, bold=True)
        #2048 Tile Rendering
        pygame.draw.rect(self.display, COLOURS[self.theme]["gridbg"], self.element_sizes["win_tile_bg"])
        pygame.draw.rect(self.display, COLOURS[self.theme]["2048"], self.element_sizes["win_tile_bg"].inflate(-SPACING * 2, -SPACING * 2), border_radius=6)
        self.render_text_by_centre("2048", self.element_sizes["win_tile_bg"].center, COLOURS[self.theme]["lfont"], font_size=50, bold=True)

    def render_losescreen(self, score: int) -> None:
        self.render_text_by_centre("You Lose...", (self.element_sizes["background"].centerx, self.element_sizes["background"].centery - 70), COLOURS[self.theme]["dfont&buttons"], font_size=60)
        self.render_text_by_centre(f"Your Score: {score}", (self.element_sizes["background"].centerx, self.element_sizes["background"].centery), COLOURS[self.theme]["dfont&buttons"], font_size=40)

    def render_menu(self) -> None:
        self.clear_display()
        self.render_text_by_centre("2048", (self.element_sizes["background"].centerx, self.element_sizes["background"].centery - 120), COLOURS[self.theme]["dfont&buttons"], font_size=70, bold=True)

    def render_settings(self) -> None:
        self.selectoption = self.themeoptions.update()
        if self.selectoption != -1: self.theme = self.themelist[self.selectoption]
        if self.themeoptions.colour != COLOURS[self.theme]["bg"]: self.create_option_box(self.selectoption)
        #Text Rendering
        font = pygame.font.SysFont('quicksand', 40, bold=True)
        self.render_text_by_centre("Settings:", (self.element_sizes["background"].centerx, self.get_line_height(60)), COLOURS[self.theme]["dfont&buttons"], font_size=60, bold=True)
        self.render_text_by_centre("Themes:", (self.element_sizes["background"].centerx, self.element_sizes["background"].centery-110), COLOURS[self.theme]["dfont&buttons"], font=font)
        self.render_text_by_centre("AI Enabled:", (self.element_sizes["background"].centerx - (font.size("AI Enabled:")[0] // 3), self.element_sizes["background"].centery + 20), COLOURS[self.theme]["dfont&buttons"], font=font)
        self.themeoptions.draw()

    def button_clicked(self, buttons: list[Button]) -> str | None:
        for button in buttons:
            button.render()
            if button.button_clicked():
                self.update_all_button_states()
                return button.text

    def update_all_button_states(self) -> None:
        "Cycles all buttons to ensure they know the current state of the mouse."
        for buttons in self.buttons.values():
            for button in buttons:
                button.button_clicked()

class GameController:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('2048')
        self.game: Game2048 = Game2048()
        self.hai: HeuristicAI = HeuristicAI()
        self.renderer: Renderer = Renderer()
        self.show_menu: bool = True
        self.KEY_MAP: dict[int, Literal['w', 'a', 's', 'd']] = {
            pygame.K_w: "w", pygame.K_UP: "w",
            pygame.K_a: "a", pygame.K_LEFT: "a",
            pygame.K_s: "s", pygame.K_DOWN: "s",
            pygame.K_d: "d", pygame.K_RIGHT: "d"
        }

    def handle_game_events(self) -> None:
        """Processes events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type != pygame.KEYDOWN or self.hai.get_state():
                continue

            direction = self.KEY_MAP.get(event.key)
            if not direction or not self.game.merge(direction, mode="can_move"):
                continue

            self.game.merge(direction, mode="execute")
            self.game.spawn_new_tile()

    def run_game(self) -> bool:
        """Executes the gameloop. Returns whether the user won."""
        while not self.game.check_full():
            if self.game.check_win():
                return True

            self.handle_game_events()
            if self.hai.get_state():
                self.hai.make_move(self.game)
                self.game.spawn_new_tile()

            self.renderer.render_grid(self.game.gamegrid)
            self.renderer.render_bottom_row(self.game.score)
            button_clicked = self.renderer.button_clicked(self.renderer.buttons["bottom_row"])
            if button_clicked == "Settings":
                self.settings()
            if button_clicked == "Menu":
                self.show_menu = True
                self.quit_if_menu()

            pygame.display.update()

        return False

    def menu(self) -> bool:
        """Renders the menu screen. Returns whether or not to quit."""
        while self.show_menu:
            self.renderer.render_menu()
            button_clicked = self.renderer.button_clicked(self.renderer.buttons["main_menu"])
            if button_clicked == "Settings":
                self.settings()
            if button_clicked in ("Play", "Quit"):
                return button_clicked == "Quit"
            pygame.display.update()
            self.check_quit()
        return False

    def quit_if_menu(self) -> None:
        if self.menu():
            pygame.quit()
            raise SystemExit

    def settings(self) -> None:
        while True:
            self.renderer.clear_display()
            button_clicked = self.renderer.button_clicked(self.renderer.buttons["settings"])
            self.renderer.render_settings()
            if button_clicked == "X": return
            if button_clicked in ("On", "Off"):
                self.hai.set_state(not self.hai.get_state())
                self.renderer.buttons["settings"][0].text = "On" if self.hai.get_state() else "Off"
            pygame.display.update()
            self.check_quit()

    def win(self) -> None:
        self.renderer.render_winscreen()
        while True:
            button_clicked = self.renderer.button_clicked(self.renderer.buttons["winscreen"])
            if button_clicked == "Restart": self.restart()
            if button_clicked:
                self.show_menu = False
                return
            pygame.display.update()
            self.check_quit()

    def loss(self) -> None:
        "Renders the losing screen. Returns whether to instantly restart or not."
        self.renderer.render_losescreen(self.game.score)
        while True:
            button_clicked = self.renderer.button_clicked(self.renderer.buttons["losescreen"])
            if button_clicked:
                self.restart()
                self.show_menu = button_clicked == "Menu"
                return
            pygame.display.update()
            self.check_quit()

    def restart(self) -> None:
        """Creates a new game instance."""
        self.game = Game2048()
        self.hai = HeuristicAI()
        self.renderer.buttons["settings"][0].text = "Off"

    def check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

    def main(self) -> None:
        while True:
            self.quit_if_menu()
            win: bool = self.run_game()
            self.renderer.clear_display()
            if win:
                self.win()
            else:
                self.loss()

if __name__ == "__main__":
    GameController().main()

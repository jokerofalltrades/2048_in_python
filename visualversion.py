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
RANDOM_LIST = random.sample(range(0, 10000), 10000)
AI_DEPTH = 5

class Heuristic_AI:
    def __init__(self, game):
        self.game = game
        self.depth = AI_DEPTH
        self.state = False

    def set_state(self, state): self.state = state
    def get_state(self): return self.state

    def generate_sequences(self):
        self.sequences = {}
        options = ["w", "a", "s", "d"]
        for i in range(4**self.depth):
            sequence = []
            for _ in range(self.depth):
                sequence.append(options[i % 4])
                i //= 4
            self.sequences["".join(sequence)] = 0
    
    def evaluate_sequences(self, game):
        # A Sequences score is defined as:
        # The Current Score
        # Minus the (tiles on the board - 12) * 50
        # Add 100 if the largest value tile is in the corner (after move 10 only)
        # Set Score to minus 1000 if the game is over.
        self.cachedmoves = game.moves
        self.cachedgrid = game.gamegrid
        self.cachedscore = game.score
        self.generate_sequences()
        for sequence in self.sequences:
            self.points = 0
            cornerbonus = 0
            for move in sequence:
                startscore = game.score
                if game.check_full():
                    self.sequences[sequence] = -100000
                    break
                if game.new_merge(move, test='grid'):
                    game.new_merge(move)
                    game.spawn_new_tile()
                else:
                    self.sequences[sequence] = -1000000
                    break
                self.intgamemgrid = [int(tile) if tile != " " else 0 for tile in game.gamegrid]
                cornerbonus += int(max(self.intgamemgrid))/2 if max(self.intgamemgrid) in [self.intgamemgrid[0],self.intgamemgrid[3],self.intgamemgrid[12],self.intgamemgrid[15]] and game.moves > 10 else 0
                self.points += (game.score - startscore) * (self.cachedmoves - game.moves + self.depth)
            self.intgamemgrid = [int(tile) if tile != " " else 0 for tile in game.gamegrid]
            tilebonus = 5**(6-len([i for i, tile in enumerate(self.intgamemgrid) if tile == " "])) if len([i for i, tile in enumerate(self.intgamemgrid) if tile == " "]) < 6 else 0
            valid_moves = sum(1 for direction in ["w", "a", "s", "d"] if game.new_merge(direction, test=True))*50
            if self.sequences[sequence] == 0:
                self.sequences[sequence] = self.points - tilebonus + cornerbonus + valid_moves
            game.gamegrid = self.cachedgrid
            game.moves = self.cachedmoves
            game.score = self.cachedscore
        return list(self.sequences.keys())[list(self.sequences.values()).index(max(self.sequences.values()))]
    
    def make_move(self, game):
        game.new_merge(self.evaluate_sequences(game)[0])

class OptionBox:
    def __init__(self, x, y, w, h, colour, highlight_colour, font, font_colour, option_list, selected = 0):
        self.colour = colour
        self.highlight_colour = highlight_colour
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.font_colour = font_colour
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.clicked = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_colour if self.menu_active else self.colour, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, self.font_colour)
        surf.blit(msg, msg.get_rect(center = self.rect.center))
        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_colour if i == self.active_option else self.colour, rect)
                msg = self.font.render(text, 1, self.font_colour)
                surf.blit(msg, msg.get_rect(center = rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

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
        self.gamegrid = [" "] * self.gridsize
        self.score = 0
        self.win = False
        self.winbefore = False
        self.moves = 0
        for _ in range(2):
            self.spawn_new_tile()
    
    def spawn_new_tile(self):
        highest_tile = max([int(tile) for tile in self.gamegrid if tile != " "]) if any(tile != " " for tile in self.gamegrid) else 2
        empty_tiles = [i for i, tile in enumerate(self.gamegrid) if tile == " "]
        if empty_tiles:
            index = empty_tiles[RANDOM_LIST[self.moves%10000] % len(empty_tiles)]
            self.gamegrid[index] = str(4 if RANDOM_LIST[self.moves%10000]%4 == 0 else 2) if highest_tile >= 4 else "2"

    def row_and_column_splitting(self):
        row_and_column_split = [[[], [], [], []], [[], [], [], []]]
        for i, tile in enumerate(self.gamegrid):
            if tile != " ":
                row_and_column_split[0][i // 4].append(tile)
                row_and_column_split[1][i % 4].append(tile)
        return row_and_column_split

    def construct_new_grid(self, direction, file_split):
        rowcolumnmatrix = [4, 1] if direction in ["a", "d"] else [1, 4]
        grid = [" " for _ in range(self.gridsize)]
        if direction in ["a","w"]:
            for i in range(4):
                for j in range(len(file_split[i])):
                    grid[i * rowcolumnmatrix[0] + j * rowcolumnmatrix[1]] = file_split[i][j]
        elif direction in ["d","s"]:
            for i in range(4):
                for j in range(len(file_split[i])):
                    grid[i * rowcolumnmatrix[0] + (3 - j) * rowcolumnmatrix[1]] = file_split[i][len(file_split[i]) - j - 1]
        return grid

    def new_merge(self, direction, test=False):
        oldgrid = self.gamegrid.copy()
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
                    if not test:
                        self.score += int(file[i])
        if not test:
            self.gamegrid = self.construct_new_grid(direction, row_and_column_split[is_column])
            self.moves += 1
        if test is None:
            return self.construct_new_grid(direction, row_and_column_split[is_column])
        if test == 'grid':
            return oldgrid != self.construct_new_grid(direction, row_and_column_split[is_column])
        return merged if test else (self.gamegrid, self.score)
    
    def check_win(self):
        self.win = False
        if "2048" in self.gamegrid and self.winbefore == False: self.win,self.winbefore = True,True
        return self.win
    
    def check_full(self):
        return all(tile != " " for tile in self.gamegrid) and not any(self.new_merge(direction, test=True) for direction in ["w", "a", "s", "d"])

class Renderer:
    colours = { 
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

    def __init__(self, window_size, theme):
        self.window_size = window_size
        self.theme = theme
        self.cachedscore = 1
        self.cachedsize = 0
        self.clicked = False
        self.themelist = [themename for themename in self.colours]
        self.create_option_box()

    def create_option_box(self, selected=0):
        self.themeoptions = OptionBox(115,175,200,250//len(self.themelist),self.colours[self.theme]["bg"],self.colours[self.theme]["highlight"],pygame.font.SysFont('quicksand', 30, bold=True),self.colours[self.theme]["dfont&buttons"],self.themelist,selected)
    
    def render_grid(self, gamegrid, window):
        x = SPACING
        y = SPACING
        window.fill((self.colours[self.theme]["bg"]))
        pygame.draw.rect(window, self.colours[self.theme]["gridbg"], (0, 0, self.window_size, self.window_size))
        for tile in gamegrid:
            if tile != " ":
                tilelen = len(str(tile))
                font = pygame.font.SysFont('quicksand', int(40/(tilelen**0.15)), bold=True)
                if int(tile) <= 2048:
                    pygame.draw.rect(window, self.colours[self.theme][str(tile)], (x, y, TILE_SIZE, TILE_SIZE), border_radius=3)
                else:
                    pygame.draw.rect(window, self.colours[self.theme]["4096+"], (x, y, TILE_SIZE, TILE_SIZE), border_radius=3)
                if int(tile) > 4:
                    text_surface = font.render(str(tile), False, self.colours[self.theme]["lfont"])
                else:
                    text_surface = font.render(str(tile), False, self.colours[self.theme]["dfont&buttons"])
                text_rect = text_surface.get_rect(center=(x+(TILE_SIZE/2), y+(TILE_SIZE/2)))
                window.blit(text_surface, text_rect)
            else:
                pygame.draw.rect(window, self.colours[self.theme]["0"], (x, y, TILE_SIZE, TILE_SIZE), border_radius=3)
            x += TILE_SIZE + SPACING
            if x >= self.window_size:
                x = SPACING
                y += TILE_SIZE + SPACING

    def render_bottom_row(self, score, window):
        pygame.draw.rect(window, self.colours[self.theme]["bg"], (0, self.window_size, self.window_size, BOTTOM_ROW_HEIGHT))
        #Rendering Buttons
        font = pygame.font.SysFont('quicksand', 25)
        settings_text = font.render("Settings", False, self.colours[self.theme]["lfont"])
        menu_text = font.render("Menu", False, self.colours[self.theme]["lfont"])
        settings_button = Rect((self.window_size-(settings_text.get_rect().width+SPACING*6+menu_text.get_rect().width), self.window_size+((BOTTOM_ROW_HEIGHT-settings_text.get_rect().height-SPACING)*0.5), settings_text.get_rect().width+SPACING*2, settings_text.get_rect().height+SPACING))
        menu_button = Rect((self.window_size-(menu_text.get_rect().width+SPACING*3), self.window_size+((BOTTOM_ROW_HEIGHT-menu_text.get_rect().height-SPACING)*0.5), menu_text.get_rect().width+SPACING*2, menu_text.get_rect().height+SPACING))
        settings_rect = settings_text.get_rect(center=settings_button.center)
        menu_rect = menu_text.get_rect(center=menu_button.center)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], settings_button, border_radius=10)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], menu_button, border_radius=10)
        window.blit(menu_text, menu_rect)
        window.blit(settings_text, settings_rect)
        #Rendering Score
        size = 50
        score_boundbox = Rect(SPACING, self.window_size+SPACING, (self.window_size-settings_button.width-menu_button.width-SPACING*4), BOTTOM_ROW_HEIGHT-SPACING*2)
        if score != self.cachedscore:
            scorefont = pygame.font.SysFont('quicksand', size)
            score_text = scorefont.render("Score: "+str(score), False, self.colours[self.theme]["dfont&buttons"])
            while not score_boundbox.contains(score_text.get_rect(center=score_boundbox.center)):
                size -= 1
                scorefont = pygame.font.SysFont('quicksand', size)
                score_text = scorefont.render("Score: "+str(score), False, self.colours[self.theme]["dfont&buttons"])
            self.cachedscore = score
            self.cachedsize = size
        else:
            scorefont = pygame.font.SysFont('quicksand', self.cachedsize)
            score_text = scorefont.render("Score: "+str(score), False, self.colours[self.theme]["dfont&buttons"])
        score_rect = score_text.get_rect(center=score_boundbox.center)
        window.blit(score_text, score_rect)
        return settings_button, menu_button
        
    def render_winscreen(self, window) -> tuple:
        #Text Rendering
        background_rect = Rect(0, 0, self.window_size, self.window_size+BOTTOM_ROW_HEIGHT)
        pygame.draw.rect(window, (self.colours[self.theme]["bg"]), background_rect)
        font = pygame.font.SysFont('quicksand', 50, bold=True)
        win_text = font.render("You Win!", False, self.colours[self.theme]["dfont&buttons"])
        win_text_rect = win_text.get_rect(center=background_rect.center)
        window.blit(win_text, win_text_rect)
        #2048 Tile Rendering
        large_tile_size = int(TILE_SIZE*1.25)
        font = pygame.font.SysFont('quicksand', 40, bold=True)
        text_2048 = font.render("2048", False, self.colours[self.theme]["lfont"])
        tile_rect = Rect((self.window_size-large_tile_size)/2, 60, large_tile_size, large_tile_size)
        pygame.draw.rect(window, self.colours[self.theme]["gridbg"], ((self.window_size-(large_tile_size+SPACING*2))/2, 50, large_tile_size+SPACING*2, large_tile_size+SPACING*2))
        pygame.draw.rect(window, self.colours[self.theme]["2048"], tile_rect, border_radius=6)
        text_rect = text_2048.get_rect(center=tile_rect.center)
        window.blit(text_2048, text_rect)
        #Button Rendering
        font = pygame.font.SysFont('quicksand', 30)
        continue_text = font.render("Continue", False, self.colours[self.theme]["lfont"])
        restart_text = font.render("Restart", False, self.colours[self.theme]["lfont"])
        continue_button = Rect((self.window_size-(continue_text.get_rect().width+restart_text.get_rect().width+SPACING*5))/2, background_rect.centery+win_text_rect.height, continue_text.get_rect().width+SPACING*2, continue_text.get_rect().height+SPACING)
        restart_button = Rect((self.window_size-restart_text.get_rect().width+SPACING+continue_text.get_rect().width)/2, background_rect.centery+win_text_rect.height, restart_text.get_rect().width+SPACING*2, restart_text.get_rect().height+SPACING)
        continue_rect = continue_text.get_rect(center=continue_button.center)
        restart_rect = restart_text.get_rect(center=restart_button.center)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], continue_button, border_radius=10)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], restart_button, border_radius=10)
        window.blit(continue_text, continue_rect)
        window.blit(restart_text, restart_rect)
        return continue_button, restart_button
    
    def render_losescreen(self, window, score) -> tuple:
        #Text Rendering
        background_rect = Rect(0, 0, self.window_size, self.window_size+BOTTOM_ROW_HEIGHT)
        pygame.draw.rect(window, (self.colours[self.theme]["bg"]), background_rect)
        font = pygame.font.SysFont('quicksand', 60, bold=True)
        font2 = pygame.font.SysFont('quicksand', 40, bold=True)
        lose_text = font.render("You Lose...", False, self.colours[self.theme]["dfont&buttons"])
        score_text = font2.render("Your Score: "+str(score), False, self.colours[self.theme]["dfont&buttons"])
        lose_text_rect = lose_text.get_rect(center=background_rect.center)
        score_text_rect = score_text.get_rect(center=background_rect.center)
        lose_text_rect.y -= 50
        score_text_rect.y += 20
        window.blit(lose_text, lose_text_rect)
        window.blit(score_text, score_text_rect)
        #Button Rendering
        font = pygame.font.SysFont('quicksand', 35)
        menu_text = font.render("Menu", False, self.colours[self.theme]["lfont"])
        restart_text = font.render("Restart", False, self.colours[self.theme]["lfont"])
        menu_button = Rect((self.window_size-menu_text.get_rect().width+SPACING+restart_text.get_rect().width)/2, background_rect.centery+lose_text_rect.height, menu_text.get_rect().width+SPACING*2, menu_text.get_rect().height+SPACING)
        restart_button = Rect((self.window_size-(menu_text.get_rect().width+restart_text.get_rect().width+SPACING*5))/2, background_rect.centery+lose_text_rect.height, restart_text.get_rect().width+SPACING*2, restart_text.get_rect().height+SPACING)
        menu_rect = menu_text.get_rect(center=menu_button.center)
        restart_rect = restart_text.get_rect(center=restart_button.center)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], menu_button, border_radius=10)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], restart_button, border_radius=10)
        window.blit(menu_text, menu_rect)
        window.blit(restart_text, restart_rect)
        return menu_button, restart_button
    
    def render_menu(self, window):
        background_rect = Rect(0, 0, self.window_size, self.window_size+BOTTOM_ROW_HEIGHT)
        pygame.draw.rect(window, (self.colours[self.theme]["bg"]), background_rect)
        #Text Rendering
        font = pygame.font.SysFont('quicksand', 70, bold=True)
        title_text = font.render("2048", False, self.colours[self.theme]["dfont&buttons"])
        title_text_rect = title_text.get_rect(center=background_rect.center)
        title_text_rect.y -= 100
        window.blit(title_text, title_text_rect)
        #Button Rendering
        font = pygame.font.SysFont('quicksand', 35)
        play_text = font.render("Play", False, self.colours[self.theme]["lfont"])
        sett_text = font.render("Settings", False, self.colours[self.theme]["lfont"])
        quit_text = font.render("Quit", False, self.colours[self.theme]["lfont"])      
        play_button = Rect((self.window_size-(play_text.get_rect().width+SPACING*2+sett_text.get_rect().width+SPACING*2+quit_text.get_rect().width+SPACING*2+SPACING*2))/2, background_rect.centery+title_text_rect.height, play_text.get_rect().width+SPACING*2, play_text.get_rect().height+SPACING)
        sett_button = Rect((self.window_size+play_text.get_rect().width+SPACING*2-(sett_text.get_rect().width+SPACING*2+quit_text.get_rect().width+SPACING*2))/2, background_rect.centery+title_text_rect.height, sett_text.get_rect().width+SPACING*2, sett_text.get_rect().height+SPACING)
        quit_button = Rect((self.window_size+play_text.get_rect().width+sett_text.get_rect().width-quit_text.get_rect().width+SPACING*4)/2, background_rect.centery+title_text_rect.height, quit_text.get_rect().width+SPACING*2, quit_text.get_rect().height+SPACING)
        play_rect = play_text.get_rect(center=play_button.center)
        sett_rect = sett_text.get_rect(center=sett_button.center)
        quit_rect = quit_text.get_rect(center=quit_button.center)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], play_button, border_radius=10)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], sett_button, border_radius=10)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], quit_button, border_radius=10)
        window.blit(play_text, play_rect)
        window.blit(sett_text, sett_rect)
        window.blit(quit_text, quit_rect)
        return play_button, sett_button, quit_button
        
    def render_settings(self, window):
        background_rect = Rect(0, 0, self.window_size, self.window_size+BOTTOM_ROW_HEIGHT)
        pygame.draw.rect(window, (self.colours[self.theme]["bg"]), background_rect)
        self.selectoption = self.themeoptions.update()
        if self.selectoption != -1: self.theme = self.themelist[self.selectoption]
        if self.themeoptions.colour != self.colours[self.theme]["bg"]: self.create_option_box(self.selectoption)
        self.themeoptions.draw(window)
        #Text Rendering
        font = pygame.font.SysFont('quicksand', 60, bold=True)
        title_text = font.render("Settings:", False, self.colours[self.theme]["dfont&buttons"])
        title_text_rect = title_text.get_rect(center=background_rect.center)
        title_text_rect.y = 0
        window.blit(title_text, title_text_rect)
        font = pygame.font.SysFont('quicksand', 40, bold=True)
        themes_text = font.render("Themes:", False, self.colours[self.theme]["dfont&buttons"])
        themes_text_rect = themes_text.get_rect(center=(background_rect.centerx, background_rect.centery-110))
        window.blit(themes_text, themes_text_rect)
        #Button Rendering
        font = pygame.font.SysFont('quicksand', 35)
        back_text = font.render("X", False, self.colours[self.theme]["lfont"])
        back_button = Rect(WINDOW_SIZE-SPACING*2-back_text.get_rect().height, SPACING, back_text.get_rect().height + SPACING, back_text.get_rect().height + SPACING)
        back_rect = back_text.get_rect(center=back_button.center)
        pygame.draw.rect(window, self.colours[self.theme]["dfont&buttons"], back_button, border_radius=10)
        window.blit(back_text, back_rect)
        return back_button
    
    def butt_clicked(self, rect):
        action = False
        pos = pygame.mouse.get_pos()
        if rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action
        
def checkquit():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
def main():
    pygame.init()
    theme = "Default"
    setup = 2
    window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + BOTTOM_ROW_HEIGHT))
    pygame.display.set_caption('2048')
    game = Game2048()
    renderer = Renderer(WINDOW_SIZE, theme)
    while True:
        if setup == 2:
            while True:
                play_butt, sett_butt, quit_butt = renderer.render_menu(window)
                if renderer.butt_clicked(play_butt):
                    setup = 1
                    break
                if renderer.butt_clicked(sett_butt):
                    while True:
                        back_butt = renderer.render_settings(window)
                        if renderer.butt_clicked(back_butt): break
                        checkquit()
                        pygame.display.update()
                if renderer.butt_clicked(quit_butt):  
                    pygame.quit()
                    sys.exit()
                checkquit()
                pygame.display.update()
        if setup == 1:
            game = Game2048()
            setup = 0
        result = gameloop(window, game, renderer, hai=Heuristic_AI(game))
        if result == "win":
            while True:
                cont_butt, rest_butt = renderer.render_winscreen(window)
                pygame.display.update()
                if renderer.butt_clicked(cont_butt): break
                if renderer.butt_clicked(rest_butt):
                    setup = 1
                    break
                checkquit()
        if result == "lose":
            while True:
                quit_butt, rest_butt = renderer.render_losescreen(window, game.score)
                pygame.display.update()
                if renderer.butt_clicked(quit_butt):
                    setup = 2
                    break
                if renderer.butt_clicked(rest_butt):
                    setup = 1
                    break
                checkquit()
        if result == "menu":
            while True:
                play_butt, sett_butt, quit_butt = renderer.render_menu(window)
                if renderer.butt_clicked(play_butt): break
                if renderer.butt_clicked(sett_butt):
                    while True:
                        back_butt = renderer.render_settings(window)
                        if renderer.butt_clicked(back_butt): break
                        checkquit()
                        pygame.display.update()
                if renderer.butt_clicked(quit_butt):
                    pygame.quit()
                    sys.exit()
                checkquit()
                pygame.display.update()        

def gameloop(window, game, renderer, hai):
    while not game.check_full():
        allfull = game.check_full()
        if game.check_win():
            return "win"
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    hai.set_state(True) if not hai.get_state() else hai.set_state(False)
                if not allfull and not hai.get_state():
                    direction = None
                    if event.key in [pygame.K_w, pygame.K_UP]: direction = "w"
                    if event.key in [pygame.K_a, pygame.K_LEFT]: direction = "a"
                    if event.key in [pygame.K_s, pygame.K_DOWN]: direction = "s"
                    if event.key in [pygame.K_d, pygame.K_RIGHT]: direction = "d"
                    if direction and (game.new_merge(direction, test=True) or game.gamegrid != game.new_merge(direction, test=None)):
                        game.gamegrid, game.score = game.new_merge(direction)
                        game.spawn_new_tile()
        if hai.get_state():
            hai.make_move(game)
            game.spawn_new_tile()
        renderer.render_grid(game.gamegrid, window)
        sett_butt, menu_butt = renderer.render_bottom_row(game.score, window)
        if renderer.butt_clicked(sett_butt):
            while True:
                back_butt = renderer.render_settings(window)
                if renderer.butt_clicked(back_butt): break
                checkquit()
                pygame.display.update()
        if renderer.butt_clicked(menu_butt): return "menu"
        pygame.display.update()
    return "lose"

if __name__ == "__main__":
    main()

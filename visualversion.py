import math
import random
import pygame
from pygame.locals import *

colours = {
  "dfont":(119,110,101),
  "lfont":(249,246,242),
  "bg":(184,172,160), 
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
  "Bottom":(252,247,241)
}
gamegrid = []
tempgrid = []
num_of_rows = 4
num_of_columns = 4
highesttile = 1
score = 0
  
def fillgrid():
    for _i in range(num_of_rows*num_of_columns):
        gamegrid.append(" ")
        tempgrid.append(" ")

def spawnnewtile():
  global highesttile
  temphighesttile = int(highesttile)
  i = 0
  tile_not_chosen = True
  allfull = True
  for i in range(num_of_rows*num_of_columns):
    if gamegrid[i] == " ":
      allfull = False
      break
  if not allfull:
    while tile_not_chosen:
      i = random.randint(0,num_of_rows*num_of_columns-1)
      if gamegrid[i] == " ":
        tile_not_chosen = False
    if highesttile > 2:
      temphighesttile = 2
    tile_to_spawn = 2**(random.randint(1,temphighesttile))
    gamegrid[i] = str(tile_to_spawn)

def rowAndColumnSplitting():
    rowAndColumnSplit = [[[],[],[],[]],[[],[],[],[]]]
    gameLen = len(gamegrid)
    for i in range(gameLen):
        if gamegrid[i] != " ":
            rowAndColumnSplit[0][i // 4].append(str(gamegrid[i]))
            rowAndColumnSplit[1][i % 4].append(str(gamegrid[i]))
    return rowAndColumnSplit

def constructNewGrid(direction, fileSplit):
    grid = [" " for _ in range(16)]
    if direction == "a":
        for i in range(4):
            for j in range(len(fileSplit[i])):
                grid[i*4+j] = fileSplit[i][j]
    if direction == "d":
        for i in range(4):
            for j in range(len(fileSplit[i])):
                grid[i*4+(3-j)] = fileSplit[i][len(fileSplit[i])-j-1]
    if direction == "w":
        for i in range(4):
            for j in range(len(fileSplit[i])):
                grid[i+j*4] = fileSplit[i][j]
    if direction == "s":
        for i in range(4):
            for j in range(len(fileSplit[i])):
                grid[i+(3-j)*4] = fileSplit[i][len(fileSplit[i])-j-1]
    return grid

def newMerge(direction, score=0, test=False):
    merged = False
    rowAndColumnSplit = rowAndColumnSplitting()
    isColumn = 0 if direction == "a" or direction == "d" else 1
    for file in rowAndColumnSplit[isColumn]:
        fileLen = len(file)
        if fileLen >= 2:
            for v in range(fileLen - 1):
                if direction == "a" or direction == "w":
                    if file[v] == file[v+1]:
                        merged = True
                        file[v] = str(int(file[v])*2)+"m"
                        file[v+1] = " "
                if direction == "d" or direction == "s":
                    if file[fileLen-v-2] == file[fileLen-v-1]:
                        merged = True
                        file[fileLen-v-1] = str(int(file[fileLen-v-1])*2)+"m"
                        file[fileLen-v-2] = " "
        for tile in file[:]:
            if tile == " ":
                file.remove(tile)
        for i in range(len(file)):
            if "m" in file[i]:
                file[i] = file[i].replace("m","")
                score += int(file[i])
    if test == False:
        gamegrid = constructNewGrid(direction, rowAndColumnSplit[isColumn])
    if test == None:
        tempgrid = constructNewGrid(direction, rowAndColumnSplit[isColumn])
    if test == True:
        return merged
    if test == None:
        return tempgrid
    return gamegrid, score

def rendergrid(window):
    x = 10
    y = 10
    pygame.draw.rect(window, colours["bg"], (0, 0, 430, 430))
    for tile in gamegrid:
        if tile != " ":
            inttile = int(tile)
            tilelen = len(str(tile))
            font = pygame.font.SysFont('quicksand', int(40/(tilelen**0.15)), bold=True)
            pygame.draw.rect(window, colours[str(tile)], (x, y, 95, 95))
            if inttile > 4:
                text_surface = font.render(str(tile), False, colours["lfont"])
            else:
                text_surface = font.render(str(tile), False, colours["dfont"])
            window.blit(text_surface, (x + 37 - int((tilelen)**2.3), y + 25 + tilelen*2))
        else:
            pygame.draw.rect(window, colours["0"], (x, y, 95, 95))
        x += 105
        if x == 430:
            x = 10
            y += 105

def renderscore(window):
    font = pygame.font.SysFont('quicksand', 50)
    text_surface = font.render("Score: "+str(score), False, (119, 110, 101))
    window.blit(text_surface, (5, 430))
    
def renderBottomRow(window):
    pygame.draw.rect(window, colours["Bottom"], (0, 430, 430, 80))
    renderscore(window)

def rungame():
    WINDOW_SIZE = 430
    check = 0
    messageactive = 0
    global score
    global highesttile
    global gamegrid
    global tempgrid
    fillgrid()
    for _i in range(2):
        spawnnewtile()
    pygame.init()
    window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 80))
    pygame.display.set_caption('2048')
    while True:
        window.fill((255,255,255))
        allfull = True
        for i in range(num_of_rows*num_of_columns):
            if gamegrid[i] == " ":
                allfull = False
        if allfull:
            if newMerge("w",test=True) or newMerge("a",test=True) or newMerge("s",test=True) or newMerge("d",test=True):
                allfull = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not allfull or check == 1:
                    if (event.key == pygame.K_w or event.key == pygame.K_UP) and (newMerge("w",test=True) or gamegrid != newMerge("w",test=None)):
                        gamegrid, score = newMerge("w", score)
                        spawnnewtile()
                    if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and (newMerge("a",test=True) or gamegrid != newMerge("a",test=None)):
                        gamegrid, score = newMerge("a", score)
                        spawnnewtile()
                    if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and (newMerge("s",test=True) or gamegrid != newMerge("s",test=None)):
                        gamegrid, score = newMerge("s", score)
                        spawnnewtile()
                    if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and (newMerge("d",test=True) or gamegrid != newMerge("d",test=None)):
                        gamegrid, score = newMerge("d", score)
                        spawnnewtile()
                    check = 0
        rendergrid(window)
        renderBottomRow(window)
        pygame.display.update()
rungame()

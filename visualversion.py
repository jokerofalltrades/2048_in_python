import sys
import random
import pygame
from pygame.locals import *

colours = { 
    "default": {
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
    },
    "sea":{
        "dfont":(43,43,43),
        "lfont":(232,232,232),
        "bg":(194, 210, 236),
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
        "Bottom":(255,255,255)
    }
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

def spawnnewtile(allfull):
    highesttile = 2
    emptyTiles = []
    for i, tile in enumerate(gamegrid):
        if tile == " ": emptyTiles.append(i)
        elif int(tile) > highesttile: highesttile = int(tile)
    if not allfull:
        index = emptyTiles[random.randint(0,len(emptyTiles)-1)]
        gamegrid[index] = str(2**random.randint(1,2)) if highesttile >= 4 else "2"

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

def rendergrid(window, theme):
    x = 10
    y = 10
    pygame.draw.rect(window, colours[theme]["bg"], (0, 0, 430, 430))
    for tile in gamegrid:
        if tile != " ":
            inttile = int(tile)
            tilelen = len(str(tile))
            font = pygame.font.SysFont('quicksand', int(40/(tilelen**0.15)), bold=True)
            pygame.draw.rect(window, colours[theme][str(tile)], (x, y, 95, 95))
            if inttile > 4:
                text_surface = font.render(str(tile), False, colours[theme]["lfont"])
            else:
                text_surface = font.render(str(tile), False, colours[theme]["dfont"])
            window.blit(text_surface, (x + 37 - int((tilelen)**2.3), y + 25 + tilelen*2))
        else:
            pygame.draw.rect(window, colours[theme]["0"], (x, y, 95, 95))
        x += 105
        if x == 430:
            x = 10
            y += 105

def renderscore(window, theme):
    font = pygame.font.SysFont('quicksand', 50)
    text_surface = font.render("Score: "+str(score), False, colours[theme]["dfont"])
    window.blit(text_surface, (5, 430))
    
def renderBottomRow(window, theme):
    pygame.draw.rect(window, colours[theme]["Bottom"], (0, 430, 430, 80))
    renderscore(window, theme)

def rungame():
    WINDOW_SIZE = 430
    check = 0
    messageactive = 0
    theme = "default"
    global score
    global highesttile
    global gamegrid
    global tempgrid
    fillgrid()
    for _i in range(2):
        spawnnewtile(all(tile != " " for tile in gamegrid))
    pygame.init()
    window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 80))
    pygame.display.set_caption('2048')
    while True:
        window.fill((colours[theme]["bg"]))
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
                        spawnnewtile(all(tile != " " for tile in gamegrid))
                    if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and (newMerge("a",test=True) or gamegrid != newMerge("a",test=None)):
                        gamegrid, score = newMerge("a", score)
                        spawnnewtile(all(tile != " " for tile in gamegrid))
                    if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and (newMerge("s",test=True) or gamegrid != newMerge("s",test=None)):
                        gamegrid, score = newMerge("s", score)
                        spawnnewtile(all(tile != " " for tile in gamegrid))
                    if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and (newMerge("d",test=True) or gamegrid != newMerge("d",test=None)):
                        gamegrid, score = newMerge("d", score)
                        spawnnewtile(all(tile != " " for tile in gamegrid))
                    check = 0
        rendergrid(window, theme)
        renderBottomRow(window, theme)
        pygame.display.update()
rungame()

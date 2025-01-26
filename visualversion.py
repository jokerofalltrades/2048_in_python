import math
import random
import time
import pygame
import os
import sys
from pygame.locals import *

gamegrid = []
tempgrid = []
num_of_rows = 4
num_of_columns = 4
highesttile = 1
score = 0

def clear():
  os.system('cls' if os.name=='nt' else 'clear')

def getch():
  chr = str(input(""))
  return chr
  
def Update():
  global highesttile
  highesttile = int(highesttile)
  printgrid()
  print(f"Score: {score}")
  print("""
Use WASD to move the numbers around the grid. 
When same numbers combine, they double their number.
Your goal is to reach 2048.
If you have no legal moves the game is over.""")
  
def fillgrid():
  for _i in range(num_of_rows*num_of_columns):
    gamegrid.append(" ")
    tempgrid.append(" ")

def printgrid():
  for _i in range(num_of_columns):
    row_to_print = ""
    for _e in range(num_of_rows):
      if len(str(gamegrid[_i*num_of_columns+_e])) == 1:
        row_to_print += f"[    {gamegrid[_i*num_of_columns+_e]} ]"
      elif len(str(gamegrid[_i*num_of_columns+_e])) == 2:
        row_to_print += f"[   {gamegrid[_i*num_of_columns+_e]} ]"
      elif len(str(gamegrid[_i*num_of_columns+_e])) == 3:
        row_to_print += f"[  {gamegrid[_i*num_of_columns+_e]} ]"
      else:
        row_to_print += f"[ {gamegrid[_i*num_of_columns+_e]} ]"
    print(row_to_print)

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

def rowAndColumnSplit():
    rowSplit = [[],[],[],[]]
    columnSplit = [[],[],[],[]]
    gameLen = len(gamegrid)
    for i in range(gameLen):
        if gamegrid[i] != " ":
            rowSplit[i // 4].append(str(gamegrid[i]))
            columnSplit[i % 4].append(str(gamegrid[i]))
    return rowSplit, columnSplit

def constructNewGrid(direction, rowSplit=None, columnSplit=None, temp=False):
    if temp == False:
        gamegrid = [" " for _ in range(16)]
    if temp == True:
        tempgrid = [" " for _ in range(16)]
    if rowSplit != None:
        if direction == "a":
            for i in range(4):
                for j in range(len(rowSplit[i])):
                    if temp == False:
                        gamegrid[i*4+j] = rowSplit[i][j]
                    else:
                        tempgrid[i*4+j] = rowSplit[i][j]
        if direction == "d":
            for i in range(4):
                for j in range(len(rowSplit[i])):
                    if temp == False:
                        gamegrid[i*4+(3-j)] = rowSplit[i][len(rowSplit[i])-j-1]
                    else:
                        tempgrid[i*4+(3-j)] = rowSplit[i][len(rowSplit[i])-j-1]
    if columnSplit != None:
        if direction == "w":
            for i in range(4):
                for j in range(len(columnSplit[i])):
                    if temp == False:
                        gamegrid[i+j*4] = columnSplit[i][j]
                    else:
                        tempgrid[i+j*4] = columnSplit[i][j]
        if direction == "s":
            for i in range(4):
                for j in range(len(columnSplit[i])):
                    if temp == False:
                        gamegrid[i+(3-j)*4] = columnSplit[i][len(columnSplit[i])-j-1]
                    else:
                        tempgrid[i+(3-j)*4] = columnSplit[i][len(columnSplit[i])-j-1]
    if temp == False:
        return gamegrid
    if temp == True:
        return tempgrid

def newMerge(direction, score=0, test=False):
    merged = False
    rowSplit, columnSplit = rowAndColumnSplit()
    if direction == "a" or direction == "d":
        for row in rowSplit:
            rowLen = len(row)
            if rowLen >= 2:
                for v in range(rowLen - 1):
                    if direction == "a":
                        if row[v] == row[v+1]:
                            merged = True
                            row[v] = str(int(row[v])*2)+"m"
                            row[v+1] = " "
                    if direction == "d":
                        if row[rowLen-v-2] == row[rowLen-v-1]:
                            merged = True
                            row[rowLen-v-1] = str(int(row[rowLen-v-1])*2)+"m"
                            row[rowLen-v-2] = " "
            for tile in row[:]:
                if tile == " ":
                    row.remove(tile)
            for i in range(len(row)):
                if "m" in row[i]:
                    row[i] = row[i].replace("m","")
                    score += int(row[i])
        if test == False:
            gamegrid = constructNewGrid(direction, rowSplit=rowSplit)
        if test == None:
            tempgrid = constructNewGrid(direction, rowSplit=rowSplit, temp=True)
    if direction == "w" or direction == "s":
        for column in columnSplit:
            columnLen = len(column)
            if columnLen >= 2:
                for v in range(columnLen - 1):
                    if direction == "w":
                        if column[v] == column[v+1]:
                            merged = True
                            column[v] = str(int(column[v])*2)+"m"
                            column[v+1] = " "
                    if direction == "s":
                        if column[columnLen-v-2] == column[columnLen-v-1]:
                            merged = True
                            column[columnLen-v-1] = str(int(column[columnLen-v-1])*2)+"m"
                            column[columnLen-v-2] = " "
            for tile in column[:]:
                if tile == " ":
                    column.remove(tile)
            for i in range(len(column)):
                if "m" in column[i]:
                    column[i] = column[i].replace("m","")
                    score += int(column[i])
        if test == False:
            gamegrid = constructNewGrid(direction, columnSplit=columnSplit)
        if test == None:
            tempgrid = constructNewGrid(direction, columnSplit=columnSplit, temp=True)
    if test == True:
        return merged
    if test == None:
        return tempgrid
    return gamegrid, score

def rendergrid(window):
    colours = {"2":(238,228,218), "4":(237,224,200), "8":(242,177,121), "16":(245,149,99), "32":(246,124,96), "64":(246,94,59), "128":(237,207,115), "256":(237,204,98), "512":(237,200,80), "1024":(237,197,63), "2048":(237,194,45)}
    x = 5
    y = 5
    for tile in gamegrid:
        if tile != " ":
            inttile = int(tile)
            tilelen = len(str(tile))
            font = pygame.font.SysFont('quicksand', int(40/(tilelen**0.15)))
            pygame.draw.rect(window, colours[str(tile)], (x, y, 100, 100))
            if inttile > 4:
                text_surface = font.render(str(tile), False, (249, 246, 242))
            else:
                text_surface = font.render(str(tile), False, (119, 110, 101))
            window.blit(text_surface, (x + 40 - int((tilelen)**2.2), y + 25 + tilelen*2))
        x += 105
        if x == 425:
            x = 5
            y += 105

def renderscore(window):
    font = pygame.font.SysFont('quicksand', 50)
    text_surface = font.render("Score: "+str(score), False, (119, 110, 101))
    window.blit(text_surface, (5, 430))

def rungame():
    WINDOW_SIZE = 425
    check = 0
    messageactive = 0
    global score
    global highesttile
    global gamegrid
    global tempgrid
    fillgrid()
    for _i in range(2):
        spawnnewtile()
    Update()
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
                        Update()
                    if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and (newMerge("a",test=True) or gamegrid != newMerge("a",test=None)):
                        gamegrid, score = newMerge("a", score)
                        spawnnewtile()
                        Update()
                    if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and (newMerge("s",test=True) or gamegrid != newMerge("s",test=None)):
                        gamegrid, score = newMerge("s", score)
                        spawnnewtile()
                        Update()
                    if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and (newMerge("d",test=True) or gamegrid != newMerge("d",test=None)):
                        gamegrid, score = newMerge("d", score)
                        spawnnewtile()
                        Update()
                    check = 0
        rendergrid(window)
        renderscore(window)
        pygame.display.update()
rungame()

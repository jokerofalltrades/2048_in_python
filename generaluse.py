import math
import random
import time
from os import system

gamegrid = []
tempgrid = []
num_of_rows = 4
num_of_columns = 4
highesttile = 1
score = 0

def clear():
  _ = system('clear')

def getch():
  chr = str(input(""))
  return chr
  
def update():
  global highesttile
  highesttile = int(highesttile)
  for i in range(len(gamegrid)):
    gamegrid[i] = tempgrid[i]
  clear()
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
      if tempgrid[i] == " ":
        tile_not_chosen = False
    if highesttile > 2:
      temphighesttile = 2
    tile_to_spawn = 2**(random.randint(1,temphighesttile))
    tempgrid[i] = tile_to_spawn

def merge(direction,test = False):
  global highesttile
  global score
  merged = False
  if direction == "w":
    for _i in range(num_of_columns):
      for _e in range(num_of_rows-1):
        if tempgrid[_e*num_of_columns+_i] == tempgrid[(_e+1)*num_of_columns+_i] and tempgrid[_e*num_of_columns+_i] != " ":
          if not test: 
            tempgrid[_e*num_of_columns+_i] = tempgrid[_e*num_of_columns+_i] + tempgrid[(_e+1)*num_of_columns+_i]
            tempgrid[(_e+1)*num_of_columns+_i] = " "
            score += tempgrid[_e*num_of_columns+_i]
            if math.log2(tempgrid[_e*num_of_columns+_i]) > highesttile:
              highesttile = math.log2(tempgrid[_e*num_of_columns+_i])
          merged = True
  if direction == "s":
    for _i in range(num_of_columns):
      for _e in range(num_of_rows):
        if tempgrid[_e*num_of_columns+_i] == tempgrid[(_e-1)*num_of_columns+_i] and tempgrid[_e*num_of_columns+_i] != " " and _e != 0:
          if not test:
            tempgrid[_e*num_of_columns+_i] = tempgrid[_e*num_of_columns+_i] + tempgrid[(_e-1)*num_of_columns+_i]
            tempgrid[(_e-1)*num_of_columns+_i] = " "
            score += tempgrid[_e*num_of_columns+_i]
            if math.log2(tempgrid[_e*num_of_columns+_i]) > highesttile:
              highesttile = math.log2(tempgrid[_e*num_of_columns+_i])
          merged = True
  if direction == "a":
    for _i in range(num_of_rows):
      for _e in range(num_of_columns):
        if _e*num_of_rows+_i != 15:
          if tempgrid[_e*num_of_rows+_i] == tempgrid[_e*num_of_rows+_i+1] and tempgrid[_e*num_of_rows+_i] != " " and ((_e*num_of_rows+_i)%4)+1 == (_e*num_of_rows+_i+1)%4:
            if not test:
              tempgrid[_e*num_of_rows+_i] = tempgrid[_e*num_of_rows+_i] + tempgrid[_e*num_of_rows+_i+1]
              tempgrid[_e*num_of_rows+_i+1] = " "
              score += tempgrid[_e*num_of_rows+_i]
              if math.log2(tempgrid[_e*num_of_rows+_i]) > highesttile:
                highesttile = math.log2(tempgrid[_e*num_of_rows+_i])
            merged = True
  if direction == "d":
    for _i in range(num_of_rows):
      for _e in range(num_of_columns):
        if tempgrid[_e*num_of_rows+_i] == tempgrid[_e*num_of_rows+_i-1] and tempgrid[_e*num_of_rows+_i] != " " and ((_e*num_of_rows+_i-1)%4)+1 == (_e*num_of_rows+_i)%4:
          if not test:
            tempgrid[_e*num_of_rows+_i] = tempgrid[_e*num_of_rows+_i] + tempgrid[_e*num_of_rows+_i-1]
            tempgrid[_e*num_of_rows+_i-1] = " "
            score += tempgrid[_e*num_of_rows+_i]
            if math.log2(tempgrid[_e*num_of_rows+_i]) > highesttile:
              highesttile = math.log2(tempgrid[_e*num_of_rows+_i])
          merged = True
  return merged

def move(direction,test = False):
  moved = False
  if direction == "w":
    for _v in range(num_of_columns):
      for _i in range(num_of_columns):
        for _e in range(num_of_rows):
          if tempgrid[(_e-1)*num_of_columns+_i] == " " and _e != 0:
            if not test:
              tempgrid[(_e-1)*num_of_columns+_i] = tempgrid[_e*num_of_columns+_i]
              tempgrid[_e*num_of_columns+_i] = " "
            moved = True
  if direction == "s":
    for _v in range(num_of_columns):
      for _i in range(num_of_columns):
        for _e in range(num_of_rows-1):
          if tempgrid[(_e+1)*num_of_columns+_i] == " ":
            if not test:
              tempgrid[(_e+1)*num_of_columns+_i] = tempgrid[_e*num_of_columns+_i]
              tempgrid[_e*num_of_columns+_i] = " "
            moved = True
  if direction == "a":
    for _v in range(num_of_rows):
      for _i in range(num_of_rows):
        for _e in range(num_of_columns):
          if tempgrid[_e*num_of_rows+_i] == " " and ((_e*num_of_rows+_i)%4)+1 == (_e*num_of_rows+_i+1)%4:
            if not test:
              tempgrid[_e*num_of_rows+_i] = tempgrid[_e*num_of_rows+_i+1]
              tempgrid[_e*num_of_rows+_i+1] = " "
            moved = True
  if direction == "d":
    for _v in range(num_of_rows):
      for _i in range(num_of_rows):
        for _e in range(num_of_columns):
          if tempgrid[_e*num_of_rows+_i] == " " and ((_e*num_of_rows+_i-1)%4)+1 == (_e*num_of_rows+_i)%4:
            if not test:
              tempgrid[_e*num_of_rows+_i] = tempgrid[_e*num_of_rows+_i-1]
              tempgrid[_e*num_of_rows+_i-1] = " "
            moved = True
  return moved
  
def play():
  check = 0
  messageactive = 0
  global score
  global highesttile
  fillgrid()
  for _i in range(2):
    spawnnewtile()
  update()
  while 1 > 0:
    allfull = True
    for i in range(num_of_rows*num_of_columns):
      if gamegrid[i] == " ":
        allfull = False
    if not allfull or check == 1:
      time.sleep(0.1)
      input = getch()
      if input.lower() == "w" and (merge(input.lower(),True) or move(input.lower(),True)):
        move(input.lower())
        merge(input.lower())
        spawnnewtile()
        update()
      if input.lower() == "s" and (merge(input.lower(),True) or move(input.lower(),True)):
        move(input.lower())
        merge(input.lower())
        spawnnewtile()
        update()
      if input.lower() == "a" and (merge(input.lower(),True) or move(input.lower(),True)):
        move(input.lower())
        merge(input.lower())
        spawnnewtile()
        update()
      if input.lower() == "d" and (merge(input.lower(),True) or move(input.lower(),True)):
        move(input.lower())
        merge(input.lower())
        spawnnewtile()
        update()
      check = 0
      if highesttile >= 11 and messageactive == 0:
        inputchosen = 0
        messageactive = 1
        clear()
        while inputchosen != 1:
          print("Well done! You beat the game by reaching 2048!")
          print("Press C to continue or E to exit.")
          input2 = getch()
          if input2.lower() == "c":
            inputchosen = 1
          elif input2.lower() == "e":
            exit()
          else:
            clear()
        update()
    else:
      if not (merge("w",True) or merge("a",True) or merge("s",True) or merge("d",True)):
        update()
        inputchosen = 0
        while inputchosen != 1:
          print("Game Over! Press Q to try again or E to exit.")
          input1 = getch()
          if input1.lower() == "q":
            tempgrid.clear()
            gamegrid.clear()
            score = 0
            highesttile = 1
            play()
          elif input1.lower() == "e":
            exit()
          else:
            clear()
      else: 
        check = 1

play()

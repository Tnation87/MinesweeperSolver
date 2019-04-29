import pyautogui
import time
import sys
import itertools
import copy
from PIL import Image
#---------------------------------------------------------------------------------------
#globals
TILES = {
          '_': Image.open('icons/notExplored.png'),
          0: Image.open('icons/empty.png'),
          1: Image.open('icons/1.png'),
          2: Image.open('icons/2.png'),
          3: Image.open('icons/3.png'),
          4: Image.open('icons/4.png'),
          5: Image.open('icons/5.png'),
          6: Image.open('icons/6.png'),
          7: Image.open('icons/7.png'),
          8: Image.open('icons/8.png'),
          'L': Image.open('icons/lost.png'),
          'M': Image.open('icons/mark.png')
        }

NOT_EXPLORED_TILES = {'_': Image.open('icons/notExplored.png')}
#---------------------------------------------------------------------------------------
def left(i, width, height):
    if i % width != 0:
        return i-1

def right(i, width, height):
    if (i+1) % width != 0:
        # not in last col
        return i+1

def above(i, width, height):
    if i-width >= 0:
        # not top row
        return i-width

def below(i, width, height):
    if i+width < width*height:
        # not bottom row
        return i+width

def top_left(i, width, height):
    top = above(i, width, height)
    if top is not None:
        return left(top, width, height)

def top_right(i, width, height):
    top = above(i, width, height)
    if top is not None:
        return right(top, width, height)

def bottom_left(i, width, height):
    bottom = below(i, width, height)
    if bottom is not None:
        return left(bottom, width, height)
def bottom_right(i, width, height):
    bottom = below(i, width, height)
    if bottom is not None:
        return right(bottom, width, height)
    
def get_neighbours(i, all_tiles):
    lengthOfboard = len(all_tiles)
    width = 1
    height = 1
    if(lengthOfboard == 81):
        width = 9
        height = 9
    elif(lengthOfboard == 256):
        width = 16
        height = 16
    elif(lengthOfboard == 480):
        width = 30
        height = 16
    functions = [top_left, above, top_right, right, bottom_right, below, bottom_left, left]
    neighbours = [f(i, width, height) for f in functions]
    return [n for n in neighbours if n is not None]
#----------------------------------------------------------------------------------------
def count_marked(i, all_tiles):
    count = 0
    neighbours = get_neighbours(i, all_tiles)
    for neighbour in neighbours:
        if list(all_tiles)[neighbour]['value'] == 'M':
            count = count + 1
    return count 
#----------------------------------------------------------------------------------------
def count_empty(i, all_tiles):
    count = 0
    neighbours = get_neighbours(i, all_tiles)
    for neighbour in neighbours:
        if list(all_tiles)[neighbour]['value'] == '_':
            count = count + 1
    return count   
#----------------------------------------------------------------------------------------
def calculate_certain(all_tiles, i):
    neighbours = get_neighbours(i, all_tiles)
    for neighbour in neighbours:
        if list(all_tiles)[neighbour]['value'] != 0 and list(all_tiles)[neighbour]['value'] != 'M' and list(all_tiles)[neighbour]['value'] != '_':
            if  count_marked(neighbour, all_tiles) == list(all_tiles)[neighbour]['value']:
                return 0
            elif count_empty(neighbour, all_tiles) == list(all_tiles)[neighbour]['value']-count_marked(neighbour, all_tiles):
                return 1
#----------------------------------------------------------------------------------------
def calculate_probability(all_tiles, i):
    prob = 100
    neighbours = get_neighbours(i, all_tiles)
    for neighbour in neighbours:
        if list(all_tiles)[neighbour]['value'] != 0 and list(all_tiles)[neighbour]['value'] != 'M' and list(all_tiles)[neighbour]['value'] != '_':
            temp = (list(all_tiles)[neighbour]['value'] - count_marked(neighbour, all_tiles))/(count_empty(neighbour, all_tiles))
            if temp < prob:
                prob = temp

    return prob
#----------------------------------------------------------------------------------------
def get_configurations(copy_all_tiles, remaining_mines):
    c = 0
    for tile in copy_all_tiles:
        if tile['value'] == '_':
            c = c + 1
    perms = list(itertools.product([0,1],repeat = c ))
    
    for perm in list(perms):
        if perm.count(1) != remaining_mines:
            perms.remove(perm)
   
    configs = []
    temp = []
    for perm in list(perms):
        i = 0
        for tile in copy_all_tiles:
            if tile['value'] == '_':
                if perm[i] == 1:
                    temp.append({'value': 'M', 'position': copy.deepcopy(tile['position'])})
                else:
                    temp.append(copy.deepcopy(tile))
                i = i+1
            else:
                temp.append(copy.deepcopy(tile))
            

        if valid(temp):
            configs.append(temp)
        temp = []

    return configs
#----------------------------------------------------------------------------------------
def valid(temp):
    for tile in temp:
        if tile['value'] != 'M' and tile['value'] != '_' and tile['value'] != 0:
            if count_marked(list(temp).index(tile) ,temp) > tile['value']:
                return False
    return True
#----------------------------------------------------------------------------------------
def get_common(configurations):
    common = []
    for tile in configurations[0]:
        if tile['value'] == '_':
            common.append(copy.deepcopy(tile))
            
    for config in list(configurations):
        for tile in list(common):
            if tile not in config:
                list(common).remove(tile)

    return common
#----------------------------------------------------------------------------------------
def play_game(all_tiles, not_explored_tiles):
    for tile in all_tiles:
        if(tile['value'] == 'L'):
            print("Game is lost due to miss calculation")
            print("% RESTRATING %")
            time.sleep(1)
            pyautogui.press('f2')
            start()
            return
        
    if len(list(not_explored_tiles)) == 0:
        print("congrats, you've won.")
        sys.exit()

    for tile in not_explored_tiles:
        probability = calculate_certain(all_tiles, list(all_tiles).index(tile))
        if probability == 0:
            x, y = tile['position'][0]+5, tile['position'][1]+5
            pyautogui.moveTo(x,y)
            time.sleep(.1)
            pyautogui.click()
            all_tiles, not_explored_tiles = update_tiles()
            play_game(all_tiles, not_explored_tiles)
        elif probability == 1:
            x, y = tile['position'][0]+5, tile['position'][1]+5
            pyautogui.moveTo(x,y)
            time.sleep(.1)
            pyautogui.click(button='right')
            all_tiles, not_explored_tiles = update_tiles()
            play_game(all_tiles, not_explored_tiles)

    print("stuck sitiuation.")
    print("calculating best possible move")
    c = 0
    for tile in all_tiles:
        if tile['value'] == '_':
            c = c + 1
    if c < 20:
        remaining_mines = remainingMines(all_tiles)
        copy_all_tiles = copy.deepcopy(all_tiles)
        configurations = get_configurations(copy_all_tiles, remaining_mines)
        common_tiles = get_common(configurations)
        if (len(list(common_tiles))) != 0:
            for tile in common_tiles:
                x, y = tile['position'][0]+5, tile['position'][1]+5
                pyautogui.moveTo(x,y)
                time.sleep(.1)
                pyautogui.click()
                all_tiles, not_explored_tiles = update_tiles()
                play_game(all_tiles, not_explored_tiles)
        else:
            print("no certain moves to do, going to try the tile with the least probability")
            probabilities = []
            for tile in all_tiles:
                if tile['value'] == '_':
                    probabilities.append({'prob': calculate_probability(all_tiles, list(all_tiles).index(tile)), 'position': copy.deepcopy(tile['position'])})
            probabilities = sorted(probabilities, key=lambda x: x['prob'])
            x,y = probabilities[0]['position'][0]+5 , probabilities[0]['position'][1]+5
            pyautogui.moveTo(x,y)
            time.sleep(.1)
            pyautogui.click()
            all_tiles, not_explored_tiles = update_tiles()
            play_game(all_tiles, not_explored_tiles)
    else:
        print("Number of unknown tiles is : " )
        print(c)
        print("Number of unclicked tiles is too much to calculate, saving memory and playing a tile based on probability alone")
        probabilities = []
        for tile in all_tiles:
            if tile['value'] == '_':
                probabilities.append({'prob': calculate_probability(all_tiles, list(all_tiles).index(tile)), 'position': copy.deepcopy(tile['position'])})
        probabilities = sorted(probabilities, key=lambda x: x['prob'])
        x,y = probabilities[0]['position'][0]+5 , probabilities[0]['position'][1]+5
        pyautogui.moveTo(x,y)
        time.sleep(.1)
        pyautogui.click()
        all_tiles, not_explored_tiles = update_tiles()
        play_game(all_tiles, not_explored_tiles)
#---------------------------------------------------------------------------------------
def remainingMines(all_tiles):
    mines = 0
    c = 0
    for tile in all_tiles:
        if tile['value'] == 'M':
            c = c+1
    lengthOfboard = len(all_tiles)
    if(lengthOfboard == 81):
        mines = 10 - c
    elif(lengthOfboard == 256):
        mines = 40 - c
    elif(lengthOfboard == 480):
        mines = 99 - c
    return mines
#---------------------------------------------------------------------------------------
def update_tiles():
    all_tiles = []
    for tile in TILES:
        positions = pyautogui.locateAllOnScreen(TILES[tile], region=(200,50, 1359 , 500))
        for p in positions:
            all_tiles.append({'value': tile, 'position': p})
    all_tiles = sorted(all_tiles, key=lambda x: (x['position'][1], x['position'][0]))

    not_explored_tiles = []
    for tile in NOT_EXPLORED_TILES:
        positions = pyautogui.locateAllOnScreen(NOT_EXPLORED_TILES[tile])
        for p in positions:
            not_explored_tiles.append({'value': tile, 'position': p})
    not_explored_tiles = sorted(not_explored_tiles, key=lambda x: (x['position'][1], x['position'][0]))
    return all_tiles, not_explored_tiles
#---------------------------------------------------------------------------------------
def print_board(all_tiles):
    width = len(set([x['position'][0] for x in all_tiles]))
    for i, tile in enumerate(all_tiles):
        print(tile['value'], end=' ')
        if (i+1)%width == 0:
            print()
#---------------------------------------------------------------------------------------           
def start():
    all_tiles, not_explored_tiles = update_tiles()
    x,y = list(all_tiles)[40]['position'][0]+5, list(all_tiles)[40]['position'][1]+5
    pyautogui.moveTo(x,y)
    time.sleep(.1)
    pyautogui.click()
    pyautogui.click()
    all_tiles, not_explored_tiles = update_tiles()
    play_game(all_tiles, not_explored_tiles)

start()
#all_tiles, not_explored_tiles = update_tiles()
#print_board(all_tiles)







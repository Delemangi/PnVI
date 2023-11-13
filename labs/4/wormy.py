# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random
import sys
import time

import pygame
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)

# бојата на другиот црв
INDIGO = (75, 50, 130)
DARKINDIGO = (75, 0, 130)

# colors for the new food source
PINK = (255, 0, 255)
YELLOW = (255, 255, 0)

BGCOLOR = BLACK

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

HEAD = 0  # syntactic sugar: index of the worm's head


# генерирање координати за новите елементи
def generate_three_apples():
    el1 = getRandomLocation()
    el2 = getRandomLocation(el1, el1)
    el3 = getRandomLocation(el1, el2)
    return el1, el2, el3


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, START_TIME

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font("freesansbold.ttf", 18)
    pygame.display.set_caption("Wormy")

    showStartScreen()
    while True:
        # броење на време
        START_TIME = time.time()
        s1, s2, s3 = runGame()
        showGameOverScreen(s1, s2, s3)


# проверка за дали се изминати 20 секунди
def is_spawned():
    return time.time() - START_TIME >= 20


# генерирање на следната насока на другиот црв
def generateNextDirection(secondWormCoords, currentDirection):
    options = [UP, DOWN, LEFT, RIGHT]
    if currentDirection == UP:
        options = [LEFT, RIGHT]
    elif currentDirection == DOWN:
        options = [LEFT, RIGHT]
    elif currentDirection == LEFT:
        options = [UP, DOWN]
    elif currentDirection == RIGHT:
        options = [UP, DOWN]
    direction = random.choice(options + [currentDirection] * 3)
    head = secondWormCoords[HEAD]

    if direction == UP and head["y"] == 0:
        return DOWN
    elif direction == DOWN and head["y"] == CELLHEIGHT - 1:
        return UP
    elif direction == LEFT and head["x"] == 0:
        return RIGHT
    elif direction == RIGHT and head["x"] == CELLWIDTH - 1:
        return LEFT
    if direction == UP and head["y"] == 1:
        return DOWN
    elif direction == DOWN and head["y"] == CELLHEIGHT - 2:
        return UP
    elif direction == LEFT and head["x"] == 1:
        return RIGHT
    elif direction == RIGHT and head["x"] == CELLWIDTH - 2:
        return LEFT

    return direction


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [
        {"x": startx, "y": starty},
        {"x": startx - 1, "y": starty},
        {"x": startx - 2, "y": starty},
    ]
    direction = RIGHT

    # другиот црв
    worm_coords_enemy = [
        {"x": startx, "y": starty},
        {"x": startx - 1, "y": starty},
        {"x": startx - 2, "y": starty},
    ]
    direction_enemy = RIGHT
    # Start the apple in a random place.
    apple = getRandomLocation()

    # бројачи за сите изедени елементи
    eaten_pink_num = 0
    eaten_yellow_num = 0
    eaten_red_num = 0

    # координати на сите елементи
    apple_pink_1, apple_pink_2, apple_pink_3 = generate_three_apples()
    eaten_pink = [False, False, False]
    apple_yellow_1, apple_yellow_2, apple_yellow_3 = generate_three_apples()
    eaten_yellow = [False, False, False]

    time_pink = START_TIME
    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # враќање на сите изедени елементи доколку црвот излезе надвор од играта
        if (
            wormCoords[HEAD]["x"] == -1
            or wormCoords[HEAD]["x"] == CELLWIDTH
            or wormCoords[HEAD]["y"] == -1
            or wormCoords[HEAD]["y"] == CELLHEIGHT
        ):
            return eaten_pink_num, eaten_yellow_num, eaten_red_num

        for wormBody in wormCoords[1:]:
            if (
                wormBody["x"] == wormCoords[HEAD]["x"]
                and wormBody["y"] == wormCoords[HEAD]["y"]
            ):
                return eaten_pink_num, eaten_yellow_num, eaten_red_num  # game over

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {"x": wormCoords[HEAD]["x"], "y": wormCoords[HEAD]["y"] - 1}
        elif direction == DOWN:
            newHead = {"x": wormCoords[HEAD]["x"], "y": wormCoords[HEAD]["y"] + 1}
        elif direction == LEFT:
            newHead = {"x": wormCoords[HEAD]["x"] - 1, "y": wormCoords[HEAD]["y"]}
        elif direction == RIGHT:
            newHead = {"x": wormCoords[HEAD]["x"] + 1, "y": wormCoords[HEAD]["y"]}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)

        # проверка за дали постои другиот црв
        has_eaten = False
        if is_spawned():
            # проверка за следната насока
            direction_enemy = generateNextDirection(worm_coords_enemy, direction_enemy)
            if direction_enemy == UP:
                newHead = {
                    "x": worm_coords_enemy[HEAD]["x"],
                    "y": worm_coords_enemy[HEAD]["y"] - 1,
                }
            elif direction_enemy == DOWN:
                newHead = {
                    "x": worm_coords_enemy[HEAD]["x"],
                    "y": worm_coords_enemy[HEAD]["y"] + 1,
                }
            elif direction_enemy == LEFT:
                newHead = {
                    "x": worm_coords_enemy[HEAD]["x"] - 1,
                    "y": worm_coords_enemy[HEAD]["y"],
                }
            elif direction_enemy == RIGHT:
                newHead = {
                    "x": worm_coords_enemy[HEAD]["x"] + 1,
                    "y": worm_coords_enemy[HEAD]["y"],
                }
            worm_coords_enemy.insert(0, newHead)

            # дали е изеден од другиот црв
            has_eaten = False
            for body in wormCoords:
                if (
                    body["x"] == worm_coords_enemy[HEAD]["x"]
                    and body["y"] == worm_coords_enemy[HEAD]["y"]
                ):
                    has_eaten = True
                    break
            if not has_eaten:
                del worm_coords_enemy[-1]

            # проверка за другиот црв дали е изеден од оригиналниот црв
            has_eaten = False
            for body in worm_coords_enemy:
                if (
                    body["x"] == wormCoords[HEAD]["x"]
                    and body["y"] == wormCoords[HEAD]["y"]
                ):
                    has_eaten = True
                    break

            drawWorm(worm_coords_enemy, INDIGO, DARKINDIGO)

            # check if worm has eaten an apply
        if wormCoords[HEAD]["x"] == apple["x"] and wormCoords[HEAD]["y"] == apple["y"]:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
            eaten_red_num += 1
        # дали е изеден од другиот црв
        elif has_eaten:
            ...
        else:
            del wormCoords[-1]  # remove worm's tail segment

        # генерирање на жолти елементи
        if time.time() - START_TIME >= 7 and time.time() - START_TIME <= 14:
            if not eaten_yellow[0]:
                drawApple(apple_yellow_1, YELLOW)
            if not eaten_yellow[1]:
                drawApple(apple_yellow_2, YELLOW)
            if not eaten_yellow[2]:
                drawApple(apple_yellow_3, YELLOW)

            if (
                wormCoords[HEAD]["x"] == apple_yellow_1["x"]
                and wormCoords[HEAD]["y"] == apple_yellow_1["y"]
                and not eaten_yellow[0]
            ):
                eaten_yellow[0] = True
                eaten_yellow_num += 1
            if (
                wormCoords[HEAD]["x"] == apple_yellow_2["x"]
                and wormCoords[HEAD]["y"] == apple_yellow_2["y"]
                and not eaten_yellow[1]
            ):
                eaten_yellow[1] = True
                eaten_yellow_num += 1
            if (
                wormCoords[HEAD]["x"] == apple_yellow_3["x"]
                and wormCoords[HEAD]["y"] == apple_yellow_3["y"]
                and not eaten_yellow[2]
            ):
                eaten_yellow[2] = True
                eaten_yellow_num += 1

        # генерирање на розови елементи
        if time.time() - time_pink >= 5:
            time_pink = time.time()
            eaten_pink = [False, False, False]
            apple_pink_1, apple_pink_2, apple_pink_3 = generate_three_apples()
        if time.time() - START_TIME >= 5:
            if not eaten_pink[0]:
                drawApple(apple_pink_1, PINK)
            if not eaten_pink[1]:
                drawApple(apple_pink_2, PINK)
            if not eaten_pink[2]:
                drawApple(apple_pink_3, PINK)

            if (
                wormCoords[HEAD]["x"] == apple_pink_1["x"]
                and wormCoords[HEAD]["y"] == apple_pink_1["y"]
                and not eaten_pink[0]
            ):
                eaten_pink[0] = True
                eaten_pink_num += 1
            if (
                wormCoords[HEAD]["x"] == apple_pink_2["x"]
                and wormCoords[HEAD]["y"] == apple_pink_2["y"]
                and not eaten_pink[1]
            ):
                eaten_pink[1] = True
                eaten_pink_num += 1
            if (
                wormCoords[HEAD]["x"] == apple_pink_3["x"]
                and wormCoords[HEAD]["y"] == apple_pink_3["y"]
                and not eaten_pink[2]
            ):
                eaten_pink[2] = True
                eaten_pink_num += 1

        drawApple(apple)
        drawScore(calc_score(eaten_pink_num, eaten_yellow_num, eaten_red_num))
        pygame.display.update()
        FPSCLOCK.tick(FPS)


# калкулација на поените
def calc_score(eaten_pink, eaten_yellow, eaten_red):
    score = 0
    score += eaten_pink * 3
    score += eaten_yellow * 3
    score += eaten_red
    return score


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render("Press a key to play.", True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font("freesansbold.ttf", 100)
    titleSurf1 = titleFont.render("Wormy!", True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render("Wormy!", True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


# измени за да не може на иста позиција да се појават повеќе елементи
def getRandomLocation(apple1=None, apple2=None):
    new_location = {
        "x": random.randint(0, CELLWIDTH - 1),
        "y": random.randint(0, CELLHEIGHT - 1),
    }
    if apple1 is not None and apple2 is not None:
        while (
            new_location["x"] == apple1["x"] and new_location["y"] == apple1["y"]
        ) or (new_location["x"] == apple2["x"] and new_location["y"] == apple2["y"]):
            new_location = {
                "x": random.randint(0, CELLWIDTH - 1),
                "y": random.randint(0, CELLHEIGHT - 1),
            }
    return new_location


# креирање на елемент за текст
def create_blit(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    if bgcolor is None:
        textSurf = BASICFONT.render(text, True, color)
    else:
        textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return textSurf, textRect


def showGameOverScreen(eaten_pink, eaten_yellow, eaten_red):
    gameOverFont = pygame.font.Font("freesansbold.ttf", 150)
    gameSurf = gameOverFont.render("Game", True, WHITE)
    overSurf = gameOverFont.render("Over", True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    # креирање на новите елементи
    newGame_blit = nt, New_RECT = create_blit(
        "Start from the beginning",
        WHITE,
        DARKGREEN,
        WINDOWWIDTH - 250,
        WINDOWHEIGHT - 90,
    )
    quitGame_blit = qt, Quit_RECT = create_blit(
        "Quit", WHITE, RED, WINDOWWIDTH - 250, WINDOWHEIGHT - 60
    )
    score1_text = f"Score:({eaten_pink}*3 + {eaten_yellow}*3 + {eaten_red}) = {calc_score(eaten_pink, eaten_yellow, eaten_red)}"
    eaten_yellow_text = f"Yellow Apples: {eaten_yellow}"
    eaten_pink_text = f"Pink Apples: {eaten_pink}"
    eaten_red_text = f"Red Apples: {eaten_red}"
    score1_blit = st, srect = create_blit(
        score1_text,
        WHITE,
        None,
        WINDOWWIDTH / 2 - 200,
        gameRect.height + overRect.height + 25,
    )
    eaten_yellow_blit = sy, yrect = create_blit(
        eaten_yellow_text,
        WHITE,
        None,
        WINDOWWIDTH / 2 - 200,
        gameRect.height + overRect.height + srect.height + 30,
    )
    eaten_pink_blit = sp, prect = create_blit(
        eaten_pink_text,
        WHITE,
        None,
        WINDOWWIDTH / 2 - 200,
        gameRect.height + overRect.height + srect.height + yrect.height + 35,
    )
    eaten_red_blit = sr, rrect = create_blit(
        eaten_red_text,
        WHITE,
        None,
        WINDOWWIDTH / 2 - 200,
        gameRect.height
        + overRect.height
        + srect.height
        + yrect.height
        + prect.height
        + 40,
    )

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)

    bgrect = pygame.Rect(
        WINDOWWIDTH / 2 - 230,
        gameRect.height + overRect.height + 15,
        255,
        srect.height + yrect.height + prect.height + rrect.height + 40,
    )
    pygame.draw.rect(DISPLAYSURF, DARKGRAY, bgrect)
    DISPLAYSURF.blit(*newGame_blit)
    DISPLAYSURF.blit(*quitGame_blit)
    DISPLAYSURF.blit(*score1_blit)
    DISPLAYSURF.blit(*eaten_yellow_blit)
    DISPLAYSURF.blit(*eaten_pink_blit)
    DISPLAYSURF.blit(*eaten_red_blit)

    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # check if the user clicked on an option button
                if New_RECT.collidepoint(event.pos):
                    return
                elif Quit_RECT.collidepoint(event.pos):
                    terminate()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawScore(score):
    scoreSurf = BASICFONT.render("Score: %s" % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords, c1=DARKGREEN, c2=GREEN):
    for coord in wormCoords:
        x = coord["x"] * CELLSIZE
        y = coord["y"] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, c1, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, c2, wormInnerSegmentRect)


def drawApple(coord, color=RED):
    x = coord["x"] * CELLSIZE
    y = coord["y"] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, color, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == "__main__":
    main()

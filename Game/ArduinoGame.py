import sys
import numpy
import pygame.mixer
import pyfirmata
from Models import *
from Videos import *
from Init import *

#below part put in init
from pynput.keyboard import Key, Controller

keyboard = Controller()

board = pyfirmata.Arduino('COM8')
it = pyfirmata.util.Iterator(board)

it.start()

digital_input_down = board.get_pin('d:10:i')
digital_input_up = board.get_pin('d:11:i')
digital_input_space = board.get_pin('d:9:i')
#till above in init


pygame.init()


#Stage 0
def Background1(player):
    global font_health
    font_health = pygame.font.Font('freesansbold.ttf', 20)
    powerLvl = font_health.render("Power Level: " + str(player.POWER_LVL), 1, BLACK)
    SCREEN.blit(powerLvl, (10, 10))
    blockSize = 100
    for x in range(100, SCREEN_WIDTH - 100, blockSize):
        for y in range(100, SCREEN_HEIGHT - 100, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(SCREEN, BLACK, rect, 1)

def get_map(field, player):
    global totalPower
    totalPower = 0
    for i in range(5):
        for j in range(9):
            if not field.SPAWN_SITE[i][j] == -1:
                spawn = Spawn(field.SPAWN_SITE[i][j], j, i)
                spawn.populate(SCREEN)
                totalPower += spawn.power
                if player.rect.colliderect(spawn.rect):
                    if player.POWER_LVL > spawn.power:
                        player.POWER_LVL += spawn.power
                    elif player.POWER_LVL == spawn.power:
                        player.POWER_LVL += 2
                    elif player.POWER_LVL + 2 >= spawn.power:
                        player.POWER_LVL -= 1
                    else:
                        movie(13, Age19)
                        menu(8, 0)
                    field.SPAWN_SITE[i][j] = -1

def isDoable():
    if totalPower < 600:
        FirstStage()

def FirstStage():
    doableCheck = False
    player = Weakling()
    field = Map()
    enemy = Boss()
    while 1:
        SCREEN.fill(WHITE)
        Background1(player)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.rect.x > 105:
                        player.rect.x -= 100
                if event.key == pygame.K_UP:
                    if player.rect.x < 905:
                        player.rect.x += 100
                if event.key == pygame.K_DOWN:
                    if player.rect.y < 505:
                        player.rect.y += 100

        downSwitch = digital_input_down.read()
        upSwitch = digital_input_up.read()
        spaceSwitch = digital_input_space.read()
        if downSwitch is True:
            keyboard.press(Key.down)
        if upSwitch is True:
            keyboard.press(Key.up)
        if spaceSwitch is True:
            keyboard.press(Key.space)
        if downSwitch is False:
            keyboard.release(Key.down)
        if upSwitch is False:
            keyboard.release(Key.up)
        if spaceSwitch is False:
            keyboard.release(Key.space)

        get_map(field, player)
        if not doableCheck:
            isDoable()
            doableCheck = True

        if player.rect.colliderect(enemy.boss_rect):
            if player.POWER_LVL >= enemy.POWER_LVL:
                movie(12, Age19)
                menu(2,0)
            else:
                movie(11, Age19)
                menu(8,0)

        player.draw(SCREEN)
        enemy.draw(SCREEN)
        pygame.display.update()

#Stage 1
def Background2():
    global x_pos_bg, y_pos_bg
    image_width = BG.get_width()
    SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
    SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
    if x_pos_bg <= -image_width:
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        x_pos_bg = 0
    x_pos_bg -= game_speed

def score():
    global points, game_speed
    points += 1
    if points % 100 == 0:
        game_speed += 1

    text = font.render("Points: " + str(points), True, BLACK)
    textRect = text.get_rect()
    textRect.center = (1000, 40)
    SCREEN.blit(text, textRect)

def add_obstacles():
    global Age19, obstacles, points
    if Age19 and points < 30:  # to change 2500 30 test
        if len(obstacles) == 0:
            if random.randint(0, 2) == 0 or random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(OBS_AGE_19))
            elif random.randint(0, 2) == 2:
                obstacles.append(Drone(DRONE))
    elif not Age19 and points < 30:  # t change 2500
        if len(obstacles) == 0:
            if random.randint(0, 2) == 0 or random.randint(0, 2) == 1:
                obstacles.append(SmallCactus(OBS_AGE_18))
            elif random.randint(0, 2) == 2:
                obstacles.append(Drone(DRONE))
    elif points > 30:  # to change 2500
        if len(obstacles) == 0:
            obstacles.append(Shrine(SHRINE))

def SecondStage():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, font, Age19
    #clock = pygame.time.Clock()
    player = Man()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    obstacles = []
    font = pygame.font.Font('freesansbold.ttf', 20)
    FPS1 = 30

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill(WHITE)
        userInput = pygame.key.get_pressed()

        Background2()

        player.draw(SCREEN)
        player.update(userInput)
        add_obstacles()

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update(game_speed,obstacles)
            if player.man_rect.colliderect(obstacle.rect) and obstacle.identify() == 9:
                pygame.time.delay(1000)
                movie(obstacle.identify(), Age19)
                menu(7, 0)
            elif player.man_rect.colliderect(obstacle.rect):
                pygame.time.delay(1000)
                movie(obstacle.identify(), Age19)
                menu(1, points)

        score()

        clock.tick(FPS1)
        pygame.display.update()

#Stage 2
def Background3(player, enemy):
    global font_health
    SCREEN2.blit(BG2, (0, 0))
    if player.HP < 3:
        Sovereign_HP = font_health.render("Health: " + str(player.HP), 1, RED)
    else:
        Sovereign_HP = font_health.render("Health: " + str(player.HP), 1, WHITE)
    if enemy.HP < 6:
        Eye_HP = font_health.render("Health: " + str(enemy.HP), 1, RED)
    elif enemy.HP < 11:
        Eye_HP = font_health.render("Health: " + str(enemy.HP), 1, YELLOW)
    else:
        Eye_HP = font_health.render("Health: " + str(enemy.HP), 1, WHITE)
    SCREEN2.blit(Sovereign_HP, (10, 10))
    SCREEN2.blit(Eye_HP, (SCREEN_WIDTH - Eye_HP.get_width() - 10, 10))

def ThirdStage():
    global font_health, SCREEN2
    FPS2 = 60
    enemy_attacks = []
    player = Sovereign()
    enemy = Eye()
    SCREEN2 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + 100))

    while 1:
        Background3(player, enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()


        userInput = pygame.key.get_pressed()
        player.draw(SCREEN2)
        enemy.draw(SCREEN2)
        player.movement(userInput)

        if player.bullet_rect.colliderect(enemy.weak_spot_rect):
            enemy.HP -= 1
            player.bullet_rect.x += SCREEN_WIDTH - 3
        if player.bullet_rect.colliderect(enemy.eye_rect):
            player.bullet_rect.x += SCREEN_WIDTH - 3

        num = random.randint(0, 2)
        if not enemy.START_ATTACK:
            enemy.start_attack()
        elif ((enemy.HP == 10 and enemy.RAGE_TIME == 0) or (enemy.HP == 1 and enemy.RAGE_TIME == 1))  and enemy.START_ATTACK:    #to cahneg 24 to 10
            if len(enemy_attacks) == 0:
                enemy_attacks.append(Attack2(ATTACK2))
                enemy.RAGE = True
                enemy.RAGE_TIME += 1
        elif enemy.START_ATTACK:
            if len(enemy_attacks) == 0:
                enemy_attacks.append(Attack1(ATTACK1, num))

        if enemy.RAGE == True:
            for attack in enemy_attacks:
                attack.draw(SCREEN2)
                attack.update(enemy_attacks, enemy)
                if player.sovereign_rect.colliderect(attack.attack_rect):
                    player.HP -= 1
        elif num >=0 or num <= 2:
            for attack in enemy_attacks:
                attack.draw(SCREEN2)
                attack.update(enemy_attacks)
                if player.sovereign_rect.colliderect(attack.part1) or player.sovereign_rect.colliderect(attack.part2) or player.sovereign_rect.colliderect(attack.part3):
                    player.HP -= 1
                    enemy_attacks.pop()

        if player.HP == 0:
            pygame.time.delay(1000)
            menu(3, enemy.HP) # die to eye
        if enemy.HP == 0:
            movie(15, Age19)
            menu(4, player.HP)
        clock.tick(FPS2)
        pygame.display.update()

#Stage 3
def Background4(player, enemy):
    global font_health
    if enemy.HP < 3:
        SCREEN3.blit(BG3SWITCH, (0, 0))
    else:
        SCREEN3.blit(BG3, (0, 0))
    if player.HP < 3:
        Champion_HP = font_health.render("Health: " + str(player.HP), 1, RED)
    else:
        Champion_HP = font_health.render("Health: " + str(player.HP), 1, BLACK)
    if enemy.HP < 3:
        Demon_HP = font_health.render("Health: " + str(enemy.HP), 1, RED)
    elif enemy.HP < 6:
        Demon_HP = font_health.render("Health: " + str(enemy.HP), 1, YELLOW)
    else:
        Demon_HP = font_health.render("Health: " + str(enemy.HP), 1, BLACK)
    SCREEN3.blit(Champion_HP, (10, 10))
    SCREEN3.blit(Demon_HP, (SCREEN_WIDTH - Demon_HP.get_width() - 10, 10))

def FourthStage(hp):
    global SCREEN3, font_health, FPS2, player_count
    font_health = pygame.font.Font('freesansbold.ttf', 20)           # remove line after integration
    SCREEN3 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    #SCREEN3 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    player = Champion()
    enemy = Demon()
    player.HP = hp
    FPS2 = 60
    enemy_count = 0
    player_count = 0
    elapsed_time1 = 0
    imageShow = False
    currentFrameCount = 0
    frameCount = 0
    vidShow1 = True
    vidShow2 = True

    def pause():
        pause = True
        elapsed_time = 0
        while pause:
            if elapsed_time > 500:
                pause = False
            elapsed_time += clock.tick(101)

    def get_task1():
        global player_count
        while player_count<enemy.TASK1_MAX_CNT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.TASK1.append(0)
                    if event.key == pygame.K_UP:
                        player.TASK1.append(2)
                    if event.key == pygame.K_DOWN:
                        player.TASK1.append(1)
                    player_count += 1

    def get_task2():
        input = True
        while input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:    #heads
                        player.TASK2 = 1
                    if event.key == pygame.K_DOWN:
                        player.TASK2 = 0
                    input = False
    while 1:
        Background4(player, enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and player.TASK_NUM == 0:
                player.TASK_NUM = 1

        player.draw(SCREEN3)
        enemy.draw(SCREEN3)

        if enemy.HP < 3 and not enemy.HARD:
            enemy.HARD = True
            enemy.TASK1_MAX_CNT = 7

        if len(enemy.TASK1) == 0:
            enemy.TASK1 = numpy.random.randint(0,3,enemy.TASK1_MAX_CNT)
        if enemy.TASK2 == -1:
            enemy.TASK2 = random.randint(0,1)

        if elapsed_time1 > 500:
            imageShow = True
            elapsed_time1 = 0

        if player.TASK_NUM == 1 and enemy_count < enemy.TASK1_MAX_CNT:
            if imageShow:
                enemy.task1(enemy.TASK1[enemy_count])
                currentFrameCount = frameCount
                enemy_count += 1
                imageShow = False
        if enemy_count == enemy.TASK1_MAX_CNT + 1 and currentFrameCount == frameCount - 1:
            print(enemy.TASK1)
            get_task1()
            player.TASK_NUM += 1
        if player.TASK_NUM == 2:
            print(enemy.TASK2)
            get_task2()
            player.TASK_NUM += 1
        if player.TASK_NUM == 3:
            if (numpy.array(player.TASK1) == numpy.array(enemy.TASK1)).all() and player.TASK2 == enemy.TASK2:
                enemy.HP -= 1
                vidShow1 = True
            elif not (numpy.array(player.TASK1) == numpy.array(enemy.TASK1)).all() and not player.TASK2 == enemy.TASK2:
                player.HP -= 1
                player.TASK1_FAIL += 1
                vidShow2 = True
            elif not (numpy.array(player.TASK1) == numpy.array(enemy.TASK1)).all():
                player.TASK1_FAIL += 1
                if player.TASK1_FAIL > 3 == 1:
                    player.HP -= 1
                    player.TASK1_FAIL = 0
            player.TASK_NUM = 0
            player_count = 0
            enemy_count = 0
            player.TASK1 = []
            enemy.TASK1 = []
            player.TASK2 = -1
            enemy.TASK2 = -1


        if (enemy.HP == 5 or enemy.HP == 2) and vidShow1:
            if enemy.HP == 5:
                movie(17, Age19)
            if enemy.HP == 2:
                movie(18, Age19)
            vidShow1 = False
        if (player.HP == 3 or player.HP == 1) and vidShow2:
            if player.HP == 3:
                movie(20, Age19)
            if player.HP == 1:
                movie(21, Age19)
            vidShow2 = False

        if player.HP == 0:
            pygame.time.delay(1000)
            movie(22, Age19)
            menu(5, enemy.HP) #die to estarossa
        if enemy.HP == 0:
            movie(19, Age19)
            menu(6, player.HP) #kill estarossa

        elapsed_time1 += clock.tick(FPS2)
        frameCount += 1
        clock.tick(FPS2)
        pygame.display.update()
        if currentFrameCount == frameCount - 1 and player.TASK_NUM == 1 and enemy_count <= enemy.TASK1_MAX_CNT:
            pause()
            if enemy_count == enemy.TASK1_MAX_CNT:
                enemy_count += 1
                currentFrameCount = frameCount

# After winning
def GameOver():
    font_end = pygame.font.Font('freesansbold.ttf', 40)
    while 1:
        SCREEN3.blit(FINALBG, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()
        text = font_end.render("You Win", True, (BLACK))
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN3.blit(text, textRect)
        pygame.display.update()

#Start Menu
def menu(menu_count, val):
    while 1:
        SCREEN.fill(WHITE)
        font_menu = pygame.font.Font('freesansbold.ttf', 30)

        if menu_count == 0:
            text = font_menu.render("Press any Key to Start:", True, (BLACK))
        elif menu_count == 1:
            text = font_menu.render("Press any Key to Restart", True, BLACK)
            score = font_menu.render("Your Score: " + str(val), True, BLACK)
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        elif menu_count == 2:
            text = font_menu.render("Moving to Stage 3, Press any Key to Start:", True, BLACK)
        elif menu_count == 3:
            text = font_menu.render("You Died, Press any Key to Restart", True, BLACK)
            enemy_hp = font_menu.render("Enemy HP: " + str(val), True, BLACK)
            hpRect = enemy_hp.get_rect()
            hpRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN2.blit(enemy_hp, hpRect)
        elif menu_count == 4:
            text = font_menu.render("Moving to Stage 4, Press any Key to Start:", True, BLACK)
            player_hp = font_menu.render("HP Remaining: " + str(val), True, BLACK)
            hpRect = player_hp.get_rect()
            hpRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN2.blit(player_hp, hpRect)     # to cahne screen2
        elif menu_count == 5:
            text = font_menu.render("You Died, Press any Key to Restart", True, BLACK)
            enemy_hp = font_menu.render("Enemy HP: " + str(val), True, BLACK)
            hpRect = enemy_hp.get_rect()
            hpRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN2.blit(enemy_hp, hpRect)
        elif menu_count == 6:
            GameOver()
        elif menu_count == 7:
            text = font_menu.render("Moving to Stage 2, Press any Key to Start:", True, (BLACK))
        elif menu_count == 8:
            text = font_menu.render("Press any Key to Restart", True, BLACK)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        if menu_count == 2:
            SCREEN.blit(SOVEREIGN, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 180))
        elif menu_count == 4:
            SCREEN.blit(CHAMPION_SHOW, (SCREEN_WIDTH // 2 - 115, SCREEN_HEIGHT // 2 - 210))
        else:
            SCREEN.blit(RUNNING, (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 150))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (menu_count == 1 or menu_count == 3 or menu_count == 5 or menu_count == 0 or menu_count == 8):
                SecondStage()
            if event.type == pygame.KEYDOWN and menu_count == 7:
                FirstStage()
            if event.type == pygame.KEYDOWN and menu_count == 2:
                movie(14, Age19)
                ThirdStage()
            if event.type == pygame.KEYDOWN and menu_count == 4:
                movie(16, Age19)
                FourthStage(val)

def start_age():
    global Age19
    while 1:
        SCREEN.fill(WHITE)
        font = pygame.font.Font('freesansbold.ttf', 30)
        text = font.render("Up Key for 18+, Down Key for <18", True, BLACK)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        pygame.display.update()
        userInput = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif userInput[pygame.K_UP]:
                Age19 = True
                movie(10, Age19)
                menu(menu_count=0, val=0)
            elif userInput[pygame.K_DOWN]:
                Age19 = False
                movie(10, Age19)
                menu(menu_count=0, val=0)

start_age()
#FourthStage(5)
#ThirdStage()
#FirstStage()
#menu(4,5)
# use pygame.transform.fns to change img dimensions and rotate if necessary
#step_index
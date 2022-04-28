import pygame, sys
from pygame import *
from pygame.locals import *
from random import randint as rd
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 140)  #120 words per minute
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 
engine.setProperty('volume', 1) 

#add zenitsu attack from demon slayer entertainment district episode 10

#add objects that can be broken that provide health or stamina

pygame.init()

clock = pygame.time.Clock()
sw, sh = pygame.display.Info().current_w, pygame.display.Info().current_h

screen = pygame.display.set_mode((sw, sh), FULLSCREEN)
displaysurf = pygame.Surface((800, 600))

bgpic = pygame.image.load("bg.png")
wadpic = pygame.image.load("wad.png")

speaking = False
level = 0

class Particle:
    def __init__(self, posx, posy, dirx, diry):
        self.size = 3
        self.position = [posx, posy]
        self.color = (rd(120, 180), rd(120, 200), rd(140, 255))
        self.direction = [dirx, diry]
    def display(self, scrollx):
        pygame.draw.circle(displaysurf, self.color, (self.position[0] - scrollx, self.position[1]), self.size)
        self.size -= .2
        self.position[0] += self.direction[0]
        self.position[1] += self.direction[1]

def writetext(position, text="Sample Text", fontsize=30, txtcolor=(0, 0, 0), txtbgcolor=None, fontttf='freesansbold'):
    fontttf += '.ttf'
    font = pygame.font.Font(fontttf, fontsize)
    txt = font.render(text, True, txtcolor, txtbgcolor)
    displaysurf.blit(txt, position)

def speech(index):
    global speaking
    speaking = True
    with open("dialogues.txt", 'r') as text:
        text = text.read().split('\n')
    if index + 1 > len(text):
        pass
    else:
        j = 200
        fadebg = pygame.Surface((800, 600))
        fadebg.fill((0, 0, 0))
        while j > 0:
            pygame.display.flip(); clock.tick(30)
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    sys.exit()
            fadebg.set_alpha(j)
            displaysurf.fill((80, 10, 10))
            writetext((10, 480), text[index], txtcolor=(255, 100, 100))
            displaysurf.blit(fadebg, (0, 0))
            screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
            j -= 20
        engine.say(text[index])
        engine.runAndWait()
        while speaking:
            pygame.display.flip(); clock.tick(30)
            displaysurf.fill((80, 10, 10))
            writetext((10, 480), text[index], txtcolor=(255, 100, 100))
            writetext((260, 560), "[Press SPACE or ENTER to proceed]", fontsize=14, txtcolor=(255, 255, 255))
            screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == KEYDOWN:
                    if ev.key == K_RETURN or ev.key == K_SPACE:
                        speaking = False
        while j < 225:
            pygame.display.flip(); clock.tick(30)
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    sys.exit()
            fadebg.set_alpha(j)
            displaysurf.blit(fadebg, (0, 0))
            screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
            j += 5

class Character:
    def __init__(self):
        self.rect = Rect(0, 0, 64, 128)
        self.grav = 0
        self.xacc = 0
        self.hitpoints = 100

class Player(Character):
    def __init__(self):
        super().__init__()
        self.rect.x = 268
        self.rect.bottom = 420
        self.end = [False, False]
        self.spritesheet = pygame.image.load("stickman spritesheet.png")
        self.animationvar = 0
        self.spritetype = "stand"
        self.direction = "right"
        self.attack = False
        self.attackcoords = [(0, 0), (0, 0), (-2, 1), (0, -20), (10, -70), (40, -65), (50, -30), (30, 40)]
        self.attackno = 256
        self.swordparticles = []
    def display(self, scrollx):
        if self.direction == "right":
            if self.attack:
                if self.spritetype == "stand":
                    self.attackno = 3*128
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, self.attackno, self.rect.w, self.rect.h))
                if self.attackno == 3*128:
                    displaysurf.blit(self.spritesheet, (self.rect.x - scrollx + (self.attackcoords[int(self.animationvar)][0]), self.rect.y + (self.attackcoords[int(self.animationvar)][1])), (int(self.animationvar)*64, self.attackno + 128, self.rect.w, self.rect.h))
                    if len(self.swordparticles) < 10:
                        self.swordparticles.append(Particle(self.rect.x + self.animationvar*10, self.rect.y - (3.5 - self.animationvar)*4, -1, 0))
                    for parts in self.swordparticles:
                        parts.display(scrollx)
                        if parts.size < 0:
                            self.swordparticles.remove(parts)
                if self.animationvar > 7.5 and self.attackno == 2*128:
                    self.attackno = 3*128
                    self.animationvar = 0
                if self.animationvar > 7.5 and self.attackno == 3*128:
                    self.attack = False

            elif not self.grav == 0:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (64, 128, self.rect.w, self.rect.h))
            elif self.spritetype == "stand":
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (3*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "walk":
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "run":
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, 128, self.rect.w, self.rect.h))
        else:
            if self.attack:
                if self.spritetype == "stand":
                    self.attackno = 3*128
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar) - 7) * -64, self.attackno, self.rect.w, self.rect.h))
                if self.attackno == 3*128:
                    displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx - (self.attackcoords[int(self.animationvar)][0]), self.rect.y + (self.attackcoords[int(self.animationvar)][1])), ((int(self.animationvar) - 7) * -64, self.attackno + 128, self.rect.w, self.rect.h))
                    if len(self.swordparticles) < 10:
                        self.swordparticles.append(Particle(self.rect.right - self.animationvar*10, self.rect.y - (3.5 - self.animationvar)*4, 1, 0))
                    for parts in self.swordparticles:
                        parts.display(scrollx)
                        if parts.size < 0:
                            self.swordparticles.remove(parts)
                if self.animationvar > 7.5 and self.attackno == 2*128:
                    self.attackno = 3*128
                    self.animationvar = 0
                if self.animationvar > 7.5 and self.attackno == 3*128:
                    self.attack = False
            elif not self.grav == 0:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (7*64, 128, self.rect.w, self.rect.h))
            elif self.spritetype == "stand":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (4*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "walk":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (((int(self.animationvar) - 7) * -1)*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "run":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (((int(self.animationvar) - 7) * -1)*64, 128, self.rect.w, self.rect.h))

class Enemy(Character):
    def __init__(self):
        super().__init__()
        self.rect.x = sw
        self.rect.bottom = 440
        self.speed = 6
    def display(self, scrollx):
        pygame.draw.rect(displaysurf, (200, 200, 255), (self.rect.x - scrollx, self.rect.y, self.rect.w, self.rect.h))

player = Player()
enemylist = []

def level0():
    speech(0)
    speech(1)
    speech(2)
    global level
    running = True
    firsthit = False
    instruct = 0
    countdown = -1
    spoke = False
    pressed = [False, False, False, False]
    scrollx = 0
    while running:
        keys_pressed = pygame.key.get_pressed()
        player.animationvar += 0.4
        if player.animationvar > 8:
            player.animationvar = 0
            if not spoke:
                if instruct == 0:
                    engine.say("Press A to go left, D to go right.")
                    engine.runAndWait()
                elif instruct == 1:
                    engine.say("Press W to jump.")
                    engine.runAndWait()
                elif instruct == 2:
                    engine.say("Press the left shift button while moving left or right to sprint.")
                    engine.runAndWait()
                elif instruct == 3:
                    engine.say("Press the space bar to unleash your power.")
                    engine.runAndWait()
                if instruct < 4:
                    spoke = True

        if instruct < 4:
            if instruct == 0:
                if keys_pressed[K_a]:
                    pressed[0] = True
                if keys_pressed[K_d]:
                    pressed[1] = True
                if not keys_pressed[K_a] and not keys_pressed[K_d] and pressed[0] and pressed[1]:
                    instruct = 1
                    spoke = False
            if instruct == 1:
                if keys_pressed[K_w]:
                    pressed[2] = True
                elif pressed[2] and player.rect.bottom == 440:
                    instruct = 2
                    spoke = False
            if instruct == 2:
                if keys_pressed[K_LSHIFT]:
                    pressed[3] = True
                elif pressed[3]:
                    instruct = 3
                    spoke = False
            if instruct == 3:
                if keys_pressed[K_SPACE]:
                    instruct = 4

        pygame.display.flip(); clock.tick(30)
        if countdown > 0:
            countdown -= 1
        if player.rect.centerx < 585:
            scrollx += (player.rect.x - scrollx - 268)/20
        else:
            scrollx += (player.rect.x - scrollx - 474)/20
        if player.rect.bottom < 440:
            player.grav += 1
        else:
            player.grav = 0
            player.rect.bottom = 440
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    # pause the game
                    running = False
                if ev.key == K_SPACE:
                    if not firsthit and instruct == 3:
                        firsthit = True
                        speech(3)
                        speech(4)
                        countdown = 1000
                    if instruct > 2:
                        player.attack = True 
                        player.animationvar = 0
                        player.attackno = 2*128
                if ev.key == K_w:
                    if player.rect.bottom == 440 and instruct > 0:
                        player.grav = -18
                if ev.key == K_x:
                    print(player.rect.x)
                if ev.key == K_z:
                    print(scrollx)
        if keys_pressed[K_a]:
            player.spritetype = "walk"
            player.direction = "left"
            if player.rect.x > 268:
                if player.xacc > -10:
                    player.xacc -= 1
            else:
                player.xacc = 0
        elif keys_pressed[K_d]:
            player.spritetype = "walk"
            player.direction = "right"
            if player.rect.x < 948:
                if player.xacc < 10:
                    player.xacc += 1
            else:
                player.xacc = 0
        else:
            player.spritetype = "stand"
            if player.xacc < 0:
                player.xacc += 1
            elif player.xacc > 0:
                player.xacc -= 1
        for enemy in enemylist:
            if player.rect.right < enemy.rect.left:
                if enemy.xacc > -enemy.speed:
                    enemy.xacc -= 1
            elif player.rect.left > enemy.rect.right:
                if enemy.xacc < enemy.speed:
                    enemy.xacc += 1
            enemy.rect.x += enemy.xacc
        if not keys_pressed[K_LSHIFT]:
            player.rect.x += player.xacc/2
        elif player.spritetype == "walk":
            if instruct > 1:
                player.spritetype = "run"
                player.rect.x += player.xacc
            else:
                player.rect.x += player.xacc/2
        if player.attack:
            if player.attackno == 2*128 and player.animationvar > 7.5:
                player.grav = -12
        player.rect.y += player.grav
        displaysurf.fill((255, 60, 0))
        displaysurf.blit(pygame.transform.scale(bgpic, (sw, 500)), (-scrollx, 0))
        pygame.draw.rect(displaysurf, (0, 0, 0), (0, 600 - 160, 800, 160))
        pygame.draw.polygon(displaysurf, (255, 220, 20), ((player.rect.x + 20 - scrollx, 500), (player.rect.right - 20 - scrollx, 500), (player.rect.centerx - scrollx, 480)))
        player.display(scrollx)
        for enemy in enemylist:
            enemy.display(scrollx)
        if instruct < 2:
            displaysurf.blit(wadpic, (100, 100))
        if countdown == 0:
            speech(5)
            speech(6)
            running = False
            level = 1
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))

<<<<<<< HEAD
enemylist = [Enemy()]

=======
>>>>>>> ea08271732d9980d02465189f45a0b9e0bb16f30
def level1():
    global level
    countdown = -1
    running = True
    scrollx = 0
    while running:
        keys_pressed = pygame.key.get_pressed()
        player.animationvar += 0.4
        if player.animationvar > 8:
            player.animationvar = 0
        pygame.display.flip(); clock.tick(30)
        if countdown > 0:
            countdown -= 1
        if player.rect.centerx < 585:
            scrollx += (player.rect.x - scrollx - 268)/20
        else:
            scrollx += (player.rect.x - scrollx - 474)/20
        if player.rect.bottom < 440:
            player.grav += 1
        else:
            player.grav = 0
            player.rect.bottom = 440
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    # pause the game
                    running = False
                if ev.key == K_SPACE:
                    player.attack = True 
                    player.animationvar = 0
                    player.attackno = 2*128
                if ev.key == K_w:
                    if player.rect.bottom == 440:
                        player.grav = -18
                if ev.key == K_x:
                    print(player.rect.x)
                if ev.key == K_z:
                    print(scrollx)
        if keys_pressed[K_a]:
            player.spritetype = "walk"
            player.direction = "left"
            if player.rect.x > 268:
                if player.xacc > -10:
                    player.xacc -= 1
            else:
                player.xacc = 0
        elif keys_pressed[K_d]:
            player.spritetype = "walk"
            player.direction = "right"
            if player.rect.x < 948:
                if player.xacc < 10:
                    player.xacc += 1
            else:
                player.xacc = 0
        else:
            player.spritetype = "stand"
            if player.xacc < 0:
                player.xacc += 1
            elif player.xacc > 0:
                player.xacc -= 1
        for enemy in enemylist:
            if player.rect.right < enemy.rect.left:
                if enemy.xacc > -enemy.speed:
                    enemy.xacc -= 1
            elif player.rect.left > enemy.rect.right:
                if enemy.xacc < enemy.speed:
                    enemy.xacc += 1
            enemy.rect.x += enemy.xacc
        if not keys_pressed[K_LSHIFT]:
            player.rect.x += player.xacc/2
        elif player.spritetype == "walk":
            player.spritetype = "run"
            player.rect.x += player.xacc
        if player.attack:
            if player.attackno == 2*128 and player.animationvar > 7.5:
                player.grav = -12
        player.rect.y += player.grav
        displaysurf.fill((255, 60, 0))
        displaysurf.blit(pygame.transform.scale(bgpic, (sw, 500)), (-scrollx, 0))
        pygame.draw.rect(displaysurf, (0, 0, 0), (0, 600 - 160, 800, 160))
        pygame.draw.polygon(displaysurf, (255, 220, 20), ((player.rect.x + 20 - scrollx, 500), (player.rect.right - 20 - scrollx, 500), (player.rect.centerx - scrollx, 480)))
        player.display(scrollx)
        for enemy in enemylist:
            enemy.display(scrollx)
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))

def screen_fade():
    j = 0
    while j < 225:
        pygame.display.flip(); clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()
        fadebg = pygame.Surface((800, 600))
        fadebg.fill((0, 0, 0))
        fadebg.set_alpha(j)
        displaysurf.blit(fadebg, (0, 0))
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
        j += 5

def menuloop():
    running = True
    while running:
        pygame.display.flip(); clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    pass # pause the game
        optcolors = [(100, 100, 0), (100, 100, 0), (100, 100, 0)]
        optrects = [Rect(400 - 180, 250, 100, 50), Rect(400 - 180, 350, 180, 50), Rect(400 - 180, 450, 100, 50)]
        mouse = [pygame.mouse.get_pos(), pygame.mouse.get_pressed()]
        mouse[0] = mouse[0][0] * 800/sw, mouse[0][1] * 600/sh
        for i in range(len(optrects)):
            if optrects[i].collidepoint(mouse[0]):
                optcolors[i] = (200, 200, 0)
                if mouse[1][0]:
                    if i == 0:
                        if level == 0:
                            screen_fade()
                            level0()
                        if level == 1:
                            screen_fade()
                            level1()
                    elif i == 1:
                        #settings
                        pass
                    elif i == 2:
                        running = False
                        pygame.quit()
                        sys.exit()
            else:
                optcolors[i] = (100, 100, 0)
        displaysurf.fill((20, 20, 20))
        writetext((400 - 120, 100), "Bloodlust", txtcolor=(255, 30, 0), fontsize=50)
        writetext((400 - 180, 250), "> Start", txtcolor=optcolors[0])
        writetext((400 - 180, 350), "> Settings", txtcolor=optcolors[1])
        writetext((400 - 180, 450), "> Exit", txtcolor=optcolors[2])
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))

if __name__ == "__main__":
    menuloop()
    

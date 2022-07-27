import pygame, sys
from pygame import *
from pygame import mixer
from pygame.locals import *
from random import randint as rd
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 160)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 
engine.setProperty('volume', 1) 

#killing enemies can occationally drop a healing item.

pygame.init()

clock = pygame.time.Clock()
sw, sh = pygame.display.Info().current_w, pygame.display.Info().current_h

pygame.display.set_caption("Bloodlust : Rise of the greatest assassin")
pygame.display.set_icon(pygame.image.load("logo.png"))

screen = pygame.display.set_mode((sw, sh), FULLSCREEN)
displaysurf = pygame.Surface((800, 600))
displayrect = Rect(0, 0, 800, 600)

wadpic = pygame.image.load("wad.png")

speaking = False
level = 0
guibool = True
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

def writetext(position, text="Sample Text", fontsize=30, txtcolor=(0, 0, 0), txtbgcolor=None, fontttf='Arial'):
    # fontttf += '.ttf'
    font = pygame.font.SysFont(fontttf, fontsize)
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
            writetext((10, 400), text[index], txtcolor=(255, 100, 100))
            displaysurf.blit(fadebg, (0, 0))
            screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
            j -= 20
        engine.say(text[index])
        engine.runAndWait()
        while speaking:
            pygame.display.flip(); clock.tick(30)
            displaysurf.fill((80, 10, 10))
            writetext((10, 400), text[index], txtcolor=(255, 100, 100))
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

class Throwable:
    def __init__(self):
        self.rect = Rect(-30, -30, 12, 12)
        self.dist = 0
        self.speed = 0
        self.damage = 20
    def throw(self, player):
        self.dist = 0
        if player.facedir == "right":
            self.rect.x = player.rect.right
            self.speed = 10
        else:
            self.rect.right = player.rect.left
            self.speed = -10
        self.rect.y = player.rect.centery
    def display(self, scrollx):
        self.dist += self.speed
        self.rect.x = player.rect.right + self.dist
        pygame.draw.circle(displaysurf, (0, 0, 0), (self.rect.centerx - scrollx, self.rect.centery), 6)
class Magic:
    def __init__(self):
        self.rect = Rect(-30, -30, 24, 24)
        self.dist = 0
        self.speed = 0
        self.damage = 25
        self.trailparticles = []
    def throw(self, player):
        self.dist = 0
        if player.facedir == "right":
            self.rect.x = player.rect.right
            self.speed = 10
        else:
            self.rect.right = player.rect.left
            self.speed = -10
        self.rect.y = player.rect.centery
    def display(self, scrollx):
        self.dist += self.speed
        self.rect.x = player.rect.right + self.dist
        if len(self.trailparticles) < 10:
            self.trailparticles.append(Particle(self.rect.centerx, self.rect.centery, self.speed/10, 0))
        for parts in self.trailparticles:
            parts.display(scrollx)
            if parts.size < 0:
                self.trailparticles.remove(parts)
        pygame.draw.circle(displaysurf, (255, 255, 0), (self.rect.centerx - scrollx, self.rect.centery), 12)

shuriken = Throwable()
fireball = Magic()

class Player(Character):
    def __init__(self):
        super().__init__()
        self.rect.bottom = 420
        self.spritesheet = pygame.image.load("stickman_spritesheet.png")
        self.animationvar = 0
        self.spritetype = "stand"
        self.direction = "right"
        self.facedir = "right"
        self.attack = False
        self.kick = False
        self.throw = False
        self.magic = False
        self.attackcoords = [(0, 0), (0, 0), (-2, 1), (0, -20), (10, -70), (40, -65), (50, -30), (30, 40)]
        self.attackno = 256
        self.swordparticles = []
        self.hitpoints = 100
        self.attackpower = 10
        self.hpcolor = [0, 255, 0]
    def display(self, scrollx):
        if self.facedir == "right":
            if self.attack:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, self.attackno, self.rect.w, self.rect.h))
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx + (self.attackcoords[int(self.animationvar)][0]), self.rect.y + (self.attackcoords[int(self.animationvar)][1])), (int(self.animationvar)*64, self.attackno + 128, self.rect.w, self.rect.h))
                if len(self.swordparticles) < 10:
                    self.swordparticles.append(Particle(self.rect.x + self.animationvar*10, self.rect.y - (3.5 - self.animationvar)*4, -1, 0))
                for parts in self.swordparticles:
                    parts.display(scrollx)
                    if parts.size < 0:
                        self.swordparticles.remove(parts)
                if self.animationvar > 7.5:
                    self.attack = False
            elif self.kick:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, self.attackno, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    self.kick = False
            elif self.throw:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, self.attackno, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    self.throw = False
                    shuriken.throw(self)
            elif self.magic:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, self.attackno, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    if self.attackno == 6*128:
                        self.attackno = 7*128
                        self.animationvar = 0
                        fireball.throw(self)
                    else:
                        self.magic = False

            elif not self.grav == 0:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (64, 128, self.rect.w, self.rect.h))
            elif self.spritetype == "stand":
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (3*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "walk":
                if player.direction == "right":
                    displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, 0, self.rect.w, self.rect.h))
                else:
                    displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), ((7 - int(self.animationvar))*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "run":
                if player.direction == "right":
                    displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, 128, self.rect.w, self.rect.h))
                else:
                    displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), ((7 - int(self.animationvar))*64, 128, self.rect.w, self.rect.h))
        else:
            if self.attack:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar) - 7) * -64, self.attackno, self.rect.w, self.rect.h))
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx - (self.attackcoords[int(self.animationvar)][0]), self.rect.y + (self.attackcoords[int(self.animationvar)][1])), ((int(self.animationvar) - 7) * -64, self.attackno + 128, self.rect.w, self.rect.h))
                if len(self.swordparticles) < 10:
                    self.swordparticles.append(Particle(self.rect.right - self.animationvar*10, self.rect.y - (3.5 - self.animationvar)*4, 1, 0))
                for parts in self.swordparticles:
                    parts.display(scrollx)
                    if parts.size < 0:
                        self.swordparticles.remove(parts)
                if self.animationvar > 7.5:
                    self.attack = False
            elif self.kick:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar) - 7) * -64, self.attackno, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    self.kick = False
            elif self.throw:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar) - 7) * -64, self.attackno, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    self.throw = False
                    shuriken.throw(self)
            elif self.magic:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar) - 7) * -64, self.attackno, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    if self.attackno == 6*128:
                        self.attackno = 7*128
                        self.animationvar = 0
                        fireball.throw(self)
                    else:
                        self.magic = False
            elif not self.grav == 0:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (7*64, 128, self.rect.w, self.rect.h))
            elif self.spritetype == "stand":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (4*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "walk":
                if self.direction == "left":
                    displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (((int(self.animationvar) - 7) * -1)*64, 0, self.rect.w, self.rect.h))
                else:
                    displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar)*64), 0, self.rect.w, self.rect.h))
            elif self.spritetype == "run":
                if self.direction == "left":
                    displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (((int(self.animationvar) - 7) * -1)*64, 128, self.rect.w, self.rect.h))
                else:
                    displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar)*64), 128, self.rect.w, self.rect.h))
        shuriken.display(scrollx)
        fireball.display(scrollx)

class Enemy(Character):
    def __init__(self, xpos):
        super().__init__()
        self.rect.x = xpos
        self.rect.bottom = 440
        self.spritesheet = pygame.image.load("enemy_spritesheet.png")
        self.spritetype = "stand"
        self.direction = "right"
        self.attack = False
        self.animationvar = 0
        self.attackcoords = [(0, 0), (0, 0), (-2, 1), (0, -20), (10, -70), (40, -65), (50, -30), (30, 40)]
        self.attackno = 256
        self.speed = 6
        self.hitpoints = 100
        self.hpcolor = [0, 255, 0]
        self.attackpower = 2
        self.selfcollide = False
    def display(self, scrollx):
        if self.direction == "right":
            if self.attack:
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx, self.rect.y), (int(self.animationvar)*64, self.attackno, self.rect.w, self.rect.h))
                displaysurf.blit(self.spritesheet, (self.rect.x - scrollx + (self.attackcoords[int(self.animationvar)][0]), self.rect.y + (self.attackcoords[int(self.animationvar)][1])), (int(self.animationvar)*64, self.attackno + 128, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
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
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), ((int(self.animationvar) - 7) * -64, self.attackno, self.rect.w, self.rect.h))
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx - (self.attackcoords[int(self.animationvar)][0]), self.rect.y + (self.attackcoords[int(self.animationvar)][1])), ((int(self.animationvar) - 7) * -64, self.attackno + 128, self.rect.w, self.rect.h))
                if self.animationvar > 7.5:
                    self.attack = False
            elif not self.grav == 0:
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (7*64, 128, self.rect.w, self.rect.h))
            elif self.spritetype == "stand":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (4*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "walk":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (((int(self.animationvar) - 7) * -1)*64, 0, self.rect.w, self.rect.h))
            elif self.spritetype == "run":
                displaysurf.blit(pygame.transform.flip(self.spritesheet, 1, 0), (self.rect.x - scrollx, self.rect.y), (((int(self.animationvar) - 7) * -1)*64, 128, self.rect.w, self.rect.h))

player = Player()
enemylist = []

mixer.music.load("fight_bgm.wav")

treeimg = pygame.image.load("tree.png")
bushimg = pygame.image.load("bush.png")
grassimg = pygame.image.load("grass.png")
fenceimg = pygame.image.load("fence.png")

def createChunk(xpos):
    global chunks
    chunksurf = Surface((800, 600))
    chunksurf.fill((0, 255, 0))
    for i in range(7):
        item = rd(0, 2)
        if item == 0:
            if i != 0 and i != 6:
                chunksurf.blit(treeimg, (i*128, 184))
            else:
                chunksurf.blit(grassimg, (i*128, 184))
        if item == 1:
            chunksurf.blit(bushimg, (i*128, 184))
        if item == 2:
            chunksurf.blit(grassimg, (i*128, 184))
    chunksurf.set_colorkey((0, 255, 0))
    chunksurf.set_alpha(210)
    chunks.append([Rect(xpos, 0, 800, 600), chunksurf])

def createGrassChunk(xpos):
    global chunks
    chunksurf = Surface((800, 600))
    chunksurf.fill((0, 255, 0))
    for i in range(7):
        chunksurf.blit(grassimg, (i*128, 184))
    chunksurf.set_colorkey((0, 255, 0))
    chunksurf.set_alpha(210)
    chunks.append([Rect(xpos, 0, 800, 600), chunksurf])

def createEndChunk(xpos):
    global chunks
    chunksurf = Surface((800, 600))
    chunksurf.fill((0, 255, 0))
    for i in range(7):
        chunksurf.blit(fenceimg, (i*128, 184))
    chunksurf.set_colorkey((0, 255, 0))
    chunksurf.set_alpha(230)
    chunks.append([Rect(xpos, 0, 800, 600), chunksurf])

chunks = []

def name_input():
    global name
    name = ""
    running = True
    while running:
        pygame.display.flip(); clock.tick(30)
        displaysurf.fill((180, 100, 10))
        writetext((30, 300), f"Enter your name: {name}", 38, (0, 0, 0))
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_BACKSPACE:
                    name = name[:-1]
                elif event.key == K_RETURN:
                    return name
                elif event.key == K_MINUS:
                    name += "_"
                elif event.key == K_SPACE:
                    name += " "
                else:
                    name += event.unicode
                    
bglines = [[[749, 603], [849, -3]], [[747, 603], [847, -3]], [[709, 603], [809, -3]], [[707, 603], [807, -3]], [[669, 603], [769, -3]], [[667, 603], [767, -3]], [[629, 603], [729, -3]], [[627, 603], [727, -3]], [[589, 603], [689, -3]], [[587, 603], [687, -3]], [[549, 603], [649, -3]], [[547, 603], [647, -3]], [[509, 603], [609, -3]], [[507, 603], [607, -3]], [[469, 603], [569, -3]], [[467, 603], [567, -3]], [[429, 603], [529, -3]], [[427, 603], [527, -3]], [[389, 603], 
[489, -3]], [[387, 603], [487, -3]], [[349, 603], [449, -3]], [[347, 603], [447, -3]], [[309, 603], [409, -3]], [[307, 603], [407, -3]], [[269, 603], [369, -3]], [[267, 603], [367, -3]], [[229, 603], [329, -3]], [[227, 603], [327, -3]], [[189, 603], [289, -3]], [[187, 603], [287, -3]], [[149, 603], [249, -3]], [[147, 603], [247, -3]], [[109, 603], [209, -3]], [[107, 603], [207, -3]], [[69, 603], [169, -3]], [[67, 603], [167, -3]], [[29, 603], [129, -3]], [[27, 603], [127, -3]], [[-11, 603], [89, -3]], [[-13, 603], [87, -3]], [[-51, 603], [49, -3]], [[-53, 603], [47, -3]], [[-91, 603], [9, -3]], [[-93, 603], [7, -3]]]

def combat_scene(enemylist, chunks):
    global level
    if level == 1:
        llimit = -2442
        rlimit = 3166
    elif level == 2:
        llimit = -4842
        rlimit = 5566
    player.rect.x = 0
    player.hitpoint = 100
    player.direction = "right"
    running = True
    scrollx = 0
    bganim = 0
    pygame.mouse.set_visible(False)
    mixer.music.play(-1)
    while running:
        keys_pressed = pygame.key.get_pressed()

        player.animationvar += 0.4
        if player.animationvar > 8:
            player.animationvar = 0

        for enemy in enemylist:
            enemy.animationvar += 0.4
            if enemy.animationvar > 8:
                enemy.animationvar = 0
        
        bganim += 0.4
        if bganim > 8:
            bganim = 0

        pygame.display.flip(); clock.tick(30)

        if player.facedir == "right":
            scrollx += (player.rect.x - scrollx - 268)/20
        else:
            scrollx += (player.rect.x - scrollx - 450)/20

        if len(bglines) < 60 and bganim > 7:
            bglines.append([[-103, 603], [-3, -3]])
        if bglines[0][0][0] > 803:
            bglines.pop(0)
        for line in bglines:
            line[0][0] += 2
            line[1][0] += 2

        if player.rect.bottom < 440:
            player.grav += 1
        else:
            player.grav = 0
            player.rect.bottom = 440

        for enemy in enemylist:
            if enemy.rect.bottom < 440:
                enemy.grav += 1
            else:
                enemy.grav = 0
                enemy.rect.bottom = 440

        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    # pause the game
                    mixer.music.stop()
                    running = False
                if ev.key == K_w:
                    if player.rect.bottom == 440:
                        player.grav = -18
                if ev.key == K_x:
                    print(player.rect.x)
                if ev.key == K_z:
                    print(scrollx)
            if ev.type == MOUSEBUTTONDOWN:
                if ev.button == 1:
                    player.attack = True 
                    player.attackno = 2*128
                    player.animationvar = 0
                if ev.button == 3:
                    player.kick = True
                    player.attackno = 4*128
                    player.animationvar = 0
                if ev.button == 4:
                    player.magic = True
                    player.attackno = 6*128
                    player.animationvar = 0
                if ev.button == 5:
                    player.throw = True
                    player.attackno = 5*128
                    player.animationvar = 0
                
        if keys_pressed[K_a]:
            if player.rect.x > llimit and not player.throw and not player.magic:
                player.spritetype = "walk"
                player.direction = "left"
                if player.xacc > -10:
                    player.xacc -= 1
            else:
                player.spritetype = "stand"
                player.xacc = 0
        elif keys_pressed[K_d]:
            if player.rect.x < rlimit and not player.throw and not player.magic:
                player.spritetype = "walk"
                player.direction = "right"
                if player.xacc < 10:
                    player.xacc += 1
            else:
                player.spritetype = "stand"
                player.xacc = 0
        else:
            player.spritetype = "stand"
            if player.xacc < 0:
                player.xacc += 1
            elif player.xacc > 0:
                player.xacc -= 1

        playerfacedir = mouse.get_rel()
        if playerfacedir[0] < 0:
            player.facedir = "left"
        elif playerfacedir[0] > 0:
            player.facedir = "right"

        if not keys_pressed[K_LSHIFT]:
            player.rect.x += player.xacc/2
        elif player.spritetype == "walk":
            if player.direction == player.facedir:
                player.spritetype = "run"
                player.rect.x += player.xacc
            else:
                player.rect.x += player.xacc/2
        # player.rect.x += player.xacc/2

        if player.attack:
            for enemy in enemylist:
                if player.rect.colliderect(enemy.rect):
                    if player.facedir == "right":
                        if enemy.rect.x > player.rect.x:
                            enemy.hitpoints -= player.attackpower
                            enemy.grav = -6
                        enemy.rect.x += 60
                    else:
                        if enemy.rect.right < player.rect.right:
                            enemy.hitpoints -= player.attackpower
                            enemy.grav = -6
                        enemy.rect.x -= 60
        if player.kick:
            for enemy in enemylist:
                if player.rect.colliderect(enemy.rect):
                    if player.facedir == "right":
                        if enemy.rect.x > player.rect.x:
                            enemy.hitpoints -= player.attackpower/2
                            enemy.grav = -3
                        enemy.rect.x += 120
                    else:
                        if enemy.rect.right < player.rect.right:
                            enemy.hitpoints -= player.attackpower/2
                            enemy.grav = -3
                        enemy.rect.x -= 120
            
        player.rect.y += player.grav
        for enemy in enemylist:
            enemy.rect.y += enemy.grav

        # enemy
        for enemy in enemylist:
            if enemy.rect.colliderect(displayrect):
                if player.rect.right < enemy.rect.left:
                    enemy.direction = "left"
                elif player.rect.left > enemy.rect.right:
                    enemy.direction = "right"
            else:
                enemy.spritetype = "stand"
        for j in range(len(enemylist)):
            for i in range(len(enemylist)):
                if i%2 == 0 and not j%2 == 0 and (enemylist[i].rect.colliderect(displayrect) or enemylist[j].rect.colliderect(displayrect)):
                    enemy = enemylist[j]
                    enemy2 = enemylist[i]
                    if enemy.rect.x > enemy2.rect.x:
                        if enemy.rect.x - enemy2.rect.x < 100:
                            enemy.direction = "right"
                            enemy2.direction = "left"
                    else:
                        if enemy2.rect.x - enemy.rect.x < 100:
                            enemy.direction = "left"
                            enemy2.direction = "right"
        for enemy in enemylist:
            if enemy.rect.colliderect(displayrect):
                if enemy.direction == "left":
                    if enemy.grav == 0:
                        if enemy.rect.x - player.rect.right < 80:
                            enemy.spritetype = "run"
                        else:
                            enemy.spritetype = "walk"
                    if enemy.spritetype != "stand":
                        if enemy.xacc > -enemy.speed:
                            enemy.xacc -= 1
                    else:
                        if enemy.xacc < 0:
                            enemy.xacc += 1
                elif enemy.direction == "right":
                    if enemy.grav == 0:
                        if player.rect.x - enemy.rect.right < 80:
                            enemy.spritetype = "run"
                        else:
                            enemy.spritetype = "walk"
                    if enemy.spritetype != "stand":
                        if enemy.xacc < enemy.speed:
                            enemy.xacc += 1
                    else:
                        if enemy.xacc > 0:
                            enemy.xacc -= 1

                if enemy.rect.colliderect(player.rect):
                    if not enemy.attack:
                        if enemy.direction == "left" and player.rect.x > enemy.rect.centerx:
                            pass
                        elif enemy.direction == "right" and player.rect.right < enemy.rect.centerx:
                            pass
                        else:
                            enemy.animationvar = 0
                            player.hitpoints -= enemy.attackpower
                            if enemy.direction == "right":
                                if player.rect.x < rlimit:
                                    player.rect.x += 30
                                    player.grav = -3
                            else:
                                if player.rect.x > llimit:
                                    player.rect.x -= 30
                                    player.grav = -3
                    enemy.attack = True
                else:
                    if enemy.spritetype == "run":
                        enemy.rect.x += enemy.xacc
                    elif enemy.spritetype == "walk":
                        enemy.rect.x += enemy.xacc/2
                if enemy.rect.colliderect(shuriken.rect):
                    if shuriken.speed > 0:
                        enemy.rect.x += 50
                    elif shuriken.speed < 0:
                        enemy.rect.x -= 50
                    shuriken.speed = 0; shuriken.dist = 0
                    shuriken.rect.x = shuriken.rect.y = -30
                    enemy.hitpoints -= shuriken.damage
                if enemy.rect.colliderect(fireball.rect):
                    if fireball.speed > 0:
                        enemy.rect.x += 100
                    elif fireball.speed < 0:
                        enemy.rect.x -= 100
                    fireball.speed = 0; fireball.dist = 0
                    fireball.rect.x = fireball.rect.y = -30
                    enemy.hitpoints -= fireball.damage
        
        for enemy in enemylist:
            if enemy.rect.x > rlimit:
                enemy.rect.x = rlimit
            if enemy.rect.x < llimit:
                enemy.rect.x = llimit
        displayrect.x = scrollx

        # display
        displaysurf.fill((255, 60, 0))
        for line in bglines:
            pygame.draw.line(displaysurf, (255, 0, 0), line[0], line[1], 6)
        for chunk in chunks:
            if chunk[0].colliderect(displayrect):
                displaysurf.blit(chunk[1], (chunk[0].x - scrollx, 0))
        pygame.draw.rect(displaysurf, (0, 0, 0), (0, 600 - 160, 800, 160))
        pygame.draw.polygon(displaysurf, (255, 220, 20), ((player.rect.x + 20 - scrollx, 500), (player.rect.right - 20 - scrollx, 500), (player.rect.centerx - scrollx, 480)))
        player.display(scrollx)
        for enemy in enemylist:
            enemy.display(scrollx)
            pygame.draw.rect(displaysurf, (0, 0, 0), (enemy.rect.x - 2 - scrollx, enemy.rect.y - 22, 54, 14))
            enemy.hpcolor = [220 - enemy.hitpoints*2, enemy.hitpoints*2 - 20, 0]
            try:
                pygame.draw.rect(displaysurf, enemy.hpcolor, (enemy.rect.x - scrollx, enemy.rect.y - 20, enemy.hitpoints//2, 10))
            except ValueError:
                enemylist.remove(enemy)
        pygame.draw.rect(displaysurf, (0, 0, 0), (28, 58, 204, 34))
        player.hpcolor = [220 - player.hitpoints*2, player.hitpoints*2 - 20, 0]
        try:
            pygame.draw.rect(displaysurf, player.hpcolor, (30, 60, player.hitpoints*2, 30))
        except ValueError:
            mixer.music.stop()
            running = False
        writetext((30, 120), f"Kills remaining : {len(enemylist)}")
        for enemy in enemylist:
            if not enemy.rect.colliderect(displayrect):
                if enemy.rect.x > displayrect.right:
                    pygame.draw.polygon(displaysurf, (255, 180, 0), ((760, 280), (760, 320), (780, 300)))
                elif enemy.rect.right < displayrect.x:
                    pygame.draw.polygon(displaysurf, (255, 180, 0), ((40, 280), (40, 320), (20, 300)))
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
        if len(enemylist) == 0:
            running = False
            level += 1
            mixer.music.stop()
    pygame.mouse.set_visible(True)

def level0():
    for i in range(0, 3):
        speech(i)
    global level, chunks
    chunks = []
    createGrassChunk(0)
    running = True
    firsthit = False
    instruct = 0
    countdown = -1
    spoke = False
    pressed = [False, False, False, False, False, False, False, False]
    scrollx = 0
    mouse_pressed_3 = False
    mouse_pressed_4 = False
    while running:
        player.facedir = player.direction
        mouse_pressed = pygame.mouse.get_pressed()
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
                    engine.say("Press the Left Mouse button to unleash your sword's power.")
                    engine.runAndWait()
                elif instruct == 4:
                    engine.say("Press the Right Mouse button to kick.")
                    engine.runAndWait()
                elif instruct == 5:
                    engine.say("Scroll down to throw a ranged weapon.")
                    engine.runAndWait()
                elif instruct == 6:
                    engine.say("Scroll up to use magic.")
                    engine.runAndWait()
                if instruct < 7:
                    spoke = True

        if instruct < 7:
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
                if keys_pressed[K_LSHIFT] and (keys_pressed[K_a] or keys_pressed[K_d]):
                    pressed[3] = True
                elif pressed[3]:
                    instruct = 3
                    spoke = False
            if instruct == 3:
                if mouse_pressed[0]:
                    pressed[4] = True
                elif pressed[4]:
                    instruct = 4
                    spoke = False
            if instruct == 4:
                if mouse_pressed[2]:
                    pressed[5] = True
                elif pressed[5]:
                    instruct = 5
                    spoke = False
            if instruct == 5:
                if mouse_pressed_3 and (shuriken.rect.x < 0 or shuriken.rect.right > 800):
                    mouse_pressed_3 = False
                    pressed[6] = True
                elif pressed[6]:
                    instruct = 6
                    spoke = False
            if instruct == 6:
                if mouse_pressed_4:
                    mouse_pressed_4 = False
                    pressed[7] = True
                elif pressed[7]:
                    instruct = 7
                    spoke = False

        pygame.display.flip(); clock.tick(30)
        if countdown > 0:
            countdown -= 1
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
            if ev.type == MOUSEBUTTONDOWN:
                if ev.button == 1:
                    if not firsthit and instruct == 2:
                        firsthit = True
                        speech(3)
                        speech(4)
                    if instruct > 2:
                        player.attack = True 
                        player.animationvar = 0
                        player.attackno = 2*128
                if ev.button == 3:
                    if instruct > 3:
                        player.kick = True
                        player.attackno = 4*128
                        player.animationvar = 0
                if ev.button == 4:
                    if instruct > 5:
                        player.magic = True
                        player.attackno = 6*128
                        player.animationvar = 0
                        mouse_pressed_4 = True
                        countdown = 1000
                if ev.button == 5:
                    if instruct > 4:
                        player.throw = True
                        player.attackno = 5*128
                        player.animationvar = 0
                        mouse_pressed_3 = True
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    # pause the game
                    running = False
                if ev.key == K_w:
                    if player.rect.bottom == 440 and instruct > 0:
                        player.grav = -18
                if ev.key == K_x:
                    print(player.rect.x)
                if ev.key == K_z:
                    print(scrollx)
        if keys_pressed[K_a]:
            player.direction = "left"
            if player.rect.x > 2:
                player.spritetype = "walk"
                if player.xacc > -10:
                    player.xacc -= 1
            else:
                player.rect.x = 0
                player.xacc = 0
                player.spritetype = "stand"
        elif keys_pressed[K_d]:
            player.direction = "right"
            if player.rect.right < 798:
                player.spritetype = "walk"
                if player.xacc < 10:
                    player.xacc += 1
            else:
                player.rect.x = 736
                player.xacc = 0
                player.spritetype = "stand"
        else:
            player.spritetype = "stand"
            if player.xacc < 0:
                player.xacc += 1
            elif player.xacc > 0:
                player.xacc -= 1
        if not keys_pressed[K_LSHIFT]:
            player.rect.x += player.xacc/2
        elif player.spritetype == "walk":
            if instruct > 1:
                player.spritetype = "run"
                player.rect.x += player.xacc
            else:
                player.rect.x += player.xacc/2
        player.rect.y += player.grav

        # display
        displaysurf.fill((255, 60, 0))
        pygame.draw.rect(displaysurf, (0, 0, 0), (0, 600 - 160, 800, 160))
        if instruct == 0:
            writetext((120, 560), "Press A to go left, D to go right.", txtcolor=(255, 255, 255), fontsize=24)
        elif instruct == 1:
            writetext((120, 560), "Press W to jump.", txtcolor=(255, 255, 255), fontsize=24)
        elif instruct == 2:
            writetext((10, 560), "Press the left shift button while moving left or right to sprint.", txtcolor=(255, 255, 255), fontsize=24)
        elif instruct == 3:
            writetext((120, 560), "Press the Left Mouse button to unleash your sword's power.", txtcolor=(255, 255, 255), fontsize=24)
        elif instruct == 4:
            writetext((120, 560), "Press the Right Mouse button to kick.", txtcolor=(255, 255, 255), fontsize=24)
        elif instruct == 5:
            writetext((120, 560), "Scroll down to throw a ranged weapon.", txtcolor=(255, 255, 255), fontsize=24)
        elif instruct == 6:
            writetext((120, 560), "Scroll up to use magic (Fireball).", txtcolor=(255, 255, 255), fontsize=24)
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
        displaysurf.blit(chunks[0][1], (chunks[0][0].x, 0))
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))

def level1():
    global chunks
    chunks = []
    for i in range(-3200, 4000, 800):
        if i == -3200 or i == 3200:
            createEndChunk(i)
        else:
            createChunk(i)
    for i in range(3):
        enemylist.append(Enemy(rd(-3000, 3000)))
    combat_scene(enemylist, chunks)

def level2():
    global chunks
    for i in range(7, 10):
        speech(i)
    name = name_input()
    chunks = []
    for i in range(-5600, 6200, 800):
        if i == -5600 or i == 5600:
            createEndChunk(i)
        else:
            createChunk(i)
    for i in range(8):
        enemylist.append(Enemy(rd(-5200, 5200)))
    combat_scene(enemylist, chunks)

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
    global level
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
                        if level == 2:
                            screen_fade()
                            level2()
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

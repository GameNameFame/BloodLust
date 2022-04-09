import pygame, sys
from pygame import *
from pygame.locals import *
from random import randint as rd

pygame.init()

clock = pygame.time.Clock()
sw, sh = pygame.display.Info().current_w, pygame.display.Info().current_h

screen = pygame.display.set_mode((sw, sh), FULLSCREEN)
displaysurf = pygame.Surface((800, 600))

def writetext(position, text="Sample Text", fontsize=30, txtcolor=(0, 0, 0), txtbgcolor=None, fontttf='freesansbold'):
    fontttf += '.ttf'
    font = pygame.font.Font(fontttf, fontsize)
    txt = font.render(text, True, txtcolor, txtbgcolor)
    displaysurf.blit(txt, position)

class Player:
    def __init__(self):
        self.rect = Rect(0, 0, 64, 128)
        self.grav = 0
        self.xacc = 0
        self.hitpoints = 100
    def display(self):
        pygame.draw.rect(displaysurf, (0, 0, 0), self.rect)

player = Player()

def mainloop(fresh=True):
    running = True
    if fresh:
        pass
    j = 0
    while j < 225:
        pygame.display.flip(); clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
        fadebg = pygame.Surface((800, 600))
        fadebg.fill((0, 0, 0))
        fadebg.set_alpha(j)
        displaysurf.blit(fadebg, (0, 0))
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))
        j += 5
    while running:
        pygame.display.flip(); clock.tick(30)
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
                if ev.key == K_w:
                    if player.rect.bottom == 440:
                        player.grav = -18
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[K_a]:
            if player.xacc > -10:
                player.xacc -= 1
        elif keys_pressed[K_d]:
            if player.xacc < 10:
                player.xacc += 1
        else:
            if player.xacc < 0:
                player.xacc += 1
            elif player.xacc > 0:
                player.xacc -= 1
        if not keys_pressed[K_LSHIFT]:
            player.rect.x += player.xacc/2
        else:
            player.rect.x += player.xacc
        player.rect.y += player.grav
        displaysurf.fill((255, 60, 0))
        pygame.draw.rect(displaysurf, (0, 0, 0), (0, 600 - 160, 800, 160))
        player.display()
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))

def menuloop():
    running = True
    while running:
        pygame.display.flip(); clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
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
                        mainloop()
                    elif i == 1:
                        mainloop(False)
                    elif i == 2:
                        running = False
                        pygame.quit()
                        sys.exit()
            else:
                optcolors[i] = (100, 100, 0)
        displaysurf.fill((20, 20, 20))
        writetext((400 - 120, 100), "Bloodlust", txtcolor=(255, 30, 0), fontsize=50)
        writetext((400 - 180, 250), "> Start", txtcolor=optcolors[0])
        writetext((400 - 180, 350), "> Continue", txtcolor=optcolors[1])
        writetext((400 - 180, 450), "> Exit", txtcolor=optcolors[2])
        screen.blit(pygame.transform.scale(displaysurf, (sw, sh)), (0, 0))

if __name__ == "__main__":
    menuloop()
import pygame
from pygame.locals import *

W, H = 800, 600

pygame.init()

screen = pygame.display.set_mode((W, H), 0, 24)

class Character(object):
    def __init__(self):
        self.W = 32
        self.H = 64
        self.posx = 0
        self.posy = 400 - self.H
        self.color = (128, 128, 128)
        self.xspeed = 10
        self.yspeed = 0
        self.maxyspeed = 50
        self.maxxspeed = 20
        self.minxspeed = 10
    def jump(self):
        self.yspeed = -24
    def crouch(self):
        print "down"
    def fall(self):
        self.posy += self.yspeed
    def left(self):
        self.posx -= self.xspeed
    def right(self):
        self.posx += self.xspeed
    def draw(self):
        pygame.draw.rect(screen, self.color,
                         (self.posx, self.posy, self.W, self.H))


class Sceenario(object):
    def __init__(self, width, height, posx, posy, color):
        self.W = width
        self.H = height
        self.posx = posx
        self.posy = posy
        self.color = color
    def draw(self, background):
        pygame.draw.rect(background, self.color,(self.posx, self.posy, self.W, self.H))
        
def cls(screen, background):
    screen.blit(background, (0,0))
        
    

def game():

    fase = 2

    
    
    canjump1 = True
    canjump2 = True

    buildspeed = False

    lastdirection = 0 # 0 para parado, 1 para direita, -1 para esquerda
    
    background = pygame.Surface((W, H))
    pygame.draw.rect(background, (0, 120, 240),(0, 0, W, H))
    hero = Character()
    hero.color = (255, 0, 0)

    if fase == 1:
        platform = pygame.Surface((80, 40))
        floorleft = pygame.Surface((350, H/3))
        floorright = pygame.Surface((350, H/3))
        pygame.draw.rect(background, (128, 128, 128),(0, 400, 350, H/3))
        pygame.draw.rect(background, (130, 130, 130),(450, 400, 350, H/3))
        pygame.draw.rect(background, (255, 255, 255),(360, 250, 80, 40))
    elif fase == 2:
        hero.posx = W/2
        floor = Sceenario(W, H/3, 0, (2*H)/3, (128, 128, 128))
        floor.draw(background)
        leftwall = Sceenario(hero.W, H/3, 0, H/3, (0, 255, 0))
        leftwall.draw(background)
        rightwall = Sceenario(hero.W, H/3, W - hero.W, H/3, (0, 255, 0))
        rightwall.draw(background)
        sceenelist = [leftwall, rightwall, floor]
              
        canjumpside=True
        pressed=0
        jump=False
    while True:
        pygame.event.pump()
        #print hero.xspeed
        if  canjump1 == True  :
            jump  = False
           # if canjump2 == True :
            pressedback=pressed
            pressed = pygame.key.get_pressed()
            #print "AAAAAAAAAAAAAA"
        else :
            jump=True
            aux= pygame.key.get_pressed()
            
            if (aux[K_LEFT] and pressedback[K_RIGHT]) or (aux[K_RIGHT] and pressedback[K_LEFT]):
                
                if aux[K_LEFT] or aux[K_RIGHT]:
                       
                   if hero.xspeed > 4 : 
                       hero.xspeed-=2
           # if canjump2 == True:
            #    pressed=pressedback
           # else:
           #     pressed=aux
               
             
        if pressed[K_UP]:
            if canjump1 == True :
                if canjump2==True:
                    hero.jump()
                    canjump1 = False
                    pressed = pygame.key.get_pressed()
             
                    canjump2 = False
        else:
            canjump2 = True                
                
        if pressed[K_DOWN]:
            hero.crouch()

        if pressed[K_LEFT] :
            hero.left()
            lastdirection = -1
            buildspeed = True
            
        elif pressed[K_RIGHT] :
            hero.right()
            lastdirection = 0
            buildspeed = True
            print "AAAAAAAAAAAAAA"
        else:
            buildspeed = False

        if buildspeed == True and jump==False and hero.xspeed < hero.maxxspeed:
                hero.xspeed += 1
        elif buildspeed==False and jump == False:
            hero.xspeed = hero.minxspeed
                
        if pressed[K_ESCAPE]:
            break

        hero.fall()

        if hero.posy > H:
            hero.posy = -hero.H
        #elif hero.posx > W:
         #   hero.posx = -hero.W
        #elif hero.posx < 0:
         #   hero.posx = W+hero.W

        if fase == 1:
            if ((hero.posy >= 400 - hero.H and hero.posx <= 350) or
               (hero.posy >= 400 - hero.H and hero.posx >= 450) or
               ((hero.posy >= 250 - hero.H and hero.posx >= 360-hero.W) and
               (hero.posy >= 250 - hero.H and hero.posx <= 440))):
                
                hero.yspeed = 0
                canjump1 = True
                
            elif hero.yspeed < hero.maxyspeed:
                hero.yspeed += 2

        elif fase == 2:

            if hero.posy >= floor.posy - hero.H:
            
                hero.yspeed = 0
                canjump1 = True
            elif hero.yspeed < hero.maxyspeed:
                hero.yspeed += 2
            
        
        
        cls(screen, background)
        hero.draw()
        pygame.display.flip()
        pygame.time.delay(10)


game()
pygame.quit()
                     
            
    
        
    

import pygame
from pygame.locals import *

W, H = 800, 600

pygame.init()

screen = pygame.display.set_mode((W, H), 0, 24)

class Character(object):
    def __init__(self):
        self.image = pygame.image.load("rino6_bg.png")
        self.image.convert_alpha()
        self.W = self.image.get_width()
        self.H = self.image.get_height()
        self.posx = 0
        self.posy = H/2 - self.H
        self.color = (128, 128, 128)
        self.xspeed = 6
        self.yspeed = 0
        self.maxyspeed = 50
        self.maxxspeed = 10
        self.minxspeed = 5
        self.masscenterx = self.posx + self.W/2
        self.masscentery = self.posy + self.H/2
    def jump(self):
        self.yspeed = -24
    def crouch(self):
        print "down"
    def fall(self):
        if self.yspeed > 0:
            for i in xrange(1, self.yspeed):
                self.posy += 1
        elif self.yspeed < 0:
            for i in xrange(1, -self.yspeed):
                self.posy -= 1
            
    def left(self):
        self.posx -= self.xspeed
    def right(self):
        self.posx += self.xspeed
    def draw(self):
        screen.blit(self.image, (self.posx, self.posy))
        #pygame.draw.rect(screen, self.color,
         #                (self.posx, self.posy, self.W, self.H))
    def updatemasscenter(self):
        self.masscenterx = self.posx + self.W/2
        self.masscentery = self.posy + self.H/2

#Calsse de senario.
class Scenario(object):
    def __init__(self, width, height, posx, posy, color):
        self.W = width
        self.H = height
        self.posx = posx
        self.posy = posy
        self.color = color
        self.masscenterx = self.posx + self.W/2
        self.masscentery = self.posy + self.H/2
        self.ActiveUP = False
        self.ActiveDOWN = False
        self.ActiveLEFT = False
        self.ActiveRIGHT = False
        self.distancex = 0
        self.distancey = 0
    def draw(self, background):
        if self.ActiveLEFT == True:
            color = (0, 255, 0)
        elif self.ActiveRIGHT == True:
            color = (0, 0, 255)
        elif self.ActiveDOWN == True:
            color = (0, 255, 255)
        elif self.ActiveUP == True:
            color = (0, 0, 0)
        else:
            color = self.color
        pygame.draw.rect(background, color,
                         (self.posx, self.posy, self.W, self.H))
        
def cls(screen, background):
    screen.blit(background, (0,0))
        
# Descobre objeto de uma lista que esta mais proximo de outro objeto      
def near(hero, scenelist):

    menorL = -1
    menorR = -1
    menorU = -1
    menorD = -1
    indexleft = 0
    indexright = 0
    indexup = 0
    indexdown = 0
    colisionlist = [0, 0, 0, 0]
    
    for i in xrange(1, scenelist[0]):
        obj = scenelist[i]
        distanciax = hero.masscenterx - obj.masscenterx
        distanciay = hero.masscentery - obj.masscentery

        #Verificando a Esquerda
        if distanciax > 0 and hero.posy + hero.H  > obj.posy and hero.posy < obj.posy + obj.H:
            if (distanciax < menorL and menorL > 0) or menorL < 0:
                indexleft = i
                menorL = distanciax

        #Verificando em cima
        if distanciay > 0 and hero.posx + hero.W > obj.posx and hero.posx < obj.posx + obj.W:
            if (distanciay < menorU and menorU > 0) or menorU < 0:
                indexup = i
                menorU = distanciay
            
        distanciax = obj.masscenterx - hero.masscenterx
        distanciay = obj.masscentery - hero.masscentery
        
        #Verificando a Direita
        if distanciax > 0 and hero.posy + hero.H  > obj.posy and hero.posy < obj.posy + obj.H:
            if (distanciax < menorR and menorR > 0) or menorR < 0:
                indexright = i
                menorR = distanciax

        #Verificando embaixo
        if distanciay > 0 and hero.posx + hero.W > obj.posx and hero.posx < obj.posx + obj.W:
            if (distanciay < menorD and menorD > 0) or menorD < 0:
                indexdown = i
                menorD = distanciay

        obj.ActiveLEFT = False
        obj.ActiveRIGHT = False
        obj.ActiveUP = False
        obj.ActiveDOWN = False
        obj.distancex = 0
        obj.distancey

    if indexleft != 0:
        scenelist[indexleft].ActiveLEFT = True
        scenelist[indexleft].distancex = hero.posx - (scenelist[indexleft].posx +
                                                     scenelist[indexleft].W)
        colisionlist[0] = scenelist[indexleft]
    else:
        colisionlist[0] = 0

    if indexright != 0:
        scenelist[indexright].ActiveRIGHT = True
        scenelist[indexright].distancex = scenelist[indexright].posx - (hero.posx +
                                                                      hero.W)
        colisionlist[1] = scenelist[indexright]
    else:
        colisionlist[1] = 0
        
    if indexup != 0:
        scenelist[indexup].ActiveUP = True
        scenelist[indexup].distancey = hero.posy - (scenelist[indexup].posy +
                                                     scenelist[indexup].H)
        colisionlist[2] = scenelist[indexup]
    else:
        colisionlist[2] = 0
        
    if indexdown != 0:
        scenelist[indexdown].ActiveDOWN = True
        scenelist[indexdown].distancey = scenelist[indexdown].posy - (hero.posy +
                                                                     hero.H)
        colisionlist[3] = scenelist[indexdown]
    else:
        colisionlist[3] = 0

    return colisionlist

def drawscene(scenelist, scenario):
    for i in xrange(1, scenelist[0]):
        scenelist[i].draw(scenario)

def game():

    fase = 1

    
    
    canjump1 = True
    canjump2 = True

    buildspeed = False

    lastdirection = 0 # 0 para parado, 1 para direita, -1 para esquerda

    scenario = pygame.Surface((W, H))
    pygame.draw.rect(scenario, (0, 120, 240),(0, 0, W, H))
    
    hero = Character()
    hero.color = (255, 0, 0)

    hero.posy = 400 - hero.H
    
    if fase == 1:
        floorleft = Scenario(350, H/3, 0, 400, (128,128,128))
        floorright = Scenario(350, H/3, 450, 400, (128,128,128))
        platform = Scenario(80, 40, 360, 250, (255,255,255))

        scenelist = [4, floorleft, floorright, platform]

        drawscene(scenelist, scenario)
        

    elif fase == 2:
        hero.posx = W/2
        hero.posy = 400 - hero.H
        floor = Scenario(W, H/3, 0, 400, (128,128,128))
        leftwall = Scenario(hero.W, H/3, 0, H/3, (0,255,0))
        rightwall = Scenario(hero.W, H/3, W - hero.W, H/3, (0,255,255))

        scenelist = [4, floor, leftwall, rightwall]

        drawscene(scenelist, scenario)
        
    elif fase == 3:
        floor = Scenario(W, H/3, 0, 2*H/3, (130, 130, 130))
        leftObst = Scenario (50, 100, 0, H/3, (255, 255, 255))
        rightObst = Scenario (50, 100, W-50, H/3, (255, 255, 255))
        topObst = Scenario (100, 50,  W/2-50, 0, (255, 255, 255))
        obj1 = Scenario (50, 50, 150, 2*H/3 - 50, (255, 255, 255))
        obj2 = Scenario (50, 50, 650, H/3 - 50, (255, 255, 255))
        obj3 = Scenario (100, 50, W/2-50, 150, (255, 255, 255))

        scenelist = [8, floor, leftObst, rightObst, topObst, obj1, obj2, obj3]

        drawscene(scenelist, scenario)
                 
    flag = 0
    flagg = 0


    while True:
        pygame.event.pump()

        pressed = pygame.key.get_pressed()

        colisionlist = near(hero, scenelist)
                                                            
        if pressed[K_UP]:
            if canjump1 == True and canjump2 == True:
                hero.jump()
                canjump1 = False
            canjump2 = False
        else:
            canjump2 = True                
                
        if pressed[K_DOWN]:
            hero.crouch()

        if pressed[K_LEFT]:
            if colisionlist[0] != 0:
                if hero.posx > colisionlist[0].posx + colisionlist[0].W:
                    if colisionlist[0].distancex < hero.xspeed and colisionlist[0].distancex > 0:
                        hero.xspeed = colisionlist[0].distancex
                    hero.left()
            else:
                hero.left()
                                                            
            lastdirection = -1
            buildspeed = True
                                                            
        elif pressed[K_RIGHT]:
            if colisionlist[1] != 0:
                if hero.posx < colisionlist[1].posx - hero.W:
                    if colisionlist[1].distancex < hero.xspeed and colisionlist[1].distancex > 0:
                        hero.xspeed = colisionlist[1].distancex
                    hero.right()
            else:
                hero.right()
            lastdirection = 1
            buildspeed = True
        else:
            buildspedd = False

        if buildspeed == True and hero.xspeed < hero.maxxspeed:
                hero.xspeed += 1
        elif hero.xspeed != hero.maxxspeed:
            hero.xspeed = hero.minxspeed
                
        if pressed[K_ESCAPE]:
            break

        if colisionlist[3] != 0:
            if colisionlist[3].distancey < hero.yspeed and colisionlist[3].distancey > 0:
                hero.yspeed = colisionlist[3].distancey + 1
        if colisionlist[2] != 0:
            if flagg == 0 and colisionlist[2].distancey < abs(hero.yspeed):
                for i in xrange (1,colisionlist[2].distancey):
                    if hero.posy == colisionlist[2].posy + colisionlist[2].H:
                        break
                    flagg = 1
                    hero.posy -= 1
                hero.yspeed = 0


        hero.fall()

        if colisionlist[3] != 0 and hero.posy >= colisionlist[3].posy - hero.H:
            hero.yspeed = 0
            canjump1 = True
            flagg = 0
        elif hero.yspeed < hero.maxyspeed:
            if flag == 1:
                hero.yspeed = 0
            hero.yspeed += 2
            canjump1 = False
            
        
            
        if hero.posy > W:
            hero.posy = -hero.H
        
        drawscene(scenelist, scenario)
      
        cls(screen, scenario)
        
        hero.updatemasscenter()

        hero.draw()
        pygame.display.flip()
        pygame.time.delay(0)

game()
pygame.quit()
                     
            
    
        
    


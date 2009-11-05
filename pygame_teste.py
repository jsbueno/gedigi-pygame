import pygame
from pygame.locals import *
from random import choice, randrange
import os

W, H = 640, 480
IMAGE_DIR= "images"

pygame.init()

tela = pygame.display.set_mode((W, H),
                               FULLSCREEN, 24)

cores = ["ffffff", "ff8000", "00ff00", "0080ff"]

def cor_hexa(cor):
    """
    Recebe uma string com 6 digitos hexa
    e devolve uma tripla de numeros RGB
    """
    tripla = cor[0:2], cor[2:4], cor[4:]
    nova_cor = []
    for componente  in tripla:
        nova_cor.append(int(componente, 16))
    return tuple(nova_cor)

def calc_color(color, size, column):
    new_color = []
    for component in color:
        new_color.append(int(component / 2.0
      + (component / 2.0) * (column / float(size))
                             ))
    return tuple(new_color)

def draw_square(surface, x, y, size, color):
    for column in range(size):
        new_color = calc_color(color, size, column)
        pygame.draw.rect(surface, new_color,
                         (x + column, y, 1, size))
                         
    
def draw_squares(spacing, size, colors, screen=tela):
    for i in range(0, W, spacing):
        for j in range(0, H, spacing):
            draw_square (screen, i, j, size, 
                             cor_hexa(choice(colors)))

class Character(object):
    def __init__(self):
        self.x = W / 2
        self.y = H / 2
        self.height = H / 6
        self.width = W / 6
        self.step = 16
        self.color = (128, 128 ,128)
        self.positions = ["00", "01"]
        self.load_images()
        self.current_position = self.positions[0]
        self.ticks = pygame.time.get_ticks()
        self.set_image()
        

         
    def load_images(self):
        self.images = {}
        
        basename = IMAGE_DIR + os.path.sep + "sticky_walk_right_%s.png"
        for position in self.positions:
            image = pygame.image.load(basename % position)
            self.images[position] = pygame.transform.scale(image, (self.width, self.height))
        
    def up(self):
        y = self.y - self.step
        if self.movement(self.x, y):
            self.y = y

    def down(self):
        y = self.y + self.step
        if self.movement(self.x, y):
            self.y = y

    def left(self):
        x = self.x - self.step
        if self.movement(x, self.y):
            self.x = x

    def right(self):
        x = self.x + self.step
        if self.movement(x, self.y):
            self.x = x
        
    def movement(self, x, y):
        can_move = self.verify_movement(x, y)
        if can_move:
            self.update_image()
        return can_move
    
    def verify_movement(self,x , y):
        ticks = pygame.time.get_ticks()
        if ticks - self.ticks < 160:
            return False
        self.ticks = ticks
        return True
    
    def draw(self):
        tela.blit(self.image, (self.x, self.y))
    
    def set_image(self):
        self.image = self.images[self.current_position]
    def update_image(self):
        p = self.positions.index (self.current_position) + 1
        if p == len(self.positions):
            p = 0
        self.current_position = self.positions[p]
        self.set_image()
        
        

def erase(screen, background):
    screen.blit(background, (0,0))

def game():
    background = pygame.Surface((W,H))
    draw_squares(32, 32, cores, background)
    character = Character()
    character.color = (0, 128, 0)
    erase(tela, background)
    while True:
        
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        if pressed[K_UP]:
            character.up()
        if pressed[K_DOWN]:
            character.down()
        if pressed[K_LEFT]:
            character.left()
        if pressed[K_RIGHT]:
            character.right()
        
        if pressed[K_ESCAPE]:
            break
        erase(tela, background)
        character.draw()
        pygame.display.flip()
        pygame.time.delay(40)

game()
pygame.quit()
    





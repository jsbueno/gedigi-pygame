import SimpleXMLRPCServer as XMLRPC
import xmlrpclib
import threading
import pygame
from pygame.locals import *
import sys

PORT = 2000

class GameOver(Exception):
    pass

class Character(object):
    def __init__(self, movementer):
        self.movementer = movementer
        
    def update(self):
        self.rect = self.movementer.rect
        
class Movementer(object):
    def __init__(self, rect=(0,0,50,50), client=False, server=""):
        self.rect = pygame.Rect(rect)
        if not client:
            self.start_server()
        else:
            self.proxy = xmlrpclib.ServerProxy(server)
            self.server = None
    def start_server(self):
        server = XMLRPC.SimpleXMLRPCServer(("0.0.0.0", PORT))
        server.register_function(self.get_rect_real)
        self.server_thread = threading.Thread()
        self.server_thread.run = server.serve_forever
        self.server = server
        self.server_thread.start()
    
    def get_rect(self):
        if self.server:
            return self.get_rect_real()
        return self.proxy.get_rect_real()
    
    def get_rect_real(self):
        return self.rect[0:4]

    def keyboard_input(self):
        if not self.server:
            return
        x, y = self.rect.topleft
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            x += 10
        if keys[K_LEFT]:
            x -= 10
        if keys[K_DOWN]:
            y += 10
        if keys[K_UP]:
            y -= 10
        if keys[K_ESCAPE]:
            self.server.server_close()
            raise GameOver
        self.rect.topleft = x,y
def init():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((400,400))

def mainloop():
    pygame.event.pump()
    m.keyboard_input()
    pygame.draw.rect(SCREEN, (255,0,0), m.get_rect())
    pygame.display.flip()
    pygame.time.delay(30)

if __name__ == "__main__":
    init()
    if len(sys.argv) == 1:
        m = Movementer()
    else:
        m = Movementer(client=True, server=sys.argv[1] + ":%d" % PORT)
    try:
        while True:
            mainloop()
    except GameOver:
            pass
    finally:
        pygame.quit()
    
        
import pygame
import events

class Game(events.Dispatcher):
    def __init__(self, size = (680, 400), rate = 25, flags = 0):
        """
        The base class for a game.
        @size: a tuple containing the resolution of the game, (w, h).
        @rate: the frame rate of the game.
        """
        events.Dispatcher.__init__(self)
        self.size = size
        self.rate = rate
        self._screen = pygame.display.set_mode(size, flags);
        self.addEvent(pygame.QUIT, lambda e: e.target.quit());

    def main(self):
        """
        Starts the game!
        """
        T = 1000 / self.rate
        clock = pygame.time.Clock()
        try:
            while True:
                for evt in pygame.event.get():
                    self.dispatch(events.Event(evt.type, self, evt))
                self.dispatch(events.Event("draw", self, self._screen))
                pygame.display.flip()
                clock.tick(T)
        except events.GameQuit:
            pass

    def quit(self):
        raise events.GameQuit()

import framework

class Game(framework.Game):
    def __init__(self):
        framework.Game.__init__(self)

if __name__ == "__main__":
	game = Game()
	game.main()

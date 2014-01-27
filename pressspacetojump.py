import pygame

from screens import StartScreen

class PressSpaceToJump():
    def __init__(self):
        ## Useful numbers and variables
        self.WORLD_HEIGHT = 200
        self.WORLD_WIDTH = 800
        self.offset = 50
        self.points = 0

        self.rate_create = 0
        
        ## Colors
        self.bg_color = pygame.Color(50, 87, 116)
        self.obs_color = pygame.Color(242, 224, 236)
        self.text_color = pygame.Color(242, 224, 236)

        ## Setup pygame
        pygame.init()

        self.display = pygame.display
        self.window = self.display.set_mode((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.display.set_caption('Press Space To Jump')
        pygame.mixer.music.load('music.ogg')
        pygame.mixer.music.play(-1)

        self.font = pygame.font.Font('fast99.ttf', 16)
        self.fps_clock = pygame.time.Clock()
        self.screen = StartScreen(self.window, self)
                
    ## Main Game
    def main(self):
        while True:
            self.screen.process()
            self.screen.render()

if(__name__ == '__main__'):
    PressSpaceToJump().main()

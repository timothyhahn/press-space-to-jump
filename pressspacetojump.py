import sys
import pygame
import random
import time

from pygame.locals import *
from components import Position, Velocity, Bounds

def valueInRange(value, min, max):
        return (value >= min) and (value <= max)

class PressSpaceToJump():
    def __init__(self):
        ## Useful numbers and variables
        self.WORLD_HEIGHT = 200
        self.WORLD_WIDTH = 800
        self.OFFSET = 50
        self.JUMP_LIMIT = 90
        self.UPWARDS = 20
        self.DOWNWARDS = -10

        self.gameRunning = True
        self.jumpCounter = 2
        self.killCounter = 0
        self.rateCreate = 1
        self.tipsy = True
        self.tipsyLeft = True
        
        ## Colors
        self.bgColor = pygame.Color(50, 87, 116)
        self.obsColor = pygame.Color(242, 224, 236)

        ## Setup pygame
        pygame.init()

        self.window = pygame.display.set_mode((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        pygame.display.set_caption('Press Space To Jump')
        pygame.mixer.music.load('music.ogg')
        pygame.mixer.music.play(-1)

        self.sounds = dict()
        self.sounds['jump'] = pygame.mixer.Sound('jump.ogg')
        self.sounds['jump2'] = pygame.mixer.Sound('jump2.ogg')
        self.sounds['hit'] = pygame.mixer.Sound('hit.ogg')

        self.font = pygame.font.Font('fast99.ttf', 16)
        self.fpsClock = pygame.time.Clock()

        # Pseudo ecs
        ## Create you
        self.you = dict()
        self.you['position'] = Position()
        self.you['velocity'] = Velocity(x = 5)
        self.you['bounds'] = Bounds(30, 30)
        self.you['health'] = 10
        self.you['color'] = pygame.Color(141, 59, 61)

        ## Create list of obstacles
        self.obs = list()

    ## Creates obstacles
    def create_obs(self, position):
        ob = dict()
        ob['position'] = position
        ob['velocity'] = Velocity()
        ob['bounds'] = Bounds(random.randint(5,40),random.randint(5, 50))
        ob['health'] = 1
        ob['color'] = self.obsColor
        return ob


    ## Handles keys
    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
        if self.gameRunning:
            if event.type == KEYDOWN:
                if event.key == (K_SPACE) and self.jumpCounter > 0:
                    self.jumpCounter -= 1
                    self.you['velocity'].y = self.UPWARDS
                    self.you['velocity'].x = 3
                    if self.jumpCounter == 1:
                        self.sounds['jump'].play()
                    else:
                        self.sounds['jump2'].play()
            elif event.type == KEYUP:
                if event.key == (K_SPACE):
                    self.you['velocity'].y = self.DOWNWARDS

    ## Check if collision occurs 
    def does_collide(self, you, obstacle):
        xOverlap = valueInRange(you['position'].x, obstacle['position'].x, obstacle['position'].x + obstacle['bounds'].x) \
                or valueInRange(obstacle['position'].x, you['position'].x, you['position'].x + you['bounds'].x)
        yOverlap = valueInRange(you['position'].y, obstacle['position'].y, obstacle['position'].y + obstacle['bounds'].y) \
                or valueInRange(obstacle['position'].y, you['position'].y, you['position'].y + you['bounds'].y)
        return xOverlap and yOverlap

    ## Checks if within distance either in front or behind you
    def does_near(self, you, obstacle, distance):
        newYou = dict()
        newYou['position'] = Position(you['position'].x - distance, you['position'].y - distance)
        newYou['bounds'] = Bounds(you['bounds'].x + (distance * 2), you['bounds'].y + (distance * 2))
        return self.does_collide(newYou, obstacle)

    ## Game Logic
    def process(self):
        ## Handle Movement
        self.you['position'].x += self.you['velocity'].x
        self.you['position'].y += self.you['velocity'].y

        if self.you['position'].y <= 0:
            self.you['position'].y = 0
            self.you['velocity'].y = 0
            self.you['velocity'].x = 1
            self.jumpCounter = 2
        elif self.you['position'].y >= self.JUMP_LIMIT:
            self.you['velocity'].y = self.DOWNWARDS

        ## Handle Collision
        for ob in self.obs:
            if self.does_collide(self.you, ob):
                self.you['health'] -= 1
                ob['health'] -= 1
                self.sounds['hit'].play()

        ## Handle Creation
        if random.randint(0, 100) < self.rateCreate: ## Rate of Creation
            y = 0
            if random.randint(0, 4) < 1: ## Create one that is "up" that you duck under
                y = self.you['bounds'].y + random.randint(5, 65)

            randomPosition = Position(self.you['position'].x + random.randint(self.WORLD_WIDTH, self.WORLD_WIDTH + 100), y)
            possibleOb = self.create_obs(randomPosition)

            collisions = filter(None, (self.does_near(possibleOb, ob, 100) for ob in self.obs))
            if not collisions:
                self.obs.append(possibleOb)

        ## Kill things off screen
        if(self.killCounter > 30):
            limit = self.you['position'].x - self.OFFSET - 50
            newObs = filter(lambda ob:ob['position'].x > limit, self.obs)
            if newObs != self.obs:
                self.obs = newObs
            self.killCounter = 0
        self.killCounter += 1

        ## Kill unhealthy things
        if self.you['health'] < 1:
            self.gameRunning = False

        newObs = filter(lambda ob: ob['health'] > 0, self.obs)
        if newObs != self.obs:
            self.obs = newObs

        ## "Bonuses"
        if 0 <= self.you['position'].x  < 10000:
            self.rateCreate = 6
            self.you['velocity'].x = 8
        elif 10000 <= self.you['position'].x  < 50000:
            self.rateCreate = 8
            self.you['velocity'].x = 13
        elif 50000 < self.you['position'].x < 100000:
            self.rateCreate = 14
            self.you['velocity'].x = 19
        elif 100000 < self.you['position'].x:
            self.rateCreate = 18
            self.you['velocity'].x = 25


        if self.tipsy:
            if self.OFFSET > 5:
                if self.OFFSET < 300:
                    if random.randint(1, 10) < 3:
                        self.tipsyLeft = not self.tipsyLeft

                    if self.tipsyLeft:
                        self.OFFSET -= random.randint(1, 3)
                    else:
                        self.OFFSET += random.randint(1, 3)
                else: 
                    self.OFFSET -= random.randint(3,5)
                    self.tipsyLeft = True
            else:
                self.OFFSET += random.randint(3,5)
                self.tipsyLeft = False
        
    ## Renders a specific object
    def render_object(self, color, p, b, rotate=False):
        y = self.WORLD_HEIGHT - p.y - b.y
        rect = pygame.Rect(p.x, y, b.x, b.y)
        if rotate: ## If the object rotates, we have to blit it onto another surface and rotate that first
            surf = pygame.Surface((30, 30))
            surf.fill(self.you['color'])
            surf.set_colorkey((255, 0 , 0))
            pygame.draw.rect(surf, color, rect)
            degree = 0
            if self.you['velocity'].y > 0:
                degree = -p.y
            else:
                degree = -180 + p.y
            rotatedSurf = pygame.transform.rotate(surf, degree)
            rotatedRect = rotatedSurf.get_rect()
            rotatedRect.center = rect.center
            self.window.blit(rotatedSurf, rotatedRect)
        else:
            pygame.draw.rect(self.window, color, rect)

    ## Render Logic
    def render(self):
        # Render you
        relativePos = Position(self.OFFSET, self.you['position'].y)
        self.render_object(self.you['color'], relativePos, self.you['bounds'], True)

        # Render obs
        for ob in self.obs:
            oRelativePos = Position(self.OFFSET + (ob['position'].x - self.you['position'].x), ob['position'].y)
            self.render_object(ob['color'], oRelativePos, ob['bounds'])

        # Render UI
        ## Render Health
        healthSurface = self.font.render('Health: ' + str(self.you['health']), False, self.obsColor)
        healthRect = healthSurface.get_rect()
        healthRect.topleft = (700, 20)
        self.window.blit(healthSurface, healthRect)

        ## Render Score
        scoreSurface = self.font.render('Score: ' + str(self.you['position'].x), False, self.obsColor)
        scoreRect = scoreSurface.get_rect()
        scoreRect.topleft = (10, 20)
        self.window.blit(scoreSurface, scoreRect)

    ## Main Game
    def main(self):
        ## Starting Countdown
        for second in range(3, 0, -1):
            self.window.fill(self.bgColor)
            startSurface = self.font.render('Press Space To Jump', False, self.obsColor)
            startRect = startSurface.get_rect()
            startRect.center = (self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2 - 10)
            self.window.blit(startSurface, startRect)

            startSurface = self.font.render(str('Game will start in %s seconds' % second), False, self.obsColor)
            startRect = startSurface.get_rect()
            startRect.center = (self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2 + 10)
            self.window.blit(startSurface, startRect)
            for event in pygame.event.get():
                self.handle_event(event)

            pygame.display.update()
            time.sleep(1)

        ## Actual Game
        while self.gameRunning:
            self.window.fill(self.bgColor)
            for event in pygame.event.get():
                self.handle_event(event)
            self.process()
            self.render()
            pygame.display.update()
            self.fpsClock.tick(30)

        ## GameOver
        for _ in range(5, 0, -1):
            self.window.fill(self.bgColor)
            gameOverSurface = self.font.render(str("You Lose With %s Points" % (self.you['position'].x)), False, self.obsColor)
            gameOverRect = gameOverSurface.get_rect()
            gameOverRect.center = (self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2)
            self.window.blit(gameOverSurface, gameOverRect)
            for event in pygame.event.get():
                self.handle_event(event)

            pygame.display.update()
            time.sleep(1)

        ## Restart
        self.__init__()
        self.main()


if(__name__ == '__main__'):
    PressSpaceToJump().main()

import sys
import time

from pygame.locals import *
import pygame
from abc import abstractmethod, ABCMeta
from rui.rui import World

from components import Position, Velocity, Bounds, Jump, Health, Sound, Render
from systems import MovementSystem, JumpSystem, CollisionSystem, SoundSystem, CreateSystem, KillSystem, RenderSystem, BonusSystem

class Screen(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, window, game):
        self.window = window
        self.game = game

    @abstractmethod
    def process(self):
        '''Processes any logic'''

    @abstractmethod
    def render(self):
        '''Renders screen'''

class StartScreen(Screen):
    def __init__(self, window, game):
        super(StartScreen, self).__init__(window, game)
        self.counter = 3

    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

    def process(self):
        if self.counter < 0:
            self.game.screen=GameScreen(self.window, self.game)

        time.sleep(1)
        for event in pygame.event.get():
                self.handle_event(event)

    def render(self):
        self.window.fill(self.game.bg_color)
        start_surface = self.game.font.render('Press Space To Jump', False, self.game.text_color)
        start_rect = start_surface.get_rect()
        start_rect.center = (self.game.WORLD_WIDTH / 2, self.game.WORLD_HEIGHT / 2 - 10)
        self.window.blit(start_surface, start_rect)

        start_surface = self.game.font.render(str('Game will start in %s seconds' % self.counter), False, self.game.text_color)
        start_rect = start_surface.get_rect()
        start_rect.center = (self.game.WORLD_WIDTH / 2, self.game.WORLD_HEIGHT / 2 + 10)
        self.window.blit(start_surface, start_rect)
        self.game.display.update()
        self.counter -= 1


class EndScreen(Screen):
    def __init__(self, window, game):
        super(EndScreen, self).__init__(window, game)
        self.counter = 5

    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

    def process(self):
        if self.counter <= 0:
            self.game.screen = StartScreen(self.window, self.game)

        time.sleep(1)
        self.counter -= 1
        for event in pygame.event.get():
                self.handle_event(event)

    def render(self):
        self.window.fill(self.game.bg_color)
        game_over_surface = self.game.font.render(str('You Lose with %s Points' % (self.game.points)), False, self.game.text_color)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.center = (self.game.WORLD_WIDTH / 2, self.game.WORLD_HEIGHT / 2)
        self.window.blit(game_over_surface, game_over_rect)
        self.game.display.update()

class GameScreen(Screen):
    def __init__(self, window, game):
        super(GameScreen, self).__init__(window, game)
        
        ## Create World
        self.world = World()

        ## Create Sound Componen
        sound_component = Sound()
        sound_component.add_sound('jump', pygame.mixer.Sound('jump.ogg'))
        sound_component.add_sound('jump2', pygame.mixer.Sound('jump2.ogg'))
        sound_component.add_sound('hit', pygame.mixer.Sound('hit.ogg'))

        ## Create You
        you = self.world.create_entity('YOU')
        you.add_component(Position())
        you.add_component(Velocity(x=5))
        you.add_component(Bounds(30, 30))
        you.add_component(Health(10))
        you.add_component(Render(pygame.Color(141, 59, 61), True))
        you.add_component(sound_component)
        you.add_component(Jump())

        self.world.add_entity(you)

        ## Add Systems
        self.world.add_system(MovementSystem())
        self.world.add_system(JumpSystem())
        self.world.add_system(CollisionSystem())
        self.world.add_system(SoundSystem())
        self.world.add_system(CreateSystem(self.game))
        self.world.add_system(KillSystem(self.game))
        self.world.add_system(BonusSystem(self.game))
        self.world.add_system(RenderSystem(self.window, self.game))

        self.game.points = 0
    
    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

        you = self.world.get_entity_by_tag('YOU')
        velocity = you.get_component(Velocity)
        sound = you.get_component(Sound)
        jump = you.get_component(Jump)
        if event.type == KEYDOWN:
            if event.key == (K_SPACE) and jump.count > 0:
                jump.count -= 1
                velocity.y = 20
                velocity.x = 3
                if jump.count == 1:
                    sound.trigger_sound('jump')
                else:
                    sound.trigger_sound('jump2')
        elif event.type == KEYUP:
            if event.key == (K_SPACE):
                velocity.y = -10

    def process(self):
        self.world.process()

        you = self.world.get_entity_by_tag('YOU')
        ## Update points
        self.game.points = you.get_component(Position).x

        ## If you are dead, die
        health = you.get_component(Health)
        if health.value <= 0:
            self.game.screen = EndScreen(self.window, self.game)
        
        ## Handle events
        for event in pygame.event.get():
                self.handle_event(event)

        

    def render(self):
        # Render UI
        ## Render Health
        you = self.world.get_entity_by_tag('YOU')
        health = you.get_component(Health)
        health_surface = self.game.font.render('Health: ' + str(health.value), False, self.game.text_color)
        health_rect = health_surface.get_rect()
        health_rect.topleft = (700, 20)
        self.window.blit(health_surface, health_rect)

        ## Render Score
        score_surface = self.game.font.render('Score: ' + str(self.game.points), False, self.game.text_color)
        score_rect = score_surface.get_rect()
        score_rect.topleft = (10, 20)
        self.window.blit(score_surface, score_rect)
        self.game.display.update()
        self.game.fps_clock.tick(30)


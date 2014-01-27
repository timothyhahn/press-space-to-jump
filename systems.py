import random
import pygame
from rui.rui import Entity, System
from components import Position, Velocity, Jump, Bounds, Health, Render, Sound
from helpers import does_collide, does_near


class MovementSystem(System):
    def process(self, delta):
        entities = self.world.get_entities_by_components(Position, Velocity)
        for entity in entities:
            position = entity.get_component(Position)
            velocity = entity.get_component(Velocity)
            position.x += velocity.x * delta
            position.y += velocity.y * delta

        you = self.world.get_entity_by_tag('YOU')
        position = you.get_component(Position)
        velocity = you.get_component(Velocity)


class JumpSystem(System):
    def process(self, delta):
        entities = self.world.get_entities_by_components(Position, Velocity, Jump)
        for entity in entities:
            position = entity.get_component(Position)
            velocity = entity.get_component(Velocity)
            jump = entity.get_component(Jump)

            if position.y <= 0:
                position.y = 0
                velocity.y = 0
                velocity.x = 1
                jump.count = 2
            elif position.y >= 90:
                velocity.y = -10

class CollisionSystem(System):
    def process(self, delta):
        obs = self.world.get_group('OBS')
        you = self.world.get_entity_by_tag('YOU')
        for ob in obs:
            if does_collide(you, ob):
                you.get_component(Health).value -= 1
                ob.get_component(Health).value -= 1
                you.get_component(Sound).trigger_sound('hit')

class SoundSystem(System):
    def process(self, delta):
        entities = self.world.get_entities_by_components(Sound)
        for entity in entities:
            sound = entity.get_component(Sound)
            for key in sound.sounds.keys():
                if sound.triggers[key]:
                    sound.play_sound(key)

class CreateSystem(System):
    def __init__(self, game):
        self.game = game

    def create_obs(self, position):
        ob = Entity()
        ob.add_component(position)
        ob.add_component(Velocity())
        ob.add_component(Bounds(random.randint(5,40),random.randint(5, 50)))
        ob.add_component(Health(1))
        ob.add_component(Render(self.game.obs_color))
        return ob

    def process(self, delta):
        ## Handle Creation
        if random.randint(0, 100) < self.game.rate_create: ## Rate of Creation
            y = 0
            you = self.world.get_entity_by_tag('YOU')
            if random.randint(0, 4) < 1: ## Create one that is "up" that you duck under
                y = you.get_component(Bounds).y + random.randint(5, 65)

            random_position = Position(you.get_component(Position).x + random.randint(self.game.WORLD_WIDTH, self.game.WORLD_WIDTH + 100), y)
            possible_ob = self.create_obs(random_position)

            collisions = filter(None, (does_near(possible_ob, ob, 100) for ob in self.world.get_group('OBS')))
            if not collisions:
                self.world.add_entity(possible_ob)
                self.world.register_entity_to_group(possible_ob, 'OBS')


class KillSystem(System):
    def __init__(self, game):
        self.counter = 0
        self.game = game

    def process(self, delta):
        entities = self.world.get_group('OBS')
        for entity in entities:
            if entity.get_component(Health).value <= 0:
                entity.kill()

        if (self.counter > 30):
            limit = self.world.get_entity_by_tag('YOU').get_component(Position).x - self.game.offset - 50
            dead_obs = filter(lambda ob: ob.get_component(Position).x < limit, entities)
            map(lambda entity: entity.kill(), dead_obs)
            self.counter = 0

        self.counter+= 1


class BonusSystem(System):
    def __init__(self, game, tipsy=True):
        self.game = game
        self.tipsy = tipsy
        self.tipsy_left = True

    def process(self, delta):
        ## "Bonuses"
        you = self.world.get_entity_by_tag('YOU')

        if 0 <= self.game.points  < 10000:
            self.game.rate_create = 8
            you.get_component(Velocity).x = 10
        elif 10000 <= self.game.points  < 50000:
            self.game.rate_create = 10
            you.get_component(Velocity).x = 15
        elif 50000 < self.game.points < 100000:
            self.game.rate_create = 12
            you.get_component(Velocity).x = 20
        elif 100000 < self.game.points:
            self.game.rate_reate = 15
            you.get_component(Velocity).x = 10

        if self.tipsy:
            if self.game.offset > 5:
                if self.game.offset < 300:
                    if random.randint(1, 10) < 3:
                        self.tipsy_left = not self.tipsy_left

                    if self.tipsy_left:
                        self.game.offset -= random.randint(1, 3)
                    else:
                        self.game.offset += random.randint(1, 3)
                else: 
                    self.game.offset -= random.randint(3,5)
                    self.tipsy_left = True
            else:
                self.game.offset += random.randint(3,5)
                self.tipsy_left = False

class RenderSystem(System):
    def __init__(self, window, game):
        self.window = window
        self.game = game

    ## Renders a specific object
    def render_object(self, color, p, b, rotate=False):
        y = self.game.WORLD_HEIGHT - p.y - b.y
        rect = pygame.Rect(p.x, y, b.x, b.y)
        surf = pygame.Surface((30, 30))
        surf.fill(color)
        pygame.draw.rect(surf, color, rect)

        if rotate: ## If the object rotates, we have to blit it onto another surface and rotate that first
            surf.set_colorkey((255, 0 , 0))
            pygame.draw.rect(surf, color, rect)
            degree = 0
            you = self.world.get_entity_by_tag('YOU')
            if you.get_component(Velocity).y > 0:
                degree = -p.y
            else:
                degree = -180 + p.y
            rotated_surf = pygame.transform.rotate(surf, degree)
            rotated_rect = rotated_surf.get_rect()
            rotated_rect.center = rect.center
            self.window.blit(rotated_surf, rotated_rect)
        else:
            pygame.draw.rect(self.window, color, rect)


    def process(self, delta):
        self.window.fill(self.game.bg_color)
        entities = self.world.get_entities_by_components(Position, Bounds, Render)
        for entity in entities:
            render = entity.get_component(Render)
            position = entity.get_component(Position)
            bounds = entity.get_component(Bounds)
            if entity.get_tag() == 'YOU':
                position = Position(self.game.offset, position.y)
            else:
                you = self.world.get_entity_by_tag('YOU')
                y_pos = you.get_component(Position)
                position = Position(self.game.offset + (position.x - y_pos.x), position.y)
            self.render_object(render.color, position, bounds, render.rotate)

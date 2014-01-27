from rui.rui import Entity
from components import Position, Bounds

def value_in_range(value, min, max):
    return value >= min and value <= max

def does_collide(you, obstacle):
    you_position = you.get_component(Position)
    you_bounds = you.get_component(Bounds)
    ob_position = obstacle.get_component(Position)
    ob_bounds = obstacle.get_component(Bounds)

    xOverlap = value_in_range(you_position.x, ob_position.x, ob_position.x + ob_bounds.x)\
            or value_in_range(ob_position.x, you_position.x, you_position.x + you_bounds.x)
    yOverlap = value_in_range(you_position.y, ob_position.y, ob_position.y + ob_bounds.y)\
            or value_in_range(ob_position.y, you_position.y, you_position.y + you_bounds.y)
    return xOverlap and yOverlap

def does_near(you, obstacle, distance):
    new_you = Entity()
    you_position = you.get_component(Position)
    you_bounds = you.get_component(Bounds)
    new_you.add_component(Position(you_position.x - distance, you_position.y - distance))
    new_you.add_component(Bounds(you_bounds.x + (distance * 2), you_bounds.y + (distance * 2)))
    return does_collide(new_you, obstacle)

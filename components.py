from rui.rui import Component

class Position(Component):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return 'x: %s, y: %s' % (self.x, self.y)


class Velocity(Component):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return 'x: %s, y: %s' % (self.x, self.y)

class Bounds(Component):
    def __init__(self, x = 5, y =  5):
        self.x = x
        self.y = y
    def __str__(self):
        return 'x: %s, y: %s' % (self.x, self.y)


class Jump(Component):
    def __init__(self, count = 2):
        self.count = count

    def __str__(self):
        return 'Jump Count: %s' % (self.count)


class Health(Component):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'health at: %s' % (self.health)


class Sound(Component):
    def __init__(self):
        self.sounds = dict()
        self.triggers = dict()

    def add_sound(self, name, sound, triggered=False):
        self.sounds[name] = sound
        self.triggers[name] = triggered

    def trigger_sound(self, name):
        self.triggers[name] = True

    def play_sound(self, name):
        self.sounds[name].play()
        self.triggers[name] = False

    def __str__(self):
        return 'Sound is %s' % (self.sound)


class Render(Component):
    def __init__(self, color, rotate=False):
        self.color = color
        self.rotate = rotate

    def __str__(self):
        return 'Color is: %s' % (self.color)


class Position:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: %s, y: %s" % (self.x, self.y)

class Velocity:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: %s, y: %s" % (self.x, self.y)

class Bounds:
    def __init__(self, x = 5, y =  5):
        self.x = x
        self.y = y
    def __str__(self):
        return "x: %s, y: %s" % (self.x, self.y)



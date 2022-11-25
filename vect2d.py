class vect2d:
    def __init__(self, x=-1, y=-1, angle=0):
        self.x = x #х координата
        self.y = y #у координата
        self.angle = angle

    #задать вектор
    def co(self, x,y):
        self.x = x
        self.y = y

    #получить вектор
    def getCo(self):
        return (self.x, self.y)

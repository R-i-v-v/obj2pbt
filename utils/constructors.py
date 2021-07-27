from math import sqrt, pi

d2r = pi / 180

def circle_intersection(circle1, circle2):
    '''
    @summary: calculates intersection points of two circles
    @param circle1: tuple(x,y,radius)
    @param circle2: tuple(x,y,radius)
    @result: tuple of intersection points (which are (x,y) tuple)
    '''
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2
    dx, dy = x2 - x1, y2 - y1
    d = sqrt(dx * dx + dy * dy)
    if d > r1 + r2:
        print("#1")
        return None  # no solutions, the circles are separate
    if d < abs(r1 - r2):
        print("#2")
        return None  # no solutions because one circle is contained within the other
    if d == 0 and r1 == r2:
        print("#3")
        return None  # circles are coincident and there are an infinite number of solutions

    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = sqrt(r1 * r1 - a * a)
    xm = x1 + a * dx / d
    ym = y1 + a * dy / d
    xs1 = xm + h * dy / d
    xs2 = xm - h * dy / d
    ys1 = ym - h * dx / d
    ys2 = ym + h * dx / d

    return (xs1, ys1), (xs2, ys2)


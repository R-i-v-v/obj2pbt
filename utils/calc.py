import numpy as np
from scipy.spatial.transform import Rotation as R


class Shape:  # shape class that makes returning a bit easier
    def __init__(self, position, scale, rotation, type):
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.type = type


# Original function given by Waffle and revised/commented by Zanth. See docs for details
def triangle(a, b, c, should_optimize):
    ab, ac, bc = np.subtract(b, a), np.subtract(c, a), np.subtract(c, b)  # vectors between the points

    # by comparing the lengths of the sides, we can determine the largest angle
    # remember: we want angle c to be the largest
    len_ab, len_ac, len_bc = np.linalg.norm(ab), np.linalg.norm(ac), np.linalg.norm(bc)

    # if angle a is the largest, swap c and a
    if len_bc > len_ab and len_bc > len_ac:
        c, a = a, c
        bc, ab = -ab, -bc
        len_bc, len_ab = len_ab, len_bc
        ac = -ac

    # if angle b is the largest, swap c and b
    elif len_ac > len_ab and len_ac > len_bc:
        c, b = b, c
        ac, ab = ab, ac
        len_ac, len_ab = len_ab, len_ac
        bc = -bc

    # if angle c is the largest, or there is an equilateral triangle...
    else:
        pass

    # calculates angle c to test if it's a right triangle
    ac_unit = np.divide(ac, np.linalg.norm(ac))
    bc_unit = np.divide(bc, np.linalg.norm(bc))
    dot_product = np.dot(ac_unit, bc_unit)
    angle_c = np.arccos(dot_product)

    if should_optimize:  # the following block of code runs only if 'optimize' checkbox is checked
        # angle c is a right angle if and only if the triangle is a right triangle
        if angle_c == np.pi / 2:

            # position calculation - our triangles are wedges, so position is the midpoint of the length surface
            position = np.divide(np.add(a, c), 2)

            # scale calculation
            scale = np.divide([0.02, len_ac, len_bc], 100)

            # rotation calculation
            z = -bc_unit                            # z is the unit vector of -bc (-bc hat). Length vector of triangle
            y = -ac_unit                            # y is the unit vector of -ac (-ac hat). Width vector of triangle
            x = np.cross(y, z)                      # x is the cross product of x and y
            matrix = np.transpose([-x, -y, z])      # matrix is the rotation matrix of the triangle
            rotation = R.from_matrix(matrix).as_euler('xyz', degrees=True) * [-1, -1, 1]
            right_triangle = Shape(position, scale, rotation, "sm_wedge_001")
            return [right_triangle]

        # isosceles check isn't ready yet
        # elif len_ab == len_ac or len_ab == len_bc or len_bc == len_ac:  # isosceles triangle check
        #     # isosceles prism position calculation
        #     r = 0
        #     position = [(a[0] + b[0] + c[0])/3, (a[1] + b[1] + c[1])/3, (a[2] + b[2] + c[2])/3 + r]
        #     return

    z = np.divide(ab, len_ab)               # z is the unit vector of ab, aka ab hat
    l1 = np.multiply(np.dot(ac, z), z)      # l1 is the length vector of triangle_0
    l2 = np.subtract(l1, ab)                # l2 is the length vector of triangle_1
    p = np.subtract(ac, l1)                 # p is the width vector. This is the vector that splits the two triangles
    width = np.linalg.norm(p)               # width is the magnitude of p. It is the length of the shared side

    y = np.divide(p, width)                 # y is the unit vector of p, aka p hat
    x = np.cross(y, z)                      # x is the cross product of y and z

    # position calculation - our triangles are wedges, so position is the midpoint of the surface between the triangles
    o = np.add(a, l1)                       # o is the splitting point of ab
    r = np.multiply(x, 0.0002)              # r is the depth vector
    position_1 = position_2 = np.divide(np.add(c, np.add(o, r)), 2)

    # scale calculation
    scale_1, scale_2 = np.divide([0.002, width, np.linalg.norm(l1)], 100), np.divide([0.002, width, np.linalg.norm(l2)], 100)

    # Rotation calculation
    matrix_1, matrix_2 = np.transpose([x, -y, -z]), np.transpose([-x, -y, z])
    rotation_1, rotation_2 = R.from_matrix(matrix_1).as_euler('xyz', degrees=True) * [-1, -1, 1], \
                             R.from_matrix(matrix_2).as_euler('xyz', degrees=True) * [-1, -1, 1]

    first_split = Shape(position_1, scale_1, rotation_1, "sm_wedge_001")
    second_split = Shape(position_2, scale_2, rotation_2, "sm_wedge_001")
    return [first_split, second_split]
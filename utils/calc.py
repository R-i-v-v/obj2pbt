import numpy as np
from scipy.spatial.transform import Rotation as R

# Function given by Waffle and revised/commented by Zanth. See docs for details
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

    # if angle c is a right angle if and only if the triangle is a right triangle
    if angle_c == np.pi / 2 and should_optimize:

        # position calculation - our triangles are corner-aligned wedges, so position is where the right angle occurs
        # which is always point c in our program
        position = np.divide(np.add(a, c), 2)

        # scale calculation
        scale = np.divide([0.02, len_ac, len_bc], 100)

        # rotation calculation
        z = -bc_unit                            # z is the unit vector of -bc, aka -bc hat. Length vector of triangle
        y = -ac_unit                            # y is the unit vector of -ac, aka -ac hat. Width vector of triangle
        x = np.cross(y, z)                      # x is the cross product of x and y
        matrix = np.transpose([-x, -y, z])      # matrix is the rotation matrix of the triangle
        rotation = R.from_matrix(matrix).as_euler('xyz', degrees=True) * [-1, -1, 1]

        return position, None, scale, None, rotation, None

    z = np.divide(ab, len_ab)               # z is the unit vector of ab, aka ab hat
    l1 = np.multiply(np.dot(ac, z), z)      # l1 is the length vector of triangle_0
    l2 = np.subtract(l1, ab)                # l2 is the length vector of triangle_1
    p = np.subtract(ac, l1)                 # p is the width vector. This is the vector that splits the two triangles
    width = np.linalg.norm(p)               # width is the magnitude of p. It is the length of the shared side

    y = np.divide(p, width)                 # y is the unit vector of p, aka p hat
    x = np.cross(y, z)                      # x is the cross product of y and z

    # position calculation - our triangles are corner-aligned wedges, so position is where the right angle occurs
    # which is the same for both triangles, since they share the point where their right angles occur
    o = np.add(a, l1)
    r = np.multiply(x, 0.0002)
    position_1 = position_2 = np.divide(np.add(c, np.add(o, r)), 2)

    # scale calculation
    scale_1, scale_2 = np.divide([0.002, width, np.linalg.norm(l1)], 100), np.divide([0.002, width, np.linalg.norm(l2)], 100)

    # Rotation calculation
    matrix_1, matrix_2 = np.transpose([x, -y, -z]), np.transpose([-x, -y, z])
    rotation_1, rotation_2 = R.from_matrix(matrix_1).as_euler('xyz', degrees=True) * [-1, -1, 1], \
                             R.from_matrix(matrix_2).as_euler('xyz', degrees=True) * [-1, -1, 1]

    return position_1, position_2, scale_1, scale_2, rotation_1, rotation_2
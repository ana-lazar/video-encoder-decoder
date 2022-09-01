import math

ZIG_ZAG_ORDER = [0, 1, 8, 16, 9, 2, 3, 10,
                 17, 24, 32, 25, 18, 11, 4, 5,
                 12, 19, 26, 33, 40, 48, 41, 34,
                 27, 20, 13, 6, 7, 14, 21, 28,
                 35, 42, 49, 56, 57, 50, 43, 36,
                 29, 22, 15, 23, 30, 37, 44, 51,
                 58, 59, 52, 45, 38, 31, 39, 46,
                 53, 60, 61, 54, 47, 55, 62, 63]


def extract8x8Values(row, col, matrix):
    block = []
    for i in range(row, row + 8):
        b = []
        for j in range(col, col + 8):
            b.append(matrix[i][j])
        block.append(b)
    return block


def subsample(matrix):
    block = []
    for i in range(0, 8, 2):
        b = []
        for j in range(0, 8, 2):
            avg = (matrix[i][j] + matrix[i + 1][j] + matrix[i][j + 1] + matrix[i + 1][j + 1]) / 4
            b.append(int(avg))
        block.append(b)
    return block


def convert_RGB_to_YUV(R, G, B, max_pixel):
    height = len(R)
    width = len(R[0])

    Y = []
    U = []
    V = []

    for i in range(height):
        y = []
        u = []
        v = []

        for j in range(width):
            y.append(convert_Y(R[i][j], G[i][j], B[i][j], max_pixel))
            u.append(convert_U(R[i][j], G[i][j], B[i][j], max_pixel))
            v.append(convert_V(R[i][j], G[i][j], B[i][j], max_pixel))

        Y.append(y)
        U.append(u)
        V.append(v)

    return Y, U, V


def convert_Y(r, g, b, max_pixel):
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return verify_range(y, max_pixel)


def convert_U(r, g, b, max_pixel):
    u = 128 - 0.169 * r - 0.331 * g + 0.499 * b
    return verify_range(u, max_pixel)


def convert_V(r, g, b, max_pixel):
    v = 128 + 0.499 * r - 0.418 * g - 0.0813 * b
    return verify_range(v, max_pixel)


def verify_range(n, value):
    if n > value:
        return int(value)
    elif n < 0:
        return 0
    return n


def getDCTValue(u, v, g):
    result = 0
    for x in range(0, 8):
        for y in range(0, 8):
            result += g[x][y] * math.cos(((2 * x + 1) * u * math.pi) / 16) * math.cos(((2 * y + 1) * v * math.pi) / 16)
    alfa_u = 1
    if u == 0:
        alfa_u = 1 / math.sqrt(2)
    alfa_v = 1
    if v == 0:
        alfa_v = 1 / math.sqrt(2)
    result = (1 / 4) * alfa_u * alfa_v * result
    return result


def zig_zag_parse(block):
    coefficients = []
    for value in ZIG_ZAG_ORDER:
        coefficients.append(block.values[value // 8][value % 8])
    return coefficients


def find_size(n):
    size = 0
    if n < 0:
        n = -1 * n
    value = 1
    while n >= value:
        value = value * 2
        size = size + 1
    return size


def entropy_encode_block(block):
    coefficients = zig_zag_parse(block)
    # DC coefficient
    elements = [find_size(coefficients[0]), coefficients[0]]
    # AC coefficients
    zeros = 0
    for i in range(1, 64):
        if coefficients[i] == 0:
            zeros = zeros + 1
        else:
            elements.append(zeros)  # run length
            elements.append(find_size(coefficients[i]))  # size
            elements.append(coefficients[i])  # amplitude
            zeros = 0
    if zeros > 0:
        elements.append(0)
        elements.append(0)
    return elements

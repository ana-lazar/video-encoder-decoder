import math

ZIG_ZAG_ORDER = [0, 1, 8, 16, 9, 2, 3, 10,
                 17, 24, 32, 25, 18, 11, 4, 5,
                 12, 19, 26, 33, 40, 48, 41, 34,
                 27, 20, 13, 6, 7, 14, 21, 28,
                 35, 42, 49, 56, 57, 50, 43, 36,
                 29, 22, 15, 23, 30, 37, 44, 51,
                 58, 59, 52, 45, 38, 31, 39, 46,
                 53, 60, 61, 54, 47, 55, 62, 63]


def upsample(block):
    matrix = []
    for i in range(0, 4):
        b = []
        for j in range(0, 4):
            b.append(block[i][j])
            b.append(block[i][j])
        matrix.append(b)
        matrix.append(b)
    return matrix


def convert_YUV_to_RGB(Y, U, V, max_pixel):
    height = len(Y)
    width = len(Y[0])

    R = []
    G = []
    B = []

    for i in range(height):
        r = []
        g = []
        b = []

        for j in range(width):
            r.append(convert_R(Y[i][j], U[i][j], V[i][j], max_pixel))
            g.append(convert_G(Y[i][j], U[i][j], V[i][j], max_pixel))
            b.append(convert_B(Y[i][j], U[i][j], V[i][j], max_pixel))

        R.append(r)
        G.append(g)
        B.append(b)

    return R, G, B


def convert_R(y, u, v, max_pixel):
    r = y + 1.402 * (v - 128)
    return int(verify_range(r, max_pixel))


def convert_G(y, u, v, max_pixel):
    g = y - 0.344 * (u - 128) - (v - 128) * 0.714
    return int(verify_range(g, max_pixel))


def convert_B(y, u, v, max_pixel):
    b = y + 1.772 * (u - 128)
    return int(verify_range(b, max_pixel))


def verify_range(n, value):
    if n > value:
        return int(value)
    elif n < 0:
        return 0
    return n


def getIDCTValue(x, y, F):
    result = 0
    for u in range(0, 8):
        alfa_u = 1
        if u == 0:
            alfa_u = 1 / math.sqrt(2)
        for v in range(0, 8):
            alfa_v = 1
            if v == 0:
                alfa_v = 1 / math.sqrt(2)
            result += alfa_u * alfa_v * F[u][v] * math.cos(((2 * x + 1) * u * math.pi) / 16) * math.cos(((2 * y + 1) * v * math.pi) / 16)
    result = (1 / 4) * result
    return result


def zig_zag_parse(elements):
    values = []
    for i in range(8):
        v = []
        for j in range(8):
            v.append(0)
        values.append(v)
    for i in range(len(ZIG_ZAG_ORDER)):
        values[ZIG_ZAG_ORDER[i] // 8][ZIG_ZAG_ORDER[i] % 8] = elements[i]
    return values


def split_to_blocks(elements):
    blocks_coefficients = []
    i = 0
    while i < len(elements):
        start = i
        # DC coefficient
        coefficients = [elements[i + 1]]
        i = i + 2
        # AC coefficients
        count = 1
        while count < 64:
            if elements[i] == 0 and elements[i + 1] == 0:
                while count < 64:
                    coefficients.append(0)
                    count = count + 1
                i = i + 2
            else:
                # add zeroes
                zeros = elements[i]
                count += zeros + 1
                while zeros > 0:
                    coefficients.append(0)
                    zeros = zeros - 1
                # actual value
                coefficients.append(elements[i + 2])
                i = i + 3
        blocks_coefficients.append(coefficients)
    return blocks_coefficients

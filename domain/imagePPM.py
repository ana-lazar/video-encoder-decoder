import math
import os

from domain.block import Block
from domain.decoder import convert_YUV_to_RGB, getIDCTValue, upsample, verify_range, split_to_blocks, zig_zag_parse
from domain.encoder import convert_RGB_to_YUV, getDCTValue, subsample, entropy_encode_block


class ImagePPM:
    def __init__(self):
        self.height = -1
        self.width = -1

        self.max_pixel = -1

        self.R = []
        self.G = []
        self.B = []

        self.Y = []
        self.U = []
        self.V = []

        self.blocks = []

        self.blocks_y = []
        self.blocks_u = []
        self.blocks_v = []

    def set_values(self, height, width, max_pixel):
        self.height = height
        self.width = width

        self.max_pixel = max_pixel

        for i in range(height):
            y = []
            v = []
            u = []
            for j in range(width):
                y.append(0)
                v.append(0)
                u.append(0)
            self.Y.append(y)
            self.U.append(u)
            self.V.append(v)

    def read_from_file(self, filename):
        path = os.path.dirname(__file__).split('/')
        path.pop()
        file = '/'.join([str(fold) for fold in path])

        f = open(file + '/' + filename, 'r')
        f.readline()
        f.readline()

        sizes = f.readline().strip().split(" ")
        self.width = int(sizes[0])
        self.height = int(sizes[1])

        self.max_pixel = int(f.readline().strip())

        for i in range(self.height):
            r = []
            g = []
            b = []

            for j in range(self.width):
                r.append(int(f.readline().strip()))
                g.append(int(f.readline().strip()))
                b.append(int(f.readline().strip()))

            self.R.append(r)
            self.G.append(g)
            self.B.append(b)

        f.close()

    def convert_to_YUV(self):
        self.Y, self.U, self.V = convert_RGB_to_YUV(self.R, self.G, self.B, self.max_pixel)

    def apply_FDCT(self):
        for b in range(len(self.blocks)):
            block = self.blocks[b]
            if block.type == 'U' or block.type == 'V':
                block.values = upsample(block.values)
            values = []
            for i in range(0, 8):
                v = []
                for j in range(0, 8):
                    v.append(block.values[i][j] - 128)
                values.append(v)
            new_block = []
            for i in range(0, 8):
                new_b = []
                for j in range(0, 8):
                    new_b.append(getDCTValue(i, j, values))
                new_block.append(new_b)
            block.values = new_block

    def quantify(self, Q):
        for b in range(len(self.blocks)):
            block = self.blocks[b]
            values = [[round(block.values[i][j] / Q[i][j]) for j in range(8)] for i in range(8)]
            block.values = values

    def apply_IDCT(self):
        for b in range(len(self.blocks)):
            block = self.blocks[b]
            new_block = []
            for i in range(0, 8):
                new_b = []
                for j in range(0, 8):
                    new_b.append(getIDCTValue(i, j, block.values))
                new_block.append(new_b)
            block.values = new_block
            values = []
            for i in range(0, 8):
                v = []
                for j in range(0, 8):
                    v.append(block.values[i][j] + 128)
                values.append(v)
            if block.type == 'U' or block.type == 'V':
                block.values = subsample(values)
            else:
                block.values = values

    def dequantify(self, Q):
        for b in range(len(self.blocks)):
            block = self.blocks[b]
            values = [[math.floor(block.values[i][j] * Q[i][j]) for j in range(8)] for i in range(8)]
            block.values = values

    def compute_blocks(self, b_type):
        if b_type == 'Y':
            matrix = self.Y
        elif b_type == 'U':
            matrix = self.U
        else:
            matrix = self.V
        blocks = []
        for i in range(0, self.height, 8):
            for j in range(0, self.width, 8):
                block = Block(b_type, i, j)
                block.compute_values(matrix)
                blocks.append(block)
        return blocks

    def recompose_matrices(self, blocks):
        for block in blocks:
            self.populate_matrix_with_values(block)

    def populate_matrix_with_values(self, block):
        values = block.values
        if block.type == 'Y':
            matrix = self.Y
        elif block.type == 'U':
            matrix = self.U
            values = upsample(block.values)
        else:
            matrix = self.V
            values = upsample(block.values)
        i1 = 0
        j1 = 0
        for i in range(block.row, block.row + 8):
            for j in range(block.col, block.col + 8):
                matrix[i][j] = values[i1][j1]
                j1 += 1
            i1 += 1
            j1 = 0

    def convert_to_RGB(self):
        self.R, self.G, self.B = convert_YUV_to_RGB(self.Y, self.U, self.V, self.max_pixel)

    def save_to_file(self, filename):
        path = os.path.dirname(__file__).split('/')
        path.pop()
        file = '/'.join([str(fold) for fold in path])

        f = open(file + '/' + filename, 'w')
        content = "P3\n" + str(self.width) + " " + str(self.height) + "\n" + str(self.max_pixel) + "\n"
        for i in range(self.height):
            for j in range(self.width):
                content += str(self.R[i][j]) + "\n" + str(self.G[i][j]) + "\n" + str(self.B[i][j]) + "\n"
        f.write(content)
        f.close()

    def separate_blocks(self):
        for block in self.blocks:
            if block.type == 'Y':
                self.blocks_y.append(block)
            elif block.type == 'U':
                self.blocks_u.append(block)
            elif block.type == 'V':
                self.blocks_v.append(block)

    def join_blocks(self):
        self.blocks = self.blocks_y + self.blocks_u + self.blocks_v

    def entropy_encode(self):
        elements = []
        c = []
        for i in range(len(self.blocks_y)):
            elements += entropy_encode_block(self.blocks_y[i]) + entropy_encode_block(self.blocks_u[i]) + \
                        entropy_encode_block(self.blocks_v[i])
        return elements

    def entropy_decode(self, elements):
        block_coefficients = split_to_blocks(elements)
        values = []
        row = 0
        col = 0
        for i in range(len(block_coefficients)):
            block = Block('', row, col)
            block.values = zig_zag_parse(block_coefficients[i])
            values.append(block.values)
            if i % 3 == 0:
                block.type = 'Y'
                self.blocks_y.append(block)
            elif i % 3 == 1:
                block.type = 'U'
                self.blocks_u.append(block)
            elif i % 3 == 2:
                block.type = 'V'
                self.blocks_v.append(block)
                if col == self.width - 8:
                    row = row + 8
                    col = 0
                else:
                    col = col + 8
        return values

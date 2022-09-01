from domain.encoder import extract8x8Values, subsample


class Block:
    def __init__(self, b_type, row, col):
        self.type = b_type
        self.row = row
        self.col = col
        self.values = []

    def compute_values(self, matrix):
        if self.type == 'Y':
            self.values = extract8x8Values(self.row, self.col, matrix)
        else:
            values = extract8x8Values(self.row, self.col, matrix)
            self.values = subsample(values)

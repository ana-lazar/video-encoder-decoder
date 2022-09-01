from domain.imagePPM import ImagePPM
from domain.block import Block
from domain.encoder import entropy_encode_block
from domain.decoder import zig_zag_parse, split_to_blocks


def run():
    Q = [[6, 4, 4, 6, 10, 16, 20, 24],
         [5, 5, 6, 8, 10, 23, 24, 22],
         [6, 5, 6, 10, 16, 23, 28, 22],
         [6, 7, 9, 12, 20, 35, 32, 25],
         [7, 9, 15, 22, 27, 44, 41, 31],
         [10, 14, 22, 26, 32, 42, 45, 37],
         [20, 26, 31, 35, 41, 48, 48, 40],
         [29, 37, 38, 39, 45, 40, 41, 40]]

    original_image = ImagePPM()
    original_image.read_from_file("files/original-dog.ppm")
    original_image.convert_to_YUV()

    blocks_y = original_image.compute_blocks('Y')
    blocks_u = original_image.compute_blocks('U')
    blocks_v = original_image.compute_blocks('V')

    original_image.blocks = blocks_y + blocks_u + blocks_v

    original_image.apply_FDCT()
    original_image.quantify(Q)

    original_image.separate_blocks()

    entropy_elements = original_image.entropy_encode()

    new_image = ImagePPM()
    new_image.set_values(original_image.height, original_image.width, original_image.max_pixel)

    new_image.entropy_decode(entropy_elements)

    new_image.join_blocks()

    new_image.dequantify(Q)
    new_image.apply_IDCT()

    new_image.recompose_matrices(new_image.blocks)

    new_image.convert_to_RGB()
    new_image.save_to_file("files/generated-dog.ppm")


if __name__ == '__main__':
    run()

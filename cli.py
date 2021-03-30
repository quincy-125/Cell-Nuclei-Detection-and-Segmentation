import argparse

from nuclei_DS import cell_seg_main
from util import warn_shut_up


def make_arg_parser():
    parser = argparse.ArgumentParser(description='nuclei segmentation command line arguments description',
                                     epilog='epilog')

    parser.add_argument('-i', '--input_data_dir',
                        type=str,
                        default='data',
                        required=True,
                        help='the path to the input image data folder')

    parser.add_argument('-o', '--output_dir',
                        type=str,
                        default='data',
                        required=True,
                        help='the path to the output folder')

    parser.add_argument('-m', '--loaded_model_name',
                        type=str,
                        default='nucles_model_v3.meta',
                        required=True,
                        help='the name of the trained model that needed to be loaded for nuclei segmentation task')

    parser.add_argument('-f', '--img_format',
                        type=str,
                        default='.png',
                        required=True,
                        help='the format of the input images')

    parser.add_argument('-w', '--no_warn_op',
                        type=str,
                        default='True',
                        required=True,
                        help='whether or not output the warning messages')

    return parser


def main():
    parser = make_arg_parser()
    args = parser.parse_args()

    warn_shut_up(no_warn_op=args.no_warn_op)

    cell_seg_main(data_folder=args.input_data_dir,
                  model_name=args.loaded_model_name,
                  format=args.img_format,
                  output_folder=args.output_dir)

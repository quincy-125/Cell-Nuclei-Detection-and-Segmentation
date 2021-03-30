import argparse

from Cell_Seg_Coord.shapely_coord import shapely_process
from nuclei_DS import cell_seg_main, process
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

    parser.add_argument('-d', '--coord_file_dir',
                        type=str,
                        default='file',
                        required=True,
                        help='the path to where the coordinate pickle files stored')

    parser.add_argument('-c', '--coord_file_name',
                        type=str,
                        default='cell_nuclei_seg_coord.pkl',
                        required=True,
                        help='the name of the coordinate pickle file in pkl format')

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

    parser.add_argument('-s', '--is_seg',
                        type=str,
                        default='True',
                        required=True,
                        help='whether or not run the segmentation algorithm on input images')

    parser.add_argument('-p', '--is_pickle',
                        type=str,
                        default='True',
                        required=True,
                        help='whether or not save the cell and nuclei segmentation coordinates in a pickle object')

    parser.add_argument('-l', '--is_load',
                        type=str,
                        default='True',
                        required=True,
                        help='whether or not load the pickle object to return the coordinate lists')

    parser.add_argument('-w', '--no_warn_op',
                        type=str,
                        default='True',
                        required=True,
                        help='whether or not output the warning messages')

    return parser


def main():
    parser = make_arg_parser()
    args = parser.parse_args()

    process(no_warn_op=args.no_warn_op,
            data_folder=args.input_data_dir,
            model_name=args.loaded_model_name,
            format=args.img_format,
            output_folder=args.output_dir,
            is_seg=args.is_seg,
            is_pickle=args.is_pickle,
            is_load=args.is_load,
            mask_img_dir=args.output_dir,
            coord_save_dir=args.coord_file_dir,
            coord_file_name=args.coord_file_name)


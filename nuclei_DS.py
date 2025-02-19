'''
detect and segement potential nuclei in miscropic images (H&E stained)
@author: Kemeng Chen 
'''
import os
import PIL

from Cell_Seg_Coord.shapely_coord import shapely_process
from util import *


def read_img_from_np(data_folder, img_arrays_path):
    """

    :param data_folder:
    :param img_arrays_path: path to the list of input np arrays of the image patches
    :return:
    """
    for i in os.listdir(img_arrays_path):
        img_arrays = os.path.join(img_arrays_path, i)

        for j in range(len(img_arrays)):
            sample_dir = os.path.join(os.path.join(data_folder, 'Sample_', str(j)))
            if not os.path.exists(sample_dir):
                os.mkdir(sample_dir)
            sample = PIL.Image.fromarray(img_arrays[j])
            sample.save(os.path.join(sample_dir, 'sample_' + str(j) + '.png'))


def cell_seg_main(data_folder, model_name, format, output_folder):
    """

    :param data_folder:
    :param model_name:
    :param format:
    :param output_folder:
    :return:
    """
    patch_size = 128
    stride = 16
    file_path = os.path.join(os.getcwd(), data_folder)
    name_list = os.listdir(file_path)
    print(str(len(name_list)), ' files detected')
    model_path = os.path.join(os.getcwd(), 'models')
    model = restored_model(os.path.join(model_path, model_name), model_path)
    print('Start time:')
    print_ctime()

    for index, temp_name in enumerate(name_list):
        ts = time()
        print('process: ', str(index), ' name: ', temp_name)
        temp_path = os.path.join(file_path, temp_name)
        if not os.path.isdir(temp_path):
            continue

        temp_image = cv2.imread(os.path.join(temp_path, temp_name + format))
        if temp_image is None:
            raise AssertionError(temp_path, ' not found')
        batch_group, shape = preprocess(temp_image, patch_size, stride, temp_path)
        mask_list = sess_interference(model, batch_group)
        c_mask = patch2image(mask_list, patch_size, stride, shape)
        c_mask = cv2.medianBlur((255 * c_mask).astype(np.uint8), 3)
        c_mask = c_mask.astype(np.float) / 255
        thr = 0.5
        c_mask[c_mask < thr] = 0
        c_mask[c_mask >= thr] = 1
        center_edge_mask, gray_map = center_edge(c_mask, temp_image)

        result_dir = os.path.join(output_folder, temp_name)
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)

        cv2.imwrite(os.path.join(result_dir, 'mask.png'), gray_map)
        cv2.imwrite(os.path.join(result_dir, 'label.png'), center_edge_mask)
        te = time()
        print('Time cost: ', str(te - ts))

    model.close_sess()
    print('mask generation done')
    print_ctime()


def process(is_img_np, img_arrays_dir, no_warn_op, data_folder, model_name, format, output_folder,
            is_seg, is_pickle, is_load, mask_img_dir, coord_save_dir, coord_file_name):
    """

    :param img_arrays_dir:
    :param is_img_np: if the input image in numpy array format
    :param no_warn_op:
    :param data_folder:
    :param model_name:
    :param format:
    :param output_folder:
    :param is_seg:
    :param is_pickle:
    :param is_load:
    :param mask_img_dir:
    :param coord_save_dir:
    :param coord_file_name:
    :return:
    """
    warn_shut_up(no_warn_op=no_warn_op)

    str_bool_dic = str_to_bool()

    is_seg = str_bool_dic[is_seg]

    if is_seg:
        if is_img_np:
            read_img_from_np(data_folder=data_folder,
                             img_arrays_path=img_arrays_dir)

        cell_seg_main(data_folder=data_folder,
                      model_name=model_name,
                      format=format,
                      output_folder=output_folder)

    shapely_process(is_pickle=is_pickle,
                    is_load=is_load,
                    mask_img_dir=mask_img_dir,
                    coord_save_dir=coord_save_dir,
                    coord_file_name=coord_file_name)
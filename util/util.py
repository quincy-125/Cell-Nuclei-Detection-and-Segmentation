'''
utility functions assisting nuclei detection and segmentation
@author: Kemeng Chen
'''
import math
import warnings
from time import time, ctime

import cv2
import numpy as np
import tensorflow as tf
from skimage.measure import label, regionprops
from skimage.morphology import square, erosion, dilation


def str_to_bool():
    """
    :return: python dictionary with keys be string type and values be boolean
    """
    str_bool_dic = {'True': True,
                    'False': False}

    return str_bool_dic


def warn_shut_up(no_warn_op):
    """
    :param no_warn_op: whether or not enable warn_shut_up function to disable tensorflow and python warning messages
    """

    str_bool_dic = str_to_bool()
    no_warn_op = str_bool_dic[no_warn_op]

    if no_warn_op:
        warnings.filterwarnings("ignore")
        tf.get_logger().setLevel('ERROR')
    else:
        raise Exception('Enable tf_shut_up function to disable all warning messages.')


def print_ctime():
    current_time = ctime(int(time()))
    print(str(current_time))


def batch2list(batch):
    mask_list = list()
    for index in range(batch.shape[0]):
        mask_list.append(batch[index, :, :])
    return mask_list


def patch2image(patch_list, patch_size, stride, shape):
    if shape[0] < patch_size:
        L = 0
    else:
        L = math.ceil((shape[0] - patch_size) / stride)
    if shape[1] < patch_size:
        W = 0
    else:
        W = math.ceil((shape[1] - patch_size) / stride)

    full_image = np.zeros([L * stride + patch_size, W * stride + patch_size])
    bk = np.zeros([L * stride + patch_size, W * stride + patch_size])
    cnt = 0
    for i in range(L + 1):
        for j in range(W + 1):
            full_image[i * stride:i * stride + patch_size, j * stride:j * stride + patch_size] += patch_list[cnt]
            bk[i * stride:i * stride + patch_size, j * stride:j * stride + patch_size] += np.ones(
                [patch_size, patch_size])
            cnt += 1
    full_image /= bk
    image = full_image[0:shape[0], 0:shape[1]]
    return image


def image2patch(in_image, patch_size, stride, blur=False, f_size=9):
    if blur is True:
        in_image = cv2.medianBlur(in_image, f_size)
    # in_image=denoise_bilateral(in_image.astype(np.float), 19, 11, 9, multichannel=False)
    shape = in_image.shape
    if shape[0] < patch_size:
        L = 0
    else:
        L = math.ceil((shape[0] - patch_size) / stride)
    if shape[1] < patch_size:
        W = 0
    else:
        W = math.ceil((shape[1] - patch_size) / stride)
    patch_list = list()

    if len(shape) > 2:
        full_image = np.pad(in_image,
                            ((0, patch_size + stride * L - shape[0]), (0, patch_size + stride * W - shape[1]), (0, 0)),
                            mode='symmetric')
    else:
        full_image = np.pad(in_image,
                            ((0, patch_size + stride * L - shape[0]), (0, patch_size + stride * W - shape[1])),
                            mode='symmetric')
    for i in range(L + 1):
        for j in range(W + 1):
            if len(shape) > 2:
                patch_list.append(full_image[i * stride:i * stride + patch_size, j * stride:j * stride + patch_size, :])
            else:
                patch_list.append(full_image[i * stride:i * stride + patch_size, j * stride:j * stride + patch_size])
    if len(patch_list) != (L + 1) * (W + 1):
        raise ValueError('Patch_list: ', str(len(patch_list), ' L: ', str(L), ' W: ', str(W)))

    return patch_list


def list2batch(patches):
    """

    :param patches:
    :return:
    """
    patch_shape = list(patches[0].shape)

    batch_size = len(patches)

    if len(patch_shape) > 2:
        batch = np.zeros([batch_size] + patch_shape)
        for index, temp in enumerate(patches):
            batch[index, :, :, :] = temp
    else:
        batch = np.zeros([batch_size] + patch_shape + [1])
        for index, temp in enumerate(patches):
            batch[index, :, :, :] = np.expand_dims(temp, axis=-1)
    return batch


def preprocess(input_image, patch_size, stride, file_path):
    f_size = 5
    g_size = 10
    shape = input_image.shape
    patch_list = image2patch(input_image.astype(np.float32) / 255.0, patch_size, stride)
    num_group = math.ceil(len(patch_list) / g_size)
    batch_group = list()
    for i in range(num_group):
        temp_batch = list2batch(patch_list[i * g_size:(i + 1) * g_size])
        batch_group.append(temp_batch)
    return batch_group, shape


def sess_interference(sess, batch_group):
    patch_list = list()
    for temp_batch in batch_group:
        mask_batch = sess.run_sess(temp_batch)[0]
        mask_batch = np.squeeze(mask_batch, axis=-1)
        mask_list = batch2list(mask_batch)
        patch_list += mask_list
    return patch_list


def center_point(mask):
    v, h = mask.shape
    center_mask = np.zeros([v, h])
    mask = erosion(mask, square(3))
    individual_mask = label(mask, connectivity=2)
    prop = regionprops(individual_mask)
    for cordinates in prop:
        temp_center = cordinates.centroid
        if not math.isnan(temp_center[0]) and not math.isnan(temp_center[1]):
            temp_mask = np.zeros([v, h])
            temp_mask[int(temp_center[0]), int(temp_center[1])] = 1
            center_mask += dilation(temp_mask, square(2))
    return np.clip(center_mask, a_min=0, a_max=1).astype(np.uint8)


def draw_individual_edge(mask):
    v, h = mask.shape
    edge = np.zeros([v, h])
    individual_mask = label(mask, connectivity=2)
    for index in np.unique(individual_mask):
        if index == 0:
            continue
        temp_mask = np.copy(individual_mask)
        temp_mask[temp_mask != index] = 0
        temp_mask[temp_mask == index] = 1
        temp_mask = dilation(temp_mask, square(3))
        temp_edge = cv2.Canny(temp_mask.astype(np.uint8), 2, 5) / 255
        edge += temp_edge
    return np.clip(edge, a_min=0, a_max=1).astype(np.uint8)


def center_edge(mask, image):
    center_map = center_point(mask)
    edge_map = draw_individual_edge(mask)
    comb_mask = center_map + edge_map
    comb_mask = np.clip(comb_mask, a_min=0, a_max=1)
    check_image = np.copy(image)
    comb_mask *= 255
    check_image[:, :, 1] = np.maximum(check_image[:, :, 1], comb_mask)
    return check_image.astype(np.uint8), comb_mask.astype(np.uint8)

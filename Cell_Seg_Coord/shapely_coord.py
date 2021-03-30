import os
import pickle
from collections import defaultdict
from statistics import mean

import cv2
import numpy as np
from shapely.geometry import MultiPolygon, Polygon

from util import str_to_bool


def mask_to_polygons(mask, epsilon=10., min_area=10.):
    """Convert a mask ndarray (binarized image) to Multipolygons"""
    # first, find contours with cv2: it's much faster than shapely
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    if not contours:
        return MultiPolygon()
    # now messy stuff to associate parent and child contours
    cnt_children = defaultdict(list)
    child_contours = set()
    assert hierarchy.shape[0] == 1
    # http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
    for idx, (_, _, _, parent_idx) in enumerate(hierarchy[0]):
        if parent_idx != -1:
            child_contours.add(idx)
            cnt_children[parent_idx].append(contours[idx])
    # create actual polygons filtering by area (removes artifacts)
    all_polygons = []
    for idx, cnt in enumerate(contours):
        if idx not in child_contours and cv2.contourArea(cnt) >= min_area:
            assert cnt.shape[1] == 1
            poly = Polygon(
                shell=cnt[:, 0, :],
                holes=[c[:, 0, :] for c in cnt_children.get(idx, [])
                       if cv2.contourArea(c) >= min_area])
            all_polygons.append(poly)
    all_polygons = MultiPolygon(all_polygons)

    return all_polygons


def mask_for_polygons(polygons, im_size):
    """Convert a polygon or multipolygon list back to
       an image mask ndarray"""
    img_mask = np.zeros(im_size, np.uint8)
    if not polygons:
        return img_mask
    # function to round and convert to int
    int_coords = lambda x: np.array(x).round().astype(np.int32)
    exteriors = [int_coords(poly.exterior.coords) for poly in polygons]
    interiors = [int_coords(pi.coords) for poly in polygons
                 for pi in poly.interiors]
    cv2.fillPoly(img_mask, exteriors, 1)
    cv2.fillPoly(img_mask, interiors, 0)
    return img_mask


def polygon_obj(img_out_dir):
    img = cv2.imread(os.path.join(img_out_dir, 'mask.png'), cv2.IMREAD_UNCHANGED)
    gray_img = cv2.convertScaleAbs(img)

    polys = mask_to_polygons(gray_img, epsilon=10., min_area=10.)

    polygons = list()

    for poly in polys:
        polygons.append(poly)

    return polygons


def polygon_coord(img_out_dir):
    polygons = polygon_obj(img_out_dir)

    polygon_exterior_coords = list()

    for i in polygons:
        poly_ex_coords = list(i.exterior.coords)
        polygon_exterior_coords.append(poly_ex_coords)

    return polygon_exterior_coords


def nuclei_coord(img_out_dir):
    polygon_exterior_coords = polygon_coord(img_out_dir)

    nuclei_coords = list()

    for i in polygon_exterior_coords:
        ex_coord_index0 = list()
        ex_coord_index1 = list()

        for j in i:
            ex_coord_index0.append(j[0])
            ex_coord_index1.append(j[1])

            ex_coord_mean0 = round(mean(ex_coord_index0), 0)
            ex_coord_mean1 = round(mean(ex_coord_index1), 0)

            nuclei_coord = [ex_coord_mean0, ex_coord_mean1]

        nuclei_coords.append(nuclei_coord)

    return nuclei_coords


def cell_nuclei_coord_store(img_out_dir):
    polygon_exterior_coords = polygon_coord(img_out_dir)
    nuclei_coords = nuclei_coord(img_out_dir)

    cell_nuclei_coords = {'img_name': img_out_dir,
                          'cell coordinates': polygon_exterior_coords,
                          'nuclei coordinates': nuclei_coords}

    return cell_nuclei_coords


def cell_nuclei_seg_store(mask_img_dir, coord_save_dir, coord_file_name):
    mask_img_names = os.listdir(mask_img_dir)

    cell_nuclei_seg_coords = list()

    for i in mask_img_names:
        img_out_path = os.path.join(mask_img_dir, i)

        cell_nuclei_coords = cell_nuclei_coord_store(img_out_dir=img_out_path)
        cell_nuclei_seg_coords.append(cell_nuclei_coords)

    if not os.path.exists(coord_save_dir):
        os.mkdir(coord_save_dir)

    full_coord_file_dir = os.path.join(coord_save_dir, coord_file_name)

    coord_file = open(full_coord_file_dir, 'wb')

    pickle.dump(cell_nuclei_seg_coords, coord_file)


def load_seg_coord(coord_save_dir, coord_file_name):
    full_coord_file_dir = os.path.join(coord_save_dir, coord_file_name)

    coord_file = open(full_coord_file_dir, 'rb')

    coords_lists = pickle.load(coord_file)

    return coords_lists


def shapely_process(is_pickle, is_load, mask_img_dir, coord_save_dir, coord_file_name):
    str_bool_dic = str_to_bool()

    is_pickle = str_bool_dic[is_pickle]
    is_load = str_bool_dic[is_load]

    if is_pickle:
        cell_nuclei_seg_store(mask_img_dir=mask_img_dir,
                              coord_save_dir=coord_save_dir,
                              coord_file_name=coord_file_name)

        if is_load:
            load_seg_coord(coord_save_dir=coord_save_dir,
                           coord_file_name=coord_file_name)

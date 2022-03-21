import os
import numpy as np
import pandas as pd
import gdcm
import pydicom


# --------------------------------------------------------
def change_range(img, new_min, new_max, actual_min=None, actual_max=None):
    if actual_min is None or actual_max is None:
        actual_min = np.min(img)
        actual_max = np.max(img)

    if actual_min == new_min and actual_max == new_max:
        return img

    img = (
        (new_max - new_min) * (img - actual_min) / (actual_max - actual_min)
    ) + new_min

    return img

# --------------------------------------------------------
def get_first_of_dicom_field_as_int(x):
    if type(x) == pydicom.multival.MultiValue:
        return int(x[0])
    else:
        return int(x)


# --------------------------------------------------------
def read_dicom(dicom_path):
    ds = pydicom.dcmread(dicom_path)
    ds.decompress()
    return ds


# --------------------------------------------------------
def get_single_window_img(dicom_path, window_center=None, window_width=None):
    dicom = read_dicom(dicom_path)
    img = dicom.pixel_array
    if 'MONOCHROME1' in dicom.PhotometricInterpretation:
        img = 2**dicom.BitsStored-img

    try:
        slope = get_first_of_dicom_field_as_int(dicom.RescaleSlope)
        intercept = get_first_of_dicom_field_as_int(dicom.RescaleIntercept)
    except:
        slope = 1
        intercept = 0

    if window_center is None:
        try:
            window_center = get_first_of_dicom_field_as_int(dicom.WindowCenter) 
            window_width = get_first_of_dicom_field_as_int(dicom.WindowWidth)
        except:
            window_center = None
            window_width = None

    img = (img*slope +intercept)

    if window_width is None:
        img_min = np.min(img)
        img_max = np.max(img)
        img = (img - img_min) / (img_max - img_min)		
    else:
        img_min = window_center - window_width//2
        img_max = window_center + window_width//2
        img[img<img_min] = img_min
        img[img>img_max] = img_max
        img = (img - img_min) / window_width

    return img

# --------------------------------------------------------
def get_dicom_img(path, window_center=None, window_width=None):
    img = None
    if window_center is None or window_width is None:
        img = get_single_window_img(path)
    elif type(window_center) == list:
        img = []
        for i in range(len(window_center)):
            img_ch = get_single_window_img(path, window_center[i], window_width[i])
            img.append(img_ch)
        img = np.array(img)
        img = np.moveaxis(img, 0, 2)
    else:
        img = get_single_window_img(path, window_center, window_width)
    
    return img

# --------------------------------------------------------
def get_valid_files_in_folder(folder, dicom_fields):
    path_list = []
    field_lists = {field:[] for field in dicom_fields.keys()}
    for root, directories, files in os.walk(folder):
        for item in files:
            path = os.path.join(root, item)
            try:
                ds = read_dicom(path)
                value_dict = {}
                for field in dicom_fields.keys():
                    if dicom_fields[field]['mandatory']:
                        value_dict[field] = getattr(ds, field)
                    else:
                        value_dict[field] = getattr(ds, field, 'Null')
            except Exception as e:
                print(e)
                continue
            path_list.append(path)
            for field in dicom_fields.keys():
                field_lists[field].append(value_dict[field])

    field_lists['path'] = path_list

    df = pd.DataFrame()
    for field in field_lists.keys():
        df[field] = field_lists[field]

    return df

# --------------------------------------------------------
def get_series_arr(df, series_id, window_center=None, window_width=None):
    df_ser = df[df['SeriesInstanceUID'] == series_id]
    df_ser = df_ser.sort_values(by=['InstanceNumber'])
    df_ser.reset_index(drop=True, inplace=True)
    img3d = []
    flip = False
    prev_img_pos_z = None
    for row in df_ser.iterrows():
        file = row[1]['path']
        img = get_dicom_img(file, window_center, window_width)
        img3d.append(img)

        img_pos_z = row[1]['ImagePositionPatient'][2]
        if prev_img_pos_z is not None and prev_img_pos_z < img_pos_z:
            flip = True
        prev_img_pos_z = img_pos_z

    img3d = np.array(img3d)
    if flip:
        img3d = np.flip(img3d, axis=0)

    return img3d
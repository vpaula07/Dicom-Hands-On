import numpy as np
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
def get_single_window_img(path, window_center=None, window_width=None):
    dicom = read_dicom(path)
    img = dicom.pixel_array
    if 'MONOCHROME1' in dicom.PhotometricInterpretation:
        img = 2**dicom.BitsStored-img

    try:
        slope = get_first_of_dicom_field_as_int(dicom.RescaleSlope)
        intercept = get_first_of_dicom_field_as_int(dicom.RescaleIntercept)
        if window_center is None:
            window_center = get_first_of_dicom_field_as_int(dicom.WindowCenter) 
            window_width = get_first_of_dicom_field_as_int(dicom.WindowWidth)

        img = (img*slope +intercept)
        img_min = window_center - window_width//2
        img_max = window_center + window_width//2
        img[img<img_min] = img_min
        img[img>img_max] = img_max

        img = (img - img_min) / window_width
    except:
        return None

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


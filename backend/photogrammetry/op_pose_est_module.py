import cv2, os, sys, numpy as np
sys.path.append("/usr/local/openpose/python")
import pyopenpose as op    

params = dict(model_folder="/usr/local/openpose/models",
              model_pose="BODY_25",    
              net_resolution="-1x368",
              disable_blending=True)
op_wrapper = op.WrapperPython()
op_wrapper.configure(params)
op_wrapper.start()

def _run_openpose(img_path):
    datum = op.Datum()
    image = cv2.imread(img_path)
    if image is None:
        raise FileNotFoundError(img_path)
    datum.cvInputData = image
    op_wrapper.emplaceAndPop([datum])
    if datum.poseKeypoints is None or len(datum.poseKeypoints) == 0:
        raise ValueError("No person detected")
    return datum.poseKeypoints[0]        

L_SHO, R_SHO = 5, 2
L_HIP, R_HIP = 12, 9

def _euclid(pA, pB):
    return np.linalg.norm(pA - pB)

def extract_measurements_from_images(front_img, side_img):
    kp_front = _run_openpose(front_img)
    kp_side  = _run_openpose(side_img)

    shoulder_px   = _euclid(kp_front[L_SHO][:2], kp_front[R_SHO][:2])
    torso_px      = _euclid(kp_front[L_SHO][:2], kp_front[L_HIP][:2])
    side_depth_px = _euclid(kp_side[L_SHO][:2],  kp_side[L_HIP][:2])

    px_to_cm = 1.0            
    return {
        "shoulder_cm": shoulder_px * px_to_cm,
        "torso_height": torso_px * px_to_cm,
        "side_depth": side_depth_px * px_to_cm
    }

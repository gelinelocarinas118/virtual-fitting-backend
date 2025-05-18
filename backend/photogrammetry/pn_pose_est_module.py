import cv2, numpy as np, tensorflow as tf
import posenet

model = posenet.load_model(101)
output_stride = model.output_stride

L_SHO, R_SHO = 5, 6
L_HIP, R_HIP = 11, 12

def _run_posenet(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(img_path)
    input_img, draw_img, scale = posenet.process_input(img,
                                                      scale_factor=1.0,
                                                      output_stride=output_stride)
    heatmaps, offsets, displacements_fwd, displacements_bwd = model(tf.constant(input_img))
    pose_scores, keypoint_scores, keypoints = posenet.decode_multiple_poses(
        heatmaps.numpy(), offsets.numpy(),
        displacements_fwd.numpy(), displacements_bwd.numpy(),
        output_stride=output_stride, max_pose_detections=1, min_pose_score=0.25)
    if pose_scores[0] == 0.0:
        raise ValueError("No landmarks detected")

    kp = keypoints[0] / scale
    return kp       # shape (17, 2)

def _euclid(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

def extract_measurements_from_images(front_img, side_img):
    kp_front = _run_posenet(front_img)
    kp_side  = _run_posenet(side_img)

    shoulder_px   = _euclid(kp_front[L_SHO], kp_front[R_SHO])
    torso_px      = _euclid(kp_front[L_SHO], kp_front[L_HIP])
    side_depth_px = _euclid(kp_side[L_SHO],  kp_side[L_HIP])

    px_to_cm = 1.0        
    return {
        "shoulder_cm": shoulder_px * px_to_cm,
        "torso_height": torso_px * px_to_cm,
        "side_depth": side_depth_px * px_to_cm
    }

import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
LND = mp_pose.PoseLandmark


def extract_measurements_from_images(front_img_path: str,
                                     side_img_path : str,
                                     height_cm     : float) -> dict:
    """
    Returns shoulder width, torso height and body depth **already in cm**.
    The conversion factor (px → cm) is derived from the person's true
    height that the user's input.
    """
    kp_front = _get_landmarks(front_img_path)
    kp_side  = _get_landmarks(side_img_path)

    # Pixel distances in the *front* image
    px_height   = _dist(kp_front[LND.LEFT_HEEL],  kp_front[LND.NOSE])      # full body
    px_shoulder = _dist(kp_front[LND.LEFT_SHOULDER], kp_front[LND.RIGHT_SHOULDER])
    px_torso    = _dist(kp_front[LND.LEFT_SHOULDER], kp_front[LND.LEFT_HIP])

    # Pixel depth in the *side* image
    px_depth = _dist(kp_side[LND.LEFT_SHOULDER], kp_side[LND.LEFT_HIP])

    # Same scale-factor for everything
    px_to_cm = height_cm / px_height

    return {
        "height_cm"   : float(height_cm),
        "shoulder_cm" : px_shoulder * px_to_cm,
        "torso_height": px_torso    * px_to_cm,
        "side_depth"  : px_depth    * px_to_cm
    }


def _get_landmarks(img_path: str):
    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        raise FileNotFoundError(img_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        res = pose.process(img_rgb)
        if not res.pose_landmarks:
            raise ValueError(f"No landmarks in {img_path}")
        return res.pose_landmarks.landmark

def _dist(a, b):
    return np.linalg.norm(
        np.array([a.x, a.y]) - np.array([b.x, b.y])
    )

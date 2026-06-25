from dataclasses import dataclass
from typing import List, Tuple

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class FaceDetectionResult:
    landmarks: List[Tuple[float, float, float]]
    image_width: int
    image_height: int
    face_count: int


class FaceDetector:
    def __init__(self) -> None:
        self._mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )

    def detect(self, image_bgr: np.ndarray) -> FaceDetectionResult | None:
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        result = self._mesh.process(rgb)
        faces = result.multi_face_landmarks or []
        if len(faces) != 1:
            return None if not faces else FaceDetectionResult([], image_bgr.shape[1], image_bgr.shape[0], len(faces))

        h, w = image_bgr.shape[:2]
        landmarks = [(lm.x, lm.y, lm.z) for lm in faces[0].landmark]
        return FaceDetectionResult(landmarks=landmarks, image_width=w, image_height=h, face_count=1)

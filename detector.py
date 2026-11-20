"""전처리 + 얼굴/눈 검출 (Haar Cascade)"""
import cv2


class FaceEyeDetector:
    def __init__(self):
        base = cv2.data.haarcascades  # OpenCV에 들어 있는 분류기 파일 경로
        self.face_cascade = cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(base + "haarcascade_eye.xml")
        if self.face_cascade.empty() or self.eye_cascade.empty():
            raise RuntimeError("Haar Cascade 파일을 불러오지 못했습니다.")

    def preprocess(self, frame):
        """흑백 변환 -> 밝기 보정 -> 잡음 줄이기"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        return cv2.GaussianBlur(gray, (3, 3), 0)

    def detect(self, frame):
        """반환: (얼굴 좌표 또는 None, 눈 좌표 리스트)"""
        gray = self.preprocess(frame)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            return None, []
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])  # 가장 큰 얼굴 1개만 사용
        roi = gray[y:y + h // 2, x:x + w]                   # 얼굴 위쪽 절반에서만 눈을 찾음
        eyes = self.eye_cascade.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=6,
                                                 minSize=(w // 10, w // 10))
        eyes = [(x + ex, y + ey, ew, eh) for ex, ey, ew, eh in eyes]
        return (x, y, w, h), eyes

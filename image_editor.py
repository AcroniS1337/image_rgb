import cv2
import numpy as np


class ImageEditor:

    def __init__(self):
        self.original: np.ndarray | None = None
        self.current:  np.ndarray | None = None

    def set_image(self, bgr: np.ndarray) -> None:
        self.original = bgr.copy()
        self.current = bgr.copy()

    def reset(self) -> np.ndarray | None:
        if self.original is None:
            return None
        self.current = self.original.copy()
        return self.current

    def has_image(self) -> bool:
        return self.current is not None

    def load_from_file(self, path: str) -> np.ndarray:
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Не удалось прочитать файл: {path}")
        self.set_image(img)
        return self.current

    def capture_from_webcam(self, camera_index: int = 0) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise RuntimeError("Не удалось подключиться к веб-камере.")
        return cap

    def save_frame_from_cap(self, cap: cv2.VideoCapture) -> np.ndarray | None:
        ret, frame = cap.read()
        if not ret:
            return None
        self.set_image(frame)
        return self.current

    def extract_channel(self, channel: str) -> np.ndarray:
        if self.current is None:
            raise ValueError("Изображение не загружено.")
        ch_map = {"R": 2, "G": 1, "B": 0}
        if channel not in ch_map:
            raise ValueError(
                f"Неверный канал: {channel}. Используйте R, G или B.")
        result = np.zeros_like(self.current)
        idx = ch_map[channel]
        result[:, :, idx] = self.current[:, :, idx]
        return result

    def resize(self, width: int, height: int) -> np.ndarray:
        if not self.has_image():
            raise ValueError("Изображение не загружено.")
        result = cv2.resize(self.current, (width, height),
                            interpolation=cv2.INTER_LANCZOS4)
        self.current = result
        return result

    def add_border(self, size: int) -> np.ndarray:
        if not self.has_image():
            raise ValueError("Изображение не загружено.")
        result = cv2.copyMakeBorder(
            self.current, size, size, size, size,
            cv2.BORDER_CONSTANT, value=(0, 0, 0))
        self.current = result
        return result

    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, thickness: int) -> np.ndarray:
        if not self.has_image():
            raise ValueError("Изображение не загружено.")
        result = self.current.copy()
        cv2.rectangle(result, (x1, y1), (x2, y2),
                      (255, 0, 0), thickness)
        self.current = result
        return result

    def save(self, path: str) -> None:
        if not self.has_image():
            raise ValueError("Нечего сохранять.")
        if not cv2.imwrite(path, self.current):
            raise IOError(f"Не удалось сохранить файл: {path}")

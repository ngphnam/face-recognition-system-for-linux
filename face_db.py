"""
face_db.py - Quản lý cơ sở dữ liệu khuôn mặt.

Mỗi người được lưu dưới dạng:
  known_faces/<tên>/
    ├── *.jpg / *.png   (ảnh gốc)
    └── encodings.npy   (mảng numpy chứa face encodings)

Module cung cấp:
  • register_face()   – đăng ký khuôn mặt mới từ ảnh hoặc webcam
  • load_database()   – nạp toàn bộ encoding đã lưu
  • list_registered()  – liệt kê người đã đăng ký
  • delete_person()    – xoá thông tin khuôn mặt
"""

import os
import shutil
from pathlib import Path
from typing import Optional

import cv2
import face_recognition
import numpy as np

# ────────────────────────────────────────────
# Đường dẫn mặc định
# ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
KNOWN_FACES_DIR = BASE_DIR / "known_faces"
KNOWN_FACES_DIR.mkdir(exist_ok=True)


def _encode_image(image_path: str) -> Optional[np.ndarray]:
    """Trả về face encoding đầu tiên tìm được trong ảnh, hoặc None."""
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    if encodings:
        return encodings[0]
    return None


def register_face_from_image(name: str, image_path: str) -> bool:
    """
    Đăng ký khuôn mặt từ file ảnh.
    Returns True nếu thành công, False nếu không phát hiện được mặt.
    """
    encoding = _encode_image(image_path)
    if encoding is None:
        return False

    person_dir = KNOWN_FACES_DIR / name
    person_dir.mkdir(parents=True, exist_ok=True)

    # Lưu ảnh gốc
    ext = Path(image_path).suffix or ".jpg"
    existing_images = list(person_dir.glob("face_*"))
    idx = len(existing_images) + 1
    dest = person_dir / f"face_{idx}{ext}"
    shutil.copy2(image_path, dest)

    # Cập nhật / tạo file encodings
    enc_file = person_dir / "encodings.npy"
    if enc_file.exists():
        existing = np.load(str(enc_file))
        updated = np.vstack([existing, encoding.reshape(1, -1)])
    else:
        updated = encoding.reshape(1, -1)
    np.save(str(enc_file), updated)

    return True


def register_face_from_webcam(name: str, num_samples: int = 5) -> int:
    """
    Chụp `num_samples` ảnh từ webcam và đăng ký.
    Returns số ảnh đăng ký thành công.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở webcam!")
        return 0

    person_dir = KNOWN_FACES_DIR / name
    person_dir.mkdir(parents=True, exist_ok=True)

    encodings_list: list[np.ndarray] = []
    existing_images = list(person_dir.glob("face_*"))
    idx = len(existing_images)
    captured = 0

    print(f"\n📸 Chuẩn bị chụp {num_samples} ảnh cho '{name}'.")
    print("   Nhấn [SPACE] để chụp, [Q] để huỷ.\n")

    while captured < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        # Hiển thị khung hình với hướng dẫn
        display = frame.copy()
        h, w = display.shape[:2]
        cv2.putText(
            display,
            f"Captured: {captured}/{num_samples}  |  SPACE=chup  Q=huy",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        # Vẽ khung xung quanh khuôn mặt phát hiện được
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model="hog")
        for top, right, bottom, left in locations:
            cv2.rectangle(display, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("Dang ky khuon mat", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("⚠️  Đã huỷ.")
            break

        if key == ord(" "):
            if not locations:
                print("   ⚠️  Không phát hiện khuôn mặt, thử lại!")
                continue

            encs = face_recognition.face_encodings(rgb, locations)
            if encs:
                idx += 1
                captured += 1
                img_path = person_dir / f"face_{idx}.jpg"
                cv2.imwrite(str(img_path), frame)
                encodings_list.append(encs[0])
                print(f"   ✅ Ảnh {captured}/{num_samples} đã lưu.")

    cap.release()
    cv2.destroyAllWindows()

    if encodings_list:
        enc_file = person_dir / "encodings.npy"
        new_encs = np.array(encodings_list)
        if enc_file.exists():
            existing = np.load(str(enc_file))
            new_encs = np.vstack([existing, new_encs])
        np.save(str(enc_file), new_encs)

    return captured


# ────────────────────────────────────────────
# Nạp & truy vấn
# ────────────────────────────────────────────

def load_database() -> tuple[list[str], list[np.ndarray]]:
    """
    Nạp toàn bộ face encodings đã lưu.
    Returns (known_names, known_encodings).
    Mỗi encoding tương ứng 1 tên.
    """
    names: list[str] = []
    encodings: list[np.ndarray] = []

    for person_dir in sorted(KNOWN_FACES_DIR.iterdir()):
        if not person_dir.is_dir():
            continue
        enc_file = person_dir / "encodings.npy"
        if not enc_file.exists():
            continue
        data = np.load(str(enc_file))
        for enc in data:
            names.append(person_dir.name)
            encodings.append(enc)

    return names, encodings


def list_registered() -> list[dict]:
    """Liệt kê tên và số ảnh đăng ký của từng người."""
    result = []
    for person_dir in sorted(KNOWN_FACES_DIR.iterdir()):
        if not person_dir.is_dir():
            continue
        enc_file = person_dir / "encodings.npy"
        n_enc = 0
        if enc_file.exists():
            n_enc = len(np.load(str(enc_file)))
        images = [
            f.name
            for f in person_dir.iterdir()
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")
        ]
        result.append(
            {"name": person_dir.name, "num_encodings": n_enc, "images": images}
        )
    return result


def delete_person(name: str) -> bool:
    """Xoá toàn bộ dữ liệu khuôn mặt của 1 người."""
    person_dir = KNOWN_FACES_DIR / name
    if person_dir.exists() and person_dir.is_dir():
        shutil.rmtree(person_dir)
        return True
    return False

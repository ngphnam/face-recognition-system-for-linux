"""
recognizer.py - Nhận diện khuôn mặt realtime qua webcam hoặc từ ảnh.

Sử dụng thư viện face_recognition (dựa trên dlib).
Thuật toán:
  1. Phát hiện vị trí khuôn mặt (HOG hoặc CNN).
  2. Tính 128-d face encoding.
  3. So sánh với database (khoảng cách Euclidean, ngưỡng 0.5).
"""

from pathlib import Path

import cv2
import face_recognition
import numpy as np

from face_db import load_database

# Ngưỡng nhận diện – càng nhỏ càng chặt
TOLERANCE = 0.5


def _best_match(
    face_encoding: np.ndarray,
    known_encodings: list[np.ndarray],
    known_names: list[str],
) -> tuple[str, float]:
    """
    Tìm người khớp nhất.
    Returns (tên, khoảng cách). Nếu không khớp → ("Unknown", 999).
    """
    if not known_encodings:
        return "Unknown", 999.0

    distances = face_recognition.face_distance(known_encodings, face_encoding)
    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])

    if best_dist <= TOLERANCE:
        return known_names[best_idx], best_dist
    return "Unknown", best_dist


def recognize_from_webcam() -> None:
    """Nhận diện khuôn mặt realtime từ webcam."""
    known_names, known_encodings = load_database()
    if not known_names:
        print("⚠️  Database trống! Hãy đăng ký ít nhất 1 khuôn mặt trước.")
        return

    print(f"✅ Đã nạp {len(known_encodings)} encoding(s) của {len(set(known_names))} người.")
    print("   Nhấn [Q] để thoát.\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở webcam!")
        return

    # Xử lý mỗi frame thứ 2 để tăng tốc
    process_frame = True

    face_locations_cache: list = []
    face_labels_cache: list = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if process_frame:
            # Giảm kích thước để xử lý nhanh hơn
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            labels: list[tuple[str, float]] = []
            for enc in face_encodings:
                name, dist = _best_match(enc, known_encodings, known_names)
                labels.append((name, dist))

            # Scale lại toạ độ
            face_locations_cache = [
                (top * 4, right * 4, bottom * 4, left * 4)
                for top, right, bottom, left in face_locations
            ]
            face_labels_cache = labels

        process_frame = not process_frame

        # Vẽ kết quả
        for (top, right, bottom, left), (name, dist) in zip(
            face_locations_cache, face_labels_cache
        ):
            if name == "Unknown":
                color = (0, 0, 255)  # Đỏ
            else:
                color = (0, 200, 0)  # Xanh lá

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Label phía dưới
            label = f"{name} ({dist:.2f})" if name != "Unknown" else "Unknown"
            label_h = 25
            cv2.rectangle(
                frame,
                (left, bottom),
                (right, bottom + label_h),
                color,
                cv2.FILLED,
            )
            cv2.putText(
                frame,
                label,
                (left + 6, bottom + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

        cv2.imshow("Face Recognition - Nhan Q de thoat", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def recognize_from_image(image_path: str) -> list[dict]:
    """
    Nhận diện khuôn mặt từ file ảnh.
    Returns danh sách dict: [{"name": ..., "distance": ..., "location": ...}]
    """
    known_names, known_encodings = load_database()
    if not known_names:
        print("⚠️  Database trống!")
        return []

    img = face_recognition.load_image_file(image_path)
    locations = face_recognition.face_locations(img, model="hog")
    encodings = face_recognition.face_encodings(img, locations)

    results: list[dict] = []
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    for loc, enc in zip(locations, encodings):
        name, dist = _best_match(enc, known_encodings, known_names)
        top, right, bottom, left = loc
        results.append(
            {"name": name, "distance": round(dist, 4), "location": loc}
        )

        color = (0, 200, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(img_bgr, (left, top), (right, bottom), color, 2)
        label = f"{name} ({dist:.2f})"
        cv2.putText(
            img_bgr,
            label,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    # Lưu ảnh kết quả
    out_path = Path(image_path).stem + "_result.jpg"
    cv2.imwrite(out_path, img_bgr)
    print(f"📁 Ảnh kết quả đã lưu: {out_path}")

    return results

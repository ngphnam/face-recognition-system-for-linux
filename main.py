#!/usr/bin/env python3
"""
main.py – Chương trình chính: Face Recognition System.

Giao diện menu console:
  1. Đăng ký khuôn mặt (webcam)
  2. Đăng ký khuôn mặt (ảnh)
  3. Nhận diện qua webcam (realtime)
  4. Nhận diện từ ảnh
  5. Danh sách đã đăng ký
  6. Xoá người đã đăng ký
  0. Thoát
"""

import sys
from pathlib import Path

from face_db import (
    register_face_from_webcam,
    register_face_from_image,
    list_registered,
    delete_person,
)
from recognizer import recognize_from_webcam, recognize_from_image

BANNER = r"""
╔═══════════════════════════════════════════════════╗
║        🧑‍💻  FACE RECOGNITION SYSTEM  🧑‍💻          ║
║     Python • OpenCV • face_recognition (dlib)     ║
╠═══════════════════════════════════════════════════╣
║  1. Đăng ký khuôn mặt  (webcam)                  ║
║  2. Đăng ký khuôn mặt  (từ file ảnh)             ║
║  3. Nhận diện realtime  (webcam)                  ║
║  4. Nhận diện từ ảnh                              ║
║  5. Danh sách người đã đăng ký                    ║
║  6. Xoá người đã đăng ký                         ║
║  0. Thoát                                        ║
╚═══════════════════════════════════════════════════╝
"""


def _input(prompt: str) -> str:
    """Wrapper để bắt Ctrl-C / Ctrl-D."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def menu_register_webcam() -> None:
    """Đăng ký khuôn mặt qua webcam."""
    name = _input("  Nhập tên người cần đăng ký: ")
    if not name:
        print("  ⚠️  Tên không được để trống!")
        return

    samples = _input("  Số ảnh muốn chụp (mặc định 5): ")
    num = int(samples) if samples.isdigit() and int(samples) > 0 else 5

    count = register_face_from_webcam(name, num_samples=num)
    if count > 0:
        print(f"\n  ✅ Đã đăng ký thành công {count} ảnh cho '{name}'.")
    else:
        print(f"\n  ❌ Không đăng ký được ảnh nào cho '{name}'.")


def menu_register_image() -> None:
    """Đăng ký khuôn mặt từ file ảnh."""
    name = _input("  Nhập tên người cần đăng ký: ")
    if not name:
        print("  ⚠️  Tên không được để trống!")
        return

    path = _input("  Đường dẫn file ảnh: ")
    if not path or not Path(path).is_file():
        print(f"  ❌ File không tồn tại: {path}")
        return

    ok = register_face_from_image(name, path)
    if ok:
        print(f"\n  ✅ Đã đăng ký thành công cho '{name}' từ ảnh.")
    else:
        print("  ❌ Không phát hiện được khuôn mặt trong ảnh!")


def menu_recognize_webcam() -> None:
    """Nhận diện realtime từ webcam."""
    print("\n  🔍 Đang khởi động nhận diện realtime...")
    recognize_from_webcam()


def menu_recognize_image() -> None:
    """Nhận diện từ file ảnh."""
    path = _input("  Đường dẫn file ảnh: ")
    if not path or not Path(path).is_file():
        print(f"  ❌ File không tồn tại: {path}")
        return

    results = recognize_from_image(path)
    if not results:
        print("  ℹ️  Không tìm thấy khuôn mặt nào trong ảnh.")
        return

    print(f"\n  📋 Tìm thấy {len(results)} khuôn mặt:\n")
    print(f"  {'#':<4} {'Tên':<20} {'Khoảng cách':<15} {'Vị trí'}")
    print(f"  {'─'*4} {'─'*20} {'─'*15} {'─'*30}")
    for i, r in enumerate(results, 1):
        top, right, bottom, left = r["location"]
        print(
            f"  {i:<4} {r['name']:<20} {r['distance']:<15.4f} "
            f"(top={top}, right={right}, bottom={bottom}, left={left})"
        )


def menu_list() -> None:
    """Liệt kê người đã đăng ký."""
    people = list_registered()
    if not people:
        print("  ℹ️  Chưa có ai được đăng ký.")
        return

    print(f"\n  📋 Danh sách ({len(people)} người):\n")
    print(f"  {'#':<4} {'Tên':<25} {'Số encoding':<15} {'Ảnh'}")
    print(f"  {'─'*4} {'─'*25} {'─'*15} {'─'*30}")
    for i, p in enumerate(people, 1):
        imgs = ", ".join(p["images"][:3])
        if len(p["images"]) > 3:
            imgs += f" ... (+{len(p['images'])-3})"
        print(f"  {i:<4} {p['name']:<25} {p['num_encodings']:<15} {imgs}")


def menu_delete() -> None:
    """Xoá người đã đăng ký."""
    name = _input("  Nhập tên người cần xoá: ")
    if not name:
        return

    confirm = _input(f"  ⚠️  Xác nhận xoá '{name}'? (y/N): ")
    if confirm.lower() != "y":
        print("  Đã huỷ.")
        return

    if delete_person(name):
        print(f"  ✅ Đã xoá '{name}' khỏi database.")
    else:
        print(f"  ❌ Không tìm thấy '{name}'.")


def main() -> None:
    """Vòng lặp menu chính."""
    actions = {
        "1": menu_register_webcam,
        "2": menu_register_image,
        "3": menu_recognize_webcam,
        "4": menu_recognize_image,
        "5": menu_list,
        "6": menu_delete,
    }

    while True:
        print(BANNER)
        choice = _input("  👉 Chọn chức năng (0-6): ")

        if choice == "0":
            print("\n  👋 Tạm biệt!\n")
            sys.exit(0)

        handler = actions.get(choice)
        if handler:
            print()
            handler()
            _input("\n  ⏎  Nhấn Enter để quay lại menu...")
        else:
            print("  ❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os
import sys
import shutil
# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import face_recognition
import numpy as np
from pathlib import Path

DATA_DIR = "/var/lib/face-auth"

def init_user_dir(username):
    user_dir = Path(DATA_DIR) / username
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def add_face_webcam(username, num_samples=5):
    user_dir = init_user_dir(username)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam!")
        return False

    encodings_list = []
    existing_images = list(user_dir.glob("face_*"))
    idx = len(existing_images)
    captured = 0

    print(f"\n Preparing to capture {num_samples} images for '{username}'.")
    print("   Press [SPACE] to capture, [Q] to cancel.\n")

    while captured < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        h, w = display.shape[:2]
        cv2.putText(
            display,
            f"Captured: {captured}/{num_samples}  |  SPACE=capture  Q=cancel",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model="hog")
        for top, right, bottom, left in locations:
            cv2.rectangle(display, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("PAM Face Registration", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Cancelled.")
            break

        if key == ord(" "):
            if not locations:
                print("No face detected, try again!")
                continue

            encs = face_recognition.face_encodings(rgb, locations)
            if encs:
                idx += 1
                captured += 1
                img_path = user_dir / f"face_{idx}.jpg"
                cv2.imwrite(str(img_path), frame)
                encodings_list.append(encs[0])
                print(f"   Image {captured}/{num_samples} saved.")

    cap.release()
    cv2.destroyAllWindows()

    if encodings_list:
        enc_file = user_dir / "encodings.npy"
        new_encs = np.array(encodings_list)
        if enc_file.exists():
            existing = np.load(str(enc_file))
            new_encs = np.vstack([existing, new_encs])
        np.save(str(enc_file), new_encs)
        return True
    return False

def list_faces():
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print("Database not found.")
        return
    
    print("\nRegistered faces list:")
    for user_dir in data_path.iterdir():
        if user_dir.is_dir():
            enc_file = user_dir / "encodings.npy"
            n_enc = len(np.load(str(enc_file))) if enc_file.exists() else 0
            print(f" - {user_dir.name}: {n_enc} encodings")

def remove_face(username):
    user_dir = Path(DATA_DIR) / username
    if user_dir.exists():
        shutil.rmtree(user_dir)
        print(f"Deleted data for user '{username}'.")
    else:
        print(f"Data for user '{username}' not found.")

def main():
    if os.geteuid() != 0:
        print("Please run this command with sudo!")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: face-auth [add|list|remove|test]")
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "add":
        username = input("Enter Linux username: ").strip()
        if username:
            add_face_webcam(username)
    elif cmd == "list":
        list_faces()
    elif cmd == "remove":
        username = input("Enter Linux username to remove: ").strip()
        if username:
            remove_face(username)
    elif cmd == "test":
        username = input("Enter Linux username to test: ").strip()
        if username:
            import subprocess
            print("Running test (5s timeout)...")
            res = subprocess.run(["/usr/local/lib/face-auth/pam_face_auth.py", username])
            if res.returncode == 0:
                print("Test successful: Face recognized!")
            else:
                print("Test failed: Face not recognized or timeout.")
    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()

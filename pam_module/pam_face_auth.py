#!/usr/bin/env python3
import os
import sys
import time
import syslog
# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import face_recognition
import numpy as np

TIMEOUT_SECS = 5
TOLERANCE = 0.5
DATA_DIR = "/var/lib/face-auth"

def log(msg):
    syslog.syslog(syslog.LOG_INFO, f"pam_face_auth: {msg}")

def print_user(msg):
    # Khi dùng pam_exec.so với tuỳ chọn 'stdout', output từ stdout sẽ được 
    # chuyển tiếp chuẩn xác qua PAM_TEXT_INFO (giống như cách Howdy làm bằng C++)
    print(f"[Face Auth] {msg}", flush=True)

def auth(username):
    user_dir = os.path.join(DATA_DIR, username)
    encodings_path = os.path.join(user_dir, "encodings.npy")

    if not os.path.exists(encodings_path):
        log(f"User {username} has no face encodings at {encodings_path}")
        return False

    try:
        known_encodings = np.load(encodings_path)
    except Exception as e:
        log(f"Failed to load encodings for {username}: {e}")
        return False

    if len(known_encodings) == 0:
        log(f"User {username} has empty encodings")
        return False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log("Failed to open webcam")
        return False

    start_time = time.time()
    success = False
    dark_frames_count = 0
    total_frames = 0
    DARK_THRESHOLD = 80  # Tăng ngưỡng lên 80 để dễ nhận diện môi trường tối hơn

    print_user(f"Attempting facial authentication for {username}...")
    log(f"Starting face auth for {username}...")

    while time.time() - start_time < TIMEOUT_SECS:
        ret, frame = cap.read()
        if not ret:
            continue

        total_frames += 1
        # Tính độ sáng trung bình của frame
        brightness = np.mean(frame)
        if brightness < DARK_THRESHOLD:
            dark_frames_count += 1

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        if not face_locations:
            continue

        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
            if True in matches:
                success = True
                break
        
        if success:
            break

    cap.release()
    if success:
        print_user(f"Identified face as {username}")
        log(f"Face recognized successfully for {username}")
    else:
        if total_frames > 0 and (dark_frames_count / total_frames) > 0.7:
            print_user("The environment is too dark, Face ID cannot be scanned")
            log(f"Face not recognized for {username} - Environment too dark (avg brightness < {DARK_THRESHOLD})")
        else:
            print_user("Facial authentication failed")
            log(f"Face not recognized for {username} within timeout")
    
    return success

if __name__ == "__main__":
    # PAM sets PAM_USER
    username = os.environ.get("PAM_USER", "")
    if not username:
        # Fallback to sys.argv[1] if testing manually
        if len(sys.argv) > 1:
            username = sys.argv[1]
        else:
            log("No PAM_USER environment variable and no argument provided")
            sys.exit(1)

    if auth(username):
        sys.exit(0)
    else:
        sys.exit(1)

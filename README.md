# 🧑‍💻 Face Recognition System

Hệ thống nhận diện khuôn mặt sử dụng Python, OpenCV và thư viện `face_recognition` (dlib).

## ✨ Tính năng

| #  | Tính năng                         | Mô tả                                                   |
|----|-----------------------------------|----------------------------------------------------------|
| 1  | Đăng ký khuôn mặt (webcam)       | Chụp nhiều ảnh từ webcam để đăng ký                      |
| 2  | Đăng ký khuôn mặt (file ảnh)     | Đăng ký từ file ảnh có sẵn (jpg, png, bmp)               |
| 3  | Nhận diện realtime (webcam)       | Nhận diện khuôn mặt trực tiếp qua webcam                 |
| 4  | Nhận diện từ ảnh                  | Nhận diện khuôn mặt trong file ảnh                        |
| 5  | Quản lý database                  | Liệt kê / xoá người đã đăng ký                           |

## 🛠 Yêu cầu hệ thống

- **Python** >= 3.9
- **cmake** (để build dlib)
- Webcam (nếu muốn dùng chức năng camera)

### Cài đặt trên Ubuntu/Debian

```bash
# Cài đặt các dependency hệ thống
sudo apt-get update
sudo apt-get install -y python3-dev cmake build-essential libopenblas-dev liblapack-dev

# (Tuỳ chọn) Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện Python
pip install -r requirements.txt
```

### Cài đặt trên macOS

```bash
brew install cmake
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Cài đặt trên Windows

```bash
# Cài Visual Studio Build Tools (C++ workload)
# Cài cmake: https://cmake.org/download/

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Sử dụng

```bash
# Chạy chương trình
python main.py
```

Chương trình sẽ hiển thị menu:

```
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
```

## 🔒 Tích hợp xác thực khuôn mặt hệ thống (Linux PAM)

Dự án cung cấp một module PAM tùy chỉnh trong thư mục `pam_module`, cho phép bạn đăng nhập máy tính hoặc chạy lệnh `sudo` bằng khuôn mặt (có thể dùng để thay thế `howdy`).

### Bước 1: Cài đặt Module PAM
Di chuyển vào thư mục `pam_module` và chạy script cài đặt:
```bash
cd pam_module
sudo bash install.sh
```
Script sẽ sao chép các file hệ thống và import dữ liệu khuôn mặt đã đăng ký từ `known_faces/` sang thư mục an toàn của PAM (`/var/lib/face-auth`).

### Bước 2: Quản lý và Kiểm tra
Sử dụng công cụ `face-auth` để quản lý khuôn mặt xác thực hệ thống:
- Đăng ký khuôn mặt mới: `sudo face-auth add`
- Kiểm tra danh sách: `sudo face-auth list`
- **Test nhận diện (BẮT BUỘC):** `sudo face-auth test`

> ⚠️ **Chú ý:** Luôn phải test thử và đảm bảo thành công trước khi gắn vào PAM để tránh bị khóa ngoài hệ thống.

### Bước 3: Gắn vào hệ thống PAM
*Lưu ý: Luôn giữ một cửa sổ Terminal có quyền `root` mở sẵn để phòng trường hợp cấu hình sai cần khôi phục.*

Thay thế cấu hình PAM hiện tại (ví dụ: đang dùng `pam_howdy.so`):
```bash
# 1. Cho lệnh sudo
sudo sed -i 's/auth.*pam_howdy.so/auth      [success=done default=ignore]  pam_exec.so  seteuid \/usr\/local\/lib\/face-auth\/pam_face_auth.py/' /etc/pam.d/sudo

# 2. Cho màn hình đăng nhập / khóa
sudo sed -i 's/auth.*pam_howdy.so/auth      [success=done default=ignore]  pam_exec.so  seteuid \/usr\/local\/lib\/face-auth\/pam_face_auth.py/' /etc/pam.d/system-auth
sudo sed -i 's/auth.*pam_howdy.so/auth      [success=done default=ignore]  pam_exec.so  seteuid \/usr\/local\/lib\/face-auth\/pam_face_auth.py/' /etc/pam.d/gdm-password
```

### Bước 4: Gỡ cài đặt
```bash
cd pam_module
sudo bash uninstall.sh
```

## 📂 Cấu trúc project

```
face-recognition-system/
├── main.py              # Chương trình chính (menu console)
├── face_db.py           # Quản lý database khuôn mặt
├── recognizer.py        # Engine nhận diện
├── requirements.txt     # Thư viện cần cài
├── README.md            # File này
└── known_faces/         # Thư mục lưu dữ liệu khuôn mặt
    ├── NguyenVanA/
    │   ├── face_1.jpg
    │   ├── face_2.jpg
    │   └── encodings.npy
    └── TranVanB/
        ├── face_1.jpg
        └── encodings.npy
```

## ⚙️ Cấu hình

| Tham số       | File            | Giá trị mặc định | Mô tả                                                     |
|---------------|-----------------|-------------------|------------------------------------------------------------|
| `TOLERANCE`   | `recognizer.py` | `0.5`             | Ngưỡng nhận diện (0.4 = chặt, 0.6 = lỏng)                |
| `num_samples` | `face_db.py`    | `5`               | Số ảnh webcam chụp khi đăng ký                              |
| `model`       | cả 2 file       | `"hog"`           | Model phát hiện mặt (`"hog"` nhanh, `"cnn"` chính xác hơn) |

## 📝 Lưu ý

- **Đăng ký nhiều ảnh** ở các góc độ khác nhau sẽ tăng độ chính xác.
- **Ánh sáng tốt** giúp nhận diện chính xác hơn.
- Model `"cnn"` chính xác hơn nhưng cần GPU (CUDA) để chạy nhanh.
- Giảm `TOLERANCE` xuống ~0.4 nếu hay bị nhận nhầm.

## 📄 License

MIT License

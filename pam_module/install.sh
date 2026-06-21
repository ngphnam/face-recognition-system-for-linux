#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run the script with sudo!"
  exit
fi

mkdir -p /usr/local/lib/face-auth
mkdir -p /var/lib/face-auth

cp pam_face_auth.py /usr/local/lib/face-auth/
cp face-auth-cli.py /usr/local/lib/face-auth/

echo "Setting up Python Virtual Environment (venv)..."
python3 -m venv /usr/local/lib/face-auth/venv
/usr/local/lib/face-auth/venv/bin/pip install -r ../requirements.txt

echo "Updating shebang for executable files..."
sed -i '1s|.*|#!/usr/local/lib/face-auth/venv/bin/python|' /usr/local/lib/face-auth/pam_face_auth.py
sed -i '1s|.*|#!/usr/local/lib/face-auth/venv/bin/python|' /usr/local/lib/face-auth/face-auth-cli.py

chmod +x /usr/local/lib/face-auth/pam_face_auth.py
chmod +x /usr/local/lib/face-auth/face-auth-cli.py

ln -sf /usr/local/lib/face-auth/face-auth-cli.py /usr/local/bin/face-auth

# Import existing faces if user wants
echo "Importing faces from known_faces/ directory (if any)..."
if [ -d "../known_faces" ]; then
    for dir in ../known_faces/*/; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            # By default, we merge everything into $SUDO_USER for convenience
            if [ -n "$SUDO_USER" ]; then
                target_user="$SUDO_USER"
            else
                target_user="root"
            fi
            echo "Found user '$name', moving to /var/lib/face-auth/$target_user/ ..."
            mkdir -p /var/lib/face-auth/$target_user
            if [ -f "$dir/encodings.npy" ]; then
                cp -n "$dir"/*.jpg /var/lib/face-auth/$target_user/ 2>/dev/null
                cp -n "$dir/encodings.npy" /var/lib/face-auth/$target_user/ 2>/dev/null
            fi
        fi
    done
fi
chown -R root:root /var/lib/face-auth
chmod -R 755 /var/lib/face-auth

echo "Files installed successfully!"
echo "Run 'sudo face-auth test' to check before modifying PAM config."

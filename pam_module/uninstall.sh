#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run the script with sudo!"
  exit
fi

echo "Uninstalling custom PAM face-auth..."

rm -f /usr/local/bin/face-auth
rm -rf /usr/local/lib/face-auth
# Delete data if desired, but commented out for safety
# rm -rf /var/lib/face-auth

echo "Restoring PAM config (removing pam_face_auth.py line)..."
sed -i '/pam_face_auth.py/d' /etc/pam.d/sudo
sed -i '/pam_face_auth.py/d' /etc/pam.d/system-auth
sed -i '/pam_face_auth.py/d' /etc/pam.d/gdm-password

echo "Uninstallation complete!"

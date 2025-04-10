fichier rules : 
/etc/udev/rules.d/99-logitech-cameras.rules

contenue : 
# Caméra gauche
SUBSYSTEM=="video4linux", KERNEL=="video[0-9]*", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="0825", ATTRS{serial}=="5C9F62E0", ATTR{index}=="0", SYMLINK+="camera_gauche"

# Caméra droite
SUBSYSTEM=="video4linux", KERNEL=="video[0-9]*", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="0825", ATTRS{serial}=="C0394790", ATTR{index}=="0", SYMLINK+="camera_droite"

# Caméra milieu
SUBSYSTEM=="video4linux", KERNEL=="video[0-9]*", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="08f6", ATTR{index}=="0", SYMLINK+="camera_milieu"



commande utile : 
v4l2-ctl --all --device=/dev/video0 #info general camera

v4l2-ctl --list-formats-ext --device=/dev/camera_droite #

pour update des rules : 
sudo udevadm control --reload-rules
sudo udevadm trigger

nom des camera : 
"/dev/camera_milieu"
"/dev/camera_droite"
"/dev/camera_gauche"
"/dev/camera_milieu_rex"

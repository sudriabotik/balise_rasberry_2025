# Liste les contr�les disponibles pour /dev/camera_haut
v4l2-ctl -d /dev/camera_haut --list-ctrls

buntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --list-ctrls

User Controls

                     brightness 0x00980900 (int)    : min=-64 max=64 step=1 default=0 value=0
                       contrast 0x00980901 (int)    : min=0 max=64 step=1 default=32 value=32
                     saturation 0x00980902 (int)    : min=0 max=128 step=1 default=85 value=85
                            hue 0x00980903 (int)    : min=-40 max=40 step=1 default=0 value=0
        white_balance_automatic 0x0098090c (bool)   : default=1 value=1
                          gamma 0x00980910 (int)    : min=72 max=500 step=1 default=100 value=100
                           gain 0x00980913 (int)    : min=0 max=100 step=1 default=0 value=0
           power_line_frequency 0x00980918 (menu)   : min=0 max=2 default=1 value=1 (50 Hz)
      white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=1 default=4600 value=4600 flags=inactive
                      sharpness 0x0098091b (int)    : min=0 max=6 step=1 default=3 value=3
         backlight_compensation 0x0098091c (int)    : min=0 max=6 step=1 default=3 value=3

Camera Controls

                  auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=3 (Aperture Priority Mode)
         exposure_time_absolute 0x009a0902 (int)    : min=1 max=5000 step=1 default=157 value=157 flags=inactive
     exposure_dynamic_framerate 0x009a0903 (bool)   : default=0 value=1

ubuntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --set-crtl=auto_exposure=0
v4l2-ctl: unrecognized option '--set-crtl=auto_exposure=0'

ubuntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --set-ctrl=auto_exposure=0
VIDIOC_S_EXT_CTRLS: failed: Invalid argument
Error setting controls: Invalid argument

v4l2-ctl -d /dev/camera_haut --list-ctrls-menus | grep -A4 auto_exposure

ubuntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --list-ctrls-menus | grep -A4 auto_exposure
                  auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=3 (Aperture Priority Mode)
				1: Manual Mode
				3: Aperture Priority Mode
         exposure_time_absolute 0x009a0902 (int)    : min=1 max=5000 step=1 default=157 value=157 flags=inactive
     exposure_dynamic_framerate 0x009a0903 (bool)   : default=0 value=1
ubuntu@ubuntu-desktop:~$ 

v4l2-ctl -d /dev/camera_haut --list-ctrls | grep exposure_time_absolute
# → plus de flag “inactive”

v4l2-ctl -d /dev/camera_haut --set-ctrl=exposure_time_absolute=200
v4l2-ctl -d /dev/camera_haut --get-ctrl=exposure_time_absolute

ubuntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --list-ctrls | grep exposure_time_absolute
         exposure_time_absolute 0x009a0902 (int)    : min=1 max=5000 step=1 default=157 value=5000
ubuntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --set-ctrl=exposure_time_absolute=200
ubuntu@ubuntu-desktop:~$ v4l2-ctl -d /dev/camera_haut --get-ctrl=exposure_time_absolute
exposure_time_absolute: 200
ubuntu@ubuntu-desktop:~$ 


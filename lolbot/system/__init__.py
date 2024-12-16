import sys

if sys.platform == "darwin":  # macOS
    from .macos import mouse, keys, window, cmd
    RESOLUTION = (584, 383)
    OS = 'macOS'
    font_path = "/System/Library/Fonts/STHeiti Light.ttc"
elif sys.platform == "win32":  # Windows
    from .windows import mouse, keys, window, cmd
    version_info = sys.getwindowsversion()
    if version_info.major == 10 and version_info.build >= 22000:
        RESOLUTION = (606, 440)
    else:
        RESOLUTION = (600, 420)
    OS = 'Windows'
    font_path = r"C:\Windows\Fonts\simsun.ttc"
else:
    raise ImportError("Unsupported operating system")

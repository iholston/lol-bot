import sys

if sys.platform == "darwin":  # macOS
    from .macos import mouse, keys, window, cmd
    RESOLUTION = (584, 383)
    OS = 'macOS'
elif sys.platform == "win32":  # Windows
    from .windows import mouse, keys, window, cmd
    RESOLUTION = (600, 420)
    OS = 'Windows'
else:
    raise ImportError("Unsupported operating system")

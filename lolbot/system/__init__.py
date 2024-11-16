import sys

if sys.platform == "darwin":  # macOS
    from .macos import mouse, keys, window, cmd
elif sys.platform == "win32":  # Windows
    from .windows import mouse, keys, window, cmd
else:
    raise ImportError("Unsupported operating system")

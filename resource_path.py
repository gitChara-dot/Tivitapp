import sys,os
def resource_path(relative_path):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = sys._MEIPASS
        else:
            base = os.path.abspath(".")

        return os.path.join(base, relative_path)

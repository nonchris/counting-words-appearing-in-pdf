import sys

if __package__ is None and not hasattr(sys, "frozen"):
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

from count_names.ui import App
from count_names.entry import read_and_extract


def main_ui():
    app = App()
    app.run_ui()


def main(doc, out_path=""):
    """Entry point for the application script"""
    read_and_extract(doc, out_path)


if __name__ == '__main__':
    print("MAIN")
    # this is more the developer mode without the ui
    # main("../../document.docx")
    main("../../mythopoetiques-dantesques-livre.pdf", "out.txt")
    # run_ui()

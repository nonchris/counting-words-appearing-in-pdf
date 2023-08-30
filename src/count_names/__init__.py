from entry import read_and_extract

def main(doc, out_path=""):
    """Entry point for the application script"""
    read_and_extract(doc, out_path)


if __name__ == '__main__':
    # main("../../document.docx")
    main("../../mythopoetiques-dantesques-livre.pdf", "out.txt")

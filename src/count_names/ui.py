import threading
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog
import os
from ctypes import windll

from count_names.entry import read_and_extract
from count_names.version import __version__


class App:
    def __init__(self):
        self.window_initialized = False
        self.window = None
        self.custom_font = None

        self.pdf_file_entry = None
        self.pdf_file_label = None

        self.page_offset_entry = None
        self.page_offset_label = None

        self.blacklist_entry = None
        self.blacklist_label = None

        self.output_dir_entry = None
        self.output_dir_label = None
        self.output_file_entry = None
        self.output_file_label = None
        self.output_hint_label = None
        self.result_label = None

        self.init_app()

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], initialdir=os.getcwd())
        self.pdf_file_entry.delete(0, tk.END)
        self.pdf_file_entry.insert(tk.END, file_path)
        self.pdf_file_label.config(text="Selected PDF:\n" + file_path, font=self.custom_font)

    def select_blacklist_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("text files", "*.txt")], initialdir=os.getcwd())
        self.blacklist_entry.delete(0, tk.END)
        self.blacklist_entry.insert(tk.END, file_path)
        self.blacklist_label.config(text="Selected PDF:\n" + file_path, font=self.custom_font)

    def select_output_directory(self):
        output_dir = filedialog.askdirectory(initialdir=os.getcwd())
        self.output_dir_entry.delete(0, tk.END)
        self.output_dir_entry.insert(tk.END, output_dir)
        self.output_dir_label.config(text="Selected Output Directory:\n" + output_dir, font=self.custom_font)

    def run_detection_try_wrapper(self, label_to_update=None):
        """ this should be called in production """
        try:
            self._run_detection(label_to_update=label_to_update)

        except Exception as e:
            self.result_label.config(text=f"Something went wrong.\n"
                                          f"Please check your inputs again!\n"
                                          f"\n"
                                          f"Error: '{type(e).__name__}'\n"
                                          f"Detail:\n"
                                          f"{e}", font=self.custom_font)

    def _run_detection(self, label_to_update=None):
        """
        the actual detection function
        executes word detection, writing,
        waits for end of detection updates label at the end and tries to open an explorer window

        use run_conversion_try_wrapper() to avoid an ui-crash if something fails
        """
        pdf_file = self.pdf_file_entry.get()
        blacklist_file = self.blacklist_entry.get()
        offset_entry = self.page_offset_entry.get()
        page_offset_entry = int(offset_entry) if offset_entry else 0
        output_dir = self.output_dir_entry.get()
        output_file = self.output_file_entry.get()

        # TODO: maybe ask when the file already exists

        out_path = f"{output_dir}/{output_file}.txt"
        path = Path(out_path)
        path_to_show = path.relative_to(path.home())

        # put counting in a thread, this might take a while!
        thread = threading.Thread(target=read_and_extract, args=(pdf_file,), daemon=True,
                                  kwargs=dict(
                                      report_to_console=False,
                                      write_result_to=out_path,
                                      label_to_update=label_to_update,
                                      blacklist_file=blacklist_file,
                                      page_offset_entry=page_offset_entry
                                  ),
                                  )

        thread.start()

        def wait_show_result():
            """ helper to check if thread is still going and finish task when it's done """
            # if we're not done, reschedule
            if thread.is_alive():
                self.window.after(1000, wait_show_result)
                return

            # try to open an explorer
            result_text = f"Result saved under:\n{path_to_show}"
            try:
                self.result_label.config(text=result_text, font=self.custom_font)
                os.startfile(output_dir)

            except AttributeError:
                self.result_label.config(
                    text=f"{result_text}\n"
                         f"Can't open a file-manager on this operation system.\n",
                    font=self.custom_font
                )

        # schedule first check if we're done
        self.window.after(1000, wait_show_result)

    def whitespace(self, cols=1):
        for i in range(0, cols):
            run_label = tk.Label(self.window, text="", font=self.custom_font)
            run_label.pack()

    def run_ui(self):
        # Start the main event loop
        self.window.mainloop()

    def init_app(self):
        if not self.window_initialized:
            # Create the main window
            self.window = tk.Tk()
            windll.shcore.SetProcessDpiAwareness(1)

            self.window.title(f"Noun-Finder v{__version__}")

            # Create a custom font with a specific size
            self.custom_font = tkfont.Font(size=12)

            x_size = 700
            y_size = 1000

            self.window.geometry(f"{x_size}x{y_size}")

            self.whitespace()

            # Create the PDF selection button
            pdf_button = tk.Button(self.window, text="Select PDF", command=self.select_pdf, font=self.custom_font)
            pdf_button.pack()

            # Create the PDF file entry field
            self.pdf_file_label = tk.Label(self.window, text="PDF File:", font=self.custom_font)
            self.pdf_file_label.pack()
            self.pdf_file_entry = tk.Entry(self.window, font=self.custom_font)
            self.pdf_file_entry.pack()

            self.whitespace(2)

            # Create the output file name entry field
            self.page_offset_label = tk.Label(self.window, text="Pages before page '1':",
                                              font=self.custom_font)
            self.page_offset_label.pack()
            self.page_offset_entry = tk.Entry(self.window, font=self.custom_font)
            self.page_offset_entry.pack()

            self.whitespace(2)

            # Create the output directory selection button
            output_dir_button = tk.Button(self.window, text="Select Output Directory",
                                          command=self.select_output_directory, font=self.custom_font)
            output_dir_button.pack()

            # Create the output directory entry field
            self.output_dir_label = tk.Label(self.window, text="Output Directory:", font=self.custom_font)
            self.output_dir_label.pack()
            self.output_dir_entry = tk.Entry(self.window, font=self.custom_font)
            self.output_dir_entry.pack()

            self.whitespace(2)

            # Create the output file name entry field
            self.output_file_label = tk.Label(self.window, text="Output File Name:", font=self.custom_font)
            self.output_file_label.pack()
            self.output_file_entry = tk.Entry(self.window, font=self.custom_font)
            self.output_file_entry.pack()
            self.output_hint_label = tk.Label(self.window, text="(Ending of the file will be .txt)",
                                              font=self.custom_font)
            self.output_hint_label.pack()

            self.whitespace(2)

            # Create blacklist selection button
            blacklist_button = tk.Button(self.window, text="Select a textfile with words to BLACKLIST",
                                         command=self.select_blacklist_file, font=self.custom_font)
            blacklist_button.pack()

            # Create the output directory entry field
            self.blacklist_label = tk.Label(self.window, text="Blacklist file:", font=self.custom_font)
            self.blacklist_label.pack()
            self.blacklist_entry = tk.Entry(self.window, font=self.custom_font)
            self.blacklist_entry.pack()

            self.whitespace(2)

            run_label = tk.Label(self.window, text="", font=self.custom_font)
            run_label.pack()

            # create label before button to be able to pass it into the function
            self.result_label = tk.Label(self.window, text="", font=self.custom_font)

            # Create the run button
            run_button = tk.Button(self.window, text="Run Conversion",
                                   command=lambda: self._run_detection(label_to_update=self.result_label),
                                   font=self.custom_font)
            run_button.pack()

            self.whitespace(1)

            # now pack result label below button
            self.result_label.pack()

            self.window_initialized = True

        self.run_ui()


if __name__ == '__main__':
    app = App()
    app.run_ui()

import os
import sys
import subprocess
import threading
import time
import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import messagebox, Toplevel, Canvas, filedialog, Text
from PIL import ImageGrab, Image, ImageTk
import pytesseract


VERSION = "v1.02"
github_link = "https://github.com/df8819/PixelReader7/"

# Set the tesseract command if not set in the PATH environment variable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust the path to tesseract executable

REFRESH_RATE = 50  # Refresh rate in milliseconds


class ScreenReaderApp:
    def __init__(self, root):
        self.root = root

        # Check if Tesseract is installed at the given path
        self.tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if not os.path.exists(self.tesseract_path):
            self.tesseract_path = filedialog.askopenfilename(
                title="Select Tesseract Executable",
                filetypes=[("Executable files", "*.exe")]
            )
            if not self.tesseract_path:
                messagebox.showerror("File Not Found",
                                     "Tesseract executable not found. Please install or select the correct file.")
                root.destroy()
                return
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        self.setup_ui()
        self.is_running = True
        self.update_thread = threading.Thread(target=self.update_preview)
        self.update_thread.daemon = True  # Ensure the thread exits when the main program does
        self.update_thread.start()

    def setup_ui(self):
        self.root.title("PixelReader7 - Extract text from everything")
        self.root.geometry("500x650")
        self.center_window(self.root)  # Center the main window
        self.root.resizable(False, False)

        style = Style(theme="superhero")  # Use the 'superhero' theme from ttkbootstrap

        # Dimension entry
        ttk.Label(self.root, text="X:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_x = ttk.Entry(self.root)
        self.entry_x.grid(row=0, column=1, padx=10, pady=5)
        self.entry_x.insert(0, "500")

        ttk.Label(self.root, text="Y:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_y = ttk.Entry(self.root)
        self.entry_y.grid(row=1, column=1, padx=10, pady=5)
        self.entry_y.insert(0, "500")

        ttk.Label(self.root, text="Width:").grid(row=2, column=0, padx=10, pady=5)
        self.entry_width = ttk.Entry(self.root)
        self.entry_width.grid(row=2, column=1, padx=10, pady=5)
        self.entry_width.insert(0, "250")

        ttk.Label(self.root, text="Height:").grid(row=3, column=0, padx=10, pady=5)
        self.entry_height = ttk.Entry(self.root)
        self.entry_height.grid(row=3, column=1, padx=10, pady=5)
        self.entry_height.insert(0, "250")

        # Create a frame to hold the buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Select Area Button
        self.select_area_button = ttk.Button(button_frame, text="Select Area", command=self.select_area, bootstyle="secondary")
        self.select_area_button.grid(row=0, column=1, padx=5, pady=5)

        # Read Screen Button
        self.read_button = ttk.Button(button_frame, text="Read Area", command=self.on_read_button_click, bootstyle="primary")
        self.read_button.grid(row=0, column=2, padx=5, pady=5)

        # Extracted.txt Button
        self.extracted_button = ttk.Button(button_frame, text="Extracted.txt", command=self.open_extracted_file, bootstyle="info")
        self.extracted_button.grid(row=0, column=0, padx=5, pady=5)

        # Preview label
        self.text_label = ttk.Label(self.root, text="Live preview of the selected area, ready to be read:")
        self.text_label.grid(row=5, column=0, columnspan=3, padx=10)

        # Preview window
        self.preview_label = ttk.Label(self.root)
        self.preview_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        # Version label
        version_label = ttk.Label(self.root, text=f"Version: {VERSION}")
        version_label.grid(row=7, column=0, columnspan=2, pady=5)

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def read_screen_area(self, x, y, width, height):
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        text = pytesseract.image_to_string(img)
        return text

    def on_read_button_click(self):
        try:
            x = int(self.entry_x.get())
            y = int(self.entry_y.get())
            width = int(self.entry_width.get())
            height = int(self.entry_height.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for dimensions.")
            return

        extracted_text = self.read_screen_area(x, y, width, height)

        # Create a new Toplevel window to display the extracted text
        text_window = Toplevel(self.root)
        text_window.title("Extracted Text")

        # Set window size relative to screen size
        screen_width = text_window.winfo_screenwidth()
        screen_height = text_window.winfo_screenheight()
        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.4)
        text_window.geometry(f"{window_width}x{window_height}")

        self.center_window(text_window)  # Center the new window

        # Create a frame to hold the Text widget
        frame = ttk.Frame(text_window)
        frame.pack(expand=1, fill='both', padx=10, pady=10)

        # Create a Text widget to display the extracted text
        text_widget = Text(frame, wrap='word')
        text_widget.pack(expand=1, fill='both')
        text_widget.insert('1.0', extracted_text)
        text_widget.config(state='normal')  # Make the text selectable

        # Add a button to save the text and close the window
        save_button = ttk.Button(text_window, text="Save Text", command=lambda: self.save_extracted_text(extracted_text, text_window), bootstyle="success")
        save_button.pack(pady=10)

    @staticmethod
    def save_extracted_text(text, window):
        with open("Extracted.txt", "a") as file:
            file.write(text + "\n")
        window.destroy()

    def open_extracted_file(self):
        file_path = "Extracted.txt"
        if os.path.exists(file_path):
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", file_path])
            else:  # linux variants
                subprocess.call(["xdg-open", file_path])
        else:
            messagebox.showinfo("File Not Found", "The Extracted.txt file does not exist yet.")

    def update_preview(self):
        while self.is_running:
            try:
                start_time = time.time()

                x = int(self.entry_x.get())
                y = int(self.entry_y.get())
                width = int(self.entry_width.get())
                height = int(self.entry_height.get())

                img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                img = img.resize((480, 400))
                img = ImageTk.PhotoImage(img)

                self.preview_label.config(image=img)
                self.preview_label.image = img

                elapsed_time = time.time() - start_time
                sleep_time = max(0, (REFRESH_RATE / 1000.0) - elapsed_time)
                time.sleep(sleep_time)
            except ValueError:
                pass
            except Exception as e:
                print(f"Error: {e}")

    def select_area(self):
        self.is_running = False  # Stop the preview update while selecting area
        selection_window = Toplevel(self.root)
        selection_window.attributes("-fullscreen", True)
        selection_window.attributes("-alpha", 0.2)
        self.center_window(selection_window)

        canvas = Canvas(selection_window, cursor="cross")
        canvas.pack(fill=ttk.BOTH, expand=True)

        rect = None
        start_x = start_y = 0

        def on_button_press(event):
            nonlocal rect, start_x, start_y
            start_x = canvas.canvasx(event.x)
            start_y = canvas.canvasy(event.y)
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='yellow', width=2)

        def on_mouse_move(event):
            nonlocal rect
            cur_x = canvas.canvasx(event.x)
            cur_y = canvas.canvasy(event.y)
            canvas.coords(rect, start_x, start_y, cur_x, cur_y)

        def on_button_release(event):
            nonlocal start_x, start_y
            end_x = canvas.canvasx(event.x)
            end_y = canvas.canvasy(event.y)
            selection_window.destroy()

            x = int(min(start_x, end_x))
            y = int(min(start_y, end_y))
            width = int(abs(end_x - start_x))
            height = int(abs(end_y - start_y))

            self.entry_x.delete(0, ttk.END)
            self.entry_x.insert(0, x)
            self.entry_y.delete(0, ttk.END)
            self.entry_y.insert(0, y)
            self.entry_width.delete(0, ttk.END)
            self.entry_width.insert(0, width)
            self.entry_height.delete(0, ttk.END)
            self.entry_height.insert(0, height)

            # Restart preview thread
            self.is_running = True
            self.update_thread = threading.Thread(target=self.update_preview)
            self.update_thread.daemon = True
            self.update_thread.start()

        canvas.bind("<ButtonPress-1>", on_button_press)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_button_release)


if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = ScreenReaderApp(root)
    root.mainloop()

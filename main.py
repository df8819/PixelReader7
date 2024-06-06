import tkinter as tk
from tkinter import messagebox, Toplevel, Canvas
from PIL import ImageGrab, Image, ImageTk
import pytesseract
import threading
import time  # Ensure the correct time module is imported

# Set the tesseract command if not set in the PATH environment variable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust the path to tesseract executable

# Initialize presets
presets = {
    "Placeholder": {"x": 1420, "y": 940, "width": 200, "height": 100}
}

refresh_rate = 100  # Refresh rate in milliseconds


class ScreenReaderApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.is_running = True
        self.update_thread = threading.Thread(target=self.update_preview)
        self.update_thread.daemon = True  # Ensure the thread exits when the main program does
        self.update_thread.start()

    def setup_ui(self):
        self.root.title("Screen Reader")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        tk.Label(self.root, text="X:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_x = tk.Entry(self.root)
        self.entry_x.grid(row=0, column=1, padx=10, pady=5)
        self.entry_x.insert(0, "1000")

        tk.Label(self.root, text="Y:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_y = tk.Entry(self.root)
        self.entry_y.grid(row=1, column=1, padx=10, pady=5)
        self.entry_y.insert(0, "500")

        tk.Label(self.root, text="Width:").grid(row=2, column=0, padx=10, pady=5)
        self.entry_width = tk.Entry(self.root)
        self.entry_width.grid(row=2, column=1, padx=10, pady=5)
        self.entry_width.insert(0, "100")

        tk.Label(self.root, text="Height:").grid(row=3, column=0, padx=10, pady=5)
        self.entry_height = tk.Entry(self.root)
        self.entry_height.grid(row=3, column=1, padx=10, pady=5)
        self.entry_height.insert(0, "100")

        self.preset_var = tk.StringVar(self.root)
        self.preset_var.set("Select Preset")
        self.preset_menu = tk.OptionMenu(self.root, self.preset_var, *presets.keys())
        self.preset_menu.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        self.preset_var.trace("w", self.on_preset_selected)

        self.read_button = tk.Button(self.root, text="Read Screen", command=self.on_read_button_click)
        self.read_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.select_area_button = tk.Button(self.root, text="Select Area", command=self.select_area)
        self.select_area_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.preview_label = tk.Label(self.root)
        self.preview_label.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

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
        save_text = messagebox.askyesno("Confirm Text",
                                        f"Extracted text:\n\n{extracted_text}\n\nDo you want to save this text?")
        if save_text:
            with open("extracted_text.txt", "a") as file:
                file.write(extracted_text + "\n")
            messagebox.showinfo("Success", "Text appended to extracted_text.txt")

    def on_preset_selected(self, *args):
        preset_name = self.preset_var.get()
        if preset_name in presets:
            preset = presets[preset_name]
            self.entry_x.delete(0, tk.END)
            self.entry_x.insert(0, preset["x"])
            self.entry_y.delete(0, tk.END)
            self.entry_y.insert(0, preset["y"])
            self.entry_width.delete(0, tk.END)
            self.entry_width.insert(0, preset["width"])
            self.entry_height.delete(0, tk.END)
            self.entry_height.insert(0, preset["height"])
        self.update_preview()

    def update_preview(self):
        while self.is_running:
            try:
                x = int(self.entry_x.get())
                y = int(self.entry_y.get())
                width = int(self.entry_width.get())
                height = int(self.entry_height.get())
                img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                img = img.resize((480, 320))
                img = ImageTk.PhotoImage(img)
                self.preview_label.config(image=img)
                self.preview_label.image = img
            except ValueError:
                pass
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(refresh_rate / 1000.0)

    def select_area(self):
        self.is_running = False  # Stop the preview update while selecting area
        selection_window = Toplevel(self.root)
        selection_window.attributes("-fullscreen", True)
        selection_window.attributes("-alpha", 0.2)

        canvas = Canvas(selection_window, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)

        rect = None
        start_x = start_y = 0

        def on_button_press(event):
            nonlocal rect, start_x, start_y
            start_x = canvas.canvasx(event.x)
            start_y = canvas.canvasy(event.y)
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

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

            self.entry_x.delete(0, tk.END)
            self.entry_x.insert(0, x)
            self.entry_y.delete(0, tk.END)
            self.entry_y.insert(0, y)
            self.entry_width.delete(0, tk.END)
            self.entry_width.insert(0, width)
            self.entry_height.delete(0, tk.END)
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
    root = tk.Tk()
    app = ScreenReaderApp(root)
    root.mainloop()

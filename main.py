import tkinter as tk
from tkinter import messagebox, Toplevel, Canvas
from PIL import ImageGrab, Image, ImageTk
import pytesseract

# Set the tesseract command if not set in the PATH environment variable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust the path to tesseract executable

# Initialize presets
presets = {
    "Digital Extremes": {"x": 3420, "y": 940, "width": 200, "height": 100}
}

refresh_rate = 250  # Refresh rate in milliseconds

def read_screen_area(x, y, width, height):
    # Capture the screen area
    img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    # Use pytesseract to extract text
    text = pytesseract.image_to_string(img)
    return text

def on_read_button_click():
    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
        width = int(entry_width.get())
        height = int(entry_height.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers for dimensions.")
        return

    # Read the screen area and extract text
    extracted_text = read_screen_area(x, y, width, height)
    # Prompt user to confirm the extracted text
    save_text = messagebox.askyesno("Confirm Text",
                                    f"Extracted text:\n\n{extracted_text}\n\nDo you want to save this text?")
    if save_text:
        with open("extracted_text.txt", "a") as file:  # Change to append mode
            file.write(extracted_text + "\n")
        messagebox.showinfo("Success", "Text appended to extracted_text.txt")

def on_preset_selected(*args):
    preset_name = preset_var.get()
    if preset_name in presets:
        preset = presets[preset_name]
        entry_x.delete(0, tk.END)
        entry_x.insert(0, preset["x"])
        entry_y.delete(0, tk.END)
        entry_y.insert(0, preset["y"])
        entry_width.delete(0, tk.END)
        entry_width.insert(0, preset["width"])
        entry_height.delete(0, tk.END)
        entry_height.insert(0, preset["height"])
    update_preview()

def update_preview():
    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
        width = int(entry_width.get())
        height = int(entry_height.get())
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        img = img.resize((400, 200))  # Resize for the preview window
        img = ImageTk.PhotoImage(img)
        preview_label.config(image=img)
        preview_label.image = img
    except ValueError:
        pass
    root.after(refresh_rate, update_preview)

def select_area():
    selection_window = Toplevel(root)
    selection_window.attributes("-fullscreen", True)
    selection_window.attributes("-alpha", 0.3)

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

        entry_x.delete(0, tk.END)
        entry_x.insert(0, x)
        entry_y.delete(0, tk.END)
        entry_y.insert(0, y)
        entry_width.delete(0, tk.END)
        entry_width.insert(0, width)
        entry_height.delete(0, tk.END)
        entry_height.insert(0, height)
        update_preview()

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_button_release)

# Create the main window
root = tk.Tk()
root.title("Screen Reader")
root.geometry("500x450")  # Increase the size of the main window

# Create and place the input fields and labels with default values
tk.Label(root, text="X:").grid(row=0, column=0, padx=10, pady=5)
entry_x = tk.Entry(root)
entry_x.grid(row=0, column=1, padx=10, pady=5)
entry_x.insert(0, "1000")  # Default value

tk.Label(root, text="Y:").grid(row=1, column=0, padx=10, pady=5)
entry_y = tk.Entry(root)
entry_y.grid(row=1, column=1, padx=10, pady=5)
entry_y.insert(0, "500")  # Default value

tk.Label(root, text="Width:").grid(row=2, column=0, padx=10, pady=5)
entry_width = tk.Entry(root)
entry_width.grid(row=2, column=1, padx=10, pady=5)
entry_width.insert(0, "100")  # Default value

tk.Label(root, text="Height:").grid(row=3, column=0, padx=10, pady=5)
entry_height = tk.Entry(root)
entry_height.grid(row=3, column=1, padx=10, pady=5)
entry_height.insert(0, "100")  # Default value

# Create and place the preset dropdown menu
preset_var = tk.StringVar(root)
preset_var.set("Select Preset")
preset_menu = tk.OptionMenu(root, preset_var, *presets.keys())
preset_menu.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
preset_var.trace("w", on_preset_selected)

# Create and place the buttons
read_button = tk.Button(root, text="Read Screen", command=on_read_button_click)
read_button.grid(row=5, column=0, columnspan=2, pady=10)

select_area_button = tk.Button(root, text="Select Area", command=select_area)
select_area_button.grid(row=6, column=0, columnspan=2, pady=10)

# Create and place the preview label
preview_label = tk.Label(root)
preview_label.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

# Run the preview update function
update_preview()

# Run the Tkinter event loop
root.mainloop()

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import ImageGrab
import pytesseract

# Set the tesseract command if not set in the PATH environment variable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust the path to tesseract executable

# Initialize presets
presets = {
    "Digital Extremes": {"x": 3420, "y": 940, "width": 200, "height": 100}
}


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


def add_preset():
    preset_name = simpledialog.askstring("Preset Name", "Enter preset name:")
    if not preset_name:
        return
    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
        width = int(entry_width.get())
        height = int(entry_height.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers for dimensions.")
        return
    presets[preset_name] = {"x": x, "y": y, "width": width, "height": height}
    preset_menu['menu'].add_command(label=preset_name, command=tk._setit(preset_var, preset_name))
    messagebox.showinfo("Success", f"Preset '{preset_name}' added.")


# Create the main window
root = tk.Tk()
root.title("Screen Reader")

# Create and place the input fields and labels
tk.Label(root, text="X:").grid(row=0, column=0, padx=10, pady=5)
entry_x = tk.Entry(root)
entry_x.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Y:").grid(row=1, column=0, padx=10, pady=5)
entry_y = tk.Entry(root)
entry_y.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Width:").grid(row=2, column=0, padx=10, pady=5)
entry_width = tk.Entry(root)
entry_width.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Height:").grid(row=3, column=0, padx=10, pady=5)
entry_height = tk.Entry(root)
entry_height.grid(row=3, column=1, padx=10, pady=5)

# Create and place the preset dropdown menu
preset_var = tk.StringVar(root)
preset_var.set("Select Preset")
preset_menu = tk.OptionMenu(root, preset_var, *presets.keys())
preset_menu.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
preset_var.trace("w", on_preset_selected)

# Create and place the buttons
read_button = tk.Button(root, text="Read Screen", command=on_read_button_click)
read_button.grid(row=5, column=0, columnspan=2, pady=10)

add_preset_button = tk.Button(root, text="Add Preset", command=add_preset)
add_preset_button.grid(row=6, column=0, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()

import os
import glob
import csv
import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog, messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
SLD_DIR = os.path.join(DATA_DIR, "SLDs")
ANNOTATIONS_DIR = os.path.join(BASE_DIR, "annotations")
OUTPUT_CSV = os.path.join(ANNOTATIONS_DIR, "draft_annotations.csv")

os.makedirs(ANNOTATIONS_DIR, exist_ok=True)

class AnnotationDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Annotation Attributes")
        self.geometry("300x250")
        
        self.result = None
        
        # Rotation
        tk.Label(self, text="Rotation:").pack(pady=5)
        self.rotation_var = tk.StringVar(value="0")
        rotations = ["0", "90", "180", "270", "Unknown"]
        self.rot_menu = tk.OptionMenu(self, self.rotation_var, *rotations)
        self.rot_menu.pack()
        
        # Confidence
        tk.Label(self, text="Confidence:").pack(pady=5)
        self.conf_var = tk.StringVar(value="High")
        confidences = ["High", "Medium", "Low"]
        self.conf_menu = tk.OptionMenu(self, self.conf_var, *confidences)
        self.conf_menu.pack()
        
        # Notes
        tk.Label(self, text="Notes (optional):").pack(pady=5)
        self.notes_entry = tk.Entry(self, width=30)
        self.notes_entry.pack()
        
        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Save", command=self.on_save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
        
    def on_save(self):
        self.result = {
            "rotation": self.rotation_var.get(),
            "confidence": self.conf_var.get(),
            "notes": self.notes_entry.get()
        }
        self.destroy()
        
    def on_cancel(self):
        self.destroy()

class Annotator:
    def __init__(self):
        self.image_paths = sorted(glob.glob(os.path.join(SLD_DIR, "SLD*.png")))
        if not self.image_paths:
            print("No SLD images found.")
            return
            
        self.current_idx = 0
        self.annotations = []
        self.load_existing_annotations()
        
        self.root = tk.Tk()
        self.root.withdraw() # Hide main tkinter window
        
        self.setup_plot()
        
    def load_existing_annotations(self):
        if os.path.exists(OUTPUT_CSV):
            with open(OUTPUT_CSV, "r", newline="") as f:
                reader = csv.DictReader(f)
                self.annotations = list(reader)
            print(f"Loaded {len(self.annotations)} existing annotations.")
            
    def save_annotations(self):
        fieldnames = ["file", "annotation_id", "x", "y", "width", "height", "rotation", "confidence", "notes"]
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.annotations)
        print(f"Saved to {OUTPUT_CSV}")

    def setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        self.drawing = False
        self.current_rect = None
        self.start_x = 0
        self.start_y = 0
        
        self.show_image()
        plt.show()

    def show_image(self):
        self.ax.clear()
        img_path = self.image_paths[self.current_idx]
        self.current_filename = os.path.basename(img_path)
        
        # Load and convert to RGB
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        elif len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
        self.ax.imshow(img)
        self.ax.set_title(f"[{self.current_idx+1}/{len(self.image_paths)}] {self.current_filename}\n"
                          f"Draw: Left-click and drag | Pan/Zoom: Use toolbar | Next/Prev: Right/Left Arrow | Quit: q")
        self.ax.axis('off')
        self.fig.canvas.draw()

    def on_mouse_press(self, event):
        # Ignore if a toolbar tool is active (e.g. pan/zoom) or outside image
        if self.fig.canvas.toolbar.mode != '' or event.button != 1 or not event.inaxes:
            return
        self.drawing = True
        self.start_x = event.xdata
        self.start_y = event.ydata
        self.current_rect = plt.Rectangle((self.start_x, self.start_y), 0, 0, fill=False, edgecolor='red', linewidth=2)
        self.ax.add_patch(self.current_rect)

    def on_mouse_move(self, event):
        if not self.drawing or not event.inaxes:
            return
        self.current_rect.set_width(event.xdata - self.start_x)
        self.current_rect.set_height(event.ydata - self.start_y)
        self.fig.canvas.draw_idle()

    def on_mouse_release(self, event):
        if not self.drawing:
            return
        self.drawing = False
        
        # Remove the temporary drawing rect
        if self.current_rect in self.ax.patches:
            self.current_rect.remove()
        self.fig.canvas.draw_idle()
            
        if not event.inaxes:
            return
            
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.xdata, event.ydata
        
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        if w < 5 or h < 5:
            return  # Ignore tiny accidental clicks
            
        dialog = AnnotationDialog(self.root)
        if dialog.result:
            # Generate ID
            existing_for_file = [a for a in self.annotations if a["file"] == self.current_filename]
            ann_id = f"MR_{len(existing_for_file) + 1:02d}"
            
            ann = {
                "file": self.current_filename,
                "annotation_id": ann_id,
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "rotation": dialog.result["rotation"],
                "confidence": dialog.result["confidence"],
                "notes": dialog.result["notes"]
            }
            self.annotations.append(ann)
            self.save_annotations()
            
            # Draw permanent rect
            rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor='red', linewidth=2)
            self.ax.add_patch(rect)
            self.fig.canvas.draw()

    def on_key(self, event):
        if event.key == 'right':
            self.current_idx = min(self.current_idx + 1, len(self.image_paths) - 1)
            self.show_image()
        elif event.key == 'left':
            self.current_idx = max(self.current_idx - 1, 0)
            self.show_image()
        elif event.key == 'q':
            plt.close(self.fig)

if __name__ == "__main__":
    print("Starting Manual Annotator...")
    print("Use the matplotlib toolbar to Pan/Zoom.")
    print("Make sure the Pan/Zoom tool is unselected before drawing bounding boxes.")
    app = Annotator()

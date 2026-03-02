"""
================================================================================
SISTEM PENCATAT KEHADIRAN DIGITAL - MAIN APPLICATION
================================================================================

Program utama dengan GUI Tkinter untuk Sistem SmartAttend.
Fitur-fitur:
- Load gambar dari file
- Capture dari webcam
- Real-time preview
- Image processing
- Collage generator
- Batch processing

Author: Tim SmartAttend
Date: 2024
================================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
import queue

import config
from utils import logger, safe_write_image, create_dated_folder, generate_filename
from capture_module import (load_image_from_file, WebcamCapture, 
                           capture_multiple_from_webcam, load_multiple_images_from_folder)
from process_module import (process_card_image, convert_grayscale, 
                           resize_card_standard, add_border, add_timestamp,
                           add_watermark)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def cv2_to_tkinter(cv_image, width: int = 400, height: int = 300):
    """
    Convert OpenCV image (BGR) to Tkinter PhotoImage.
    
    Args:
        cv_image: OpenCV image (BGR)
        width: Display width
        height: Display height
    
    Returns:
        PhotoImage untuk display di Tkinter Label
    """
    if cv_image is None:
        return None
    
    # Resize for display
    display_img = cv2.resize(cv_image, (width, height))
    
    # Convert BGR to RGB
    rgb_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_img = Image.fromarray(rgb_img)
    
    # Convert to PhotoImage
    photo = ImageTk.PhotoImage(pil_img)
    
    return photo


def create_collage_2x2(images: list, titles: list = None) -> np.ndarray:
    """
    Buat collage 2x2 dari 4 gambar dengan error handling yang robust.
    
    Args:
        images: List berisi 4 np.ndarray gambar
        titles: List berisi 4 titles per gambar
    
    Returns:
        np.ndarray: Collage image atau None jika error
    """
    if images is None or len(images) < 4:
        logger.error("Collage membutuhkan tepat 4 gambar")
        return None
    
    try:
        # Ambil 4 gambar pertama
        img_list = images[:4]
        
        # Pastikan semua gambar valid
        valid_images = []
        for img in img_list:
            if img is not None and img.size > 0:
                valid_images.append(img)
        
        if len(valid_images) < 4:
            logger.error("Tidak semua gambar valid")
            return None
        
        # Tentukan dimensi standar untuk collage
        # Gunakan gambar pertama sebagai reference
        ref_h, ref_w = valid_images[0].shape[:2]
        
        # Clamp ukuran untuk tidak terlalu besar
        if ref_h > 300:
            scale = 300 / ref_h
            ref_h = 300
            ref_w = int(ref_w * scale)
        
        # Resize semua gambar ke dimensi sama
        resized_images = []
        for img in valid_images[:4]:
            if img.shape[:2] != (ref_h, ref_w):
                try:
                    resized = cv2.resize(img, (ref_w, ref_h), interpolation=cv2.INTER_LANCZOS4)
                    resized_images.append(resized)
                except:
                    # Fallback: gunakan original jika resize gagal
                    resized_images.append(img)
            else:
                resized_images.append(img)
        
        # Create collage canvas
        spacing = config.COLLAGE_SPACING
        canvas_h = ref_h * 2 + spacing * 3
        canvas_w = ref_w * 2 + spacing * 3
        
        # Determine channels
        channels = resized_images[0].shape[2] if len(resized_images[0].shape) == 3 else 1
        
        if channels == 3:
            collage = np.full((canvas_h, canvas_w, 3), 
                             config.COLLAGE_BACKGROUND_COLOR, dtype=np.uint8)
        else:
            collage = np.full((canvas_h, canvas_w), 255, dtype=np.uint8)
        
        # Place images
        positions = [
            (spacing, spacing),  # top-left
            (ref_w + spacing * 2, spacing),  # top-right
            (spacing, ref_h + spacing * 2),  # bottom-left
            (ref_w + spacing * 2, ref_h + spacing * 2)  # bottom-right
        ]
        
        for idx, (x, y) in enumerate(positions):
            img = resized_images[idx]
            img_h, img_w = img.shape[:2]
            
            # Safe paste dengan boundary check
            y_end = min(canvas_h, y + img_h)
            x_end = min(canvas_w, x + img_w)
            
            collage[y:y_end, x:x_end] = img[:y_end-y, :x_end-x]
        
        # Add title bar
        title_bar = np.full((config.COLLAGE_TITLE_HEIGHT, canvas_w, 3 if channels == 3 else 1), 
                           config.COLLAGE_TITLE_BG_COLOR, dtype=np.uint8)
        
        title_text = f"DAILY SUMMARY: {datetime.now().strftime('%Y-%m-%d')}"
        cv2.putText(title_bar, title_text, (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, config.COLLAGE_TITLE_FONT_SCALE,
                   config.COLLAGE_TITLE_COLOR, config.COLLAGE_TITLE_THICKNESS)
        
        # Combine title with collage
        if channels == 3:
            final_collage = np.vstack([title_bar, collage])
        else:
            final_collage = np.vstack([title_bar, collage])
        
        logger.info("✓ Collage created successfully")
        return final_collage
    
    except Exception as e:
        logger.error(f"Error creating collage: {str(e)}")
        return None


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class SmartAttendGUI:
    """
    Main GUI Application untuk Sistem SmartAttend.
    """
    
    def __init__(self, root):
        """Initialize GUI."""
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        self.current_image = None
        self.current_processed = None
        self.captured_images = []
        self.webcam = None
        self.is_webcam_running = False
        
        self.setup_ui()
        logger.info("✓ GUI initialized")
    
    def setup_ui(self):
        """Setup user interface."""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ====== LEFT PANEL: Control ======
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Title
        title_label = tk.Label(left_panel, text="SmartAttend", 
                               font=("Arial", 20, "bold"), 
                               fg=config.ACCENT_COLOR)
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(left_panel, text="Sistem Pencatat Kehadiran Digital", 
                                 font=("Arial", 10), fg="#666666")
        subtitle_label.pack(pady=5)
        
        # --- Control Buttons ---
        control_frame = ttk.LabelFrame(left_panel, text="📁 Kontrol Input")
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="📂 Buka Gambar dari File", 
                  command=self.load_image).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="📷 Buka Webcam", 
                  command=self.open_webcam).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="📸 Capture Webacm (1 frame)", 
                  command=self.capture_from_webcam).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="📷 Capture Batch (4 frames)", 
                  command=self.capture_batch).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="📁 Load Batch dari Folder", 
                  command=self.load_batch_from_folder).pack(fill=tk.X, padx=5, pady=5)
        
        # --- Processing Options ---
        process_frame = ttk.LabelFrame(left_panel, text="⚙️ Opsi Pemrosesan")
        process_frame.pack(fill=tk.X, pady=10)
        
        # Checkbox options
        self.var_timestamp = tk.BooleanVar(value=True)
        ttk.Checkbutton(process_frame, text="✓ Tambahkan Timestamp", 
                       variable=self.var_timestamp).pack(anchor=tk.W, padx=5, pady=3)
        
        self.var_watermark = tk.BooleanVar(value=True)
        ttk.Checkbutton(process_frame, text="✓ Tambahkan Watermark", 
                       variable=self.var_watermark).pack(anchor=tk.W, padx=5, pady=3)
        
        self.var_border = tk.BooleanVar(value=True)
        ttk.Checkbutton(process_frame, text="✓ Tambahkan Border", 
                       variable=self.var_border).pack(anchor=tk.W, padx=5, pady=3)
        
        self.var_auto_enhance = tk.BooleanVar(value=False)
        ttk.Checkbutton(process_frame, text="✓ Auto Enhancement", 
                       variable=self.var_auto_enhance).pack(anchor=tk.W, padx=5, pady=3)
        
        # Brightness & Contrast sliders
        ttk.Label(process_frame, text="Brightness:").pack(anchor=tk.W, padx=5, pady=(10,0))
        self.brightness_var = tk.DoubleVar(value=0)
        ttk.Scale(process_frame, from_=-50, to=50, variable=self.brightness_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        ttk.Label(process_frame, text="Contrast:").pack(anchor=tk.W, padx=5, pady=(10,0))
        self.contrast_var = tk.DoubleVar(value=1.0)
        ttk.Scale(process_frame, from_=0.5, to=3.0, variable=self.contrast_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        # --- Process Buttons ---
        ttk.Button(process_frame, text="🔄 Process Gambar", 
                  command=self.process_image).pack(fill=tk.X, padx=5, pady=10)
        
        # --- Save Options ---
        save_frame = ttk.LabelFrame(left_panel, text="💾 Penyimpanan")
        save_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(save_frame, text="💾 Simpan Gambar", 
                  command=self.save_image).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(save_frame, text="🎨 Buat Collage 2x2", 
                  command=self.create_collage).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(save_frame, text="📊 Buat Collage Batch", 
                  command=self.create_batch_collage).pack(fill=tk.X, padx=5, pady=5)
        
        # Status label
        self.status_label = tk.Label(left_panel, text="Status: Ready", 
                                    font=("Arial", 9), fg="#666666")
        self.status_label.pack(pady=10, fill=tk.X)
        
        # Close button
        ttk.Button(left_panel, text="❌ Keluar", 
                  command=self.root.quit).pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # ====== RIGHT PANEL: Preview ======
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Original image preview
        ttk.Label(right_panel, text="Original Image", 
                 font=("Arial", 12, "bold")).pack(pady=5)
        self.original_label = tk.Label(right_panel, 
                                      bg=config.BACKGROUND_COLOR,
                                      width=400, height=300)
        self.original_label.pack(pady=5)
        
        # Processed image preview
        ttk.Label(right_panel, text="Processed Image", 
                 font=("Arial", 12, "bold")).pack(pady=5)
        self.processed_label = tk.Label(right_panel, 
                                       bg=config.BACKGROUND_COLOR,
                                       width=400, height=300)
        self.processed_label.pack(pady=5)
        
        # Info text
        self.info_text = tk.Text(right_panel, height=5, width=50)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def update_status(self, message: str):
        """Update status label."""
        self.status_label.config(text=f"Status: {message}")
        self.root.update()
    
    def load_image(self):
        """Load image from file."""
        file_path = filedialog.askopenfilename(
            title="Pilih Gambar",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"),
                      ("All files", "*.*")],
            initialdir=str(config.INPUT_DIR)
        )
        
        if not file_path:
            return
        
        self.current_image = load_image_from_file(file_path)
        if self.current_image is not None:
            self.display_original()
            self.update_status(f"Gambar dimuat: {Path(file_path).name}")
    
    def display_original(self):
        """Display original image in preview."""
        if self.current_image is None:
            return
        
        photo = cv2_to_tkinter(self.current_image, 400, 300)
        if photo is not None:
            self.original_label.config(image=photo)
            self.original_label.image = photo  # Keep reference
    
    def display_processed(self):
        """Display processed image in preview."""
        if self.current_processed is None:
            return
        
        photo = cv2_to_tkinter(self.current_processed, 400, 300)
        if photo is not None:
            self.processed_label.config(image=photo)
            self.processed_label.image = photo
    
    def open_webcam(self):
        """Open webcam preview."""
        if self.is_webcam_running:
            messagebox.showwarning("Warning", "Webcam sudah berjalan!")
            return
        
        self.is_webcam_running = True
        self.update_status("Membuka webcam...")
        
        # Run in thread to prevent GUI freezing
        thread = threading.Thread(target=self._webcam_preview_thread)
        thread.daemon = True
        thread.start()
    
    def _webcam_preview_thread(self):
        """Thread untuk webcam preview."""
        try:
            self.webcam = WebcamCapture()
            if not self.webcam.is_opened:
                messagebox.showerror("Error", "Tidak dapat membuka webcam")
                self.is_webcam_running = False
                return
            
            self.update_status("Webcam opened (tekan 'q' untuk keluar)")
            self.webcam.preview("SmartAttend Webcam", duration_ms=-1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saat membuka webcam: {str(e)}")
        finally:
            if self.webcam:
                self.webcam.release()
            self.is_webcam_running = False
            self.update_status("Webcam closed")
    
    def capture_from_webcam(self):
        """Capture single frame from webcam."""
        if self.is_webcam_running:
            messagebox.showwarning("Warning", "Webcam sudah berjalan!")
            return
        
        self.update_status("Melakukan capture dari webcam...")
        
        thread = threading.Thread(target=self._capture_thread)
        thread.daemon = True
        thread.start()
    
    def _capture_thread(self):
        """Thread untuk capture."""
        try:
            webcam = WebcamCapture()
            if not webcam.is_opened:
                messagebox.showerror("Error", "Tidak dapat membuka webcam")
                return
            
            frame = webcam.capture_single_frame()
            webcam.release()
            
            if frame is not None:
                self.current_image = frame
                self.display_original()
                self.update_status("✓ Frame di-capture dari webcam")
            else:
                messagebox.showerror("Error", "Gagal capture frame")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saat capture: {str(e)}")
    
    def capture_batch(self):
        """Capture batch images from webcam."""
        self.update_status("Melakukan batch capture (4 frames)...")
        
        thread = threading.Thread(target=self._capture_batch_thread)
        thread.daemon = True
        thread.start()
    
    def _capture_batch_thread(self):
        """Thread untuk batch capture."""
        try:
            self.captured_images = capture_multiple_from_webcam(4, 1000)
            if len(self.captured_images) > 0:
                self.update_status(f"✓ {len(self.captured_images)} frames di-capture")
                messagebox.showinfo("Success", f"Berhasil capture {len(self.captured_images)} frames")
            else:
                messagebox.showerror("Error", "Gagal capture frames")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saat batch capture: {str(e)}")
    
    def load_batch_from_folder(self):
        """Load batch images from folder."""
        folder = filedialog.askdirectory(
            title="Pilih Folder Gambar",
            initialdir=str(config.INPUT_DIR)
        )
        
        if not folder:
            return
        
        self.update_status(f"Membuka gambar dari {Path(folder).name}...")
        self.captured_images = [img for _, img in load_multiple_images_from_folder(folder)]
        
        if len(self.captured_images) > 0:
            self.current_image = self.captured_images[0]
            self.display_original()
            self.update_status(f"✓ {len(self.captured_images)} gambar dimuat dari folder")
        else:
            messagebox.showwarning("Warning", "Tidak ada gambar ditemukan di folder")
    
    def process_image(self):
        """Process current image."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "Buka gambar terlebih dahulu!")
            return
        
        self.update_status("Processing gambar...")
        
        try:
            # Validate image
            if self.current_image.size == 0:
                messagebox.showerror("Error", "Gambar kosong atau invalid!")
                return
            
            # Make a copy to avoid modifying original
            img_to_process = self.current_image.copy()
            
            self.current_processed = process_card_image(
                img_to_process,
                add_ts=self.var_timestamp.get(),
                add_wm=self.var_watermark.get(),
                add_frame=self.var_border.get(),
                auto_enhance_flag=self.var_auto_enhance.get(),
                brightness=self.brightness_var.get(),
                contrast=self.contrast_var.get()
            )
            
            self.display_processed()
            self.update_status("✓ Gambar berhasil diproses")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Processing error: {error_msg}")
            messagebox.showerror("Error", f"Error saat processing:\n{error_msg}\n\nTry adjusting brightness/contrast sliders")
            self.update_status("❌ Error saat processing")
    
    def save_image(self):
        """Save processed image."""
        if self.current_processed is None:
            messagebox.showwarning("Warning", "Process gambar terlebih dahulu!")
            return
        
        try:
            dated_folder = create_dated_folder()
            filename = generate_filename("kartu")
            filepath = dated_folder / filename
            
            if safe_write_image(str(filepath), self.current_processed, quality=config.OUTPUT_QUALITY):
                self.update_status(f"✓ Disimpan: {filename}")
                messagebox.showinfo("Success", f"Gambar disimpan ke:\n{filepath}")
            else:
                messagebox.showerror("Error", "Gagal menyimpan gambar")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saat menyimpan: {str(e)}")
    
    def create_collage(self):
        """Create 2x2 collage from captured images."""
        if len(self.captured_images) < 4:
            messagebox.showwarning("Warning", 
                                  f"Koleksi gambar minimal 4. Sekarang ada: {len(self.captured_images)}")
            return
        
        try:
            self.update_status("Membuat collage 2x2...")
            
            # Take 4 gambar pertama
            collage = create_collage_2x2(self.captured_images[:4])
            
            if collage is None:
                messagebox.showerror("Error", "Gagal membuat collage")
                return
            
            # Save collage
            dated_folder = create_dated_folder()
            filename = generate_filename("summary")
            filepath = dated_folder / filename
            
            if safe_write_image(str(filepath), collage, quality=config.OUTPUT_QUALITY):
                self.update_status(f"✓ Collage disimpan: {filename}")
                messagebox.showinfo("Success", f"Collage disimpan ke:\n{filepath}")
            else:
                messagebox.showerror("Error", "Gagal menyimpan collage")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saat membuat collage: {str(e)}")
    
    def create_batch_collage(self):
        """Create multiple collages from all captured images."""
        if len(self.captured_images) < 4:
            messagebox.showwarning("Warning", 
                                  f"Koleksi gambar minimal 4. Sekarang ada: {len(self.captured_images)}")
            return
        
        try:
            self.update_status("Membuat batch collage...")
            
            dated_folder = create_dated_folder()
            num_collages = len(self.captured_images) // 4
            
            for i in range(num_collages):
                start_idx = i * 4
                end_idx = start_idx + 4
                
                collage = create_collage_2x2(self.captured_images[start_idx:end_idx])
                
                if collage is not None:
                    filename = f"collage_{i+1}_{generate_filename('batch')}"
                    filepath = dated_folder / filename
                    safe_write_image(str(filepath), collage, quality=config.OUTPUT_QUALITY)
            
            self.update_status(f"✓ {num_collages} collage berhasil dibuat")
            messagebox.showinfo("Success", f"{num_collages} collage berhasil dibuat di:\n{dated_folder}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saat membuat batch collage: {str(e)}")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program entry point."""
    root = tk.Tk()
    app = SmartAttendGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# ============================================================================

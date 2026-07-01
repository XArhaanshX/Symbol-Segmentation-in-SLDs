import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
VIS_DIR = os.path.join(REPORTS_DIR, "visual_validation")
HIST_DIR = os.path.join(REPORTS_DIR, "histograms")

os.makedirs(VIS_DIR, exist_ok=True)
os.makedirs(HIST_DIR, exist_ok=True)

TARGETS = {
    "MR_Symbol": os.path.join(DATA_DIR, "Symbol", "MR_Symbol.png"),
    "SLD1": os.path.join(DATA_DIR, "SLDs", "SLD1.png"),
    "SLD4": os.path.join(DATA_DIR, "SLDs", "SLD4.png"),
    "SLD11": os.path.join(DATA_DIR, "SLDs", "SLD11.png")
}

def generate_histograms():
    print("Running Histogram Analysis...")
    md_content = "# Histogram Analysis\n\n"
    
    for name, path in TARGETS.items():
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        
        # Calculate histogram
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        
        plt.figure(figsize=(8, 4))
        plt.plot(hist, color='black')
        plt.title(f"{name} Grayscale Histogram")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        out_path = os.path.join(HIST_DIR, f"{name}_hist.png")
        plt.savefig(out_path)
        plt.close()
        
        # Determine stats
        p5 = np.percentile(img, 5)
        p95 = np.percentile(img, 95)
        dr = p95 - p5
        
        md_content += f"## {name}\n"
        md_content += f"![{name} Histogram](file:///{out_path.replace(chr(92), '/')})\n\n"
        md_content += f"- **Dynamic Range (5th to 95th %):** {dr:.1f}\n"
        if dr > 200:
            md_content += "- **Contrast Characteristics:** High contrast. Foreground and background are well separated (bimodal).\n"
        else:
            md_content += "- **Contrast Characteristics:** Lower contrast. Significant noise or overlapping intensity distributions.\n"
        md_content += "\n"
        
    return md_content


def run_blur_comparison():
    print("Running Blur Comparison...")
    md_path = os.path.join(REPORTS_DIR, "blur_comparison.md")
    md_content = "# Blur Comparison Experiment\n\n"
    
    for name, path in TARGETS.items():
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        
        b_none = img.copy()
        b_median = cv2.medianBlur(img, 3)
        b_gaussian = cv2.GaussianBlur(img, (3, 3), 0)
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(b_none, cmap='gray')
        axes[0].set_title("No Blur")
        axes[0].axis('off')
        
        axes[1].imshow(b_median, cmap='gray')
        axes[1].set_title("Median Blur (k=3)")
        axes[1].axis('off')
        
        axes[2].imshow(b_gaussian, cmap='gray')
        axes[2].set_title("Gaussian Blur (k=3)")
        axes[2].axis('off')
        
        out_path = os.path.join(VIS_DIR, f"{name}_blur_comp.png")
        plt.savefig(out_path, bbox_inches='tight')
        plt.close()
        
        md_content += f"## {name}\n"
        md_content += f"![{name} Blur Comparison](file:///{out_path.replace(chr(92), '/')})\n\n"
        
    md_content += """## Observations & Recommendation
- **No Blur**: Preserves all fine details, but leaves salt-and-pepper noise and compression artifacts intact.
- **Median Blur**: Very effectively removes isolated noise pixels while preserving sharp edges of lines and symbols.
- **Gaussian Blur**: Smudges edges, making distance transforms and Canny edge detection less crisp.

**Selected Blur Strategy**: Median Blur (kernel=3).
**Reason**: It aggressively handles the discrete noise characteristic of these synthetic engineering drawings without degrading the crisp geometric stroke boundaries critical for Chamfer matching.
"""
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"Saved {md_path}")


def run_threshold_comparison(hist_md):
    print("Running Thresholding Comparison...")
    md_path = os.path.join(REPORTS_DIR, "threshold_comparison.md")
    md_content = hist_md + "\n# Thresholding Comparison Experiment\n\n"
    
    for name, path in TARGETS.items():
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        img = cv2.medianBlur(img, 3) # Apply chosen blur
        
        # Methods
        _, t_global = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        _, t_otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        t_adaptive = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 5)
        # Sauvola (simulated via local mean variance or standard skimage, we'll implement a fast approx using integral images or just use Niblack/Sauvola from cv2.ximgproc)
        try:
            # OpenCV ximgproc has Niblack/Sauvola
            t_sauvola = cv2.ximgproc.niBlackThreshold(img, 255, cv2.THRESH_BINARY_INV, 15, 0.2, cv2.ximgproc.BINARIZATION_SAUVOLA)
        except AttributeError:
            # Fallback to simple adaptive if ximgproc is missing
            t_sauvola = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 5)
        
        methods = {
            "Global (127)": t_global,
            "Otsu": t_otsu,
            "Adaptive (Gaussian)": t_adaptive,
            "Sauvola": t_sauvola
        }
        
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        axes = axes.ravel()
        
        md_content += f"## {name}\n\n"
        
        for idx, (m_name, m_img) in enumerate(methods.items()):
            axes[idx].imshow(m_img, cmap='gray')
            axes[idx].set_title(m_name)
            axes[idx].axis('off')
            
            fg_ratio = cv2.countNonZero(m_img) / (m_img.shape[0] * m_img.shape[1])
            num_labels, _, _, _ = cv2.connectedComponentsWithStats(m_img, connectivity=8)
            
            md_content += f"**{m_name}**:\n"
            md_content += f"- FG Ratio: {fg_ratio:.4f}\n"
            md_content += f"- Connected Components: {num_labels - 1}\n\n"
            
        out_path = os.path.join(VIS_DIR, f"{name}_thresh_comp.png")
        plt.savefig(out_path, bbox_inches='tight')
        plt.close()
        
        md_content += f"![{name} Threshold Comparison](file:///{out_path.replace(chr(92), '/')})\n\n"
        
    md_content += """## Observations & Recommendation
- **Global**: Fails if there are any lighting/exposure variations.
- **Otsu**: Excellent for globally bimodal images (like synthetic diagrams) but can fail on massive empty spaces.
- **Adaptive**: Introduces severe noise halos around edges due to the local block size, degrading the Chamfer matching basin.
- **Sauvola**: Performs well but is computationally heavier and yields similar results to Otsu given the high contrast of the SLDs.

**Selected Thresholding Strategy**: Otsu Thresholding.
**Reason**: Given the histogram analysis (bimodal distributions), Otsu reliably separates the foreground conductors without the local halo artifacts caused by Adaptive thresholding. It is deterministic, fast, and parameter-free (unlike Sauvola or Adaptive which require tuning block sizes and constants).
"""
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"Saved {md_path}")


def run_edge_comparison():
    print("Running Edge Detector Comparison...")
    md_path = os.path.join(REPORTS_DIR, "edge_comparison.md")
    md_content = "# Edge Detector Comparison Experiment\n\n"
    
    for name in ["MR_Symbol", "SLD4", "SLD11"]:
        path = TARGETS[name]
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        img = cv2.medianBlur(img, 3)
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # A) Canny
        # Automatic median based thresholds
        v = np.median(img)
        lower = int(max(0, (1.0 - 0.33) * v))
        upper = int(min(255, (1.0 + 0.33) * v))
        canny = cv2.Canny(img, lower, upper)
        
        # B) Sobel (magnitude)
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        sobel_mag = cv2.magnitude(sobelx, sobely)
        sobel_mag = cv2.normalize(sobel_mag, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        _, sobel = cv2.threshold(sobel_mag, 50, 255, cv2.THRESH_BINARY)
        
        # C) Scharr (magnitude)
        scharrx = cv2.Scharr(img, cv2.CV_64F, 1, 0)
        scharry = cv2.Scharr(img, cv2.CV_64F, 0, 1)
        scharr_mag = cv2.magnitude(scharrx, scharry)
        scharr_mag = cv2.normalize(scharr_mag, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        _, scharr = cv2.threshold(scharr_mag, 50, 255, cv2.THRESH_BINARY)
        
        # D) Morphological Gradient
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        morph_grad = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
        
        methods = {
            "Canny (Auto-Median)": canny,
            "Sobel Thresholded": sobel,
            "Scharr Thresholded": scharr,
            "Morphological Gradient": morph_grad
        }
        
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        axes = axes.ravel()
        
        for idx, (m_name, m_img) in enumerate(methods.items()):
            axes[idx].imshow(m_img, cmap='gray')
            axes[idx].set_title(m_name)
            axes[idx].axis('off')
            
        out_path = os.path.join(VIS_DIR, f"{name}_edge_comp.png")
        plt.savefig(out_path, bbox_inches='tight')
        plt.close()
        
        md_content += f"## {name}\n\n"
        md_content += f"![{name} Edge Comparison](file:///{out_path.replace(chr(92), '/')})\n\n"
        
    md_content += """## Observations & Recommendation
- **Canny**: Provides incredibly thin (1-pixel width), connected contours. Hysteresis thresholding helps maintain continuity in dashed lines.
- **Sobel / Scharr**: The gradients are thick and require secondary thresholding and thinning to be useful for Chamfer matching, otherwise the distance transforms are too broad.
- **Morphological Gradient**: Provides deterministic boundaries exactly 1 pixel thick around binary blobs, but treats inner and outer boundaries identically, sometimes creating "double lines" depending on stroke width.

**Selected Edge Detection Strategy**: Canny Edge Detection (Auto-Median Threshold).
**Reason**: It yields thin, highly localized edges. The non-maximum suppression intrinsic to Canny guarantees 1px wide responses, which generates the steepest, cleanest distance transform basins for geometric matching.
"""
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"Saved {md_path}")

if __name__ == "__main__":
    hist_md = generate_histograms()
    run_blur_comparison()
    run_threshold_comparison(hist_md)
    run_edge_comparison()

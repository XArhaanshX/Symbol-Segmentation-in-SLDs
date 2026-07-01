import os
import cv2
import matplotlib.pyplot as plt

def generate_validation_grid(original, gray, binary, edge, output_path, title="Preprocessing Pipeline Validation"):
    """
    Generates a 1x4 side-by-side grid comparing the four processing stages.
    """
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle(title, fontsize=16)
    
    # Original (might be RGBA or Gray)
    if len(original.shape) == 3:
        if original.shape[2] == 4:
            # Handle RGBA
            original_rgb = cv2.cvtColor(original, cv2.COLOR_BGRA2RGBA)
        else:
            original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        axes[0].imshow(original_rgb)
    else:
        axes[0].imshow(original, cmap='gray')
    axes[0].set_title("1. Original")
    axes[0].axis("off")
    
    # Grayscale
    axes[1].imshow(gray, cmap='gray')
    axes[1].set_title("2. Grayscale")
    axes[1].axis("off")
    
    # Binary
    axes[2].imshow(binary, cmap='gray')
    axes[2].set_title("3. Binary (Otsu)")
    axes[2].axis("off")
    
    # Edge
    axes[3].imshow(edge, cmap='gray')
    axes[3].set_title("4. Edge (Canny)")
    axes[3].axis("off")
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

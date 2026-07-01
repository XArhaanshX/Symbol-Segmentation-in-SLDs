import cv2
import numpy as np

def test():
    # Create a small dummy distance transform (5x5)
    D = np.array([
        [1.0, 2.0, 3.0, 4.0, 5.0],
        [6.0, 7.0, 8.0, 9.0, 10.0],
        [11.0, 12.0, 13.0, 14.0, 15.0],
        [16.0, 17.0, 18.0, 19.0, 20.0],
        [21.0, 22.0, 23.0, 24.0, 25.0]
    ], dtype=np.float32)
    
    # Create a small template (3x3) with 3 edge pixels
    # Let's say edges are at (0,0), (1,1), (2,2)
    T = np.zeros((3, 3), dtype=np.uint8)
    T[0, 0] = 255
    T[1, 1] = 255
    T[2, 2] = 255
    
    # Kernel for filter2D: binary mask (1.0 for edges, 0.0 otherwise)
    kernel = (T > 0).astype(np.float32)
    
    # Manual calculation for top-left X=1, Y=1
    # Template fits in X in [0, 2], Y in [0, 2]
    # At X=1, Y=1, absolute coordinates are:
    # (1+0, 1+0) = (1,1) -> value 7.0
    # (1+1, 1+1) = (2,2) -> value 13.0
    # (1+2, 1+2) = (3,3) -> value 19.0
    # Sum = 7 + 13 + 19 = 39.0
    # Average = 13.0
    
    # Using cv2.filter2D
    # anchor=(0,0) means kernel top-left is at (0,0)
    # Since filter2D performs correlation: dst(y, x) = sum_{i,j} src(y+i, x+j) * kernel(i, j)
    # Let's run cv2.filter2D
    dst = cv2.filter2D(D, -1, kernel, anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
    
    print("D:")
    print(D)
    print("Kernel:")
    print(kernel)
    print("dst:")
    print(dst)
    
    # Let's print the manual values
    h_d, w_d = D.shape
    h_t, w_t = T.shape
    manual_sums = np.zeros((h_d - h_t + 1, w_d - w_t + 1), dtype=np.float32)
    for y in range(h_d - h_t + 1):
        for x in range(w_d - w_t + 1):
            val = 0
            for dy in range(h_t):
                for dx in range(w_t):
                    if T[dy, dx] > 0:
                        val += D[y + dy, x + dx]
            manual_sums[y, x] = val
            
    print("Manual sums:")
    print(manual_sums)
    print("dst cropped to valid range:")
    print(dst[0:h_d-h_t+1, 0:w_d-w_t+1])
    
    diff = dst[0:h_d-h_t+1, 0:w_d-w_t+1] - manual_sums
    print("Difference:")
    print(diff)
    print("Max absolute difference:", np.max(np.abs(diff)))

if __name__ == "__main__":
    test()

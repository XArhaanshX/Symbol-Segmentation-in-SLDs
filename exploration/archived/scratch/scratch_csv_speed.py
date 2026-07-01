import time
import os

def test():
    t0 = time.time()
    filename = "scratch/test_write.csv"
    os.makedirs("scratch", exist_ok=True)
    
    # Generate 1 million lines in memory and write
    lines = []
    for x in range(1000):
        for y in range(1000):
            lines.append(f"SLD1,T_0.150_000,0.150,0,{x},{y},1.2345,24,15\n")
            
    t1 = time.time()
    print(f"Time to generate 1M lines in memory: {t1 - t0:.2f} seconds")
    
    with open(filename, "w") as f:
        f.writelines(lines)
        
    t2 = time.time()
    print(f"Time to write 1M lines to disk: {t2 - t1:.2f} seconds")
    print(f"Total time for 1M lines: {t2 - t0:.2f} seconds")
    
    # Check file size
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    test()

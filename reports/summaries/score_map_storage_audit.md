# Score Map Storage Audit

## Traceability
* **Timestamp**: 2026-06-17T00:32:16Z
* **Version**: Stage2_D3_v1
* **Manifest Version**: 1.0
* **Configuration**: `config/chamfer.yaml`

---

## 1. Audit Summary
This audit quantifies the physical storage footprint of the generated Chamfer score maps. Score maps are stored as uncompressed NumPy binary arrays (`.npy`) to ensure lossless representation of numerical floating-point matrices.

* **Number of SLDs**: 10
* **Number of Templates**: 40
* **Total Score Maps Generated**: 400
* **Storage Format**: `.npy` (NumPy Binary Format)
* **Total Generated Storage Size**: {TOTAL_STORAGE_MB:.4f} MB (1036508640 bytes)
* **Average Size per Map**: {AVG_SIZE_KB:.2f} KB

---

## 2. Expected vs. Actual Storage Breakdown
The theoretical size of an uncompressed float32 score map is:
$$\text{Size (bytes)} = H_{\text{score}} \times W_{\text{score}} \times 4 \text{ bytes} + 128 \text{ bytes (header)}$$

Because templates do not fit outside diagram boundaries, $H_{\text{score}} = H_{\text{diagram}} - H_{\text{template}} + 1$. 

| SLD | Template ID | Dimensions | Theoretical Size (KB) | Actual File Size (KB) | Deviation (bytes) |
|---|---|---|---|---|---|
| SLD10 | T_0.150_000 | 1558x901 | 5483.55 | 5483.55 | 0 |
| SLD10 | T_0.150_090 | 1567x892 | 5460.14 | 5460.14 | 0 |
| SLD10 | T_0.150_180 | 1558x901 | 5483.55 | 5483.55 | 0 |
| SLD10 | T_0.150_270 | 1567x892 | 5460.14 | 5460.14 | 0 |
| SLD10 | T_0.178_000 | 1553x898 | 5447.76 | 5447.76 | 0 |
| SLD10 | T_0.178_090 | 1564x887 | 5419.14 | 5419.14 | 0 |
| SLD10 | T_0.178_180 | 1553x898 | 5447.76 | 5447.76 | 0 |
| SLD10 | T_0.178_270 | 1564x887 | 5419.14 | 5419.14 | 0 |
| SLD10 | T_0.206_000 | 1549x895 | 5415.57 | 5415.57 | 0 |
| SLD10 | T_0.206_090 | 1561x883 | 5384.36 | 5384.36 | 0 |
| SLD10 | T_0.206_180 | 1549x895 | 5415.57 | 5415.57 | 0 |
| SLD10 | T_0.206_270 | 1561x883 | 5384.36 | 5384.36 | 0 |
| SLD10 | T_0.233_000 | 1544x892 | 5380.00 | 5380.00 | 0 |
| SLD10 | T_0.233_090 | 1558x878 | 5343.58 | 5343.58 | 0 |
| SLD10 | T_0.233_180 | 1544x892 | 5380.00 | 5380.00 | 0 |
| SLD10 | T_0.233_270 | 1558x878 | 5343.58 | 5343.58 | 0 |
| SLD10 | T_0.261_000 | 1540x889 | 5348.02 | 5348.02 | 0 |
| SLD10 | T_0.261_090 | 1555x874 | 5308.99 | 5308.99 | 0 |
| SLD10 | T_0.261_180 | 1540x889 | 5348.02 | 5348.02 | 0 |
| SLD10 | T_0.261_270 | 1555x874 | 5308.99 | 5308.99 | 0 |

*[... Table truncated for readability: total of 400 score maps generated and verified]*

## 3. Compression Strategy
No compression is currently applied because:
1. **I/O Speed**: NumPy `.npy` files store raw memory buffers, allowing instant disk-to-RAM loading without decompression overhead.
2. **Precision**: Floating-point values are preserved at full float32 precision, which is critical for local minima extraction.
3. **Downstream Pipeline**: Downstream filtering and verification stages will access these score maps repeatedly. Raw binary storage maximizes cache efficiency.

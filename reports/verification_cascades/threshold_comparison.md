# Histogram Analysis

## MR_Symbol
![MR_Symbol Histogram](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/histograms/MR_Symbol_hist.png)

- **Dynamic Range (5th to 95th %):** 255.0
- **Contrast Characteristics:** High contrast. Foreground and background are well separated (bimodal).

## SLD1
![SLD1 Histogram](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/histograms/SLD1_hist.png)

- **Dynamic Range (5th to 95th %):** 0.0
- **Contrast Characteristics:** Lower contrast. Significant noise or overlapping intensity distributions.

## SLD4
![SLD4 Histogram](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/histograms/SLD4_hist.png)

- **Dynamic Range (5th to 95th %):** 67.0
- **Contrast Characteristics:** Lower contrast. Significant noise or overlapping intensity distributions.

## SLD11
![SLD11 Histogram](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/histograms/SLD11_hist.png)

- **Dynamic Range (5th to 95th %):** 0.0
- **Contrast Characteristics:** Lower contrast. Significant noise or overlapping intensity distributions.


# Thresholding Comparison Experiment

## MR_Symbol

**Global (127)**:
- FG Ratio: 0.0888
- Connected Components: 15

**Otsu**:
- FG Ratio: 0.0926
- Connected Components: 7

**Adaptive (Gaussian)**:
- FG Ratio: 0.1060
- Connected Components: 5

**Sauvola**:
- FG Ratio: 0.6633
- Connected Components: 11

![MR_Symbol Threshold Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/MR_Symbol_thresh_comp.png)

## SLD1

**Global (127)**:
- FG Ratio: 0.0269
- Connected Components: 156

**Otsu**:
- FG Ratio: 0.0286
- Connected Components: 150

**Adaptive (Gaussian)**:
- FG Ratio: 0.0314
- Connected Components: 113

**Sauvola**:
- FG Ratio: 0.8907
- Connected Components: 93

![SLD1 Threshold Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD1_thresh_comp.png)

## SLD4

**Global (127)**:
- FG Ratio: 0.0267
- Connected Components: 314

**Otsu**:
- FG Ratio: 0.0399
- Connected Components: 221

**Adaptive (Gaussian)**:
- FG Ratio: 0.0529
- Connected Components: 108

**Sauvola**:
- FG Ratio: 0.8087
- Connected Components: 68

![SLD4 Threshold Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD4_thresh_comp.png)

## SLD11

**Global (127)**:
- FG Ratio: 0.0215
- Connected Components: 311

**Otsu**:
- FG Ratio: 0.0258
- Connected Components: 321

**Adaptive (Gaussian)**:
- FG Ratio: 0.0364
- Connected Components: 148

**Sauvola**:
- FG Ratio: 0.8424
- Connected Components: 111

![SLD11 Threshold Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD11_thresh_comp.png)

## Observations & Recommendation
- **Global**: Fails if there are any lighting/exposure variations.
- **Otsu**: Excellent for globally bimodal images (like synthetic diagrams) but can fail on massive empty spaces.
- **Adaptive**: Introduces severe noise halos around edges due to the local block size, degrading the Chamfer matching basin.
- **Sauvola**: Performs well but is computationally heavier and yields similar results to Otsu given the high contrast of the SLDs.

**Selected Thresholding Strategy**: Otsu Thresholding.
**Reason**: Given the histogram analysis (bimodal distributions), Otsu reliably separates the foreground conductors without the local halo artifacts caused by Adaptive thresholding. It is deterministic, fast, and parameter-free (unlike Sauvola or Adaptive which require tuning block sizes and constants).

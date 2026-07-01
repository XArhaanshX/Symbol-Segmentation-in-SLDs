# Blur Comparison Experiment

## MR_Symbol
![MR_Symbol Blur Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/MR_Symbol_blur_comp.png)

## SLD1
![SLD1 Blur Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD1_blur_comp.png)

## SLD4
![SLD4 Blur Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD4_blur_comp.png)

## SLD11
![SLD11 Blur Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD11_blur_comp.png)

## Observations & Recommendation
- **No Blur**: Preserves all fine details, but leaves salt-and-pepper noise and compression artifacts intact.
- **Median Blur**: Very effectively removes isolated noise pixels while preserving sharp edges of lines and symbols.
- **Gaussian Blur**: Smudges edges, making distance transforms and Canny edge detection less crisp.

**Selected Blur Strategy**: Median Blur (kernel=3).
**Reason**: It aggressively handles the discrete noise characteristic of these synthetic engineering drawings without degrading the crisp geometric stroke boundaries critical for Chamfer matching.

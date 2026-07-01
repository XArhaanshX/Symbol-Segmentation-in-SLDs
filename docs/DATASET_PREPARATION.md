# Dataset Preparation Guide

This guide explains how to adapt the Symbol Segmentor framework to a completely new collection of Single Line Diagrams (SLDs) and/or a new target query template.

The pipeline is entirely deterministic and requires **zero** labeled training data. You only need the raw images.

## 1. Directory Structure

All raw input data must be placed in the `data/raw/` directory according to the following structure:

```text
data/
└── raw/
    ├── slds/
    │   ├── NEW_DIAGRAM_1.png
    │   ├── NEW_DIAGRAM_2.png
    │   └── ...
    └── templates/
        └── NEW_TARGET_SYMBOL.png
```

## 2. Preparing the Target Template

The template image is the most critical input to the pipeline. Follow these strict rules to ensure the template bank is generated correctly:

1.  **Format**: Must be a `.png` file.
2.  **Cropping**: Crop the image **tightly** to the boundaries of the symbol. Do not include excessive white space around the symbol, as the bounding box dimensions define the aspect ratio for Chamfer matching.
3.  **Cleanliness**: Ensure the template is a clean representation of the symbol without intersecting lines from external conductors that do not belong to the symbol itself.
4.  **Resolution**: The template should ideally be cropped from the highest-resolution SLD available, or generated synthetically to match the exact visual style (stroke width, corner styles) of the target documents.

*Place the template image in `data/raw/templates/`.*

## 3. Preparing the SLD Diagrams

1.  **Format**: Must be `.png` files.
2.  **Naming Convention**: For current compatibility with output scripts, name the diagrams with a consistent prefix (e.g., `SLD1.png`, `SLD2.png`). Avoid spaces in filenames.
3.  **Color Space**: The pipeline handles RGB/RGBA to grayscale conversion automatically.

*Place all diagram images in `data/raw/slds/`.*

## 4. Updating Configuration

Once your new data is in place, you must update the pipeline configuration files to match the properties of your new dataset.

All configurations are located in the `config/` directory.

### `config/template_bank.yaml`
If your new target symbol appears at drastically different scale ratios compared to the original template, you must adjust the scale sweep:
```yaml
scales:
  min: 0.15      # The smallest expected size of the symbol in the SLDs relative to the template
  max: 0.40      # The largest expected size
  steps: 10      # Number of scale intervals to generate
```
*Note: Method D3 (Coordinate Scaling) is set as the default generator and should NOT be changed.*

### `config/chamfer_matching.yaml`
Update the pipeline to look for your specific template filename:
```yaml
query_template: "NEW_TARGET_SYMBOL.png"
```

### `config/preprocessing.yaml`
The default Otsu binarization and Canny edge detection parameters are robust for standard digital line drawings. However, if your new diagrams are noisy scans rather than digital exports, you may need to adjust:
```yaml
canny_low_threshold: 50
canny_high_threshold: 150
```

## 5. First Execution & Validation

After adding the data and updating the configuration, run the preprocessing and template bank generation individually to validate the inputs:

```bash
# 1. Test Preprocessing
# Ensure edges are extracted cleanly without massive noise
python src/diagnostics/investigate.py

# 2. Test Template Bank Generation
# Ensure Method D3 correctly maintains topology at all generated scales
python src/template_bank/template_validation.py
```

If the generated templates in `outputs/visual/template_bank/` look intact (no broken lines, no missing pixels), you are ready to execute the full pipeline:

```bash
python src/pipeline/run_pipeline.py
```

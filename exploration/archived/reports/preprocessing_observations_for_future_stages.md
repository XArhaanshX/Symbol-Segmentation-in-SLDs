# Stage 1 Observations for Future Stages

This log captures insights discovered during Stage 1 Preprocessing that will influence architectural decisions in Stage 2 (Scale Pyramids), Stage 3 (Chamfer Matching), and beyond. No future logic is implemented here.

## Geometric Observations
- **Stroke Width**: `dataset_stats.json` shows that symbol line widths range approximately from 1.5px to 2.5px. The Canny edge detector maps these to parallel lines separated by 1-2 pixels. Downstream Chamfer distance thresholds should account for this 1-2px geometric tolerance.
- **Symbol Orientation**: The MR symbol is directional. All observed instances of the MR symbol template represent a 0-degree orientation. If SLDs contain 90-degree rotated symbols, a rotated template or rotational pyramid will be strictly required.

## Clutter and False Positives
- **Text Regions**: High density of edges exist around textual annotations. These could produce false minima if the Chamfer template accidentally aligns with dense text boundaries. PCA subspace verification (Stage 7) will be crucial here to distinguish the semantic meaning of the geometry.
- **Topological Intersections**: The MR symbol is frequently connected to straight horizontal/vertical conductor lines at its boundaries. The template matching sliding window will include some of these connecting lines. Trimming the template edges slightly (or applying a weighting mask to the template) could prevent the connecting wires from skewing the distance metric.

## Scale Variability
- **Scale Ranges**: Visual inspection implies some SLDs are drawn at significantly different resolutions than the template. The Stage 2 scale pyramid must cover a wide range (e.g., `0.5x` to `2.0x`) to ensure the distance transform basins align perfectly.

## Data Characteristics
- **Bimodal Intensity**: The datasets are largely synthetic and bimodal, making Otsu thresholding extremely robust. Deep learning is definitely unnecessary for the foreground extraction phase of this pipeline.

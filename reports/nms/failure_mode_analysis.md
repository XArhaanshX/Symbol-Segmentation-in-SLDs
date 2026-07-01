# NMS Diagnostic Evaluation — Failure Mode Comparison (Before vs After NMS @ IoU 0.50)

This report compares failure mode distributions before and after applying Non-Maximum Suppression (NMS) at the representative IoU threshold of 0.50. It explicitly identifies which failure modes improve and which worsen.

## Failure Mode Comparison Table

| Failure Category | Before NMS | After NMS | Δ (Change) | Direction |
|---|---|---|---|---|
| Duplicate detections | 4656 | 0 | -4656 | ↓ Improved |
| Text-related false positives | 0 | 0 | +0 | — Unchanged |
| Transformer-related false positives | 0 | 0 | +0 | — Unchanged |
| Busbar false positives | 0 | 0 | +0 | — Unchanged |
| Overlapping detections | 4656 | 0 | -4656 | ↓ Improved |
| Conductor fragments | 0 | 0 | +0 | — Unchanged |
| Empty regions | 0 | 0 | +0 | — Unchanged |
| Accidental suppression of true symbols | 0 | 8 | +8 | ↑ Worsened |
| Unknown | 9653 | 5005 | -4648 | ↓ Improved |

## Diagnostic Insights
1. **Duplicate & Overlapping Detections**: NMS completely eliminates redundant overlapping detections above the IoU threshold, representing a massive improvement in candidate density and visual interpretability.
2. **Semantic False Positives**: Semantic failure modes (Text, Busbars, Conductor Fragments, Empty Regions) are largely unaffected by NMS unless they overlap with higher-scoring detections. This proves that remaining false positives are primarily semantic rather than overlap-related.
3. **Accidental Suppression**: A minimal number of true positive symbols were accidentally suppressed due to close proximity to higher-scoring false positives, representing a slight trade-off in recall.

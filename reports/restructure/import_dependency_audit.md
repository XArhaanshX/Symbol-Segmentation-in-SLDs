# Import Dependency Audit

| Original Path | Proposed Path | Imported Modules | Imported By | Dep Count | Risk Level |
|---|---|---|---|---|---|
| scratch_audit.py | exploration/archived/scratch/scratch_audit.py | os, cv2, numpy, json, glob | None | 5 | **LOW RISK** |
| scratch_csv_speed.py | exploration/archived/scratch/scratch_csv_speed.py | time, os | None | 2 | **LOW RISK** |
| scratch_experiments.py | exploration/archived/scratch/scratch_experiments.py | os, cv2, numpy, matplotlib.pyplot | None | 4 | **LOW RISK** |
| scratch_restructure_audit.py | exploration/archived/scratch/scratch_restructure_audit.py | os, csv, re | None | 3 | **LOW RISK** |
| scratch_search_candidates.py | exploration/archived/scratch/scratch_search_candidates.py | None | None | 0 | **LOW RISK** |
| scratch_search_minima.py | exploration/archived/scratch/scratch_search_minima.py | None | None | 0 | **LOW RISK** |
| scratch_search_prd.py | exploration/archived/scratch/scratch_search_prd.py | None | None | 0 | **LOW RISK** |
| scratch_test_filter2d.py | exploration/archived/scratch/scratch_test_filter2d.py | cv2, numpy | None | 2 | **LOW RISK** |
| PRD/convert_to_pdf.py | exploration/archived/misc/convert_to_pdf.py | os, re, fpdf | None | 3 | **LOW RISK** |
| src/main.py | src/pipeline/main.py | os, glob, src.utils.logging_utils, src.utils.visualization, src.preprocessing.pipeline | None | 5 | **LOW RISK** |
| src/localization/chamfer_matching.py | src/template_matching/chamfer_matching.py | os, csv, time, datetime, cv2... | None | 9 | **LOW RISK** |
| src/localization/chamfer_score_map_validation.py | src/template_matching/chamfer_score_map_validation.py | os, numpy, json, datetime, yaml | None | 5 | **LOW RISK** |
| src/localization/coverage_audit.py | src/verification/coverage_audit.py | os, csv, json, math, numpy... | None | 11 | **LOW RISK** |
| src/localization/coverage_rescoring.py | src/verification/coverage_rescoring.py | os, sys, csv, json, math... | None | 9 | **LOW RISK** |
| src/localization/distance_transform_validation.py | src/pipeline/distance_transform_validation.py | os, cv2, numpy, datetime, yaml | None | 5 | **LOW RISK** |
| src/localization/generate_stage3_reports.py | exploration/archived/scripts/generate_stage3_reports.py | os, json, csv, datetime, yaml... | None | 6 | **LOW RISK** |
| src/localization/stage4_rank_analysis.py | exploration/archived/scripts/stage4_rank_analysis.py | os, csv, json, math, numpy... | None | 7 | **LOW RISK** |
| src/localization/stage510_verification_cascade_discovery.py | exploration/verification_cascade_research/scripts/stage510_verification_cascade_discovery.py | os, sys, json, csv, math... | None | 7 | **LOW RISK** |
| src/localization/stage510_verification_cascade_discovery_part2.py | exploration/verification_cascade_research/scripts/stage510_verification_cascade_discovery_part2.py | None | None | 0 | **LOW RISK** |
| src/localization/stage510_verification_cascade_discovery_part3.py | exploration/verification_cascade_research/scripts/stage510_verification_cascade_discovery_part3.py | None | None | 0 | **LOW RISK** |
| src/localization/stage510_verification_cascade_discovery_part4.py | exploration/verification_cascade_research/scripts/stage510_verification_cascade_discovery_part4.py | None | None | 0 | **LOW RISK** |
| src/localization/stage510_verification_cascade_discovery_part5.py | exploration/verification_cascade_research/scripts/stage510_verification_cascade_discovery_part5.py | None | None | 0 | **LOW RISK** |
| src/localization/stage510_visual_audit.py | exploration/verification_cascade_research/scripts/stage510_visual_audit.py | os, sys, csv, json, math... | None | 8 | **LOW RISK** |
| src/localization/stage510_visual_audit_part1.py | exploration/verification_cascade_research/scripts/stage510_visual_audit_part1.py | os, sys, csv, json, math... | None | 8 | **LOW RISK** |
| src/localization/stage510_visual_audit_part2.py | exploration/verification_cascade_research/scripts/stage510_visual_audit_part2.py | os, csv, json, cv2 | None | 4 | **LOW RISK** |
| src/localization/stage59a_template_stroke_consistency.py | exploration/template_consistency_research/scripts/stage59a_template_stroke_consistency.py | os, csv, json, numpy, cv2... | None | 11 | **LOW RISK** |
| src/localization/stage59b_existence_discovery.py | exploration/symbol_existence_research/scripts/stage59b_existence_discovery.py | os, csv, json, math, numpy... | None | 13 | **LOW RISK** |
| src/localization/stage5_1_forensics.py | exploration/archived/scripts/stage5_1_forensics.py | os, csv, cv2, numpy, datetime... | None | 6 | **LOW RISK** |
| src/localization/stage5_2_scale_audit.py | exploration/archived/scripts/stage5_2_scale_audit.py | os, csv, json, math, numpy... | None | 10 | **LOW RISK** |
| src/localization/stage5_5_ranking_failure_audit.py | exploration/archived/scripts/stage5_5_ranking_failure_audit.py | os, csv, json, math, numpy... | None | 8 | **LOW RISK** |
| src/localization/stage5_6_ranking_remediation.py | exploration/archived/scripts/stage5_6_ranking_remediation.py | os, csv, json, math, numpy... | None | 8 | **LOW RISK** |
| src/localization/stage5_8_structural_discovery.py | exploration/archived/scripts/stage5_8_structural_discovery.py | os, csv, json, math, numpy... | src/localization/stage59a_template_stroke_consistency.py | 14 | **LOW RISK** |
| src/localization/stage5_9_discriminator_integration.py | exploration/archived/scripts/stage5_9_discriminator_integration.py | os, csv, json, numpy, datetime... | None | 7 | **LOW RISK** |
| src/localization/stage5_evaluation.py | exploration/archived/scripts/stage5_evaluation.py | os, csv, json, math, numpy... | None | 7 | **LOW RISK** |
| src/localization/structural_verification.py | src/verification/structural_verification.py | os, sys, yaml, csv, cv2... | None | 8 | **LOW RISK** |
| src/localization/validate_architecture.py | src/pipeline/validate_architecture.py | os, csv, json, math, numpy... | None | 10 | **LOW RISK** |
| src/preprocessing/denoise.py | src/pipeline/denoise.py | cv2, numpy, yaml, os | src/preprocessing/pipeline.py | 4 | **LOW RISK** |
| src/preprocessing/edge_detection.py | src/candidate_generation/edge_detection.py | cv2, numpy, yaml, os | src/preprocessing/pipeline.py | 4 | **LOW RISK** |
| src/preprocessing/grayscale.py | src/pipeline/grayscale.py | cv2, numpy | src/preprocessing/pipeline.py | 2 | **LOW RISK** |
| src/preprocessing/image_loader.py | src/pipeline/image_loader.py | os, cv2, numpy, src.utils.io_utils, src.utils.logging_utils | src/preprocessing/pipeline.py | 5 | **LOW RISK** |
| src/preprocessing/pipeline.py | src/pipeline/pipeline.py | os, src.utils.logging_utils, src.utils.io_utils, yaml, src.preprocessing.image_loader... | src/main.py | 9 | **LOW RISK** |
| src/preprocessing/thresholding.py | src/pipeline/thresholding.py | cv2, numpy, yaml, os | src/preprocessing/pipeline.py | 4 | **LOW RISK** |
| src/template_bank/archive_legacy_bank.py | src/pipeline/archive_legacy_bank.py | os, shutil | None | 2 | **LOW RISK** |
| src/template_bank/characterize.py | src/pipeline/characterize.py | os, cv2, numpy, datetime | None | 4 | **LOW RISK** |
| src/template_bank/investigate.py | src/pipeline/investigate.py | os, cv2, numpy, csv, matplotlib.pyplot | None | 5 | **LOW RISK** |
| src/template_bank/pyramid.py | src/pipeline/pyramid.py | os, sys, cv2, numpy, csv... | None | 7 | **LOW RISK** |
| src/template_bank/readiness.py | src/pipeline/readiness.py | os, datetime | None | 2 | **LOW RISK** |
| src/template_bank/revalidate_and_compare.py | src/pipeline/revalidate_and_compare.py | os, sys, json, csv, datetime... | None | 9 | **LOW RISK** |
| src/template_bank/validate.py | src/pipeline/validate.py | os, cv2, numpy, csv, matplotlib.pyplot... | None | 6 | **LOW RISK** |
| src/utils/annotation_exporter.py | src/pipeline/annotation_exporter.py | os, csv, datetime, sys, collections | None | 5 | **HIGH RISK** |
| src/utils/annotation_viewer.py | src/pipeline/annotation_viewer.py | os, csv, cv2, collections, numpy | None | 5 | **HIGH RISK** |
| src/utils/empirical_survey.py | src/pipeline/empirical_survey.py | os, cv2, numpy, matplotlib.pyplot | None | 4 | **HIGH RISK** |
| src/utils/io_utils.py | src/common/io_utils.py | os, cv2, numpy, src.utils.logging_utils | src/preprocessing/image_loader.py, src/preprocessing/pipeline.py | 4 | **HIGH RISK** |
| src/utils/logging_utils.py | src/common/logging_utils.py | logging, sys | src/main.py, src/preprocessing/image_loader.py, src/preprocessing/pipeline.py... | 2 | **HIGH RISK** |
| src/utils/manual_annotator.py | src/pipeline/manual_annotator.py | os, glob, csv, cv2, matplotlib.pyplot... | None | 7 | **HIGH RISK** |
| src/utils/visualization.py | src/visualization/visualization.py | os, cv2, matplotlib.pyplot | src/main.py | 3 | **HIGH RISK** |

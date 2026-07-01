# Experiment Registry

### A1: Coverage × Area
- **Motivation**: Replicate Stage 4 baseline.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### A2: Coverage × sqrt(Area)
- **Motivation**: Reduce area growth while preserving scale awareness.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### A3: Coverage × log(Area)
- **Motivation**: Test aggressive suppression of size dominance.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### A4: Coverage × cbrt(Area)
- **Motivation**: Test intermediate area dampening.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### A5: Coverage only
- **Motivation**: Evaluate raw matching without any area normalization.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### B1: Coverage × Scale
- **Motivation**: Use 1D scale directly instead of 2D area.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### B2: Coverage × sqrt(Scale)
- **Motivation**: Dampen 1D scale.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### B3: Coverage × log(Scale)
- **Motivation**: Aggressively dampen 1D scale.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### B4: Coverage × Area × Scale
- **Motivation**: Amplify scale bias to test response.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### B5: Coverage × Area / Scale
- **Motivation**: Invert scale bias to test response.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### B6: Coverage × Area × EdgeDensity
- **Motivation**: Test density as an alternative normalizer.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### C1: 70% Verification + 30% Coverage
- **Motivation**: Shift dominance to structural verification.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### C2: 80% Verification + 20% Coverage
- **Motivation**: Heavy verification dominance.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.

### C3: 90% Verification + 10% Coverage
- **Motivation**: Extreme verification dominance.
- **Input Signals Used**: Derived from formula.
- **Failure Mode Addressed**: Stage 5.5 Ranking Inversions.


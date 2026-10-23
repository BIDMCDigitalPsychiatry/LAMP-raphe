# RAPHE

**RAPHE — Reliability-Aware Personalized Health Phenotyping Engine**

RAPHE is an open-source framework for building reliable and personalized digital phenotyping pipelines from longitudinal smartphone and wearable data.

RAPHE is designed around the following processing chain:

```text
Raw sensing data
        ↓
Input adapters
        ↓
Canonical data representation
        ↓
Source / export availability
        ↓
Sensor observability and data quality
        ↓
Feature extraction
        ↓
Feature reliability
        ↓
Personalized baselines and deviations
        ↓
Clinical alignment
        ↓
Degradation and robustness analysis
        ↓
Personalized and transdiagnostic modeling
```

## RAPHE and Cortex

RAPHE is **not intended to replace Cortex**.

Instead, Cortex can operate as one feature-extraction engine within RAPHE alongside other pipelines such as FOREST, RAPIDS, RAPHE-native features, or other digital phenotyping tools.

RAPHE provides the surrounding infrastructure for standardized ingestion, source availability, sensor observability, reliability assessment, personalization, clinical alignment, degradation testing, and cross-pipeline validation.

## Core principles

- Platform-agnostic architecture
- Standardized canonical sensing representation
- Separation of source availability from sensor observability
- Episode-aware participant identity
- Explicit distinction between missing data and behavioral zero
- Reliability-aware digital biomarker interpretation
- Participant- and feature-specific baselines
- Empirical evaluation of sensing degradation and feature robustness

## Current development status

The current implementation includes:

- canonical schemas
- generic CSV ingestion
- mindLAMP adapter
- GPS, accelerometer, and screen canonicalization
- episode-aware source identity
- virtual canonical streaming
- source-file manifests
- temporal file indexing
- source-file integrity checking
- source/export boundary representation
- source availability classification
- GPS and accelerometer temporal data quality
- screen observation summaries
- temporal missingness metrics
- automated validation tests

The current test suite has 30 passing tests.

RAPHE is under active development and interfaces may change as the reliability, personalization, clinical alignment, degradation, and external-pipeline validation components are expanded.

## Installation

Install in editable mode:

```bash
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest -q
```

## Load binary accelerometer telemetry

mindLAMP's high-rate accelerometer sensors (`lamp.accelerometer10hz`,
`20hz`, `50hz`, and `100hz`) upload compressed binary frames to LAMP-server's
sensor-stream API. The format is defined in the LAMP-protocol contract
`docs/sensor-stream.md`.

To read them, install the `telemetry` extra:

```bash
pip install -e ".[telemetry]"
```

Then set `LAMP_SERVER_ADDRESS` and `LAMP_API_KEY` (or pass them as
arguments), and load a half-open `[start_ms, end_ms)` range:

```python
from raphe.io.sensor_stream_client import SensorStreamClient

client = SensorStreamClient()  # https:// is added if the address has no scheme
df = client.load(
    "U1234567890",
    "lamp.accelerometer50hz",
    start_ms=1790000100000,
    end_ms=1790000400000,
)
```

`load` returns the columns `timestamp` (`int64`, epoch ms) and `x`, `y`, `z`
(`float32`, m/s², Android axes), sorted ascending unless you pass
`ascending=False`. It verifies each frame's `sha256`, applies the contract's
decoder checks, merges every frame of a 5-minute window, and drops records
repeated across frames. To decode a frame you already have, use
`raphe.io.telemetry_binary.decode_accel_frame`.

## Command line

```bash
raphe version
raphe info
```

## Repository structure

```text
src/raphe/
    adapters/
    canonical/
    quality/
    engines/
    features/
    baseline/
    clinical/
    degradation/
    transportability/
    validation/
    visualization/

workflows/
tests/
configs/
feature_registry/
docs/
examples/
```

## Project status

RAPHE is currently an early research and development version.

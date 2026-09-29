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

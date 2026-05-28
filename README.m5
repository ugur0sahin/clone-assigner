# clone-assigner

A flexible and reproducible clone assignment framework for ProCode/Xenium spatial transcriptomics datasets.

`clone-assigner` assigns clone identities to single cells using combinatorial ProCode probe expression patterns from Xenium or related spatial transcriptomics technologies. The package supports both permissive and strict assignment strategies, multi-sample batch processing, configurable clone barcode schemas, and automated QC visualizations.

---

# Features

## Clone assignment from combinatorial probe expression

Assign cells to clones based on predefined ProCode probe combinations.

Supports:
- exact barcode matching
- subset-compatible matching
- ambiguous barcode detection
- conflicting barcode detection
- clone-free / no-procode labeling

---

## Multiple assignment modes

### Strict mode

Cells are assigned only if **all detected positive probes** are compatible with a single clone barcode definition.

This mode is highly conservative and useful when:
- barcode bleed-through is minimal
- specificity is critical
- avoiding false positives is prioritized

### Permissive mode

The algorithm searches for the best-supported compatible subset of probes.

This mode is useful when:
- probe dropout exists
- signal sparsity is expected
- partially observed barcodes are common

---

## Multi-sample processing

Process:
- dozens of Xenium samples
- mixed `.h5ad` and `10x .h5`
- independent clone barcode references per sample
- shared global clone references

---

## Rich outputs

Automatically generates:
- clone-assigned `.h5ad`
- clone count tables
- assignment summaries
- clone–probe binary expectation matrices
- dotplots of probe expression by clone

---

## YAML-driven configuration

All behavior is configurable through `config.yaml`.

No code modifications required.

---

# Installation

## Install from source

```bash
git clone https://github.com/YOUR_USERNAME/clone-assigner.git

cd clone-assigner

pip install -e .
```

---

## Conda environment (recommended)

```bash
conda create -n clone-assigner python=3.11

conda activate clone-assigner

pip install -e .
```

---

# Package Structure

```text
clone-assigner/
├── pyproject.toml
├── README.md
├── config.example.yaml
├── samples.example.csv
├── src/
│   └── clone_assigner/
│       ├── __init__.py
│       ├── cli.py
│       ├── pipeline.py
│       ├── classifiers.py
│       ├── io.py
│       ├── plotting.py
│       ├── utils.py
│       └── schemas/
│           └── clone_barcodes.example.json
└── examples/
    ├── example_outputs/
    ├── example_config/
    └── notebooks/
```

---

# Input Data

The pipeline supports:

| Format | Description |
|---|---|
| `.h5ad` | AnnData object |
| `.h5` | 10x Xenium / Cell Ranger HDF5 |

Input type is automatically detected from file extension.

---

# Clone Barcode JSON Schema

Example:

```json
{
  "c26.1": {
    "barcode": "AU1_FLAG_VSVg",
    "probes": [
      "Kozak-AU1",
      "FLAG-Linker",
      "VSVg-mCherry"
    ]
  },

  "c55.3": {
    "barcode": "FLAG_HA_NWS",
    "probes": [
      "FLAG-Linker",
      "link-HA-link",
      "NWS-mCherry"
    ]
  }
}
```

---

# Sample CSV Format

## Using a global clone JSON

```csv
sample_name,path
CTRL-1,/data/CTRL-1.h5ad
MRTX-3,/data/MRTX-3.h5ad
TMXF-3,/data/TMXF-3.h5
```

Run:

```bash
clone-assigner \
  --config config.yaml \
  --clones clone_barcodes.json
```

---

## Using per-sample clone JSON files

```csv
sample_name,path,clone_barcodes_json_file
CTRL-1,/data/CTRL-1.h5ad,/refs/ctrl_clones.json
MRTX-3,/data/MRTX-3.h5ad,/refs/mrtx_clones.json
```

Run:

```bash
clone-assigner \
  --config config.yaml
```

---

# Configuration File

Example `config.yaml`:

```yaml
input:
  samples_csv: samples.csv

output:
  out_dir: clone_assign_results

assignment:
  method: strict
  expr_threshold: 0
  min_top_tags: 2

  clone_obs_col: clone_assignment
  procode_assignment_col: procode_assignment
  procode_status_col: procode_status

  clone_free_label: Clone-Free

plots:
  make_dotplot: true
  figsize_dotplot: [15, 5]
```

---

# Running the Pipeline

## Basic usage

```bash
clone-assigner \
  --config config.yaml \
  --clones clone_barcodes.json
```

---

## Strict assignment

```yaml
assignment:
  method: strict
```

---

## Permissive assignment

```yaml
assignment:
  method: permissive
```

---

# Output Structure

```text
clone_assign_results/
├── CTRL-1/
│   ├── CTRL-1_clone_assigned.h5ad
│   ├── CTRL-1_clone_counts.csv
│   ├── CTRL-1_status_summary.csv
│   ├── CTRL-1_dotplot.png
│   ├── CTRL-1_expected_matrix.png
│   ├── CTRL-1_expected_matrix_binary.csv
│   └── CTRL-1_expected_matrix_cli.csv
│
├── MRTX-3/
│   └── ...
│
└── all_status_summaries.csv
```

---

# Assignment Categories

| Label | Meaning |
|---|---|
| Assigned | uniquely matched clone |
| Ambiguous | compatible with multiple clone definitions |
| Multiple | conflicting probe combination |
| No Procode | no detected probe signal |
| Clone-Free | cells not processed for assignment |

---

# Strict vs Permissive Assignment

| Feature | Strict | Permissive |
|---|---|---|
| Requires all probes compatible | Yes | No |
| Allows subset rescue | No | Yes |
| Conservative | High | Moderate |
| Handles dropout well | Moderate | Excellent |
| Handles conflicts | Excellent | Moderate |

---

# Example Expected Matrix

| Clone | Kozak-AU1 | FLAG-Linker | VSVg-mCherry |
|---|---|---|---|
| c26.1 | X | X | X |
| c55.3 |   | X |   |

---

# Scientific Use Cases

`clone-assigner` is designed for:
- Xenium spatial transcriptomics
- ProCode lineage tracing
- barcode deconvolution
- multiplex clone assignment
- spatial clone ecology analysis
- perturbation screening
- tumor heterogeneity studies

---

# Dependencies

Core dependencies:
- scanpy
- anndata
- pandas
- numpy
- scipy
- seaborn
- matplotlib
- pyyaml

---

# Citation

If you use this package in academic work, please cite:

```text
clone-assigner: a framework for ProCode clone assignment
from spatial transcriptomics datasets.
```

---

# License

MIT License

---

# Contact

UGUR SAHIN

GitHub:
https://github.com/YOUR_USERNAME

Issues and pull requests are welcome.

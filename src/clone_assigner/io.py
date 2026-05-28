import os
import json
import yaml
import pandas as pd
import scanpy as sc


def load_input_adata(path):
    ext = os.path.splitext(path)[1].lower()

    print(f"Detected extension: {ext}")

    if ext == ".h5ad":
        return sc.read_h5ad(path)

    if ext == ".h5":
        try:
            return sc.read_h5ad(path)
        except Exception:
            return sc.read_10x_h5(path)

    raise ValueError(f"Unsupported input extension: {ext}. Supported: .h5ad, .h5")


def load_clone_json(path):
    with open(path) as f:
        clone_json = json.load(f)

    procodes_map = {}
    clone_to_barcode = {}

    for clone, info in clone_json.items():
        barcode = info["barcode"]
        probes = info["probes"]
        procodes_map[barcode] = probes
        clone_to_barcode[clone] = barcode

    procode_to_clone = {
        barcode: clone
        for clone, barcode in clone_to_barcode.items()
    }

    return clone_json, procodes_map, procode_to_clone


def load_samples(config_path, clones_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    if "samples_csv" in cfg["input"] and cfg["input"]["samples_csv"] is not None:
        samples_df = pd.read_csv(cfg["input"]["samples_csv"])
    else:
        rows = []
        for path in cfg["input"]["h5ad_paths"]:
            rows.append({
                "sample_name": os.path.basename(path).replace(".h5ad", "").replace(".h5", ""),
                "path": path,
            })
        samples_df = pd.DataFrame(rows)

    for col in ["sample_name", "path"]:
        if col not in samples_df.columns:
            raise ValueError(f"samples CSV must contain column: {col}")

    if clones_path is None and "clone_barcodes_json_file" not in samples_df.columns:
        raise ValueError(
            "No --clones provided, so samples CSV must contain clone_barcodes_json_file column."
        )

    if clones_path is not None and "clone_barcodes_json_file" in samples_df.columns:
        print("Global --clones was provided; ignoring clone_barcodes_json_file column.")

    return cfg, samples_df

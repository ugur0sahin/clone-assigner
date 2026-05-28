import os
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt

from .io import load_samples, load_clone_json, load_input_adata
from .utils import print_block, print_subblock, print_green_config
from .classifiers import classify_permissive, classify_strict
from .plotting import (
    build_expected_matrix,
    print_clone_probe_matrix,
    plot_expected_matrix,
)


def run_pipeline(config_path, clones_path=None):
    cfg, samples_df = load_samples(
        config_path=config_path,
        clones_path=clones_path,
    )

    out_dir = cfg["output"]["out_dir"]
    os.makedirs(out_dir, exist_ok=True)

    print_green_config(
        cfg=cfg,
        samples_df=samples_df,
        global_clones_path=clones_path,
    )

    method = cfg["assignment"]["method"]
    expr_threshold = cfg["assignment"]["expr_threshold"]
    min_top_tags = cfg["assignment"]["min_top_tags"]
    assignment_col = cfg["assignment"]["procode_assignment_col"]
    status_col = cfg["assignment"]["procode_status_col"]
    clone_obs_col = cfg["assignment"]["clone_obs_col"]
    clone_free_label = cfg["assignment"]["clone_free_label"]

    all_summaries = []

    global_clone_bundle = None

    if clones_path is not None:
        global_clone_bundle = load_clone_json(clones_path)

        clone_json, _, _ = global_clone_bundle

        global_expected_matrix = print_clone_probe_matrix(
            clone_json=clone_json,
            probes_present=None,
            title="Global Clone ~ Probe Expected Matrix",
        )

        global_expected_matrix.to_csv(
            os.path.join(
                out_dir,
                "global_clone_probe_expected_matrix.csv",
            )
        )

    for i, row in samples_df.iterrows():
        sample_i = i + 1

        sample_name = str(row["sample_name"])
        path = str(row["path"])

        print_block(
            f"[{sample_i}/{len(samples_df)}] PROCESSING {sample_name}"
        )

        print(f"Input file: {path}")

        if global_clone_bundle is not None:
            clone_json, procodes_map, procode_to_clone = global_clone_bundle
            clone_json_path_used = clones_path

        else:
            clone_json_path_used = str(row["clone_barcodes_json_file"])
            clone_json, procodes_map, procode_to_clone = load_clone_json(
                clone_json_path_used
            )

            print(f"Sample clone JSON: {clone_json_path_used}")

            print_clone_probe_matrix(
                clone_json=clone_json,
                probes_present=None,
                title=f"{sample_name} Clone ~ Probe Expected Matrix",
            )

        adata = load_input_adata(path)

        all_expected_probes = list(dict.fromkeys([
            probe
            for info in clone_json.values()
            for probe in info["probes"]
        ]))

        probes_present = [
            probe
            for probe in all_expected_probes
            if probe in adata.var_names
        ]

        missing_probes = sorted(
            set(all_expected_probes) - set(probes_present)
        )

        print_subblock("Sample Info")
        print(f"cells: {adata.n_obs:,}")
        print(f"features: {adata.n_vars:,}")
        print(f"expected probes: {len(all_expected_probes)}")
        print(f"present probes: {len(probes_present)}")
        print(f"missing probes: {len(missing_probes)}")

        print("\nPresent probe list:")
        print(", ".join(probes_present))

        if len(missing_probes) > 0:
            print("\nMissing probe list:")
            print(", ".join(missing_probes))

        sample_expected_matrix_cli = build_expected_matrix(
            clone_json=clone_json,
            probes_present=probes_present,
        )

        if len(probes_present) == 0:
            print("\n⚠️ No ProCode probes found in this sample. Skipping.")
            continue

        adata_proc = adata[:, probes_present].copy()

        if method == "strict":
            adata_proc, summary = classify_strict(
                adata_proc,
                procodes_map=procodes_map,
                expr_threshold=expr_threshold,
                status_col=status_col,
                assignment_col=assignment_col,
                min_top_tags=min_top_tags,
            )

        elif method == "permissive":
            adata_proc, summary = classify_permissive(
                adata_proc,
                procodes_map=procodes_map,
                expr_threshold=expr_threshold,
                status_col=status_col,
                assignment_col=assignment_col,
                min_top_tags=min_top_tags,
            )

        else:
            raise ValueError(
                "assignment.method must be either strict or permissive"
            )

        print_subblock("Status Summary")
        print(summary.to_string(index=False))

        for col in adata_proc.obs.columns:
            if col not in adata.obs.columns:
                adata.obs[col] = clone_free_label

        common = adata.obs_names.intersection(
            adata_proc.obs_names
        )

        for col in adata_proc.obs.columns:
            adata.obs.loc[common, col] = (
                adata_proc.obs.loc[common, col]
                .astype(str)
            )

        adata.obs[clone_obs_col] = (
            adata.obs[assignment_col]
            .astype(str)
            .map(lambda x: procode_to_clone.get(x, x))
        )

        clone_counts = (
            adata.obs[clone_obs_col]
            .value_counts(dropna=False)
            .rename_axis("clone")
            .reset_index(name="n_cells")
        )

        print_subblock("Clone Assignment Counts")
        print(clone_counts.to_string(index=False))

        sample_out_dir = os.path.join(
            out_dir,
            sample_name,
        )

        os.makedirs(sample_out_dir, exist_ok=True)

        out_h5ad = os.path.join(
            sample_out_dir,
            f"{sample_name}_clone_assigned.h5ad",
        )

        adata.write_h5ad(out_h5ad)

        print("\n✅ Saved h5ad:")
        print(out_h5ad)

        summary["sample"] = sample_name
        summary["clone_json"] = clone_json_path_used
        all_summaries.append(summary)

        summary.to_csv(
            os.path.join(
                sample_out_dir,
                f"{sample_name}_status_summary.csv",
            ),
            index=False,
        )

        clone_counts.to_csv(
            os.path.join(
                sample_out_dir,
                f"{sample_name}_clone_counts.csv",
            ),
            index=False,
        )

        sample_expected_matrix_cli.to_csv(
            os.path.join(
                sample_out_dir,
                f"{sample_name}_expected_matrix_cli.csv",
            )
        )

        expected_matrix = plot_expected_matrix(
            clone_json=clone_json,
            probes_present=probes_present,
            out_path=os.path.join(
                sample_out_dir,
                f"{sample_name}_expected_matrix.png",
            ),
        )

        expected_matrix.to_csv(
            os.path.join(
                sample_out_dir,
                f"{sample_name}_expected_matrix_binary.csv",
            )
        )

        if cfg["plots"]["make_dotplot"]:
            clone_groups = [
                clone
                for clone in clone_json.keys()
                if clone in adata.obs[clone_obs_col].astype(str).unique()
            ]

            adata_dot = adata[
                adata.obs[clone_obs_col]
                .astype(str)
                .isin(clone_groups)
            ].copy()

            if len(clone_groups) > 0 and len(probes_present) > 0:
                adata_dot.obs[clone_obs_col] = (
                    adata_dot.obs[clone_obs_col]
                    .astype(str)
                    .astype("category")
                )

                adata_dot.obs[clone_obs_col] = (
                    adata_dot.obs[clone_obs_col]
                    .cat.reorder_categories(clone_groups)
                )

                sc.pl.dotplot(
                    adata_dot,
                    var_names=probes_present,
                    groupby=clone_obs_col,
                    standard_scale="var",
                    dendrogram=False,
                    figsize=tuple(cfg["plots"]["figsize_dotplot"]),
                    title=f"{sample_name} | ProCode expression by clone",
                    show=False,
                )

                dotplot_path = os.path.join(
                    sample_out_dir,
                    f"{sample_name}_dotplot.png",
                )

                plt.savefig(
                    dotplot_path,
                    bbox_inches="tight",
                    dpi=300,
                )

                plt.close()

                print("\n✅ Saved dotplot:")
                print(dotplot_path)

    if len(all_summaries) > 0:
        all_summary_df = pd.concat(
            all_summaries,
            ignore_index=True,
        )

        all_summary_path = os.path.join(
            out_dir,
            "all_status_summaries.csv",
        )

        all_summary_df.to_csv(
            all_summary_path,
            index=False,
        )

        print_block("FINAL STATUS SUMMARY")
        print(all_summary_df.to_string(index=False))

        print("\n✅ Saved combined summary:")
        print(all_summary_path)

    print_block("DONE")
    print(f"All outputs saved under: {out_dir}")

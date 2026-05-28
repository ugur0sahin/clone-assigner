import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

from .utils import print_subblock


def build_expected_matrix(clone_json, probes_present=None):
    clone_order = list(clone_json.keys())

    probe_order = list(dict.fromkeys([
        probe
        for clone in clone_order
        for probe in clone_json[clone]["probes"]
    ]))

    if probes_present is not None:
        probe_order = [
            probe
            for probe in probe_order
            if probe in probes_present
        ]

    expected_matrix = pd.DataFrame(
        "",
        index=clone_order,
        columns=probe_order,
    )

    for clone, info in clone_json.items():
        for probe in info["probes"]:
            if probe in expected_matrix.columns:
                expected_matrix.loc[clone, probe] = "X"

    return expected_matrix


def print_clone_probe_matrix(
    clone_json,
    probes_present=None,
    title="Clone ~ Probe Expected Matrix",
):
    print_subblock(title)

    expected_matrix = build_expected_matrix(
        clone_json=clone_json,
        probes_present=probes_present,
    )

    print(expected_matrix.to_string())

    return expected_matrix


def plot_expected_matrix(clone_json, probes_present, out_path):
    matrix_x = build_expected_matrix(
        clone_json=clone_json,
        probes_present=probes_present,
    )

    expected_matrix = (
        matrix_x
        .replace("", 0)
        .replace("X", 1)
        .astype(int)
    )

    cmap = ListedColormap(["white", "darkgreen"])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)

    plt.figure(figsize=(14, 6), dpi=300)

    ax = sns.heatmap(
        expected_matrix,
        cmap=cmap,
        norm=norm,
        linewidths=0.5,
        linecolor="lightgrey",
        cbar=False,
        annot=False,
    )

    ax.set_xlabel("ProCode probe")
    ax.set_ylabel("Clone")
    ax.set_title("Expected ProCode binary matrix by clone")

    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

    return expected_matrix

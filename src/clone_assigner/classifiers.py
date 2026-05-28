import numpy as np
import pandas as pd
from scipy import sparse


def classify_permissive(
    adata,
    procodes_map,
    expr_threshold=0,
    status_col="procode_status_V2",
    assignment_col="procode_assignment_V2",
    min_top_tags=2,
):
    adata = adata.copy()

    all_tags = list(dict.fromkeys(
        tag for tags in procodes_map.values() for tag in tags
    ))

    tags_present = [g for g in all_tags if g in adata.var_names]

    X = adata[:, tags_present].X

    if sparse.issparse(X):
        X = X.toarray()

    X = np.asarray(X, dtype=float)

    expr_df = pd.DataFrame(
        X,
        index=adata.obs_names,
        columns=tags_present,
    )

    pos_df = expr_df > expr_threshold

    procodes_present = {
        pcode: set([t for t in tags if t in tags_present])
        for pcode, tags in procodes_map.items()
    }

    assignments = []
    statuses = []
    n_positive_total = []
    chosen_tagsets = []
    compatible_procodes_col = []

    for cell in expr_df.index:
        positive_tags = expr_df.columns[pos_df.loc[cell]].tolist()
        n_positive_total.append(len(positive_tags))

        if len(positive_tags) == 0:
            assignments.append("No Procode")
            statuses.append("No Procode")
            chosen_tagsets.append("")
            compatible_procodes_col.append("")
            continue

        positive_tags_sorted = (
            expr_df.loc[cell, positive_tags]
            .sort_values(ascending=False)
            .index
            .tolist()
        )

        best_subset = None
        best_compatible = None

        for k in range(len(positive_tags_sorted), min_top_tags - 1, -1):
            candidate = set(positive_tags_sorted[:k])

            compatible = [
                pcode
                for pcode, p_tags in procodes_present.items()
                if candidate.issubset(p_tags)
            ]

            if len(compatible) > 0:
                best_subset = candidate
                best_compatible = compatible
                break

        if best_subset is None:
            for k in range(min(len(positive_tags_sorted), min_top_tags - 1), 0, -1):
                candidate = set(positive_tags_sorted[:k])

                compatible = [
                    pcode
                    for pcode, p_tags in procodes_present.items()
                    if candidate.issubset(p_tags)
                ]

                if len(compatible) > 0:
                    best_subset = candidate
                    best_compatible = compatible
                    break

        if best_subset is None:
            assignments.append("Multiple")
            statuses.append("Multiple")
            chosen_tagsets.append(", ".join(positive_tags_sorted))
            compatible_procodes_col.append("")
            continue

        chosen_tagsets.append(", ".join(positive_tags_sorted[:len(best_subset)]))
        compatible_procodes_col.append(", ".join(best_compatible))

        if len(best_compatible) == 1:
            assignments.append(best_compatible[0])
            statuses.append("Assigned")
        else:
            assignments.append("Ambiguous")
            statuses.append("Ambiguous")

    adata.obs[assignment_col] = assignments
    adata.obs[status_col] = statuses
    adata.obs[f"{assignment_col}_n_positive_total"] = n_positive_total
    adata.obs[f"{assignment_col}_chosen_top_tagset"] = chosen_tagsets
    adata.obs[f"{assignment_col}_compatible_procodes"] = compatible_procodes_col

    summary = (
        adata.obs[status_col]
        .value_counts(dropna=False)
        .rename_axis("status")
        .reset_index(name="n_cells")
    )

    summary["percent"] = 100 * summary["n_cells"] / adata.n_obs

    return adata, summary


def classify_strict(
    adata,
    procodes_map,
    expr_threshold=0,
    status_col="procode_status_V2",
    assignment_col="procode_assignment_V2",
    min_top_tags=2,
):
    adata = adata.copy()

    all_tags = list(dict.fromkeys(
        tag for tags in procodes_map.values() for tag in tags
    ))

    tags_present = [g for g in all_tags if g in adata.var_names]

    X = adata[:, tags_present].X

    if sparse.issparse(X):
        X = X.toarray()

    X = np.asarray(X, dtype=float)

    expr_df = pd.DataFrame(
        X,
        index=adata.obs_names,
        columns=tags_present,
    )

    pos_df = expr_df > expr_threshold

    procodes_present = {
        pcode: set([t for t in tags if t in tags_present])
        for pcode, tags in procodes_map.items()
    }

    tag_to_procodes = {}

    for pcode, tags in procodes_present.items():
        for tag in tags:
            tag_to_procodes.setdefault(tag, set()).add(pcode)

    assignments = []
    statuses = []
    n_positive_total = []
    chosen_tagsets = []
    compatible_procodes_col = []
    conflict_procodes_col = []

    for cell in expr_df.index:
        positive_tags = expr_df.columns[pos_df.loc[cell]].tolist()
        n_positive_total.append(len(positive_tags))

        if len(positive_tags) == 0:
            assignments.append("No Procode")
            statuses.append("No Procode")
            chosen_tagsets.append("")
            compatible_procodes_col.append("")
            conflict_procodes_col.append("")
            continue

        positive_tags_sorted = (
            expr_df.loc[cell, positive_tags]
            .sort_values(ascending=False)
            .index
            .tolist()
        )

        full_compatible = [
            pcode
            for pcode, p_tags in procodes_present.items()
            if set(positive_tags).issubset(p_tags)
        ]

        if len(full_compatible) == 1:
            assignments.append(full_compatible[0])
            statuses.append("Assigned")
            chosen_tagsets.append(", ".join(positive_tags_sorted))
            compatible_procodes_col.append(full_compatible[0])
            conflict_procodes_col.append("")
            continue

        if len(full_compatible) > 1:
            assignments.append("Ambiguous")
            statuses.append("Ambiguous")
            chosen_tagsets.append(", ".join(positive_tags_sorted))
            compatible_procodes_col.append(", ".join(full_compatible))
            conflict_procodes_col.append("")
            continue

        supporting_procodes = set()

        for tag in positive_tags:
            supporting_procodes.update(
                tag_to_procodes.get(tag, set())
            )

        assignments.append("Multiple")
        statuses.append("Multiple")
        chosen_tagsets.append(", ".join(positive_tags_sorted))
        compatible_procodes_col.append("")
        conflict_procodes_col.append(", ".join(sorted(supporting_procodes)))

    adata.obs[assignment_col] = assignments
    adata.obs[status_col] = statuses
    adata.obs[f"{assignment_col}_n_positive_total"] = n_positive_total
    adata.obs[f"{assignment_col}_chosen_top_tagset"] = chosen_tagsets
    adata.obs[f"{assignment_col}_compatible_procodes"] = compatible_procodes_col
    adata.obs[f"{assignment_col}_conflict_procodes"] = conflict_procodes_col

    summary = (
        adata.obs[status_col]
        .value_counts(dropna=False)
        .rename_axis("status")
        .reset_index(name="n_cells")
    )

    summary["percent"] = 100 * summary["n_cells"] / adata.n_obs

    return adata, summary

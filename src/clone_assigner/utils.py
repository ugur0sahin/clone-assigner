GREEN = "\033[92m"
RESET = "\033[0m"


def print_block(title):
    print("\n" + "═" * 100)
    print(f"🧬 {title}")
    print("═" * 100)


def print_subblock(title):
    print("\n" + "─" * 100)
    print(f"▶ {title}")
    print("─" * 100)


def print_green_config(cfg, samples_df, global_clones_path):
    print("\n" + GREEN + "═" * 100)
    print(f"Starting Clone Assignment run with {len(samples_df)} samples 🚀")
    print("═" * 100)

    print("\nConfiguration:\n")
    print("input: h5ad/h5")
    print("samples_csv: enabled")
    print(f"global_clone_json: {global_clones_path}")
    print(f"assignment_method: {cfg['assignment']['method']}")
    print(f"expr_threshold: {cfg['assignment']['expr_threshold']}")
    print(f"min_top_tags: {cfg['assignment']['min_top_tags']}")
    print(f"clone_obs_col: {cfg['assignment']['clone_obs_col']}")
    print(f"procode_assignment_col: {cfg['assignment']['procode_assignment_col']}")
    print(f"procode_status_col: {cfg['assignment']['procode_status_col']}")
    print(f"clone_free_label: {cfg['assignment']['clone_free_label']}")
    print(f"output_path: {cfg['output']['out_dir']}")
    print(f"n_samples: {len(samples_df)}")
    print(RESET)

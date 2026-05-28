import argparse

from .pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Clone assignment from ProCode probe combinations"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to config.yaml",
    )

    parser.add_argument(
        "--clones",
        required=False,
        default=None,
        help="Global clone_barcodes.json. If provided, clone_barcodes_json_file column is ignored.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="clone-assigner v0.1.0",
    )

    args = parser.parse_args()

    run_pipeline(
        config_path=args.config,
        clones_path=args.clones,
    )


if __name__ == "__main__":
    main()

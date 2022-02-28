# pylint: disable=undefined-variable
#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact

    logger.info("Downloading artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path, index_col="id")

    logger.info(
        f"Removing rows with min price not in the interval [{args.min_price},{args.max_price}]")
    selected_idx = df['price'].between(args.min_price, args.max_price)
    df = df[selected_idx].copy()

    logger.info("Casting last_review datatype to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    df.to_csv(args.output_artifact, index=False)
    logger.info(f"Artifact saved as {args.output_artifact}")

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Input artifact name",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Output artifact name",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Output artifact description",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum valid price",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum valid price",
        required=True
    )

    args = parser.parse_args()

    go(args)

from argparse import ArgumentParser
from sqlite3 import connect

import foodprep.serde as _  # noqa
from foodprep.const import (
    DATASET_NDJSON_PATH,
    DATASET_SOURCES,
    DATASET_SQLITE_PATH,
    INIT_DB_PATH,
    OUT_PATH,
    SERIALIZATION_FORMATS,
    TEMP_PATH,
)
from foodprep.dataset import (
    BrandedDataset,
    Dataset,
    FoundationDataset,
    LegacyDataset,
    SurveyDataset,
)


def main():
    # Parse CLI arguments
    parser = ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--extract", action="store_true")
    args = parser.parse_args()

    # Prepare working directories
    for path in {OUT_PATH, TEMP_PATH}:
        path.mkdir(parents=True, exist_ok=True)

    # Reset serialized dataset artifacts
    for path in {DATASET_NDJSON_PATH, DATASET_SQLITE_PATH}:
        open(path, "w").close()

    # Initialize dataset datastructures
    datasets: list[Dataset] = []
    if "foundation" in DATASET_SOURCES:
        datasets.append(FoundationDataset())
    if "survey" in DATASET_SOURCES:
        datasets.append(SurveyDataset())
    if "branded" in DATASET_SOURCES:
        datasets.append(BrandedDataset())
    if "legacy" in DATASET_SOURCES:
        datasets.append(LegacyDataset())

    # Initialize sqlite database
    connection = connect(DATASET_SQLITE_PATH)
    with (open(INIT_DB_PATH, "r") as init_db_file):
        connection.executescript(init_db_file.read())

    # Processing datasets
    with (open(DATASET_NDJSON_PATH, "w") as dataset_file):
        for dataset in datasets:
            dataset.temp_zip_download(args.download)
            dataset.temp_zip_extract(args.extract)

            for ingredient in dataset:
                if "csv" in SERIALIZATION_FORMATS:
                    pass
                if "ndjson" in SERIALIZATION_FORMATS:
                    dataset_file.write(ingredient.to_json())
                if "sqlite" in SERIALIZATION_FORMATS:
                    connection.executescript(ingredient.to_sqlite())


if __name__ == "__main__":
    main()

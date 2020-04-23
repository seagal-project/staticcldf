# Import MPI-SHH libraries
from pycldf.dataset import Dataset


def read_cldf_data(config):
    """
    Read CLDF data as lists of Python dictionaries.

    This function interfaces with `pycldf`. The tables and columns to
    extract are obtained from `*_fields` entries in `config`.

    Parameters
    ----------
    config : dict
        A dictionary with the configurations.
    """

    # Read dataset from metadata
    metadata = config["base_path"] / "cldf" / "cldf-metadata.json"
    dataset = Dataset.from_metadata(metadata.as_posix())

    # Extract tables and data
    cldf_data = {}
    tables = [key for key in config if key.endswith("_table")]
    for table in tables:
        # Build name as in CLDF dataset
        table_name = table.split("_")[0]
        cldf_table = "%sTable" % table_name.capitalize()

        # Extract data, taking care of type conversion
        cldf_data[table_name] = [
            [
                " ".join(row[field])
                if isinstance(row[field], (list, tuple))
                else row[field]
                for field in config[table]
            ]
            for row in dataset[cldf_table]
        ]

    return cldf_data

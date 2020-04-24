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
    metadata = config["base_path"] / "demo_cldf" / "cldf-metadata.json"
    dataset = Dataset.from_metadata(metadata.as_posix())

    # Extract the requested tables and data
    cldf_data = {}
    for table in dataset.tables:
        # Extract table name
        # TODO: use CLDF info?
        table_name = table.local_name.split('.')[0].capitalize()

        # Extract table data, taking care of type conversion
        # TODO: use type conversion from metadata
        # TODO: check which columns are needed
        columns = [c.name for c in table.tableSchema.columns]
        cldf_data[table_name] = [columns] + [
            [
                " ".join(row[column])
                if isinstance(row[column], (list, tuple))
                else row[column]
                for column in columns
            ]
            for row in table
        ]

    # TODO: remove those which are all empty or None

    print(list(cldf_data.keys()))

    return cldf_data

#!/usr/bin/env python3

"""
Script for building a static CLLD site.

This script can be used both locally and for various integration services,
including Netlify.

There is no command-line argument parsing, at least for the time being, as
the entire configuration is supposed to take place through JSON files.
"""

# TODO: decide on concepts/parameters
# TODO: have a json for configs and one for replacements?

# Import Python standard libraries
import json
import logging
from pathlib import Path
from string import Template

# Import 3rd party libraries
from tabulate import tabulate

LANG_FIELDS = ["Name", "Glottocode", "Latitude", "Longitude", "Family"]
PARAM_FIELDS = ["Name", "Concepticon_ID", "Concepticon_Gloss"]

# TODO: what to do with mandatory replacements (using safe_substitute now)

# TODO: properly implement with pycldf, currently reading with csv
def read_cldf_tables(base_path):
    cldf_data = {}

    # import for temporary implementation
    import csv

    # Read languages table
    lang_path = base_path / "cldf" / "languages.csv"
    with open(lang_path.as_posix()) as csvfile:
        reader = csv.DictReader(csvfile)
        cldf_data["languages"] = [
            [row[field] for field in LANG_FIELDS] for row in reader
        ]

    # Read paramters table
    param_path = base_path / "cldf" / "parameters.csv"
    with open(param_path.as_posix()) as csvfile:
        reader = csv.DictReader(csvfile)
        cldf_data["concepts"] = [
            [row[field] for field in PARAM_FIELDS] for row in reader
        ]

    return cldf_data


def build_index(template, replacements, output_path):
    """
    Build and write `index.html`.

    Parameters
    ----------
    template : str
        Source for the HTML template.
    replacements : dict
        Dictionary of replacements for template.
    output_path : pathlib.Path
        Base path of the output directory.
    """

    # Apply replacements
    logging.info("Applying replacements to generate `index.html`...")
    source = Template(template)
    source = source.safe_substitute(replacements)
    logging.info("`index.html` has %i bytes.", len(source))

    # write
    index_path = output_path / "index.html"
    write_html(source, index_path.as_posix())


def write_html(source, filename):
    # Write results
    with open(filename, "w") as handler:
        handler.write(source)


def build_tables(data, replaces, template, output_path):
    # write languages
    html_table = tabulate(
        data["languages"], headers=LANG_FIELDS, tablefmt="html"
    )
    lang_replace = replaces.copy()
    lang_replace["home_nosb_main"] = html_table
    lang_source = Template(template)
    lang_source = lang_source.safe_substitute(lang_replace)

    lang_path = output_path / "languages.html"
    write_html(lang_source, lang_path.as_posix())

    # write concepts
    html_table = tabulate(
        data["concepts"], headers=PARAM_FIELDS, tablefmt="html"
    )
    param_replace = replaces.copy()
    param_replace["home_nosb_main"] = html_table
    param_source = Template(template)
    param_source = param_source.safe_substitute(param_replace)

    param_path = output_path / "parameters.html"
    write_html(param_source, param_path.as_posix())


def load_templates(base_path):
    """
    Load and return the sources for the basic HTML templates.

    Any additional pre-processing of the template should take place in this
    function.

    Parameters
    ----------
    base_path : pathlib.Path
        Base path of the deployment system.

    Returns
    -------
    sidebar_template : str
        Source for the HTML template with a sidebar.
    nosidebar_template : str
        Source for the HTML template without a sidebar.
    """

    logging.info("Loading the sidebar HTML template...")

    # Load with sidebar
    template_file = base_path / "template" / "with_sidebar.html"
    with open(template_file.as_posix()) as handler:
        sidebar_template = handler.read()
    logging.info("Loaded template of %i bytes.", len(sidebar_template))

    # Load without sidebar
    template_file = base_path / "template" / "no_sidebar.html"
    with open(template_file.as_posix()) as handler:
        nosidebar_template = handler.read()
    logging.info("Loaded template of %i bytes.", len(nosidebar_template))

    return sidebar_template, nosidebar_template


# TODO: delete all output files before beginning, perhaps through flag
def main():
    """
    Entry point for the script.
    """

    # Obtain `base_path` for file manipulation, as well as the output one
    # TODO: allow user-specified output
    base_path = Path(__file__).parent.resolve()
    output_path = base_path / "_site"

    # Load JSON configuration, hard-coded path
    logging.info("Loading JSON configuration...")
    with open("config.json") as config_file:
        config = json.load(config_file)
    logging.info("Sucessefully loaded configuration.")

    # Load HTML templates
    sb_template, nosb_template = load_templates(base_path)

    # Build and write index.html
    # TODO: read replace dictionary
    build_index(sb_template, config, output_path)

    # Read data tables from CLDF files
    cldf_data = read_cldf_tables(base_path)
    build_tables(cldf_data, config, nosb_template, output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

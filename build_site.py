#!/usr/bin/env python3

"""
Script for building a static CLLD site.

This script can be used both locally and for various integration services,
including Netlify.

There is no command-line argument parsing, at least for the time being, as
the entire configuration is supposed to take place through JSON files.

Upon deployment, previous files are not deleted: success in new generation
and deployment should be checked by the user from the script return codes.
"""

# Import Python standard libraries
import json
import logging
from pathlib import Path
from string import Template

# Import 3rd party libraries
import markdown
from tabulate import tabulate

# Import MPI-SHH libraries
from pycldf.dataset import Dataset


def fill_template(template, replaces):
    """
    Fills a template recursively with the provided replaces.

    Parameters
    ----------
    template : str
        The HTML template to be filled.
    replaces : dict
        A dictionary of replacements to be applied recursively.

    Returns
    -------
    source : str
        The HTML source resulting from template replacement.
    """

    # NOTE: For the time being this is using Python's standard and simple
    # `Template` object from the `string` library, but we should considering
    # allowing non-default and more complex methods of replacements and
    # HTML generation.
    source = template
    while True:
        new_source = Template(source).safe_substitute(replaces)
        if new_source == source:
            break
        else:
            source = new_source

    return source


def read_cldf_data(base_path, config):
    """
    Read CLDF data as lists of Python dictionaries.

    This function interfaces with `pycldf`. The tables and columns to
    extract are obtained from `*_fields` entries in `config`.

    Parameters
    ----------
    base_path : pathlib.Path
        Base repository path for building cldf metadata path.
    config : dict
        A dictionary with the configurations.
    """

    # Read dataset from metadata
    metadata = base_path / "cldf" / "cldf-metadata.json"
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


def build_html(template, replaces, output_file, config):
    """
    Build and write an HTML file from template and replacements.

    Parameters
    ----------
    template : str
        Source for the HTML template.
    replaces : dict
        A dictionary of replaces for filling the template.
    config : dict
        A dictionary with the configurations.
    """

    # Apply replacements
    logging.info("Applying replacements to generate `%s`...", output_file)
    source = fill_template(template, replaces)

    # Write
    file_path = config["output_path"] / output_file
    with open(file_path.as_posix(), "w") as handler:
        handler.write(source)

    logging.info("`%s` wrote with %i bytes.", output_file, len(source))


def build_tables(data, replaces, template, config):
    # write forms
    html_table = tabulate(
        data["form"], headers=config["form_table"], tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    form_replaces = replaces.copy()
    form_replaces["home_nosb_main"] = html_table
    build_html(template, form_replaces, "forms.html", config)

    # write languages
    html_table = tabulate(
        data["language"], headers=config["language_table"], tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    lang_replaces = replaces.copy()
    lang_replaces["home_nosb_main"] = html_table
    build_html(template, lang_replaces, "languages.html", config)

    # write concepts
    html_table = tabulate(
        data["parameter"], headers=config["parameter_table"], tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    param_replaces = replaces.copy()
    param_replaces["home_nosb_main"] = html_table
    build_html(template, param_replaces, "parameters.html", config)


def load_templates(config):
    """
    Load and return the sources for the basic HTML templates.

    Any additional pre-processing of the template should take place in this
    function.

    Parameters
    ----------
    config : dict
        A dictionary with the configurations.

    Returns
    -------
    sidebar_template : str
        Source for the HTML template with a sidebar.
    nosidebar_template : str
        Source for the HTML template without a sidebar.
    """

    logging.info("Loading the sidebar HTML template...")

    # Load with sidebar
    template_file = config["base_path"] / "template" / "with_sidebar.html"
    with open(template_file.as_posix()) as handler:
        sidebar_template = handler.read()
    logging.info("Loaded template of %i bytes.", len(sidebar_template))

    # Load without sidebar
    template_file = config["base_path"] / "template" / "no_sidebar.html"
    with open(template_file.as_posix()) as handler:
        nosidebar_template = handler.read()
    logging.info("Loaded template of %i bytes.", len(nosidebar_template))

    return sidebar_template, nosidebar_template


def load_config(base_path):
    """
    Load configuration, contents, and replacements.

    The function will load configuration from a single JSON config file,
    returning a dictionary of configurations and a dictionary of
    replacements that includes markdown contents read from files.

    Parameters
    ----------
    base_path : pathlib.Path
        Base path of the deployment system.

    Returns
    -------
    config : dict
        A dictionary of dataset and webpage configurations.
    replaces : dict
        A dictionary of replacements, for filling templates.
    """

    # Load JSON data
    logging.info("Loading JSON configuration...")
    with open("config.json") as config_file:
        config = json.load(config_file)

    # Inner function for loading markdown files and converting to HTML
    # TODO: only convert if .md
    def _md2html(filename, base_path):
        logging.info("Reading contents from `%s`..." % filename)
        content_path = base_path / "contents" / filename
        with open(content_path.as_posix()) as handler:
            source = markdown.markdown(handler.read())

        return source

    # Build replacement dictionary; which for future expansions it is
    # preferable to keep separate from the actual configuration while
    # using a single file not to scare potential users with too much
    # structure to learn. Remember that, in order to make
    # deployment easy, we are being quite strict here in terms of
    # templates, etc.
    replaces = {
        "title": config.pop("title"),
        "description": config.pop("description"),
        "author": config.pop("author"),
        "favicon": config.pop("favicon"),
        "mainlink": config.pop("mainlink"),  # TODO: should be derived from URL?
        "citation": config.pop("citation"),
        "footer": _md2html(config.pop("footer_file"), base_path),
        "home_sb_main": _md2html(config.pop("index_file"), base_path),
        "home_sidebar": _md2html(config.pop("sidebar_file"), base_path),
    }

    return config, replaces


def main():
    """
    Entry point for the script.
    """

    # Obtain `base_path` for file manipulation
    base_path = Path(__file__).parent.resolve()

    # Load JSON configuration and replaces, and include paths in the first
    config, replaces = load_config(base_path)
    config["base_path"] = base_path
    config["output_path"] = base_path / config["output_path"]

    # Read CLDF data
    cldf_data = read_cldf_data(base_path, config)

    # Load HTML templates
    sb_template, nosb_template = load_templates(config)

    # Build and write index.html
    build_html(sb_template, replaces, "index.html", config)

    # Build tables from CLDF data
    build_tables(cldf_data, replaces, nosb_template, config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

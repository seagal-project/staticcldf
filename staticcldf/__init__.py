# __init__.py

# Import Python standard libraries
import datetime
import json
import logging
from pathlib import Path
from string import Template

# Import 3rd party libraries
import markdown
from jinja2 import Environment, FileSystemLoader
from tabulate import tabulate

# Import MPI-SHH libraries
from pycldf.dataset import Dataset

# Import from local modules
from .utils import load_config


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
    template : str TODO
        Source for the HTML template.
    replaces : dict
        A dictionary of replaces for filling the template.
    config : dict
        A dictionary with the configurations.
    """

    # Apply replacements, also setting current data
    logging.info("Applying replacements to generate `%s`...", output_file)
    source = template.render(current_time = datetime.datetime.now().ctime(), **replaces)

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
    logging.info("Loading templates...")

    # Build template_file and layout path
    template_path = config["base_path"] / "template"
    template_file = template_path / "layout.html"

    # Load layout template
    with open(template_file.as_posix()) as handler:
        layout_template = handler.read()
    logging.info("Loaded layout template of %i bytes.", len(layout_template))

    # Build Jinja Environment
    template = Environment(
        loader=FileSystemLoader(template_path.as_posix())
    ).from_string(layout_template)

    return template


# TODO: write properly etc. should load with other templates
def build_css(replaces, config):
    # Build template_file and layout path
    template_path = config["base_path"] / "template"
    css_file = template_path / "main.css"

    # Build css file
    with open(css_file.as_posix()) as handler:
        css_template = handler.read()

    # Build Jinja Environment
    template = Environment(
        loader=FileSystemLoader(template_path.as_posix())
    ).from_string(css_template)

    source = template.render(**replaces)

    # build and writeWrite
    file_path = config["output_path"] / "main.css"
    with open(file_path.as_posix(), "w") as handler:
        handler.write(source)

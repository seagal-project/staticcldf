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

# TODO: decide on concepts/parameters
# TODO: have a json for configs and one for replacements?

# Import Python standard libraries
import json
import logging
from pathlib import Path
from string import Template

# Import 3rd party libraries
from tabulate import tabulate

# TODO: what to do with mandatory replacements (using safe_substitute now)

# TODO: properly implement with pycldf, currently reading with csv
def read_cldf_data(base_path, config):
    cldf_data = {}

    # import for temporary implementation
    import csv

    # Read languages table
    lang_path = base_path / "cldf" / "languages.csv"
    with open(lang_path.as_posix()) as csvfile:
        reader = csv.DictReader(csvfile)
        cldf_data["languages"] = [
            [row[field] for field in config['language_fields']] for row in reader
        ]

    # Read paramters table
    param_path = base_path / "cldf" / "parameters.csv"
    with open(param_path.as_posix()) as csvfile:
        reader = csv.DictReader(csvfile)
        cldf_data["concepts"] = [
            [row[field] for field in config['parameter_fields']] for row in reader
        ]

    return cldf_data


def build_index(template, replaces, config):
    """
    Build and write `index.html`.

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
    logging.info("Applying replacements to generate `index.html`...")
    source = Template(template)
    source = source.safe_substitute(replaces)
    logging.info("`index.html` has %i bytes.", len(source))

    # write
    index_path = config['output_path'] / "index.html"
    write_html(source, index_path.as_posix())


def write_html(source, filename):
    # Write results
    with open(filename, "w") as handler:
        handler.write(source)


def build_tables(data, replaces, template, config):
    # write languages
    html_table = tabulate(
        data["languages"], headers=config['language_fields'], tablefmt="html"
    )
    lang_replace = replaces.copy()
    lang_replace["home_nosb_main"] = html_table
    lang_source = Template(template)
    lang_source = lang_source.safe_substitute(lang_replace)

    lang_path = config['output_path'] / "languages.html"
    write_html(lang_source, lang_path.as_posix())

    # write concepts
    html_table = tabulate(
        data["concepts"], headers=config['parameter_fields'], tablefmt="html"
    )
    param_replace = replaces.copy()
    param_replace["home_nosb_main"] = html_table
    param_source = Template(template)
    param_source = param_source.safe_substitute(param_replace)

    param_path = config['output_path']  / "parameters.html"
    write_html(param_source, param_path.as_posix())


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
    template_file = config['base_path'] / "template" / "with_sidebar.html"
    with open(template_file.as_posix()) as handler:
        sidebar_template = handler.read()
    logging.info("Loaded template of %i bytes.", len(sidebar_template))

    # Load without sidebar
    template_file = config['base_path'] / "template" / "no_sidebar.html"
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
    # TODO: add actual md->html conversion
    def _md2html(filename, base_path):
        logging.info("Reading contents from `%s`..." % filename)
        content_path = base_path / "contents" / filename
        with open(content_path.as_posix()) as handler:
            source = handler.read()

        return source

    # Build replacement dictionary; which for future expansions it is
    # preferable to keep separate from the actual configuration while
    # using a single file not to scare potential users with too much
    # structure to learn. Remember that, in order to make
    # deployment easy, we are being quite strict here in terms of
    # templates, etc.
    replaces = {
        "title" : config.pop("title"),
        "description" : config.pop("description"),
        "author" : config.pop("author"),
        "icon" : config.pop("icon"), # TODO: rename to favicon
        "mainlink": config.pop("mainlink"), # TODO: should be derived from URL?
        "citation": config.pop("citation"),
        "footer" : _md2html(config.pop("footer_file"), base_path),
        "home_sb_main" : _md2html(config.pop("index_file"), base_path),
        "home_sidebar" : _md2html(config.pop("sidebar_file"), base_path),
    }

    return config, replaces

def main():
    """
    Entry point for the script.
    """

    # Obtain `base_path` for file manipulation
    base_path = Path(__file__).parent.resolve()

    # Load JSON configuration and replaces, and include paths in the first
    # TODO: allow user-specified output
    config, replaces = load_config(base_path)
    config['base_path'] = base_path
    config['output_path'] = base_path / "_site"

    # Load HTML templates
    sb_template, nosb_template = load_templates(config)

    # Build and write index.html
    # TODO: read replace dictionary
    build_index(sb_template, replaces, config)

    # Read data tables from CLDF files
    cldf_data = read_cldf_data(base_path, config)
    build_tables(cldf_data, replaces, nosb_template, config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

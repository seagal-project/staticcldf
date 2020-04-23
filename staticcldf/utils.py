"""
Utility functions.
"""

# Import Python standard libraries
import json
import logging

# Import 3rd party libraries
from jinja2 import Environment, FileSystemLoader
import markdown


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

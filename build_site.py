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
import logging
from pathlib import Path

# Import library
from staticcldf import fill_template, read_cldf_data, build_html, build_tables, load_templates, load_config

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

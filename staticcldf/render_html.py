import datetime
import logging

from tabulate import tabulate

from . import utils


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


# TODO: write properly etc. should load with other templates
def build_css(replaces, config):
    # Build template_file and layout path
    template_path = config["base_path"] / "template"
    css_file = template_path / "main.css"

    # Build css file
    with open(css_file.as_posix()) as handler:
        css_template = handler.read()

    # Build Jinja Environment
    from jinja2 import Environment, FileSystemLoader

    template = Environment(
        loader=FileSystemLoader(template_path.as_posix())
    ).from_string(css_template)

    source = template.render(**replaces)

    # build and writeWrite
    file_path = config["output_path"] / "main.css"
    with open(file_path.as_posix(), "w") as handler:
        handler.write(source)


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
    source = template.render(
        current_time=datetime.datetime.now().ctime(), **replaces
    )

    # Write
    file_path = config["output_path"] / output_file
    with open(file_path.as_posix(), "w") as handler:
        handler.write(source)

    logging.info("`%s` wrote with %i bytes.", output_file, len(source))


def render_html(cldf_data, replaces, config):
    # Load Jinja HTML template
    template = utils.load_templates(config)

    # Build and write index.html
    build_html(template, replaces, "index.html", config)

    # Build tables from CLDF data
    build_tables(cldf_data, replaces, template, config)

    # Build CSS files from template
    build_css(replaces, config)

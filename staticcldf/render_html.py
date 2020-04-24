import datetime
import logging

from tabulate import tabulate

from . import utils


def build_tables(data, replaces, template_env, config):
    # write forms
    html_table = tabulate(
        data["Forms"], headers="firstrow", tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    form_replaces = replaces.copy()
    form_replaces["contents"] = html_table
    build_html(template_env, form_replaces, "forms.html", config)

    # write languages
    html_table = tabulate(
        data["Languages"], headers="firstrow", tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    lang_replaces = replaces.copy()
    lang_replaces["contents"] = html_table
    build_html(template_env, lang_replaces, "languages.html", config)

    # write concepts
    html_table = tabulate(
        data["Parameters"], headers="firstrow", tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    param_replaces = replaces.copy()
    param_replaces["contents"] = html_table
    build_html(template_env, param_replaces, "parameters.html", config)

    # write cognates
    html_table = tabulate(
        data["Cognates"], headers="firstrow", tablefmt="html"
    )
    html_table = html_table.replace(
        "<table>", '<table id="data_table" class="display">'
    )
    param_replaces = replaces.copy()
    param_replaces["contents"] = html_table
    build_html(template_env, param_replaces, "cognates.html", config)

# TODO: write properly etc. should load with other templates;
# TODO: also copy images if needed
def build_css(replaces, config):
    # Build template_file and layout path
    template_path = config["base_path"] / "template_html"
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


def build_html(template_env, replaces, output_file, config):
    """
    Build and write an HTML file from template and replacements.
    """

    tables = [
        {'name': 'Languages', 'url':'languages.html'},
        {'name': 'Parameters', 'url':'parameters.html'},
        {'name': 'Forms', 'url':'forms.html'},
        {'name': 'Cognates', 'url':'cognates.html'},
    ]

    # Load proper template and apply replacements, also setting current date
    logging.info("Applying replacements to generate `%s`...", output_file)
    template = template_env.get_template("layout.html")
    source = template.render(
        tables=tables,
        file=output_file,
        current_time=datetime.datetime.now().ctime(), **replaces
    )

    # Write
    file_path = config["output_path"] / output_file
    with open(file_path.as_posix(), "w") as handler:
        handler.write(source)

    logging.info("`%s` wrote with %i bytes.", output_file, len(source))


def render_html(cldf_data, replaces, config):
    # Load Jinja HTML template environment
    template_env = utils.load_template_env(config)

    # Build and write index.html
    build_html(template_env, replaces, "index.html", config)

    # Build tables from CLDF data
    build_tables(cldf_data, replaces, template_env, config)

    # Build CSS files from template
    build_css(replaces, config)

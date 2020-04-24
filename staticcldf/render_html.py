import datetime
import logging

from tabulate import tabulate

from . import utils

# TODO: fix navigation bar


def build_tables(data, replaces, template_env, config):
    for table in data:
        values = [
            [cell["value"] for cell in row] for row in data[table]["rows"]
        ]

        html_table = tabulate(
            values, headers=data[table]["columns"], tablefmt="html"
        )
        html_table = html_table.replace(
            "<table>", '<table id="data_table" class="display">'
        )

        table_replaces = replaces.copy()
        table_replaces["contents"] = html_table
        build_html(template_env, table_replaces, "%s.html" % table, config)


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
        {"name": "Languages", "url": "languages.html"},
        {"name": "Parameters", "url": "parameters.html"},
        {"name": "Forms", "url": "forms.html"},
        {"name": "Cognates", "url": "cognates.html"},
    ]

    # Load proper template and apply replacements, also setting current date
    logging.info("Applying replacements to generate `%s`...", output_file)
    if output_file == "index.html":
        template = template_env.get_template("index.html")
    else:
        template = template_env.get_template("datatable.html")
    source = template.render(
        tables=tables,
        file=output_file,
        current_time=datetime.datetime.now().ctime(),
        **replaces
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

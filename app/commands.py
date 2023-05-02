# -*- coding: utf-8 -*-
"""Click commands."""
import os
import socket
import sys
from string import Template
from subprocess import call

import click
import toml
from flask import Flask, current_app
from flask.cli import with_appcontext
from werkzeug.exceptions import MethodNotAllowed, NotFound


@click.command()
def test():
    """Run the tests."""
    import pytest

    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.join(here, os.pardir)
    test_path = os.path.join(project_root, "tests")

    rv = pytest.main([test_path, "--verbose"])
    exit(rv)


@click.command()
@click.option(
    "-f",
    "--format",
    default=False,
    is_flag=True,
    help="Format code using black and isort",
)
@click.option(
    "-o",
    "--output-file",
    default=None,
    help="Specify lint problems output file",
)
def lint(format, output_file):
    linter(format, output_file)


def getfiles_paths(path):
    files = []

    for dirpath, dirs, filenames in os.walk(path):
        files = files + [os.path.abspath(os.path.join(dirpath, f)) for f in filenames]

        for dir in dirs:
            files = files + getfiles_paths(dir)

    return files


def linter(format, output_file):
    """Lint and check code style with flake8 and isort."""

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args)
        click.echo(f"{description}: {' '.join(command_line)}")
        click.echo(os.getcwd())
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if format:
        execute_tool("Fixing import order", "isort", ".")
        execute_tool("Formating code with black", "black", ".")
    execute_tool(
        "Checking code style",
        "flake8",
        "app/",
        "" if not output_file else f"--output-file={output_file}",
    )


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".pyc") or filename.endswith(".pyo"):
                full_pathname = os.path.join(dirpath, filename)
                click.echo("Removing {}".format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option("--url", default=None, help="Url to test (ex. /static/image.png)")
@click.option(
    "--order", default="rule", help="Property on Rule to order by (default: rule)"
)
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_headers = ("Rule", "Endpoint", "Arguments")

    if url:
        try:
            rule, arguments = current_app.url_map.bind("localhost").match(
                url, return_rule=True
            )
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(("<{}>".format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(), key=lambda rule: getattr(rule, order)
        )
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ""
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += "{:" + str(max_rule_length) + "}"
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        max_endpoint_length = max_endpoint_length if max_endpoint_length > 8 else 8
        str_template += "  {:" + str(max_endpoint_length) + "}"
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = max_arguments_length if max_arguments_length > 9 else 9
        str_template += "  {:" + str(max_arguments_length) + "}"
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo("-" * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))


@click.command()
@click.option(
    "--service",
    default=False,
    is_flag=True,
    help="Register Service",
)
@click.option(
    "--public",
    default=False,
    is_flag=True,
    help="Configure nginx server to be public",
)
@with_appcontext
def config_app(service: bool, public: bool):
    url = configure_nginx(public)
    if service:
        configure_systemd_process()

    click.echo(f"App is running on {url}")


def configure_systemd_process():
    click.echo("Configuring sytemd #### Requires sudo ####")
    app_name = (
        toml.load(os.path.join(os.getcwd(), "pyproject.toml"))
        .get("tool", {})
        .get("poetry", {})
        .get("name")
    )

    systemd_template = os.path.join(os.getcwd(), "config", "systemd.conf")
    systemd_conf_path = os.path.join(os.getcwd(), "config", f"{app_name}.service")
    python_path = ""
    for p in sys.path:
        try:
            if os.path.exists(os.path.join(p, "gunicorn")):
                python_path = os.path.join(p.split("/lib")[0], "bin", "gunicorn")
        except Exception:
            pass

    call(["sudo", "mkdir", "-p", f"/var/log/{app_name}"])
    call(["sudo", "touch", "-a", f"/var/log/{app_name}/access.log"])

    with open(systemd_template, "r") as fp:
        systemd_conf = Template(fp.read()).substitute(
            PATH=os.getcwd(),
            PYTHON_PATH=python_path,
        )
    with open(systemd_conf_path, "w") as fp:
        fp.write(systemd_conf)
    call(
        [
            "sudo",
            "mv",
            "-f",
            systemd_conf_path,
            f"/etc/systemd/system/{app_name}.service",
        ]
    )
    call(["sudo", "systemctl", "daemon-reload"])
    call(["sudo", "systemctl", "enable", f"{app_name}.service"])
    call(["sudo", "systemctl", "restart", f"{app_name}.service"])


def configure_nginx(public: bool):
    click.echo("Configuring nginx #### Requires sudo ####")

    app_name = (
        toml.load(os.path.join(os.getcwd(), "pyproject.toml"))
        .get("tool", {})
        .get("poetry", {})
        .get("name")
    )

    nginx_template = os.path.join(os.getcwd(), "config", "nginx.conf")
    nginx_conf_path = os.path.join(os.getcwd(), "config", app_name)
    host = "0.0.0.0" if public else "127.0.0.1"
    with open(nginx_template, "r") as fp:
        nginx_conf = Template(fp.read()).substitute(
            PORT=current_app.config["PORT"],
            PATH=os.getcwd(),
            URL_PREFIX=current_app.config["DASH_APP_URL"],
            APP_NAME=app_name,
            HOST=host,
        )
    with open(nginx_conf_path, "w") as fp:
        fp.write(nginx_conf)
    call(
        [
            "sudo",
            "mv",
            nginx_conf_path,
            f"/etc/nginx/sites-available/{app_name}",
        ]
    )
    call(
        [
            "sudo",
            "ln",
            "-sf",
            f"/etc/nginx/sites-available/{app_name}",
            f"/etc/nginx/sites-enabled/{app_name}",
        ],
    )
    click.echo("You need to restart nginx by running the following command")
    click.echo("sudo service nginx restart")


def get_ip():
    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)

    return IP_addres


def register_commands(app: Flask):
    """Register Click commands."""
    app.cli.add_command(test)
    app.cli.add_command(lint)
    app.cli.add_command(clean)
    app.cli.add_command(urls)
    app.cli.add_command(config_app, "config-app")

    return app

# -*- coding: utf-8 -*-

"""Console script for datavault."""

import click
import logging

import sys

from datavault import DataVault


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    log_level = logging.DEBUG

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)


@click.command()
@click.argument('port', type=int)
@click.argument('password', default='admin')
def main(port, password):
    """Console script for datavault."""
    setup_logging()

    vault = DataVault(port=port, admin_password=password)

    if port < 0 or port > 65535:
        sys.exit(255)

    try:
        vault.start()
    except KeyboardInterrupt:
        vault.stop()


if __name__ == "__main__":
    main()

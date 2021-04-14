import click

from faint.favs import favs

@click.group()
def cli():
    pass

cli.add_command(favs)

if __name__ == "__main__":
    cli()
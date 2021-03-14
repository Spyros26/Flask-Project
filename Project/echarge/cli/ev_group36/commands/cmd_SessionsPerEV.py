import click
import requests


url = "http://localhost:8765/evcharge/api/SessionsPerEV/"

class Context:
    def __init__(self, ev, datefrom, dateto, format, apikey):
        self.ev = ev
        self.datefrom = datefrom
        self.dateto = dateto
        self.format = format
        self.apikey = apikey
        

@click.group()
@click.option("--ev")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--format", default="json", show_default=True)
@click.option("--apikey")
@click.pass_context
def cli(ctx, ev, datefrom, dateto, format, apikey):
    ctx.obj = Context(ev, datefrom, dateto, format, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.ev + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto + "?format=" + ctx.obj.format, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
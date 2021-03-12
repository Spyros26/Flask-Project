import click
import requests


url = "http://127.0.0.1:5000/SessionsPerEV/"

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
@click.option("--format")
@click.option("--apikey")
@click.pass_context
def cli(ctx, ev, datefrom, dateto, format, apikey):
    ctx.obj = Context(ev, datefrom, dateto, format, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.ev + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto + "?format=" + ctx.obj.format, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
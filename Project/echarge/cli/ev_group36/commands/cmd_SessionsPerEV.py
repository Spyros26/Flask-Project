import click
import requests


url = "http://127.0.0.1:5000/SessionsPerEV/"

class Context:
    def __init__(self, ev, datefrom, dateto, apikey):
        self.ev = ev
        self.datefrom = datefrom
        self.dateto = dateto
        self.apikey = apikey
        

@click.group()
@click.option("--ev")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--apikey")
@click.pass_context
def cli(ctx, ev, datefrom, dateto, apikey):
    ctx.obj = Context(ev, datefrom, dateto, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.ev + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
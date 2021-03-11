import click
import requests


url = "http://127.0.0.1:5000/SessionsPerProvider/"

class Context:
    def __init__(self, provider, datefrom, dateto, apikey):
        self.provider = provider
        self.datefrom = datefrom
        self.dateto = dateto
        self.apikey = apikey
        

@click.group()
@click.option("--provider")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--apikey")
@click.pass_context
def cli(ctx, provider, datefrom, dateto, apikey):
    ctx.obj = Context(provider, datefrom, dateto, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.provider + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
import click
import requests


url = "http://localhost:8765/evcharge/api/SessionsPerProvider/"

class Context:
    def __init__(self, provider, datefrom, dateto, format, apikey):
        self.provider = provider
        self.datefrom = datefrom
        self.dateto = dateto
        self.format = format
        self.apikey = apikey
        

@click.group()
@click.option("--provider")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--format")
@click.option("--apikey")
@click.pass_context
def cli(ctx, provider, datefrom, dateto, format, apikey):
    ctx.obj = Context(provider, datefrom, dateto, format, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    if not ctx.obj.format:
        ctx.obj.format = "json"
    response = requests.get(url + ctx.obj.provider + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto + "?format=" + ctx.obj.format, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
import click
import requests


url = "http://127.0.0.1:5000/SessionsPerPoint/"

class Context:
    def __init__(self, point, datefrom, dateto, format, apikey):
        self.point = point
        self.datefrom = datefrom
        self.dateto = dateto
        self.format = format
        self.apikey = apikey
        

@click.group()
@click.option("--point")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--format")
@click.option("--apikey")
@click.pass_context
def cli(ctx, point, datefrom, dateto, format, apikey):
    ctx.obj = Context(point, datefrom, dateto, format, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.point + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto + "?format=" + ctx.obj.format, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
    

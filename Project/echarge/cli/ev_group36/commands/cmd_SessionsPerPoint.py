import click
import requests


url = "http://127.0.0.1:5000/SessionsPerPoint/"

class Context:
    def __init__(self, point, datefrom, dateto, apikey):
        self.point = point
        self.datefrom = datefrom
        self.dateto = dateto
        self.apikey = apikey
        

@click.group()
@click.option("--point")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--apikey")
@click.pass_context
def cli(ctx, point, datefrom, dateto, apikey):
    ctx.obj = Context(point, datefrom, dateto, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.point + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
    

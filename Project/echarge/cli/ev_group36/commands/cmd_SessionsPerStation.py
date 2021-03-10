import click
import requests


url = "http://127.0.0.1:5000/SessionsPerStation/"

class Context:
    def __init__(self, station, datefrom, dateto, apikey):
        self.station = station
        self.datefrom = datefrom
        self.dateto = dateto
        self.apikey = apikey
        

@click.group()
@click.option("--station")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--apikey")
@click.pass_context
def cli(ctx, station, datefrom, dateto, apikey):
    ctx.obj = Context(station, datefrom, dateto, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.station + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
import click
import requests


url = "http://localhost:8765/evcharge/api/SessionsPerStation/"

class Context:
    def __init__(self, station, datefrom, dateto, format, apikey):
        self.station = station
        self.datefrom = datefrom
        self.dateto = dateto
        self.format = format
        self.apikey = apikey
        

@click.group()
@click.option("--station")
@click.option("--datefrom")
@click.option("--dateto")
@click.option("--format", default="json", show_default=True)
@click.option("--apikey")
@click.pass_context
def cli(ctx, station, datefrom, dateto, format, apikey):
    ctx.obj = Context(station, datefrom, dateto, format, apikey)


@cli.command()
@click.pass_context
def show(ctx):
    response = requests.get(url + ctx.obj.station + "/" + ctx.obj.datefrom + "/" + ctx.obj.dateto + "?format=" + ctx.obj.format, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
import click
import requests


url = "http://localhost:8765/evcharge/api/logout"

class Context:
    def __init__(self, apikey):
        self.apikey = apikey
        

@click.group()
@click.option("--apikey")
@click.pass_context
def cli(ctx, apikey):
    ctx.obj = Context(apikey)


@cli.command()
@click.pass_context
def logout(ctx):
    response = requests.post(url, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
    

import click
import requests


url = "http://127.0.0.1:5000/logout"

class Context:
    def __init__(self, apikey):
        self.apikey = apikey
        

@click.group()
@click.option("--apikey")
@click.pass_context
def cli(ctx, apikey):
    ctx.obj = Context(apikey)


@cli.command()
@token_required
@click.pass_context
def logout(ctx):
    response = requests.post(url, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
    

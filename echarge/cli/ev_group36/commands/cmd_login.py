import click
import requests


url = "http://localhost:8765/evcharge/api/login"

class Context:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        

@click.group()
@click.option("--username")
@click.option("--password")
@click.pass_context
def cli(ctx, username, password):
    ctx.obj = Context(username, password)


@cli.command()
@click.pass_context
def login(ctx):
    response = requests.post(url, data = {'username':ctx.obj.username, 'password':ctx.obj.password})
    print(response.text)
    

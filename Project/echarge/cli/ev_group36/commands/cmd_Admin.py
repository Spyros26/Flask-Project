import click
import requests


url = "http://127.0.0.1:5000/admin/usermod/"
url2 = "http://127.0.0.1:5000/admin/users/"
url3 = "http://127.0.0.1:5000/admin/healthcheck"
url4 = "http://127.0.0.1:5000/admin/resetsessions"

class Context:
    def __init__(self, username, password, apikey):
        self.username = username
        self.password = password
        self.apikey = apikey
        

@click.group()
@click.option("--username")
@click.option("--password")
@click.option("--apikey")
@click.pass_context
def cli(ctx, username, password, apikey):
    ctx.obj = Context(username, password, apikey)


@cli.command()
@click.pass_context
def usermod(ctx):
    response = requests.post(url + ctx.obj.username + "/" + ctx.obj.password, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
    
@cli.command()
@click.pass_context
def users(ctx):
    response = requests.get(url2 + ctx.obj.username, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)

@cli.command()
@click.pass_context
def healthcheck(ctx):
    response = requests.get(url3, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)

@cli.command()
@click.pass_context
def resetsessions(ctx):
    response = requests.post(url4, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
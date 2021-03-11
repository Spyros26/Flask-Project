import click
import requests


url = "http://127.0.0.1:5000/admin/usermod/"
url2 = "http://127.0.0.1:5000/admin/users/"
url3 = "http://127.0.0.1:5000/admin/healthcheck"
url4 = "http://127.0.0.1:5000/admin/resetsessions"
url5 = "http://127.0.0.1:5000/admin/system/sessionsupd"

class Context:
    def __init__(self, username, password, source, role, apikey):
        self.username = username
        self.password = password
        self.source = source
        self.role = role
        self.apikey = apikey
        

@click.group()
@click.option("--username")
@click.option("--password")
@click.option("--source")
@click.option("--role")
@click.option("--apikey")
@click.pass_context
def cli(ctx, username, password, source, role, apikey):
    ctx.obj = Context(username, password, source, role, apikey)


@cli.command()
@click.pass_context
def usermod(ctx):
    response = requests.post(url + ctx.obj.username + "/" + ctx.obj.password + "/" + ctx.obj.role, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
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

@cli.command()
@click.pass_context
def sessionsupd(ctx):
    response = requests.post(url5, data = {'file':ctx.obj.source}, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
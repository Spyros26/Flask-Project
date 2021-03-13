import click
import requests


url = "http://localhost:8765/evcharge/api/admin/usermod/"
url2 = "http://localhost:8765/evcharge/api/admin/users/"
url3 = "http://localhost:8765/evcharge/api/admin/healthcheck"
url4 = "http://localhost:8765/evcharge/api/admin/resetsessions"
url5 = "http://localhost:8765/evcharge/api/admin/system/sessionsupd"

class Context:
    def __init__(self, username, password, source, role, format, apikey):
        self.username = username
        self.password = password
        self.source = source
        self.role = role
        self.format = format
        self.apikey = apikey
        

@click.group()
@click.option("--username")
@click.option("--password")
@click.option("--source")
@click.option("--role")
@click.option("--format")
@click.option("--apikey")
@click.pass_context
def cli(ctx, username, password, source, role, format, apikey):
    ctx.obj = Context(username, password, source, role, format, apikey)


@cli.command()
@click.pass_context
def usermod(ctx):
    response = requests.post(url + ctx.obj.username + "/" + ctx.obj.password + "/" + ctx.obj.role, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
    
@cli.command()
@click.pass_context
def users(ctx):
    if not ctx.obj.format:
        ctx.obj.format = "json"
    response = requests.get(url2 + ctx.obj.username + "?format=" + ctx.obj.format, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
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
    if not ctx.obj.format:
        ctx.obj.format = "json"
    response = requests.post(url5 + "?format=" + ctx.obj.format, data = {'file':ctx.obj.source}, headers = {'X-OBSERVATORY-AUTH':ctx.obj.apikey})
    print(response.text)
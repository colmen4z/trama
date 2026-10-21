from collections import defaultdict
from pathlib import Path
from typing import Annotated
import typer
from jinja2 import Environment, FileSystemLoader
from rich.prompt import Prompt
from rich.console import Console

app = typer.Typer()
console = Console()


def create_project_dir(
    name: str,
    base_path: Path
):
    project_dir = base_path / name if base_path.name != name else base_path
    project_dir.mkdir(parents=True, exist_ok=True)
    console.print(f'[green][INFO][/green] Project initialized in [cyan]{project_dir}[/cyan]')
    return project_dir


def ask(
    prompt_text: str,
    error_msg: str,
    note_text: str,
    is_required: bool,
    default_value: str = ""
) -> str:
    if note_text:
        console.print(f'[bright_black][NOTE] {note_text}[/bright_black]')

    value = Prompt.ask(prompt_text, default=default_value) if default_value else Prompt.ask(prompt_text)
    
    if is_required and not value.strip():
        console.print(f'[red][ERROR][/red] [bright_red]{error_msg}[/bright_red]')
        raise typer.Exit(code=1)

    return value.strip()


@app.command()
def init():
    current_path = Path.cwd()

    # Project settings prompts
    project_name = ask(
        prompt_text='Enter the project name [red](required)[/red]',
        error_msg='The project name is required',
        note_text='You can just type . to name and create the project in the current directory',
        is_required=True
    )
    project_description = ask(
        prompt_text='Enter the project description [bright_black](not required)[/bright_black]',
        error_msg='',
        note_text='',
        is_required=False
    )
    project_author = ask(
        prompt_text='Enter the project author name [bright_black](not required)[/bright_black]',
        error_msg='',
        note_text='',
        is_required=False
    )
    project_version = '0.0.1'
    console.print(f'[green]Project version set {project_version}[/green] \n')

    # Server settings prompts
    server_host = ask(
        prompt_text='Enter the project server host [bright_black](not required)[/bright_black]',
        error_msg='',
        note_text='',
        is_required=False,
        default_value='127.0.0.1'
    )
    server_port = ask(
        prompt_text='Enter the project server port [bright_black](not required)[/bright_black]',
        error_msg='',
        note_text='',
        is_required=False,
        default_value='1507'
    )


    if project_name == '.':
        real_project_name = current_path.name
        project_path = current_path
    else:
        real_project_name = project_name
        project_path = current_path / project_name

    create_project_dir(real_project_name, project_path)

    templates_dir = Path(__file__).parent / 'blueprints' / 'project'

    if not templates_dir.exists():
        console.print(f'[red][ERROR][/red] [bright_red]Templates directory not found at {templates_dir}[/bright_red]')
        raise typer.Exit(code=1)

    env = Environment(loader=FileSystemLoader(str(templates_dir)))

    try:
        template = env.get_template("trama.yaml.j2")
    except Exception as e:
        console.print(f'[red][ERROR][/red] [bright_red]Could not load trama.yaml.j2[/bright_red]')
        raise typer.Exit(code=1)

    context = {
        "project_name": real_project_name,
        "project_description": project_description,
        "project_author": project_author,
        "project_version": project_version,
        "server_host": server_host,
        "server_port": server_port,
    }

    rendered_content = template.render(context)
    output_file = project_path / "test.yaml"
    output_file.write_text(rendered_content, encoding="utf-8")

    console.print(f'[bold green]Successfully generated configuration at:[/bold green] [cyan]{output_file}[/cyan]')

@app.command()
def test():
    pass


def main():
    app()

if __name__ == '__main__':
    main()
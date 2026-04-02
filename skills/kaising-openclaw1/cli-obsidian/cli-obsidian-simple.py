#!/usr/bin/env python3
"""
CLI-Obsidian: Simple standalone version for testing
"""

import click
import json
import os
from pathlib import Path
from datetime import datetime


@click.group(invoke_without_command=True)
@click.option('--vault-path', '-v', type=click.Path(), help='Path to Obsidian vault')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def cli(ctx, vault_path, json_output):
    """CLI-Obsidian: Agent-native interface for Obsidian"""
    ctx.ensure_object(dict)
    ctx.obj['json_output'] = json_output
    ctx.obj['vault_path'] = vault_path or os.getcwd()
    
    if ctx.invoked_subcommand is None:
        click.echo("Use --help for available commands")


@cli.command()
@click.option('--title', '-t', required=True, help='Note title')
@click.option('--tags', help='Comma-separated tags')
@click.pass_context
def create(ctx, title, tags):
    """Create a new note"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    safe_title = title.replace('/', '-').replace('\\', '-')
    note_path = vault_path / f"{safe_title}.md"
    
    content = f"# {title}\n\n"
    if tags:
        content += f"Tags: {tags}\n\n"
    content += f"Created: {datetime.now().isoformat()}\n"
    
    note_path.write_text(content)
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({
            "action": "create",
            "path": str(note_path.absolute()),
            "title": title,
            "tags": tags.split(',') if tags else []
        }, indent=2))
    else:
        click.echo(f"✓ Created: {note_path.name}")


@cli.command()
@click.option('--limit', default=20, help='Max notes')
@click.pass_context
def list(ctx, limit):
    """List notes"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    notes = [f.stem for f in vault_path.glob("*.md") if not f.name.startswith('.')]
    notes = notes[:limit]
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({"notes": notes}, indent=2))
    else:
        click.echo(f"📊 Found {len(notes)} notes:")
        for n in notes:
            click.echo(f"  📄 {n}")


@cli.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """Search notes"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    results = []
    
    for f in vault_path.glob("*.md"):
        if query.lower() in f.name.lower():
            results.append(f.stem)
        elif query.lower() in f.read_text().lower():
            results.append(f.stem)
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({"results": results}, indent=2))
    else:
        click.echo(f"🔍 Found {len(results)} results for '{query}':")
        for r in results[:10]:
            click.echo(f"  📄 {r}")


if __name__ == '__main__':
    cli()

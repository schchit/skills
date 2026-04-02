"""Note management commands"""

import click
import json
from pathlib import Path
from datetime import datetime


@click.group()
@click.pass_context
def cli(ctx):
    """Note management commands"""
    pass


@cli.command()
@click.option('--title', '-t', required=True, help='Note title')
@click.option('--tags', help='Comma-separated tags')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def create(ctx, title, tags, output):
    """Create a new note"""
    vault_path = ctx.obj.get('vault_path', Path.cwd())
    
    # Generate filename
    if output:
        note_path = Path(output)
    else:
        safe_title = title.replace('/', '-').replace('\\', '-')
        note_path = Path(vault_path) / f"{safe_title}.md"
    
    # Create content
    content = f"# {title}\n\n"
    if tags:
        content += f"Tags: {tags}\n\n"
    content += f"Created: {datetime.now().isoformat()}\n\n"
    
    # Write file
    note_path.write_text(content)
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({
            "action": "create",
            "path": str(note_path.absolute()),
            "title": title,
            "tags": tags.split(',') if tags else [],
            "created": datetime.now().isoformat()
        }, indent=2))
    else:
        click.echo(f"✓ Created note: {note_path.name}")
        click.echo(f"  Path: {note_path.absolute()}")


@cli.command()
@click.option('--tag', help='Filter by tag')
@click.option('--limit', default=20, help='Max notes to show')
@click.pass_context
def list(ctx, tag, limit):
    """List notes in vault"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    
    notes = []
    for f in vault_path.glob("*.md"):
        if f.name.startswith('.'):
            continue
        notes.append({
            "name": f.stem,
            "path": str(f.absolute()),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    
    notes = notes[:limit]
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({"notes": notes}, indent=2))
    else:
        click.echo(f"📊 Found {len(notes)} notes:\n")
        for n in notes:
            click.echo(f"  📄 {n['name']}")


@cli.command()
@click.argument('title')
@click.pass_context
def open(ctx, title):
    """Open a note"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    
    # Try exact match first
    note_path = vault_path / f"{title}.md"
    if not note_path.exists():
        # Try fuzzy match
        for f in vault_path.glob("*.md"):
            if title.lower() in f.stem.lower():
                note_path = f
                break
    
    if not note_path.exists():
        if ctx.obj.get('json_output'):
            click.echo(json.dumps({"error": f"Note not found: {title}"}))
        else:
            click.echo(f"✗ Note not found: {title}")
        return
    
    content = note_path.read_text()
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({
            "title": title,
            "path": str(note_path.absolute()),
            "content": content
        }, indent=2))
    else:
        click.echo(f"📄 {note_path.name}:\n")
        click.echo(content[:500])
        if len(content) > 500:
            click.echo("\n... (truncated)")

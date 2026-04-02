"""Vault management commands"""

import click
import json
from pathlib import Path


@click.group()
@click.pass_context
def cli(ctx):
    """Vault management commands"""
    pass


@cli.command()
@click.pass_context
def info(ctx):
    """Show vault information"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    
    # Count files
    md_files = list(vault_path.glob("*.md"))
    attachments = list(vault_path.glob("*.{png,jpg,jpeg,gif,pdf}"))
    
    info = {
        "path": str(vault_path.absolute()),
        "notes": len(md_files),
        "attachments": len(attachments),
        "exists": vault_path.exists()
    }
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps(info, indent=2))
    else:
        click.echo("📊 Vault Information:")
        click.echo(f"  Path: {vault_path.absolute()}")
        click.echo(f"  Notes: {len(md_files)}")
        click.echo(f"  Attachments: {len(attachments)}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show vault statistics"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    
    md_files = list(vault_path.glob("*.md"))
    total_words = 0
    total_chars = 0
    
    for f in md_files:
        content = f.read_text()
        total_words += len(content.split())
        total_chars += len(content)
    
    stats = {
        "total_notes": len(md_files),
        "total_words": total_words,
        "total_chars": total_chars,
        "avg_words_per_note": total_words // len(md_files) if md_files else 0
    }
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps(stats, indent=2))
    else:
        click.echo("📈 Vault Statistics:")
        click.echo(f"  Total Notes: {len(md_files)}")
        click.echo(f"  Total Words: {total_words:,}")
        click.echo(f"  Total Characters: {total_chars:,}")
        click.echo(f"  Avg Words/Note: {stats['avg_words_per_note']:,}")

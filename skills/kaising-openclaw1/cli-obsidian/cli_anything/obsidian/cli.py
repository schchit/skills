"""
CLI-Obsidian: Make your Obsidian vault agent-native

Usage:
    cli-obsidian                          # Enter REPL mode
    cli-obsidian note create --title "X"  # Create note
    cli-obsidian --json note list         # JSON output for agents
"""

import click
import json
import os
from pathlib import Path
from datetime import datetime

from .commands import note, vault, search, export
from .utils.repl_skin import ReplSkin


@click.group(invoke_without_command=True)
@click.option('--vault-path', '-v', type=click.Path(exists=True), help='Path to Obsidian vault')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def cli(ctx, vault_path, json_output):
    """CLI-Obsidian: Agent-native interface for Obsidian
    
    \b
    Examples:
      cli-obsidian                          # Enter REPL mode
      cli-obsidian note create -t "Notes"   # Create note
      cli-obsidian note list --json         # List notes (JSON)
      cli-obsidian search "query"           # Search notes
    """
    ctx.ensure_object(dict)
    ctx.obj['json_output'] = json_output
    
    # Auto-detect vault path
    if vault_path is None:
        # Try common locations
        common_paths = [
            Path.home() / "Obsidian Vault",
            Path.home() / "Documents" / "Obsidian",
            Path.cwd(),
        ]
        for p in common_paths:
            if p.exists() and (p / ".obsidian").exists():
                vault_path = str(p)
                break
    
    ctx.obj['vault_path'] = vault_path or os.getcwd()
    
    # Enter REPL if no subcommand
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@click.command()
@click.pass_context
def repl(ctx):
    """Enter interactive REPL mode"""
    skin = ReplSkin("Obsidian", version="1.0.0")
    skin.print_banner()
    
    vault_path = ctx.obj.get('vault_path', os.getcwd())
    click.echo(f"📁 Vault: {vault_path}")
    click.echo()
    
    # Simple REPL loop
    while True:
        try:
            cmd = click.prompt(
                "obsidian",
                prompt_suffix="> ",
                default="help"
            )
            
            if cmd.lower() in ('quit', 'exit', 'q'):
                skin.print_goodbye()
                break
            
            # Parse and execute command
            parts = cmd.split()
            if not parts:
                continue
                
            # Basic command routing (simplified for MVP)
            if parts[0] == 'help':
                click.echo("""
Available commands:
  note create -t "Title"   Create new note
  note list                List all notes
  note open "Title"        Open note
  search "query"           Search notes
  vault info               Show vault info
  help                     Show this help
  quit/exit                Exit REPL
""")
            elif parts[0] == 'note' and len(parts) >= 2:
                if parts[1] == 'create':
                    # Simple create
                    title = "Untitled"
                    for i, p in enumerate(parts):
                        if p in ('-t', '--title') and i + 1 < len(parts):
                            title = parts[i + 1]
                    note_path = Path(vault_path) / f"{title}.md"
                    note_path.write_text(f"# {title}\n\nCreated: {datetime.now().isoformat()}\n")
                    click.echo(f"✓ Created: {note_path}")
                elif parts[1] == 'list':
                    notes = list(Path(vault_path).glob("*.md"))
                    for n in notes[:20]:
                        click.echo(f"  📄 {n.stem}")
                    if len(notes) > 20:
                        click.echo(f"  ... and {len(notes) - 20} more")
            elif parts[0] == 'search' and len(parts) > 1:
                query = ' '.join(parts[1:])
                click.echo(f"🔍 Searching for: {query}")
                # Simple filename search
                for f in Path(vault_path).glob("*.md"):
                    if query.lower() in f.name.lower():
                        click.echo(f"  📄 {f.name}")
            elif parts[0] == 'vault':
                if parts[1] == 'info':
                    notes = list(Path(vault_path).glob("*.md"))
                    click.echo(f"📊 Vault Stats:")
                    click.echo(f"  Notes: {len(notes)}")
                    click.echo(f"  Path: {vault_path}")
            else:
                click.echo(f"Unknown command: {cmd}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            click.echo()
            continue
        except Exception as e:
            click.echo(f"Error: {e}")


# Register subcommands
cli.add_command(repl)
cli.add_command(note.cli)
cli.add_command(vault.cli)
cli.add_command(search.cli)
cli.add_command(export.cli)


if __name__ == '__main__':
    cli()

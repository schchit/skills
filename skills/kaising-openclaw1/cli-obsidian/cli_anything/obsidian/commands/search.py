"""Search commands"""

import click
import json
from pathlib import Path


@click.group()
@click.pass_context
def cli(ctx):
    """Search commands"""
    pass


@cli.command()
@click.argument('query')
@click.option('--limit', default=20, help='Max results')
@click.pass_context
def search(ctx, query, limit):
    """Search notes by filename"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    
    results = []
    query_lower = query.lower()
    
    for f in vault_path.glob("*.md"):
        if query_lower in f.name.lower():
            results.append({
                "name": f.stem,
                "path": str(f.absolute()),
                "match": "filename"
            })
        if len(results) >= limit:
            break
    
    # Also search content
    if len(results) < limit:
        for f in vault_path.glob("*.md"):
            if f.name.startswith('.'):
                continue
            content = f.read_text().lower()
            if query_lower in content and f.stem not in [r['name'] for r in results]:
                # Find context
                idx = content.find(query_lower)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(query) + 50)
                context = content[start:end].replace('\n', ' ')
                
                results.append({
                    "name": f.stem,
                    "path": str(f.absolute()),
                    "match": "content",
                    "context": f"...{context}..."
                })
            
            if len(results) >= limit:
                break
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps({"results": results}, indent=2))
    else:
        click.echo(f"🔍 Search results for '{query}':\n")
        for r in results:
            match_type = "📄" if r['match'] == 'filename' else "📝"
            click.echo(f"  {match_type} {r['name']}")
            if 'context' in r:
                click.echo(f"      {r['context']}")

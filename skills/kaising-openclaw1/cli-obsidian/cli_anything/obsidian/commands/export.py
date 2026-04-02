"""Export commands"""

import click
import json
from pathlib import Path
from datetime import datetime


@click.group()
@click.pass_context
def cli(ctx):
    """Export commands"""
    pass


@cli.command()
@click.option('--output', '-o', required=True, help='Output directory')
@click.option('--format', '-f', default='markdown', type=click.Choice(['markdown', 'html', 'json']))
@click.pass_context
def markdown(ctx, output, format):
    """Export vault to specified format"""
    vault_path = Path(ctx.obj.get('vault_path', Path.cwd()))
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_files = list(vault_path.glob("*.md"))
    exported = []
    
    for f in md_files:
        content = f.read_text()
        
        if format == 'json':
            out_file = output_dir / f"{f.stem}.json"
            data = {
                "title": f.stem,
                "content": content,
                "exported": datetime.now().isoformat()
            }
            out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        elif format == 'html':
            out_file = output_dir / f"{f.stem}.html"
            content_br = content.replace('\n', '<br>')
            html = f"""<!DOCTYPE html>
<html>
<head><title>{f.stem}</title></head>
<body>
{content_br}
</body>
</html>"""
            out_file.write_text(html)
        else:  # markdown
            out_file = output_dir / f.name
            out_file.write_text(content)
        
        exported.append(str(out_file.absolute()))
    
    result = {
        "action": "export",
        "format": format,
        "count": len(exported),
        "output_dir": str(output_dir.absolute()),
        "files": exported[:10]  # Limit to first 10
    }
    
    if ctx.obj.get('json_output'):
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"✓ Exported {len(exported)} notes to {output_dir}")
        click.echo(f"  Format: {format}")

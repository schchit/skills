"""REPL skin for consistent UI"""

import click


class ReplSkin:
    """Consistent REPL interface styling"""
    
    def __init__(self, app_name: str, version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version
    
    def print_banner(self):
        """Print branded startup banner"""
        click.echo(f"╔══════════════════════════════════════╗")
        click.echo(f"║       cli-{self.app_name.lower()} v{self.version:<18}║")
        click.echo(f"║     {self.app_name} CLI for AI Agents        ║")
        click.echo(f"╚══════════════════════════════════════╝")
    
    def print_goodbye(self):
        """Print exit message"""
        click.echo("\n👋 Goodbye!")
    
    def success(self, message: str):
        """Print success message"""
        click.echo(f"✓ {message}")
    
    def error(self, message: str):
        """Print error message"""
        click.echo(f"✗ {message}")
    
    def warning(self, message: str):
        """Print warning message"""
        click.echo(f"⚠ {message}")
    
    def info(self, message: str):
        """Print info message"""
        click.echo(f"● {message}")
    
    def table(self, headers: list, rows: list):
        """Print formatted table"""
        # Simple table
        header_line = " | ".join(str(h) for h in headers)
        click.echo(header_line)
        click.echo("-" * len(header_line))
        for row in rows:
            click.echo(" | ".join(str(c) for c in row))

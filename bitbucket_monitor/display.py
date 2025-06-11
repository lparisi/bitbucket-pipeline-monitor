"""
Terminal display utilities for the Bitbucket Pipeline Monitor.
"""
from typing import List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .models import Pipeline, PipelineStep, PipelineVariable


class PipelineDisplay:
    """Display utilities for pipeline information."""
    
    STATUS_COLORS = {
        "SUCCESSFUL": "green",
        "COMPLETED": "green",
        "FAILED": "red",
        "ERROR": "red",
        "STOPPED": "yellow",
        "PAUSED": "yellow",
        "IN_PROGRESS": "blue",
        "PENDING": "cyan",
        "RUNNING": "blue",
    }
    
    def __init__(self) -> None:
        """Initialize the display with a Rich console."""
        self.console = Console()
    
    def _get_status_color(self, status: str) -> str:
        """Get the color for a status string."""
        return self.STATUS_COLORS.get(status.upper(), "white")
    
    def display_pipeline(self, pipeline: Pipeline) -> None:
        """
        Display pipeline information in the terminal.
        
        Args:
            pipeline: The pipeline to display
        """
        # Clear the console
        self.console.clear()
        
        # Create layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=4),
            Layout(name="main")
        )
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header with pipeline info
        status_color = self._get_status_color(pipeline.status)
        header_text = Text()
        header_text.append(f"Pipeline: ", style="bold")
        header_text.append(f"{pipeline.pipeline_name}\n", style=f"bold {status_color}")
        header_text.append(f"Status: ", style="bold")
        header_text.append(f"{pipeline.status}\n", style=status_color)
        header_text.append(f"Duration: ", style="bold")
        header_text.append(f"{pipeline.duration_str}")
        
        header = Panel(
            header_text,
            title=f"[bold]{pipeline.repository}[/bold] ({pipeline.branch})",
            subtitle=f"Started: {pipeline.created_on.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        layout["header"].update(header)
        
        # Left side - Commit info
        commit_text = Text()
        commit_text.append(f"Commit: ", style="bold")
        commit_text.append(f"{pipeline.commit.hash[:8]}\n")
        commit_text.append(f"Author: ", style="bold")
        commit_text.append(f"{pipeline.commit.author}\n")
        commit_text.append(f"Date: ", style="bold")
        commit_text.append(f"{pipeline.commit.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        commit_text.append(f"Message:\n", style="bold")
        commit_text.append(f"{pipeline.commit.message}")
        
        commit_panel = Panel(commit_text, title="[bold]Commit Information[/bold]")
        
        # Variables table
        variables_table = Table(title="Pipeline Variables", show_header=True, header_style="bold")
        variables_table.add_column("Variable")
        variables_table.add_column("Value")
        
        for var in pipeline.variables:
            value = var.value if not var.secured else "********"
            variables_table.add_row(var.key, value)
        
        left_content = Text()
        left_content.append(commit_panel)
        left_content.append("\n\n")
        left_content.append(variables_table)
        layout["left"].update(left_content)
        
        # Right side - Steps
        steps_table = Table(title="Pipeline Steps", show_header=True, header_style="bold")
        steps_table.add_column("Step")
        steps_table.add_column("Status")
        steps_table.add_column("Duration")
        
        for step in pipeline.steps:
            status_style = self._get_status_color(step.status)
            steps_table.add_row(
                step.name,
                Text(step.status, style=status_style),
                step.duration_str
            )
        
        layout["right"].update(steps_table)
        
        # Render the layout
        self.console.print(layout)
    
    def display_loading(self, message: str = "Loading pipeline data...") -> Progress:
        """
        Display a loading spinner.
        
        Args:
            message: Message to display
            
        Returns:
            Progress object that can be updated
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        task_id = progress.add_task(message, total=None)
        return progress

"""
Command-line interface for the Bitbucket Pipeline Monitor.
"""
from typing import Optional
import time
import typer
from rich.console import Console

from .api import BitbucketAPIClient
from .models import Pipeline
from .display import PipelineDisplay

app = typer.Typer(help="Monitor Bitbucket pipeline executions")
console = Console()


@app.command("monitor")
def monitor_pipeline(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository in format workspace/repo-name"),
    pipeline_uuid: Optional[str] = typer.Option(None, "--pipeline-uuid", "-p", help="UUID of the pipeline to monitor"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch to monitor the latest pipeline for"),
    refresh: int = typer.Option(0, "--refresh", "-f", help="Refresh interval in seconds (0 for no refresh)"),
) -> None:
    """
    Monitor a Bitbucket pipeline execution in real-time.
    
    Displays information about the pipeline, including branch, commit, custom pipeline,
    variables, and execution duration.
    """
    if not pipeline_uuid and not branch:
        console.print("[bold red]Error:[/bold red] Either --pipeline-uuid or --branch must be specified")
        raise typer.Exit(1)
    
    try:
        api_client = BitbucketAPIClient()
        display = PipelineDisplay()
        
        # Function to fetch and display pipeline data
        def update_pipeline() -> Optional[Pipeline]:
            try:
                # Get pipeline data
                if pipeline_uuid:
                    pipeline_data = api_client.get_pipeline(repo, pipeline_uuid)
                else:
                    pipeline_data = api_client.get_latest_pipeline(repo, branch)
                
                # Get additional data
                steps_data = api_client.get_pipeline_steps(repo, pipeline_data["uuid"])
                variables_data = api_client.get_pipeline_variables(repo, pipeline_data["uuid"])
                
                # Add steps and variables to pipeline data
                pipeline_data["steps"] = steps_data
                pipeline_data["variables"] = variables_data
                
                # Create Pipeline object
                pipeline = Pipeline.from_api_response(pipeline_data)
                
                # Display pipeline
                display.display_pipeline(pipeline)
                
                return pipeline
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
                return None
        
        # Initial update
        pipeline = update_pipeline()
        if not pipeline:
            raise typer.Exit(1)
        
        # If refresh is enabled, keep updating
        if refresh > 0:
            try:
                while True:
                    time.sleep(refresh)
                    pipeline = update_pipeline()
                    
                    # If pipeline is completed, stop refreshing
                    if pipeline and pipeline.status in ["COMPLETED", "SUCCESSFUL", "FAILED", "STOPPED", "ERROR"]:
                        status_color = display._get_status_color(pipeline.status)
                        console.print(f"\n[bold]Pipeline completed with status: [bold {status_color}]{pipeline.status}[/]")
                        break
            except KeyboardInterrupt:
                console.print("\n[bold]Monitoring stopped.[/bold]")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()

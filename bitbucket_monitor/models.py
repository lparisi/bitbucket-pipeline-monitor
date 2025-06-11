"""
Data models for the Bitbucket Pipeline Monitor.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CommitInfo(BaseModel):
    """Information about the commit that triggered the pipeline."""
    hash: str
    message: str
    author: str
    date: datetime


class PipelineVariable(BaseModel):
    """A variable used in the pipeline execution."""
    key: str
    value: str
    secured: bool = False


class PipelineStep(BaseModel):
    """A step in the pipeline execution."""
    name: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    @property
    def duration_str(self) -> str:
        """Get a human-readable duration string."""
        if not self.duration_seconds:
            return "Not completed"
        
        minutes, seconds = divmod(self.duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class Pipeline(BaseModel):
    """Information about a pipeline execution."""
    uuid: str
    repository: str
    branch: str
    commit: CommitInfo
    pipeline_name: str = Field(..., description="Name of the custom pipeline being used")
    status: str
    created_on: datetime
    completed_on: Optional[datetime] = None
    variables: List[PipelineVariable] = []
    steps: List[PipelineStep] = []
    
    @property
    def duration_seconds(self) -> Optional[int]:
        """Get the duration of the pipeline in seconds."""
        if not self.completed_on:
            # If not completed, calculate duration from now
            now = datetime.now()
            return int((now - self.created_on).total_seconds())
        return int((self.completed_on - self.created_on).total_seconds())
    
    @property
    def duration_str(self) -> str:
        """Get a human-readable duration string."""
        if not self.duration_seconds:
            return "Not started"
        
        minutes, seconds = divmod(self.duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Pipeline":
        """
        Create a Pipeline instance from the Bitbucket API response.
        
        Args:
            data: The raw API response data
            
        Returns:
            A Pipeline instance
        """
        # Extract commit info
        commit_data = data.get("commit", {})
        commit = CommitInfo(
            hash=commit_data.get("hash", ""),
            message=commit_data.get("message", ""),
            author=commit_data.get("author", {}).get("display_name", ""),
            date=datetime.fromisoformat(commit_data.get("date", "").replace("Z", "+00:00"))
        )
        
        # Extract pipeline variables
        variables = []
        for var in data.get("variables", []):
            variables.append(
                PipelineVariable(
                    key=var.get("key", ""),
                    value=var.get("value", "") if not var.get("secured", False) else "********",
                    secured=var.get("secured", False)
                )
            )
        
        # Extract steps
        steps = []
        for step_data in data.get("steps", []):
            step = PipelineStep(
                name=step_data.get("name", ""),
                status=step_data.get("state", {}).get("name", ""),
                start_time=datetime.fromisoformat(step_data.get("started_on", "").replace("Z", "+00:00")) 
                    if step_data.get("started_on") else None,
                end_time=datetime.fromisoformat(step_data.get("completed_on", "").replace("Z", "+00:00"))
                    if step_data.get("completed_on") else None
            )
            
            # Calculate duration if both start and end times are available
            if step.start_time and step.end_time:
                step.duration_seconds = int((step.end_time - step.start_time).total_seconds())
            
            steps.append(step)
        
        # Create the pipeline instance
        return cls(
            uuid=data.get("uuid", ""),
            repository=data.get("repository", {}).get("full_name", ""),
            branch=data.get("target", {}).get("ref_name", ""),
            commit=commit,
            pipeline_name=data.get("target", {}).get("selector", {}).get("pattern", "default"),
            status=data.get("state", {}).get("name", ""),
            created_on=datetime.fromisoformat(data.get("created_on", "").replace("Z", "+00:00")),
            completed_on=datetime.fromisoformat(data.get("completed_on", "").replace("Z", "+00:00"))
                if data.get("completed_on") else None,
            variables=variables,
            steps=steps
        )

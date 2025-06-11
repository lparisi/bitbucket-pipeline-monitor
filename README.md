# Bitbucket Pipeline Monitor CLI

A command-line tool that provides an intuitive interface for monitoring Bitbucket pipeline executions.

## Features

- Monitor active pipeline executions in real-time
- Display branch and commit information
- Show which custom pipeline is being used
- List pipeline variables in use
- Track and display pipeline execution duration
- Provide a clean, intuitive terminal UI for monitoring

## Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/bitbucket-pipeline-monitor.git
cd bitbucket-pipeline-monitor

# Install dependencies using uv
uv pip install -r requirements.txt

# Install the package in development mode
uv pip install -e .
```

## Configuration

Create a `.env` file in the project root with your Bitbucket credentials:

```
BITBUCKET_USERNAME=your_username
BITBUCKET_APP_PASSWORD=your_app_password
# Or use workspace and token for OAuth
# BITBUCKET_WORKSPACE=your_workspace
# BITBUCKET_ACCESS_TOKEN=your_access_token
```

## Usage

```bash
# Monitor a specific pipeline
bitbucket-pipeline monitor --repo username/repo-name --pipeline-uuid PIPELINE-UUID

# Monitor the latest pipeline for a branch
bitbucket-pipeline monitor --repo username/repo-name --branch develop

# Monitor with continuous refresh (every 5 seconds)
bitbucket-pipeline monitor --repo username/repo-name --branch main --refresh 5
```

## Development

This CLI tool is built using:
- Python with type hints
- Rich for terminal UI
- Typer for CLI interface
- Pydantic for data validation
- Requests for API communication

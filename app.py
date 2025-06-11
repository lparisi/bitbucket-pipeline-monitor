#!/usr/bin/env python
"""
Main application file for the Bitbucket Pipeline Monitor extension.
"""
from typing import Dict, Any, Optional, List
import os
import json
import time
from datetime import datetime
import jwt
from flask import Flask, request, render_template, redirect, url_for, jsonify, g

from models.pipeline import PipelineData
from utils.bitbucket_api import BitbucketAPI
from utils.auth import require_auth, get_jwt_token

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.before_request
def before_request() -> None:
    """Set up context for each request."""
    g.start_time = time.time()
    
    # Extract JWT token if present
    token = request.args.get('jwt')
    if token:
        g.jwt_token = token
        try:
            g.jwt_claims = jwt.decode(
                token,
                app.config['JWT_SHARED_SECRET'],
                algorithms=['HS256']
            )
            g.client_key = g.jwt_claims.get('iss')
        except jwt.InvalidTokenError:
            g.jwt_claims = None
            g.client_key = None

@app.route('/')
def index() -> str:
    """Render the index page."""
    return render_template('index.html')

@app.route('/installed', methods=['POST'])
def installed() -> Dict[str, str]:
    """Handle the installation of the extension."""
    data = request.get_json()
    # Store client info in database (not implemented here)
    return jsonify({"status": "installed"})

@app.route('/uninstalled', methods=['POST'])
def uninstalled() -> Dict[str, str]:
    """Handle the uninstallation of the extension."""
    data = request.get_json()
    # Remove client info from database (not implemented here)
    return jsonify({"status": "uninstalled"})

@app.route('/pipeline-monitor')
@require_auth
def pipeline_monitor() -> str:
    """
    Render the pipeline monitor page.
    
    Displays information about the current pipeline execution.
    """
    repo_path = request.args.get('repoPath')
    pipeline_id = request.args.get('pipelineId')
    
    if not repo_path or not pipeline_id:
        return render_template('error.html', message="Missing repository path or pipeline ID")
    
    # Get pipeline data from Bitbucket API
    api = BitbucketAPI(get_jwt_token())
    pipeline_data = api.get_pipeline_details(repo_path, pipeline_id)
    
    # Process pipeline data
    pipeline = PipelineData.from_api_response(pipeline_data)
    
    return render_template(
        'pipeline_monitor.html',
        pipeline=pipeline,
        repo_path=repo_path
    )

@app.route('/api/pipeline/<repo_path>/<pipeline_id>')
@require_auth
def get_pipeline_data(repo_path: str, pipeline_id: str) -> Dict[str, Any]:
    """
    API endpoint to get pipeline data.
    
    Args:
        repo_path: Repository path in format username/repo-name
        pipeline_id: UUID of the pipeline
        
    Returns:
        JSON response with pipeline data
    """
    api = BitbucketAPI(get_jwt_token())
    pipeline_data = api.get_pipeline_details(repo_path, pipeline_id)
    
    if not pipeline_data:
        return jsonify({"error": "Pipeline not found"}), 404
    
    pipeline = PipelineData.from_api_response(pipeline_data)
    return jsonify(pipeline.to_dict())

@app.route('/webhook/build-status', methods=['POST'])
def webhook_build_status() -> Dict[str, str]:
    """Handle build status webhook events."""
    data = request.get_json()
    # Process webhook data (not fully implemented here)
    return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=True)

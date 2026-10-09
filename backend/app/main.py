import os
from fastapi import FastAPI, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import engine, Base, get_db
from app.models import Project, AuditIssue
from app.audit_engine import audit_codebase
from app.graph_engine import generate_codebase_graph

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodeCompass API",
    version="1.0.0",
    description="""
    Core API for CodeCompass, an AST-based static analysis and code auditing tool.
    Provides endpoints for running codebase audits, retrieving historical project reports,
    and generating call-graph visualisations.
    """
)

# Fix 1: Static API key read from environment variable at startup.
# If the variable is not set, the guard is permissive (local dev mode).
# To activate enforcement: set CODECOMPASS_API_KEY in your shell or run_demo.bat
# before starting Uvicorn.  The frontend reads the same value from secrets.toml.
_API_KEY = os.getenv("CODECOMPASS_API_KEY", "").strip()


def verify_api_key(x_api_key: str = Header("", alias="X-API-Key")):
    """
    FastAPI dependency — enforces the static API key boundary.
    Raises HTTP 401 if the server key is configured and the header does not match.
    When CODECOMPASS_API_KEY is not set (empty), all requests are allowed through
    so the app works out-of-the-box without extra configuration.
    """
    if _API_KEY and x_api_key.strip() != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")


@app.get("/")
def read_root():
    """
    Public health check endpoint.
    
    Returns a simple status message indicating that the backend is online.
    This endpoint is intentionally unauthenticated to allow the frontend 
    to verify connectivity and display a status indicator.
    
    Returns:
        dict: A dictionary containing a status message.
    """
    return {"message": "CodeCompass Engine is online"}


@app.post("/api/audit")
def run_audit(
    project_name: str = Query(..., description="Name of the project"),
    directory_path: str = Query(..., description="Path to the codebase directory"),
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)          # Fix 1: API key guard
) -> Dict[str, Any]:
    """
    Executes a static analysis audit on a specified codebase directory.
    
    This endpoint parses all Python files in the given directory using the AST engine,
    calculates a Code Readiness Score (CRS), and identifies anti-patterns. The results 
    are persisted to the SQLite database and returned to the client.
    
    Args:
        project_name (str): The human-readable name of the project being audited.
        directory_path (str): The absolute or relative file system path to the target directory.
        db (Session): The SQLAlchemy database session dependency.
        _ (None): The API key verification dependency.
        
    Returns:
        Dict[str, Any]: A dictionary containing the audit status, project metrics, 
                        CRS score, and a list of identified issues.
    """

    # 1. Run AST Static Auditor
    audit_results = audit_codebase(directory_path)

    # 2. Save Project Record to DB
    new_project = Project(
        project_name=project_name,
        crs_score=audit_results["crs_score"],
        total_files=audit_results["total_files"],
        total_functions=audit_results["total_functions"]
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # 3. Save Detected Issues to DB
    for issue in audit_results["issues"]:
        db_issue = AuditIssue(
            project_id=new_project.id,
            rule_name=issue["rule_name"],
            severity=issue["severity"],
            file_path=issue["file_path"],
            line_number=issue["line_number"],
            viva_tip=issue["viva_tip"]
        )
        db.add(db_issue)

    db.commit()

    return {
        "status": "success",
        "project_id": new_project.id,
        "project_name": new_project.project_name,
        "crs_score": new_project.crs_score,
        "total_files": new_project.total_files,
        "total_functions": new_project.total_functions,
        "issues_found": len(audit_results["issues"]),
        "issues": audit_results["issues"]
    }


@app.get("/api/projects/{project_id}")
def get_project_report(
    project_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)          # Fix 1: API key guard
):
    """
    Retrieves a historical project audit report by its unique ID.
    
    Args:
        project_id (int): The primary key ID of the project in the database.
        db (Session): The SQLAlchemy database session dependency.
        _ (None): The API key verification dependency.
        
    Returns:
        dict: A dictionary containing the `project` metadata and a list of associated `issues`.
        
    Raises:
        HTTPException: If no project with the specified ID exists (HTTP 404).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    issues = db.query(AuditIssue).filter(AuditIssue.project_id == project_id).all()

    return {
        "project": project,
        "issues": issues
    }


@app.get("/api/graph")
def get_codebase_graph(
    directory_path: str = Query(..., description="Path to project code directory"),
    _: None = Depends(verify_api_key)          # Fix 1: API key guard
):
    """
    Generates a call-graph representation of the specified codebase.
    
    This endpoint parses the codebase to extract function definitions and invocations,
    returning a structured list of nodes and edges suitable for graph visualisation.
    
    Args:
        directory_path (str): The file system path to the target directory.
        _ (None): The API key verification dependency.
        
    Returns:
        dict: A dictionary containing the status and the generated graph data 
              (nodes and edges).
    """
    graph_data = generate_codebase_graph(directory_path)
    return {
        "status": "success",
        "graph": graph_data
    }
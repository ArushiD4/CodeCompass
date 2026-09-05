from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import engine, Base, get_db
from app.models import Project, AuditIssue
from app.audit_engine import audit_codebase
from app.graph_engine import generate_codebase_graph

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeCompass API", version="1.0.0", description="API for CodeCompass, a code auditing tool.")

@app.get("/")
def read_root():
    return {"message": "CodeCompass Engine is online"}

@app.post("/api/audit")
def run_audit(
    project_name: str = Query(..., description = "Name of the project" ),
    directory_path: str = Query(..., description = "Path to the codebase directory"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:

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
            project_id=new_project.id, # Uses parent ID generated above
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
def get_project_report(project_id: int, db: Session = Depends(get_db)):
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
    directory_path: str = Query(..., description="Path to project code directory")
):
    """
    Generates nodes and edges for call-graph visualization.
    """
    graph_data = generate_codebase_graph(directory_path)
    return {
        "status": "success",
        "graph": graph_data
    }
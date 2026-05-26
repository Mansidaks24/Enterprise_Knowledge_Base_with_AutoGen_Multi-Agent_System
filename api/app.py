from fastapi import FastAPI
from pydantic import BaseModel
from main import EnterpriseKnowledgeBase
from datetime import datetime
from monitoring.metrics_collector import MetricsCollector

app = FastAPI(
    title="Enterprise Knowledge Base API",
    version="1.0.0"
)

# Initialize system once
kb = EnterpriseKnowledgeBase()


# -----------------------------------
# Request Models
# -----------------------------------

class QueryRequest(BaseModel):

    query: str


# -----------------------------------
# Health Check
# -----------------------------------

@app.get("/")
def root():

    return {

        "status": "running",

        "system": "Enterprise KB",

        "timestamp": datetime.now().isoformat()
    }


# -----------------------------------
# Query Endpoint
# -----------------------------------

@app.post("/query")
def process_query(request: QueryRequest):

    response = kb.process_query(
        request.query
    )

    return response


# -----------------------------------
# System Report
# -----------------------------------

@app.get("/system-report")
def system_report():

    return {

        "report":
            kb.generate_system_report()
    }


# -----------------------------------
# Conversation History
# -----------------------------------

@app.get("/history")
def history():

    return {

        "history":
            kb.conversation_history
    }


# -----------------------------------
# Export Logs
# -----------------------------------

@app.post("/export-logs")
def export_logs():

    logs = kb.export_all_logs()

    return {

        "status": "success",

        "logs": logs
    }
    
@app.get("/logs")
def get_logs():

    try:

        with open(
            "logs/system.log",
            "r"
        ) as f:

            logs = f.readlines()

        return {

            "logs": logs[-50:]
        }

    except Exception as e:

        return {

            "error": str(e)
        }
        
@app.get("/metrics")
def get_metrics():

    metrics = MetricsCollector.generate_metrics(
        kb.conversation_history
    )

    return metrics

@app.get("/analytics")
def get_analytics():

    analytics = MetricsCollector.generate_analytics(
        kb.conversation_history
    )

    return analytics
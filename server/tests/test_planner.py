import pytest
from fastapi.testclient import TestClient
import os
from pathlib import Path

# Import the FastAPI app
from server.main import app

client = TestClient(app)


def load_sample_note():
    """Load the sample note fixture"""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_note.md"
    return fixture_path.read_text()


class TestPlannerAPI:
    """Test suite for the planner API endpoints"""
    
    def test_planday_with_valid_note(self):
        """Test POST /planner/planday with valid note"""
        sample_note = load_sample_note()
        
        response = client.post(
            "/planner/planday",
            json={"note": sample_note}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "scheduleMarkdown" in data
        assert "headline" in data
        
        # Validate schedule contains expected elements
        assert "Lunch" in data["scheduleMarkdown"]
        assert "Dinner" in data["scheduleMarkdown"]
        assert "| Time | Plan |" in data["scheduleMarkdown"]
        
        # Validate headline
        assert "Focus:" in data["headline"]
        assert "Finish draft presentation" in data["headline"]
    
    def test_planday_with_date(self):
        """Test POST /planner/planday with date parameter"""
        sample_note = load_sample_note()
        
        response = client.post(
            "/planner/planday",
            json={
                "note": sample_note,
                "date": "2025-06-28"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "scheduleMarkdown" in data
        assert "headline" in data
    
    def test_planday_missing_note(self):
        """Test POST /planner/planday with missing note"""
        response = client.post(
            "/planner/planday",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_planday_invalid_date(self):
        """Test POST /planner/planday with invalid date format"""
        sample_note = load_sample_note()
        
        response = client.post(
            "/planner/planday",
            json={
                "note": sample_note,
                "date": "invalid-date"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid date format" in data["detail"]
    
    def test_planday_empty_note(self):
        """Test POST /planner/planday with empty note"""
        response = client.post(
            "/planner/planday",
            json={"note": ""}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "scheduleMarkdown" in data
        assert "headline" in data
        assert data["headline"] == "Balanced day"
    
    def test_planday_priorities_parsing(self):
        """Test that priorities are parsed and scheduled correctly"""
        test_note = """
# Daily Note

## Top 3 Priorities
- [ ] Priority 1 Task
- [ ] Priority 2 Task  
- [ ] Priority 3 Task

## Tasks
- [ ] Regular task 1
- [ ] Regular task 2
        """
        
        response = client.post(
            "/planner/planday",
            json={"note": test_note}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "Priority: Priority 1 Task" in data["scheduleMarkdown"]
        assert "Priority: Priority 2 Task" in data["scheduleMarkdown"]
        assert "Priority: Priority 3 Task" in data["scheduleMarkdown"]
        assert "Priority 1 Task" in data["headline"]
    
    def test_planday_ignore_completed_tasks(self):
        """Test that completed tasks are ignored"""
        test_note = """
# Daily Note

## Tasks
- [ ] Incomplete task
- [x] Completed task
- [ ] Another incomplete task
        """
        
        response = client.post(
            "/planner/planday",
            json={"note": test_note}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "Incomplete task" in data["scheduleMarkdown"]
        assert "Another incomplete task" in data["scheduleMarkdown"]
        assert "Completed task" not in data["scheduleMarkdown"]
    
    def test_planner_health(self):
        """Test GET /planner/health endpoint"""
        response = client.get("/planner/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "OK"
        assert data["service"] == "planner"
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__])

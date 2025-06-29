from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import re
from datetime import datetime

planner_router = APIRouter(prefix="/planner", tags=["planner"])


class PlanDayRequest(BaseModel):
    note: str = Field(..., description="The daily note content")
    date: Optional[str] = Field(None, description="Optional date in YYYY-MM-DD format")


class PlanDayResponse(BaseModel):
    scheduleMarkdown: str = Field(..., description="Generated schedule as markdown table")
    headline: str = Field(..., description="Generated headline for the day")


def create_time_slots():
    """Creates the initial time slots from 06:00 to 23:00"""
    slots = []
    
    for hour in range(6, 23):
        start_time = f"{hour:02d}:00"
        end_time = f"{hour + 1:02d}:00"
        time_range = f"{start_time}–{end_time}"
        
        plan = ""
        
        # Insert fixed blocks
        if hour == 12:
            plan = "Lunch"
        elif hour == 18:
            plan = "Dinner"
        
        slots.append({
            "time": time_range,
            "plan": plan
        })
    
    return slots


def parse_note(note: str):
    """Parses the note to extract priorities and tasks"""
    lines = note.split('\n')
    priorities = []
    tasks = []
    
    in_priorities_section = False
    priorities_processed = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for Top 3 Priorities section header
        if ('top 3 priorities' in line.lower() or 
            (line.lower().startswith('#') and 'priorities' in line.lower())):
            in_priorities_section = True
            continue
        
        # Check if we've moved to a new section
        if in_priorities_section and line.startswith('#') and i > 0:
            in_priorities_section = False
            priorities_processed = True
        
        # Extract tasks/priorities using regex
        task_match = re.match(r'^- \[ \] (.+)', line)
        completed_task_match = re.match(r'^- \[x\] (.+)', line)
        
        if task_match:
            task_text = task_match.group(1).strip()
            
            if in_priorities_section and len(priorities) < 3:
                priorities.append(task_text)
            elif not in_priorities_section or priorities_processed:
                tasks.append(task_text)
        
        # Skip completed tasks
        if completed_task_match:
            continue
    
    return priorities, tasks


def generate_markdown_table(schedule):
    """Generates a markdown table from the schedule"""
    markdown = "| Time | Plan |\n"
    markdown += "|------|------|\n"
    
    for slot in schedule:
        plan = slot["plan"] or ""
        markdown += f"| {slot['time']} | {plan} |\n"
    
    return markdown


def generate_schedule_from_note(note: str, date: Optional[str] = None):
    """Main function to generate schedule from note"""
    # Create initial timeline from 06:00 to 23:00 (17 hours)
    time_slots = create_time_slots()
    
    # Parse the note to extract priorities and tasks
    priorities, tasks = parse_note(note)
    
    # Create a copy of time slots to populate
    schedule = time_slots.copy()
    
    # Track used slots
    current_slot_index = 0
    
    # Place Top 3 Priorities first (2-hour blocks each)
    for priority in priorities[:3]:
        if current_slot_index < len(schedule) - 1:
            # Skip lunch and dinner slots
            while (current_slot_index < len(schedule) and 
                   (schedule[current_slot_index]["time"] == "12:00–13:00" or 
                    schedule[current_slot_index]["time"] == "18:00–19:00")):
                current_slot_index += 1
            
            if current_slot_index < len(schedule) - 1:
                # Assign 2-hour block
                schedule[current_slot_index]["plan"] = f"Priority: {priority}"
                current_slot_index += 1
                
                if (current_slot_index < len(schedule) and 
                    schedule[current_slot_index]["time"] != "12:00–13:00" and 
                    schedule[current_slot_index]["time"] != "18:00–19:00"):
                    schedule[current_slot_index]["plan"] = f"Priority: {priority} (cont'd)"
                    current_slot_index += 1
    
    # Fill remaining tasks (1 hour each)
    for task in tasks:
        # Skip lunch and dinner slots
        while (current_slot_index < len(schedule) and 
               (schedule[current_slot_index]["time"] == "12:00–13:00" or 
                schedule[current_slot_index]["time"] == "18:00–19:00")):
            current_slot_index += 1
        
        if current_slot_index < len(schedule):
            schedule[current_slot_index]["plan"] = f"Task: {task}"
            current_slot_index += 1
        else:
            break  # No more slots available
    
    # Generate markdown table
    schedule_markdown = generate_markdown_table(schedule)
    
    # Generate headline
    headline = f"Focus: {priorities[0]}" if priorities else "Balanced day"
    
    return schedule_markdown, headline


@planner_router.post("/planday", response_model=PlanDayResponse)
async def plan_day(request: PlanDayRequest):
    """
    Generate a daily schedule from a note
    
    Accepts a daily note and returns a Markdown schedule + headline.
    
    - **note**: The content of the daily note (required)
    - **date**: Optional date in YYYY-MM-DD format
    
    Returns:
    - **scheduleMarkdown**: A two-column markdown table with Time and Plan
    - **headline**: A focus headline for the day
    """
    try:
        # Validate date format if provided
        if request.date:
            try:
                datetime.strptime(request.date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Date must be in YYYY-MM-DD format."
                )
        
        # Generate schedule
        schedule_markdown, headline = generate_schedule_from_note(request.note, request.date)
        
        return PlanDayResponse(
            scheduleMarkdown=schedule_markdown,
            headline=headline
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while generating schedule: {str(e)}"
        )


@planner_router.get("/health")
async def planner_health():
    """Health check endpoint for planner service"""
    return {"status": "OK", "service": "planner", "timestamp": datetime.now().isoformat()}

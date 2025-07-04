"""
Calendar Integration for VaultPilot with EvoAgentX

Integrates calendar functionality to enhance daily planning and scheduling
features within Obsidian vaults.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import subprocess
import platform

from .api_models import TaskPlanningRequest, TaskPlanningResponse, Task, TaskPlan


class CalendarIntegration:
    """
    Calendar integration service for VaultPilot, leveraging EvoAgentX's
    calendar API capabilities for enhanced scheduling and planning.
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.supported_platforms = ['Darwin']  # macOS
        
    async def get_calendar_events(self, date: str, duration_days: int = 1) -> List[Dict[str, Any]]:
        """
        Get calendar events for specified date range
        
        Args:
            date: Date in YYYY-MM-DD format
            duration_days: Number of days to fetch events for
            
        Returns:
            List of calendar events with time, title, and details
        """
        if self.platform not in self.supported_platforms:
            return self._get_mock_events(date, duration_days)
        
        try:
            events = await self._fetch_macos_calendar_events(date, duration_days)
            return events
        except Exception as e:
            print(f"Calendar fetch error: {e}")
            return self._get_mock_events(date, duration_days)
    
    async def create_schedule_with_calendar(self, request: TaskPlanningRequest, calendar_date: Optional[str] = None) -> TaskPlanningResponse:
        """
        Create enhanced task schedule that integrates with calendar events
        
        Args:
            request: Task planning request
            calendar_date: Specific date for calendar integration
            
        Returns:
            Enhanced task planning response with calendar integration
        """
        # Get calendar events for the specified date
        target_date = calendar_date or datetime.now().strftime('%Y-%m-%d')
        calendar_events = await self.get_calendar_events(target_date)
        
        # Generate base task plan
        base_tasks = await self._generate_base_tasks(request)
        
        # Integrate with calendar events
        integrated_schedule = await self._integrate_with_calendar(base_tasks, calendar_events, target_date)
        
        # Create enhanced task plan
        enhanced_plan = TaskPlan(
            title=f"Calendar-Integrated Plan: {request.goal[:50]}...",
            description=f"Integrated planning for {target_date} combining tasks with calendar events",
            tasks=integrated_schedule['tasks'],
            estimated_duration=integrated_schedule['total_duration']
        )
        
        return TaskPlanningResponse(
            plan=enhanced_plan,
            timeline=integrated_schedule['timeline'],
            milestones=integrated_schedule['milestones']
        )
    
    async def _fetch_macos_calendar_events(self, date: str, duration_days: int) -> List[Dict[str, Any]]:
        """Fetch calendar events from macOS Calendar using AppleScript"""
        
        # Calculate end date
        start_date = datetime.strptime(date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=duration_days)
        
        # AppleScript to fetch calendar events
        applescript = f'''
        tell application "Calendar"
            set startDate to date "{start_date.strftime('%m/%d/%Y')}"
            set endDate to date "{end_date.strftime('%m/%d/%Y')}"
            set eventList to {{}}
            
            repeat with cal in calendars
                set calEvents to (every event of cal whose start date >= startDate and start date <= endDate)
                repeat with evt in calEvents
                    set eventRecord to {{summary:(summary of evt), startDate:(start date of evt), endDate:(end date of evt), description:(description of evt)}}
                    set end of eventList to eventRecord
                end repeat
            end repeat
            
            return eventList
        end tell
        '''
        
        try:
            # Execute AppleScript
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return self._parse_applescript_events(result.stdout)
            else:
                print(f"AppleScript error: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Calendar integration error: {e}")
            return []
    
    def _parse_applescript_events(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parse AppleScript output into structured events"""
        events = []
        
        # TODO: Implement proper AppleScript output parsing
        # This is a simplified version - actual implementation would need
        # to handle AppleScript's output format properly
        
        # For now, return empty list and rely on mock data
        return events
    
    def _get_mock_events(self, date: str, duration_days: int) -> List[Dict[str, Any]]:
        """Generate mock calendar events for testing/fallback"""
        
        base_date = datetime.strptime(date, '%Y-%m-%d')
        
        mock_events = [
            {
                "title": "Team Standup",
                "start_time": (base_date + timedelta(hours=9)).isoformat(),
                "end_time": (base_date + timedelta(hours=9, minutes=30)).isoformat(),
                "description": "Daily team standup meeting",
                "type": "meeting"
            },
            {
                "title": "Project Review",
                "start_time": (base_date + timedelta(hours=14)).isoformat(),
                "end_time": (base_date + timedelta(hours=15)).isoformat(),
                "description": "Weekly project review session",
                "type": "meeting"
            },
            {
                "title": "Focus Block",
                "start_time": (base_date + timedelta(hours=10)).isoformat(),
                "end_time": (base_date + timedelta(hours=12)).isoformat(),
                "description": "Deep work focus time",
                "type": "focus"
            }
        ]
        
        return mock_events
    
    async def _generate_base_tasks(self, request: TaskPlanningRequest) -> List[Task]:
        """Generate base tasks from planning request"""
        
        # Extract tasks from goal and context
        goal_words = request.goal.lower().split()
        
        base_tasks = []
        
        if "research" in goal_words:
            base_tasks.append(Task(
                title="Research Planning",
                description="Conduct initial research and gather resources",
                priority="high",
                estimated_time="2 hours"
            ))
        
        if "write" in goal_words or "document" in goal_words:
            base_tasks.append(Task(
                title="Writing Session",
                description="Focused writing and documentation work",
                priority="high",
                estimated_time="3 hours"
            ))
        
        if "review" in goal_words:
            base_tasks.append(Task(
                title="Review and Analysis",
                description="Review materials and provide analysis",
                priority="medium",
                estimated_time="1 hour"
            ))
        
        # Add generic tasks if no specific ones identified
        if not base_tasks:
            base_tasks.extend([
                Task(
                    title="Task Planning",
                    description="Break down the goal into actionable steps",
                    priority="high",
                    estimated_time="30 minutes"
                ),
                Task(
                    title="Execution",
                    description="Execute the main work",
                    priority="high",
                    estimated_time="2 hours"
                ),
                Task(
                    title="Review",
                    description="Review and finalize work",
                    priority="medium",
                    estimated_time="30 minutes"
                )
            ])
        
        return base_tasks
    
    async def _integrate_with_calendar(self, tasks: List[Task], events: List[Dict], target_date: str) -> Dict[str, Any]:
        """Integrate tasks with calendar events to create realistic schedule"""
        
        # Parse target date
        base_date = datetime.strptime(target_date, '%Y-%m-%d')
        
        # Create time slots accounting for calendar events
        busy_times = []
        for event in events:
            try:
                start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
                busy_times.append((start, end))
            except:
                continue
        
        # Find available time slots
        available_slots = self._find_available_slots(base_date, busy_times)
        
        # Schedule tasks in available slots
        scheduled_tasks = self._schedule_tasks_in_slots(tasks, available_slots)
        
        # Calculate timeline and milestones
        timeline = self._calculate_integrated_timeline(scheduled_tasks, events)
        milestones = self._generate_calendar_milestones(scheduled_tasks, target_date)
        
        return {
            'tasks': scheduled_tasks,
            'total_duration': timeline,
            'timeline': timeline,
            'milestones': milestones,
            'calendar_integration': True
        }
    
    def _find_available_slots(self, base_date: datetime, busy_times: List[tuple]) -> List[tuple]:
        """Find available time slots between calendar events"""
        
        # Define working hours (9 AM to 6 PM)
        work_start = base_date.replace(hour=9, minute=0, second=0, microsecond=0)
        work_end = base_date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Sort busy times
        busy_times.sort(key=lambda x: x[0])
        
        available_slots = []
        current_time = work_start
        
        for busy_start, busy_end in busy_times:
            # Add slot before this busy time if there's space
            if current_time < busy_start and (busy_start - current_time).total_seconds() >= 1800:  # 30 min minimum
                available_slots.append((current_time, busy_start))
            
            # Move current time to after this busy period
            current_time = max(current_time, busy_end)
        
        # Add final slot if there's time left
        if current_time < work_end:
            available_slots.append((current_time, work_end))
        
        return available_slots
    
    def _schedule_tasks_in_slots(self, tasks: List[Task], available_slots: List[tuple]) -> List[Task]:
        """Schedule tasks within available time slots"""
        
        scheduled_tasks = []
        slot_index = 0
        
        for task in tasks:
            if slot_index >= len(available_slots):
                # No more slots available, mark task for later
                task.status = "pending"
                task.dependencies.append("waiting_for_available_slot")
                scheduled_tasks.append(task)
                continue
            
            # Estimate task duration in minutes
            duration_str = task.estimated_time.lower()
            if "hour" in duration_str:
                duration_minutes = int(duration_str.split()[0]) * 60
            elif "minute" in duration_str:
                duration_minutes = int(duration_str.split()[0])
            else:
                duration_minutes = 60  # Default 1 hour
            
            # Find slot that can accommodate this task
            while slot_index < len(available_slots):
                slot_start, slot_end = available_slots[slot_index]
                slot_duration = (slot_end - slot_start).total_seconds() / 60
                
                if slot_duration >= duration_minutes:
                    # Schedule task in this slot
                    task.description += f" (Scheduled: {slot_start.strftime('%H:%M')}-{(slot_start + timedelta(minutes=duration_minutes)).strftime('%H:%M')})"
                    scheduled_tasks.append(task)
                    
                    # Update slot start time for next task
                    new_start = slot_start + timedelta(minutes=duration_minutes + 15)  # 15 min buffer
                    if new_start < slot_end:
                        available_slots[slot_index] = (new_start, slot_end)
                    else:
                        slot_index += 1
                    break
                else:
                    slot_index += 1
            
            if slot_index >= len(available_slots):
                # No suitable slot found
                task.status = "pending"
                task.dependencies.append("no_available_slot")
                scheduled_tasks.append(task)
        
        return scheduled_tasks
    
    def _calculate_integrated_timeline(self, tasks: List[Task], events: List[Dict]) -> str:
        """Calculate realistic timeline considering calendar constraints"""
        
        total_task_time = 0
        for task in tasks:
            duration_str = task.estimated_time.lower()
            if "hour" in duration_str:
                total_task_time += int(duration_str.split()[0]) * 60
            elif "minute" in duration_str:
                total_task_time += int(duration_str.split()[0])
        
        # Account for calendar event time
        meeting_time = len(events) * 30  # Assume 30 min average per event
        
        total_minutes = total_task_time + meeting_time
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        elif total_minutes < 480:  # Less than 8 hours
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
        else:
            days = total_minutes // 480  # 8 hours per day
            remaining_hours = (total_minutes % 480) // 60
            return f"{days} days, {remaining_hours} hours"
    
    def _generate_calendar_milestones(self, tasks: List[Task], target_date: str) -> List[Dict]:
        """Generate milestones that account for calendar integration"""
        
        milestones = []
        
        # Morning milestone
        morning_tasks = [t for t in tasks if "09:" in t.description or "10:" in t.description or "11:" in t.description]
        if morning_tasks:
            milestones.append({
                "title": "Morning Session Complete",
                "description": f"Complete {len(morning_tasks)} morning tasks",
                "target_date": target_date,
                "tasks": [t.id for t in morning_tasks]
            })
        
        # Afternoon milestone  
        afternoon_tasks = [t for t in tasks if "13:" in t.description or "14:" in t.description or "15:" in t.description]
        if afternoon_tasks:
            milestones.append({
                "title": "Afternoon Progress",
                "description": f"Complete {len(afternoon_tasks)} afternoon tasks",
                "target_date": target_date,
                "tasks": [t.id for t in afternoon_tasks]
            })
        
        return milestones
    
    async def export_schedule_to_calendar(self, task_plan: TaskPlan, target_date: str) -> bool:
        """
        Export generated schedule back to calendar as events
        
        Args:
            task_plan: Generated task plan to export
            target_date: Date to schedule tasks
            
        Returns:
            True if successful, False otherwise
        """
        if self.platform not in self.supported_platforms:
            print("Calendar export not supported on this platform")
            return False
        
        try:
            success_count = 0
            for task in task_plan.tasks:
                # Extract scheduled time from task description
                time_match = self._extract_scheduled_time(task.description)
                if time_match:
                    event_created = await self._create_calendar_event(task, target_date, time_match)
                    if event_created:
                        success_count += 1
            
            print(f"Created {success_count}/{len(task_plan.tasks)} calendar events")
            return success_count > 0
            
        except Exception as e:
            print(f"Calendar export error: {e}")
            return False
    
    def _extract_scheduled_time(self, description: str) -> Optional[Dict[str, str]]:
        """Extract scheduled time from task description"""
        # Look for pattern like "(Scheduled: 09:00-10:30)"
        import re
        pattern = r'Scheduled: (\d{2}:\d{2})-(\d{2}:\d{2})'
        match = re.search(pattern, description)
        
        if match:
            return {
                'start_time': match.group(1),
                'end_time': match.group(2)
            }
        return None
    
    async def _create_calendar_event(self, task: Task, date: str, time_info: Dict[str, str]) -> bool:
        """Create calendar event for a scheduled task"""
        
        # AppleScript to create calendar event
        applescript = f'''
        tell application "Calendar"
            set targetDate to date "{date}"
            set startTime to time "{time_info['start_time']}" of targetDate
            set endTime to time "{time_info['end_time']}" of targetDate
            
            tell calendar "VaultPilot Tasks"
                make new event with properties {{summary:"{task.title}", start date:startTime, end date:endTime, description:"{task.description}"}}
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
            
        except Exception as e:
            print(f"Event creation error: {e}")
            return False

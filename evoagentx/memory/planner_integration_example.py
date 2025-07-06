"""
Example integration of persistent memory with EvoAgentX planner agent

This shows how to add memory capabilities to your existing planner/reflection agent
for improved UX through conversation history and context awareness.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from evoagentx.memory import MemoryCapableMixin, MemoryConfig


class PlannerAgent(MemoryCapableMixin):
    """Enhanced planner agent with persistent memory for better user experience"""
    
    def __init__(self, name: str = "daily_planner"):
        self.name = name
        self.agent_id = f"planner_{name}"
        
        # Configure memory for conversational planning
        memory_config = MemoryConfig(
            max_working_memory_tokens=3000,  # Larger memory for planning context
            max_working_memory_messages=30,  # Keep more messages for continuity
            summarize_threshold=8,           # Summarize less frequently
            enable_vector_store=True,        # Enable semantic search (if dependencies available)
            vector_similarity_threshold=0.6, # More permissive similarity for planning
            auto_cleanup_days=60,            # Keep planning history longer
            db_path=f"planner_memory_{name}.sqlite"  # Separate DB per planner
        )
        
        super().__init__(memory_config=memory_config)
        
        # Planner-specific state
        self.current_goals = []
        self.completed_tasks = []
        
    def plan_day(self, user_request: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Plan a day based on user request with memory-enhanced context"""
        
        # Remember the planning request with rich metadata
        self.remember(
            content=user_request,
            role="user",
            metadata={
                "action": "plan_request",
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "session_type": "planning"
            },
            importance=0.8  # Planning requests are important
        )
        
        # Get relevant context from memory - look for similar planning sessions
        memory_context = self.recall(
            query=f"planning {user_request}",
            include_summaries=True
        )
        
        # Search for specific past planning patterns
        past_plans = self.search_memories("daily plan schedule", limit=5)
        past_reflections = self.search_memories("reflection review", limit=3)
        
        # Generate plan using memory context
        plan = self._generate_enhanced_plan(
            user_request=user_request,
            memory_context=memory_context,
            past_plans=past_plans,
            past_reflections=past_reflections,
            additional_context=context
        )
        
        # Remember the generated plan with high importance
        self.remember(
            content=json.dumps(plan, indent=2),
            role="assistant",
            metadata={
                "action": "plan_response",
                "plan_type": plan.get("type", "daily"),
                "task_count": len(plan.get("tasks", [])),
                "estimated_duration": plan.get("estimated_duration"),
                "timestamp": datetime.now().isoformat()
            },
            importance=0.9  # Generated plans are very important
        )
        
        return plan
    
    def _generate_enhanced_plan(
        self, 
        user_request: str,
        memory_context: List[str],
        past_plans: List[Any],
        past_reflections: List[Any],
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate plan using memory-enhanced context"""
        
        # Analyze patterns from past plans
        common_patterns = self._analyze_planning_patterns(past_plans)
        lessons_learned = self._extract_lessons_from_reflections(past_reflections)
        
        # Create base plan structure
        plan = {
            "type": "daily_plan",
            "user_request": user_request,
            "generated_at": datetime.now().isoformat(),
            "tasks": [],
            "estimated_duration": "8 hours",
            "priority_focus": self._determine_priority_focus(user_request, memory_context),
            "memory_insights": {
                "context_items_used": len(memory_context),
                "past_plans_referenced": len(past_plans),
                "lessons_applied": lessons_learned,
                "common_patterns": common_patterns
            }
        }
        
        # Generate tasks based on request and memory context
        tasks = self._generate_tasks_with_memory(user_request, memory_context, common_patterns)
        plan["tasks"] = tasks
        
        # Add memory-informed recommendations
        plan["recommendations"] = self._generate_memory_based_recommendations(
            past_plans, past_reflections, user_request
        )
        
        return plan
    
    def _generate_tasks_with_memory(self, request: str, context: List[str], patterns: Dict) -> List[Dict]:
        """Generate tasks informed by memory context"""
        # This would integrate with your actual task generation logic
        # Here's a simple example
        
        base_tasks = [
            {"task": "Review planning request", "duration": "15 min", "priority": "high"},
            {"task": "Check calendar for conflicts", "duration": "10 min", "priority": "high"},
        ]
        
        # Add context-informed tasks
        if "presentation" in request.lower():
            base_tasks.append({
                "task": "Prepare presentation materials", 
                "duration": "2 hours", 
                "priority": "high",
                "memory_note": "Based on past presentation planning patterns"
            })
        
        if "meeting" in request.lower() and patterns.get("meeting_prep_time"):
            base_tasks.append({
                "task": "Meeting preparation",
                "duration": patterns["meeting_prep_time"],
                "priority": "medium",
                "memory_note": f"Typical prep time from past plans: {patterns['meeting_prep_time']}"
            })
        
        return base_tasks
    
    def _analyze_planning_patterns(self, past_plans: List[Any]) -> Dict[str, Any]:
        """Analyze patterns from past planning sessions"""
        patterns = {
            "common_task_types": [],
            "typical_durations": {},
            "frequent_priorities": [],
            "meeting_prep_time": "30 min"  # Default
        }
        
        # This would analyze actual past plans
        # For now, return simple patterns
        return patterns
    
    def _extract_lessons_from_reflections(self, reflections: List[Any]) -> List[str]:
        """Extract actionable lessons from past reflections"""
        lessons = []
        
        # Analyze reflection content for patterns
        for reflection in reflections:
            content = getattr(reflection, 'content', str(reflection))
            if "time management" in content.lower():
                lessons.append("Focus on better time management")
            if "overcommit" in content.lower():
                lessons.append("Avoid overcommitting to tasks")
            if "break" in content.lower():
                lessons.append("Include adequate breaks in schedule")
        
        return lessons
    
    def _determine_priority_focus(self, request: str, context: List[str]) -> str:
        """Determine the main priority focus based on request and context"""
        if "urgent" in request.lower() or "deadline" in request.lower():
            return "urgent_tasks"
        elif "creative" in request.lower() or "brainstorm" in request.lower():
            return "creative_work"
        elif "meeting" in request.lower():
            return "collaboration"
        else:
            return "balanced_productivity"
    
    def _generate_memory_based_recommendations(
        self, 
        past_plans: List[Any], 
        reflections: List[Any], 
        request: str
    ) -> List[str]:
        """Generate recommendations based on memory analysis"""
        recommendations = []
        
        if past_plans:
            recommendations.append("Based on past planning sessions, consider scheduling buffer time between tasks")
        
        if reflections:
            recommendations.append("Previous reflections suggest focusing on time management")
        
        if "presentation" in request.lower():
            recommendations.append("Allocate extra time for presentation preparation based on past patterns")
        
        return recommendations
    
    def add_reflection(self, reflection_text: str, reflection_type: str = "daily") -> str:
        """Add a reflection to memory with high importance for future planning"""
        
        reflection_data = {
            "reflection": reflection_text,
            "type": reflection_type,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "insights": self._extract_insights_from_reflection(reflection_text)
        }
        
        # Store reflection with very high importance
        self.remember(
            content=json.dumps(reflection_data, indent=2),
            role="reflection",
            metadata={
                "action": "reflection",
                "reflection_type": reflection_type,
                "insights_count": len(reflection_data["insights"]),
                "timestamp": datetime.now().isoformat()
            },
            importance=0.95  # Reflections are extremely important for learning
        )
        
        return f"Reflection recorded. Extracted {len(reflection_data['insights'])} insights for future planning."
    
    def _extract_insights_from_reflection(self, reflection: str) -> List[str]:
        """Extract actionable insights from reflection text"""
        insights = []
        
        # Simple keyword-based insight extraction
        # In practice, this could use NLP or LLM analysis
        text_lower = reflection.lower()
        
        if "too much time" in text_lower or "overestimated" in text_lower:
            insights.append("Tendency to overestimate task duration")
        
        if "not enough time" in text_lower or "underestimated" in text_lower:
            insights.append("Tendency to underestimate task complexity")
        
        if "distracted" in text_lower or "interruption" in text_lower:
            insights.append("Need better focus management strategies")
        
        if "productive" in text_lower and "morning" in text_lower:
            insights.append("Higher productivity in morning hours")
        
        return insights
    
    def get_planning_insights(self) -> Dict[str, Any]:
        """Get insights from memory for planning improvement"""
        
        # Search for different types of content
        all_plans = self.search_memories("plan daily schedule", limit=10)
        all_reflections = self.search_memories("reflection", limit=10)
        
        insights = {
            "total_planning_sessions": len(all_plans),
            "total_reflections": len(all_reflections),
            "memory_stats": self.memory_stats(),
            "recent_patterns": self._analyze_recent_patterns(),
            "improvement_suggestions": self._generate_improvement_suggestions()
        }
        
        return insights
    
    def _analyze_recent_patterns(self) -> Dict[str, Any]:
        """Analyze recent planning patterns from memory"""
        # Get recent context
        recent_context = self.recall(include_summaries=True)
        
        patterns = {
            "frequent_request_types": [],
            "common_challenges": [],
            "successful_strategies": []
        }
        
        # Analyze recent context for patterns
        for item in recent_context[:10]:  # Last 10 items
            if "presentation" in item.lower():
                patterns["frequent_request_types"].append("presentation_planning")
            if "meeting" in item.lower():
                patterns["frequent_request_types"].append("meeting_scheduling")
            if "time management" in item.lower():
                patterns["common_challenges"].append("time_management")
        
        return patterns
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate suggestions for planning improvement based on memory"""
        suggestions = []
        
        # Base suggestions
        suggestions.extend([
            "Consider using time-blocking for better schedule management",
            "Regular reflection helps improve future planning accuracy",
            "Review past similar plans before creating new ones"
        ])
        
        # Memory-based suggestions
        stats = self.memory_stats()
        if stats["working_memory_items"] > 20:
            suggestions.append("Rich conversation history available - leverage past insights")
        
        return suggestions


# Example usage function
def demo_enhanced_planner():
    """Demonstrate the enhanced planner with memory"""
    print("=== Enhanced Planner with Persistent Memory Demo ===")
    
    # Create planner with memory
    planner = PlannerAgent("demo_planner")
    
    # Day 1: Initial planning
    print("\n--- Day 1: Initial Planning ---")
    plan1 = planner.plan_day(
        "I need to prepare for a big presentation tomorrow and review 3 project proposals",
        context="High-stakes client presentation, deadline is firm"
    )
    print(f"Generated plan with {len(plan1['tasks'])} tasks")
    print(f"Memory insights: {plan1['memory_insights']}")
    
    # Add reflection for Day 1
    reflection1 = planner.add_reflection(
        "Presentation prep took longer than expected. Need to allocate more time for research phase. "
        "Good focus in morning hours, but got distracted after lunch.",
        reflection_type="daily"
    )
    print(f"Reflection: {reflection1}")
    
    # Day 2: Planning with memory context
    print("\n--- Day 2: Planning with Memory Context ---")
    plan2 = planner.plan_day(
        "Another presentation today, plus need to follow up on yesterday's client meeting",
        context="Building on yesterday's presentation feedback"
    )
    print(f"Generated plan with {len(plan2['tasks'])} tasks")
    print(f"Recommendations: {plan2['recommendations']}")
    print(f"Memory insights: {plan2['memory_insights']}")
    
    # Day 3: Complex planning
    print("\n--- Day 3: Complex Planning ---")
    plan3 = planner.plan_day(
        "Urgent: Fix critical bug, prepare for team standup, review quarterly goals, "
        "and brainstorm ideas for new feature",
        context="Mixed urgent and strategic work"
    )
    print(f"Priority focus: {plan3['priority_focus']}")
    print(f"Recommendations: {plan3['recommendations']}")
    
    # Get overall insights
    print("\n--- Planning Insights ---")
    insights = planner.get_planning_insights()
    print(f"Total planning sessions: {insights['total_planning_sessions']}")
    print(f"Total reflections: {insights['total_reflections']}")
    print(f"Memory stats: {insights['memory_stats']}")
    print(f"Improvement suggestions: {insights['improvement_suggestions']}")


if __name__ == "__main__":
    demo_enhanced_planner()

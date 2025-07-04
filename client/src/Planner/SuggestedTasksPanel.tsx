import React, { useState, useEffect } from 'react';

interface SuggestedTask {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  estimatedTime: string;
  category: string;
}

const SuggestedTasksPanel: React.FC = () => {
  const [tasks, setTasks] = useState<SuggestedTask[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set());

  // Mock AI-generated tasks for demonstration
  const mockTasks: SuggestedTask[] = [
    {
      id: '1',
      title: 'Review code changes',
      description: 'Review pending pull requests from team members',
      priority: 'high',
      estimatedTime: '30 min',
      category: 'Development'
    },
    {
      id: '2',
      title: 'Update documentation',
      description: 'Update API documentation for new endpoints',
      priority: 'medium',
      estimatedTime: '45 min',
      category: 'Documentation'
    },
    {
      id: '3',
      title: 'Team standup prep',
      description: 'Prepare updates for daily standup meeting',
      priority: 'medium',
      estimatedTime: '10 min',
      category: 'Meeting'
    }
  ];

  const generateSuggestions = async () => {
    setIsLoading(true);
    // Simulate AI processing
    setTimeout(() => {
      setTasks(mockTasks);
      setIsLoading(false);
    }, 1500);
  };

  const toggleTaskSelection = (taskId: string) => {
    const newSelected = new Set(selectedTasks);
    if (newSelected.has(taskId)) {
      newSelected.delete(taskId);
    } else {
      newSelected.add(taskId);
    }
    setSelectedTasks(newSelected);
  };

  const addSelectedTasks = () => {
    const selected = tasks.filter(task => selectedTasks.has(task.id));
    console.log('Adding tasks to plan:', selected);
    // Here you would integrate with the main planning system
    alert(`Added ${selected.length} task(s) to your plan!`);
    setSelectedTasks(new Set());
  };

  const refineSuggestions = () => {
    console.log('Refining suggestions...');
    generateSuggestions();
  };

  const getPriorityColor = (priority: SuggestedTask['priority']) => {
    switch (priority) {
      case 'high': return 'text-red-600 dark:text-red-400';
      case 'medium': return 'text-yellow-600 dark:text-yellow-400';
      case 'low': return 'text-green-600 dark:text-green-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  useEffect(() => {
    // Auto-generate initial suggestions
    generateSuggestions();
  }, []);

  return (
    <aside className="w-64 max-w-xs bg-white dark:bg-gray-800 p-4 border-l border-gray-200 dark:border-gray-700 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🤖 AI Suggestions</h3>
        <button
          onClick={generateSuggestions}
          disabled={isLoading}
          className="text-sm px-2 py-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors disabled:opacity-50"
        >
          {isLoading ? '⟳' : '↻'}
        </button>
      </div>

      <div className="flex-1 flex flex-col gap-2 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin text-2xl">🤖</div>
            <span className="ml-2 text-sm text-gray-500">Analyzing...</span>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">🎯</div>
            <span className="text-sm text-gray-500">No suggestions yet.</span>
            <button
              onClick={generateSuggestions}
              className="block mt-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Generate suggestions
            </button>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                selectedTasks.has(task.id)
                  ? 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
              onClick={() => toggleTaskSelection(task.id)}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {task.title}
                </h4>
                <input
                  type="checkbox"
                  checked={selectedTasks.has(task.id)}
                  onChange={() => toggleTaskSelection(task.id)}
                  className="ml-2 text-blue-600"
                />
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                {task.description}
              </p>
              <div className="flex items-center justify-between text-xs">
                <span className={`font-medium ${getPriorityColor(task.priority)}`}>
                  {task.priority.toUpperCase()}
                </span>
                <span className="text-gray-500">{task.estimatedTime}</span>
              </div>
              <div className="mt-1">
                <span className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                  {task.category}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {tasks.length > 0 && (
        <div className="mt-4 flex gap-2">
          <button
            onClick={addSelectedTasks}
            disabled={selectedTasks.size === 0}
            className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add to Plan ({selectedTasks.size})
          </button>
          <button
            onClick={refineSuggestions}
            className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded text-sm hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            ✨ Refine
          </button>
        </div>
      )}
    </aside>
  );
};

export default SuggestedTasksPanel;

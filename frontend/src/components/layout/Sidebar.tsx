"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Task {
  id: number;
  topic: string;
}

interface SidebarProps {
  onTaskSelect: (taskId: number) => void;
  refreshTrigger: boolean; // New prop to trigger a refresh
}

export default function Sidebar({ onTaskSelect, refreshTrigger }: SidebarProps) {
  const [tasks, setTasks] = useState<Task[]>([]);

  const fetchTasks = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/tasks");
      if (!response.ok) throw new Error("Failed to fetch tasks");
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error(error);
    }
  };

  // This useEffect will now run once on mount, AND every time refreshTrigger changes
  useEffect(() => {
    fetchTasks();
  }, [refreshTrigger]);

  const handleDeleteTask = async (taskId: number) => {
    event?.stopPropagation();
    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error("Failed to delete task");
      setTasks(currentTasks => currentTasks.filter(task => task.id !== taskId));
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  return (
    <aside className="w-64 flex-shrink-0 bg-gray-900 p-4 flex flex-col">
      <div className="font-bold text-lg mb-4">The Knowledge Vessel</div>
      <nav>
        <ul>
          <li className="mb-2">
            <Link href="/" className="text-gray-300 hover:text-white font-semibold">
              Dashboard
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/analytics" className="text-gray-300 hover:text-white font-semibold">
              Analytics
            </Link>
          </li>
        </ul>
      </nav>
      
      <div className="mt-8 pt-4 border-t border-gray-700 overflow-y-auto">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Task History</h3>
        <ul>
          {tasks.map((task) => (
            <li key={task.id} className="mb-2 flex justify-between items-center group rounded-md hover:bg-gray-800">
              <button
                onClick={() => onTaskSelect(task.id)}
                className="text-left flex-1 text-gray-400 group-hover:text-white truncate p-1"
              >
                {task.topic}
              </button>
              <button
                onClick={() => handleDeleteTask(task.id)}
                className="ml-2 text-gray-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1"
                title="Delete task"
              >
                &#x2715;
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
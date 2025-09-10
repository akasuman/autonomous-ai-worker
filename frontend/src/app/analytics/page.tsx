"use client";

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Stats {
  total_tasks: number;
  total_documents: number;
  top_topics: { topic: string; count: number }[];
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/api/analytics/stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  const handleTaskSelect = (_taskId: number) => {
    // This page doesn't need to handle task selection,
    // but the Sidebar component requires the prop.
  };

  return (
    <div className="flex h-screen bg-black text-white">
      {/* --- ADD THE MISSING PROP HERE --- */}
      <Sidebar onTaskSelect={handleTaskSelect} refreshTrigger={false} />
      
      <main className="flex-1 flex flex-col overflow-y-auto">
        <Header />
        <div className="p-4">
          <h1 className="text-2xl font-bold mb-4">Analytics Dashboard</h1>
          {isLoading ? (
            <p>Loading stats...</p>
          ) : stats ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-gray-400">Total Tasks Created</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-4xl font-bold">{stats.total_tasks}</p>
                </CardContent>
              </Card>
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-gray-400">Total Documents Stored</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-4xl font-bold">{stats.total_documents}</p>
                </CardContent>
              </Card>
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-gray-400">Top 5 Searched Topics</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {stats.top_topics.map((item) => (
                      <li key={item.topic} className="flex justify-between">
                        <span>{item.topic}</span>
                        <span className="font-bold">{item.count}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          ) : (
            <p>Could not load analytics data.</p>
          )}
        </div>
      </main>
    </div>
  );
}
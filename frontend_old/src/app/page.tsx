"use client";

import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import ResultCard from "@/components/ResultCard";

interface Article {
  title: string;
  description: string;
  url: string;
  urlToImage?: string;
  summary?: string;
  topics?: string;
}

interface HistoryResult {
  id: number;
  score: number;
  payload: {
    title: string;
    url: string;
  }
}

export default function Home() {
  const [topic, setTopic] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [historyQuery, setHistoryQuery] = useState("");
  const [historyResults, setHistoryResults] = useState<HistoryResult[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(false);

  const handleSearch = async () => {
    if (!topic) return;
    setIsLoading(true);
    setSearched(true);
    setArticles([]);
    setHistoryResults([]);
    try {
      const response = await fetch(`http://localhost:8000/api/search/${topic}`);
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      if (data.articles && data.articles.length > 0) {
        setArticles(data.articles);
      } else {
        setArticles([]);
      }
    } catch (error) {
      console.error("Failed to fetch:", error);
    } finally {
      setIsLoading(false);
      setRefreshTrigger(prev => !prev);
    }
  };

  const handleTaskSelect = async (taskId: number) => {
    setIsLoading(true);
    setSearched(true);
    setArticles([]);
    setHistoryResults([]);
    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`);
      if (!response.ok) throw new Error("Failed to fetch task details");
      const data = await response.json();
       if (data.articles && data.articles.length > 0) {
        setArticles(data.articles);
      } else {
        setArticles([]);
      }
    } catch (error) {
      console.error("Failed to fetch task details:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleHistorySearch = async () => {
    if (!historyQuery) return;
    setIsHistoryLoading(true);
    setHistoryResults([]);
    try {
      const response = await fetch(`http://localhost:8000/api/search/history?q=${historyQuery}`);
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setHistoryResults(data);
    } catch (error) {
      console.error("Failed to fetch history:", error);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar onTaskSelect={handleTaskSelect} refreshTrigger={refreshTrigger} />
      <main className="flex-1 flex flex-col overflow-y-auto">
        <Header />
        <div className="p-4 space-y-8">
          <div>
            <h2 className="text-lg font-semibold mb-2">Search for New Articles</h2>
            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input
                type="text"
                placeholder="Enter a topic to research..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="bg-gray-900 border-gray-700"
              />
              <Button onClick={handleSearch} disabled={isLoading}>
                {isLoading ? "Searching..." : "Search"}
              </Button>
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Search Your Knowledge Base</h2>
            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input
                type="text"
                placeholder="Search past results by meaning..."
                value={historyQuery}
                onChange={(e) => setHistoryQuery(e.target.value)}
                className="bg-gray-900 border-gray-700"
              />
              <Button onClick={handleHistorySearch} disabled={isHistoryLoading}>
                {isHistoryLoading ? "Searching..." : "Search History"}
              </Button>
            </div>
            <div className="mt-4">
              {isHistoryLoading && <p>Searching history...</p>}
              {historyResults.length > 0 && (
                <div className="p-4 bg-gray-900 rounded-md">
                   <h3 className="font-semibold mb-2">Similar Past Results:</h3>
                   <ul className="list-disc pl-5 space-y-2">
                      {historyResults.map(result => (
                        <li key={result.id}>
                          <a href={result.payload.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                            {result.payload.title}
                          </a>
                          <span className="text-xs text-gray-500 ml-2">(Similarity: {result.score.toFixed(2)})</span>
                        </li>
                      ))}
                   </ul>
                </div>
              )}
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8">
            <h2 className="text-lg font-semibold mb-2">New Search Results</h2>
            {isLoading && <p>Loading results...</p>}
            {!isLoading && searched && articles.length === 0 && (
              <p>No results found for "{topic}". Please try another topic.</p>
            )}
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {articles.map((article) => (
                <ResultCard
                  key={article.url}
                  title={article.title}
                  description={article.description}
                  url={article.url}
                  imageUrl={article.urlToImage}
                  summary={article.summary}
                  topics={article.topics}
                />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
"use client";

import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import ResultCard from "@/components/ResultCard";
import { StockDataCard } from "@/components/StockDataCard";
import { StockHistoryChart } from "@/components/StockHistoryChart";

// --- INTERFACES ---
interface StockData {
  Symbol: string;
  Name: string;
  Industry: string;
  Description: string;
  MarketCapitalization: string;
  PERatio: string;
  DividendYield: string;
  '52WeekHigh': string;
  '52WeekLow': string;
  AnalystTargetPrice: string;
}

interface Article {
  title: string;
  description: string;
  url: string;
  urlToImage?: string;
  summary?: string;
  topics?: string;
}

// --- MODIFIED: Renamed HistoryResult to Document and updated its structure ---
// This now correctly matches the data sent by your backend's database search.
interface Document {
  id: number;
  content: {
    title: string;
    url: string;
  };
  summary: string | null;
}

export default function Home() {
  const [topic, setTopic] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  
  const [historyQuery, setHistoryQuery] = useState("");
  // --- MODIFIED: Use the new Document interface for state ---
  const [historyResults, setHistoryResults] = useState<Document[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  const [stockSymbol, setStockSymbol] = useState("");
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [isStockLoading, setIsStockLoading] = useState(false);
  const [stockError, setStockError] = useState<string | null>(null);
  const [stockHistory, setStockHistory] = useState([]);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleSearch = async () => {
    if (!topic) return;
    setIsLoading(true);
    setSearched(true);
    setArticles([]);
    setStockData(null);
    setStockHistory([]);
    try {
      const response = await fetch(`${apiUrl}/api/search/${topic}`);
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      // Assuming the task object contains an 'articles' array
      setArticles(data.articles || []);
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
    setStockData(null);
    setStockHistory([]);
    try {
      const response = await fetch(`${apiUrl}/api/tasks/${taskId}`);
      if (!response.ok) throw new Error("Failed to fetch task details");
      const data = await response.json();
      setArticles(data.articles || []);
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
    setStockData(null);
    setStockHistory([]);
    try {
      const response = await fetch(`${apiUrl}/api/search/history?q=${historyQuery}`);
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setHistoryResults(data);
    } catch (error) {
      console.error("Failed to fetch history:", error);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  const handleStockSearch = async () => {
    if (!stockSymbol) return;
    setIsStockLoading(true);
    setStockError(null);
    setStockData(null);
    setArticles([]);
    setHistoryResults([]);
    setStockHistory([]);

    const symbol = stockSymbol.toUpperCase();
    try {
      const [overviewRes, historyRes] = await Promise.all([
        fetch(`${apiUrl}/api/stock/${symbol}`),
        fetch(`${apiUrl}/api/stock/${symbol}/history`)
      ]);
      if (!overviewRes.ok) {
        const errData = await overviewRes.json();
        throw new Error(errData.detail || "Stock symbol not found.");
      }
      const overviewData = await overviewRes.json();
      setStockData(overviewData);
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setStockHistory(historyData);
      }
    } catch (err) {
      if (err instanceof Error) {
        setStockError(err.message);
      } else {
        setStockError("An unknown error occurred.");
      }
    } finally {
      setIsStockLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar onTaskSelect={handleTaskSelect} refreshTrigger={refreshTrigger} />
      <main className="flex-1 flex flex-col overflow-y-auto">
        <Header />
        <div className="p-4 space-y-8">
          {/* Search for New Articles Section */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Search for New Articles</h2>
            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input type="text" placeholder="Enter a topic..." value={topic} onChange={(e) => setTopic(e.target.value)} className="bg-gray-900 border-gray-700" />
              <Button onClick={handleSearch} disabled={isLoading}>{isLoading ? "Searching..." : "Search News"}</Button>
            </div>
          </div>
          
          {/* Search Your Knowledge Base Section */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Search Your Knowledge Base</h2>
            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input type="text" placeholder="Search past results by keyword..." value={historyQuery} onChange={(e) => setHistoryQuery(e.target.value)} className="bg-gray-900 border-gray-700" />
              <Button onClick={handleHistorySearch} disabled={isHistoryLoading}>{isHistoryLoading ? "Searching..." : "Search History"}</Button>
            </div>
            <div className="mt-4">
              {isHistoryLoading && <p>Searching knowledge base...</p>}
              {historyResults.length > 0 && (
                <div className="p-4 bg-gray-900 rounded-md">
                  <h3 className="font-semibold mb-2">Past Results:</h3>
                  <ul className="list-disc pl-5 space-y-2">
  {historyResults
    .filter(result => result.content && result.content.url)
    .map(result => (
      <li key={result.id}>
        <a href={result.content.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
          {result.content.title}
        </a>
      </li>
  ))}
</ul>
                </div>
              )}
            </div>
          </div>

          {/* Search for Stock Data Section */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Search for Stock Data</h2>
            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input type="text" placeholder="Enter a stock symbol..." value={stockSymbol} onChange={(e) => setStockSymbol(e.target.value)} className="bg-gray-900 border-gray-700" />
              <Button onClick={handleStockSearch} disabled={isStockLoading}>{isStockLoading ? "Fetching..." : "Search Stock"}</Button>
            </div>
          </div>
          
          {/* Main Results Area */}
          <div className="border-t border-gray-800 pt-8">
            <h2 className="text-lg font-semibold mb-2">Results</h2>
            {isLoading && <p>Loading articles...</p>}
            {isStockLoading && <p>Loading stock data...</p>}
            {stockError && <p className="text-red-500">{stockError}</p>}
            
            {/* News Article Results */}
            {!isLoading && searched && articles.length === 0 && topic && <p>{`No results found for "${topic}".`}</p>}
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {articles.map((article) => (
                <ResultCard key={article.url} {...article} imageUrl={article.urlToImage} />
              ))}
            </div>
            
            {/* Stock Data Results */}
            {stockData && <StockDataCard data={stockData} />}
            {stockHistory.length > 0 && <StockHistoryChart data={stockHistory} />}
          </div>
        </div>
      </main>
    </div>
  );
}
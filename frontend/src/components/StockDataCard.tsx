import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

// --- CHANGE 1 of 2: Define a specific type for the stock data object ---
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

// A helper component for displaying each data point
const DataPoint = ({ label, value }: { label: string; value: string | number }) => (
  <div className="flex justify-between border-b border-gray-800 py-2">
    <span className="text-gray-400">{label}</span>
    <span className="font-medium text-white">{value}</span>
  </div>
);

// --- CHANGE 2 of 2: Use the new StockData interface for the 'data' prop ---
export const StockDataCard = ({ data }: { data: StockData }) => {
  if (!data || !data.Symbol) {
    return null;
  }

  return (
    <Card className="bg-gray-800 border-gray-700 mt-4">
      <CardHeader>
        <CardTitle>{data.Name} ({data.Symbol})</CardTitle>
        <CardDescription>{data.Industry}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-gray-300 mb-4 text-sm">{data.Description}</p>
        <div className="space-y-2">
            <DataPoint label="Market Capitalization" value={`$${(parseInt(data.MarketCapitalization) / 1_000_000_000).toFixed(2)}B`} />
            <DataPoint label="P/E Ratio (TTM)" value={data.PERatio} />
            <DataPoint label="Dividend Yield" value={`${(parseFloat(data.DividendYield) * 100).toFixed(2)}%`} />
            <DataPoint label="52 Week High" value={`$${data['52WeekHigh']}`} />
            <DataPoint label="52 Week Low" value={`$${data['52WeekLow']}`} />
            <DataPoint label="Analyst Target Price" value={`$${data.AnalystTargetPrice}`} />
        </div>
      </CardContent>
    </Card>
  );
};
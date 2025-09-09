"use client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ChartData {
  Date: string;
  Close: number;
}

export const StockHistoryChart = ({ data }: { data: ChartData[] }) => {
  if (!data || data.length === 0) {
    return <div className="text-center text-gray-500 mt-4">No historical data available to display chart.</div>;
  }

  return (
    <div className="mt-6 bg-gray-800 p-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-4 text-white">Stock Performance (Past Year)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
          <XAxis dataKey="Date" stroke="#A0AEC0" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#A0AEC0" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
          <Tooltip contentStyle={{ backgroundColor: '#1A202C', border: '1px solid #4A5568' }} />
          <Line type="monotone" dataKey="Close" stroke="#4299E1" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
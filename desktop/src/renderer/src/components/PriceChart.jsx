import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  
  const data = payload[0].payload;
  console.log(data);

  return (
    <div className="bg-mist-900 border border-mist-700 rounded-md p-3 shadow-lg text-sm">
      <p className="font-semibold mb-1">{data.Date}</p>
      <p className="text-mist-300">Close ${data.Close.toFixed(2)}</p>
      <p className="text-mist-300">Volume {data.Volume.toLocaleString('en-US')}</p>
    </div>
  );
}

function PriceChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="Date"
          tick={{ fontSize: 12 }}
          minTickGap={20}
        />
        <YAxis
          domain={["auto", "auto"]}
          tickFormatter={(v) => `$${v.toFixed(0)}`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey="Close"
          stroke="#00786f"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default PriceChart;
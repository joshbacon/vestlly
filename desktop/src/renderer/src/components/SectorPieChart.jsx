import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { buildSectorBreakdown } from '../utils/sectorBreakdown';

const COLORS = [
  '#4a90d9', '#e07a5f', '#81b29a', '#f2cc8f', '#3d5a80',
  '#e56b6f', '#6d597a', '#b56576', '#355070', '#eaac8b',
];

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;

  const sector = payload[0].payload;

  return (
    <div className="bg-mist-900 border border-mist-700 rounded-md p-3 shadow-lg text-sm">
      <p className="font-semibold mb-1">{sector.name} ({sector.value} stocks)</p>
      <ul className="space-y-0.5">
        {sector.industries.map(({ industry, count }) => (
          <li key={industry} className="text-mist-300">
            {industry}: {count}
          </li>
        ))}
      </ul>
    </div>
  );
}

function SectorPieChart({ marketData }) {
  const data = buildSectorBreakdown(marketData);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={120}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export default SectorPieChart;
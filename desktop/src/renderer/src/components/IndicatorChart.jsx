import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";

function CustomTooltip({ active, payload, tag, column, tagT, columnT, columnE, tagF, columnF, columnS }) {
  if (!active || !payload?.length) return null;
  
  const data = payload[0].payload;

  return (
    <div className="bg-mist-900 border border-mist-700 rounded-md p-3 shadow-lg text-sm">
      <p className="font-semibold mb-1">{data['date']}</p>
      <p className="text-[#00786f]">{tag} {data[column] != null ? data[column].toFixed(2) : ''}</p>
      { columnT!= null || columnE != null ?
        <p className="text-[#0078af]">{tagT} {`${data[columnT] != null ? data[columnT].toFixed(2) : ''} ${columnT!= null && columnE != null ? '-' : ''} ${data[columnE] != null ? data[columnE].toFixed(2) : ''}`}</p> :
        <></>
      }
      { columnF!= null || columnS != null ?
        <p className="text-[#6c7800]">{tagF} {`${data[columnF] != null ? data[columnF].toFixed(2) : ''} ${columnT!= null && columnE != null ? '-' : ''} ${data[columnS] != null ? data[columnS].toFixed(2) : ''}`}</p> :
        <></>
      }
    </div>
  );
}

function IndicatorChart({ data, tag, column, tagT, columnT, columnE, tagF, columnF, columnS }) {
  console.log(data);
  console.log(column);
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          minTickGap={1}
        />
        <YAxis
          domain={["auto", "auto"]}
          tickFormatter={(v) => `${v.toFixed(0)}`}
        />
        <Tooltip
          content={<CustomTooltip />}
          tag={tag}
          column={column}
          tagT={tagT}
          columnT={columnT}
          columnE={columnE}
          tagF={tagF}
          columnF={columnF}
          columnS={columnS}
        />
        <Line
          type="monotone"
          dataKey={column}
          stroke="#00786f"
          strokeWidth={2}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey={columnT}
          stroke="#0078af"
          strokeWidth={2}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey={columnE}
          stroke="#0078af"
          strokeWidth={2}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey={columnF}
          stroke="#6c7800"
          strokeWidth={2}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey={columnS}
          stroke="#6c7800"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default IndicatorChart;
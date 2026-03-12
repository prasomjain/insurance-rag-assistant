import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ConfidencePoint } from "../../api";

interface ConfidenceChartProps {
  points: ConfidencePoint[];
}

export function ConfidenceChart({ points }: ConfidenceChartProps) {
  const data = points.map((point, index) => ({
    idx: index + 1,
    confidence: Number((point.confidence * 100).toFixed(2)),
  }));

  return (
    <section className="glass-card rounded-2xl p-5 h-80">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Query Confidence Scores
      </h3>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="idx" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={[0, 100]} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="confidence"
            stroke="#38bdf8"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}

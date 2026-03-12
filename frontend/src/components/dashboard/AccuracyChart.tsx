import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MetricsSummary } from "../../api";

interface AccuracyChartProps {
  metrics: MetricsSummary;
}

export function AccuracyChart({ metrics }: AccuracyChartProps) {
  const data = [
    { metric: "Accuracy", value: Number((metrics.accuracy * 100).toFixed(2)) },
    {
      metric: "Faithfulness",
      value: Number((metrics.faithfulness * 100).toFixed(2)),
    },
  ];

  return (
    <section className="glass-card rounded-2xl p-5 h-80">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Accuracy vs Faithfulness
      </h3>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="metric" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Bar
            dataKey="value"
            name="Score (%)"
            fill="#06b6d4"
            radius={[6, 6, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}

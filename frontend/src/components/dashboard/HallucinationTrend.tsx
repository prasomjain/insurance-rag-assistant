import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HallucinationPoint } from "../../api";

interface HallucinationTrendProps {
  points: HallucinationPoint[];
}

export function HallucinationTrend({ points }: HallucinationTrendProps) {
  const data = points.map((point, index) => ({
    idx: index + 1,
    hallucination: Number((point.hallucination_rate * 100).toFixed(2)),
  }));

  return (
    <section className="glass-card rounded-2xl p-5 h-80">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Hallucination Trend
      </h3>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="idx" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={[0, 100]} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="hallucination"
            stroke="#f97316"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { LatencyBucket } from "../../api";

interface LatencyChartProps {
  buckets: LatencyBucket[];
}

export function LatencyChart({ buckets }: LatencyChartProps) {
  return (
    <section className="glass-card rounded-2xl p-5 h-80">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Latency Distribution
      </h3>
      <ResponsiveContainer width="100%" height="90%">
        <AreaChart data={buckets}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="bucket" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" allowDecimals={false} />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#22c55e"
            fill="#22c55e33"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </section>
  );
}

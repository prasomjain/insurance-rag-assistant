import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ModelComparisonItem } from "../../api";

interface ModelComparisonProps {
  models: ModelComparisonItem[];
}

export function ModelComparison({ models }: ModelComparisonProps) {
  const data = models.map((model) => ({
    model: model.model_version,
    accuracy: Number((model.accuracy * 100).toFixed(1)),
    faithfulness: Number((model.faithfulness * 100).toFixed(1)),
    confidence: Number((model.confidence * 100).toFixed(1)),
  }));

  return (
    <section className="glass-card rounded-2xl p-5 h-80">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Naive vs Improved Model Comparison
      </h3>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="model" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={[0, 100]} />
          <Tooltip />
          <Bar dataKey="accuracy" fill="#06b6d4" radius={[5, 5, 0, 0]} />
          <Bar dataKey="faithfulness" fill="#14b8a6" radius={[5, 5, 0, 0]} />
          <Bar dataKey="confidence" fill="#3b82f6" radius={[5, 5, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}

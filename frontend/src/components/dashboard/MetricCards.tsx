import {
  BarChart3,
  ShieldCheck,
  AlertTriangle,
  Clock,
  Sparkles,
} from "lucide-react";
import type { MetricsSummary } from "../../api";

interface MetricCardsProps {
  metrics: MetricsSummary;
}

const cards = [
  {
    key: "accuracy",
    label: "Accuracy",
    icon: BarChart3,
    format: (v: number) => `${(v * 100).toFixed(1)}%`,
  },
  {
    key: "faithfulness",
    label: "Faithfulness",
    icon: ShieldCheck,
    format: (v: number) => `${(v * 100).toFixed(1)}%`,
  },
  {
    key: "hallucination_rate",
    label: "Hallucination",
    icon: AlertTriangle,
    format: (v: number) => `${(v * 100).toFixed(1)}%`,
  },
  {
    key: "avg_latency",
    label: "Avg Latency",
    icon: Clock,
    format: (v: number) => `${v.toFixed(2)}s`,
  },
  {
    key: "confidence",
    label: "Confidence",
    icon: Sparkles,
    format: (v: number) => `${(v * 100).toFixed(1)}%`,
  },
] as const;

export function MetricCards({ metrics }: MetricCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const value = metrics[card.key as keyof MetricsSummary] as number;
        return (
          <article
            key={card.key}
            className="glass-card rounded-2xl p-4 border border-white/10"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-wider text-slate-400">
                {card.label}
              </p>
              <Icon className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-2xl font-semibold mt-2 text-slate-100">
              {card.format(value ?? 0)}
            </p>
          </article>
        );
      })}
    </div>
  );
}

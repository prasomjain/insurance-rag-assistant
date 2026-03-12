import { useEffect, useState } from "react";
import {
  fetchConfidenceScores,
  fetchHallucinationTrend,
  fetchLatencyDistribution,
  fetchMetrics,
  fetchModelComparison,
  type ConfidencePoint,
  type HallucinationPoint,
  type LatencyBucket,
  type MetricsSummary,
  type ModelComparisonItem,
} from "../../api";
import { AccuracyChart } from "./AccuracyChart";
import { ConfidenceChart } from "./ConfidenceChart";
import { HallucinationTrend } from "./HallucinationTrend";
import { LatencyChart } from "./LatencyChart";
import { MetricCards } from "./MetricCards";
import { ModelComparison } from "./ModelComparison";

const emptyMetrics: MetricsSummary = {
  accuracy: 0,
  faithfulness: 0,
  hallucination_rate: 0,
  context_relevance: 0,
  avg_latency: 0,
  confidence: 0,
  total_queries: 0,
};

export function EvaluationDashboard() {
  const [metrics, setMetrics] = useState<MetricsSummary>(emptyMetrics);
  const [trend, setTrend] = useState<HallucinationPoint[]>([]);
  const [comparison, setComparison] = useState<ModelComparisonItem[]>([]);
  const [latencyBuckets, setLatencyBuckets] = useState<LatencyBucket[]>([]);
  const [confidencePoints, setConfidencePoints] = useState<ConfidencePoint[]>(
    [],
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [
          metricsResp,
          trendResp,
          compareResp,
          latencyResp,
          confidenceResp,
        ] = await Promise.all([
          fetchMetrics(),
          fetchHallucinationTrend(),
          fetchModelComparison(),
          fetchLatencyDistribution(),
          fetchConfidenceScores(),
        ]);

        setMetrics(metricsResp);
        setTrend(trendResp.points);
        setComparison(compareResp.models);
        setLatencyBuckets(latencyResp.buckets);
        setConfidencePoints(confidenceResp.points);
      } catch (err) {
        setError(
          "Unable to load evaluation analytics. Verify backend is running.",
        );
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          <div className="glass-card rounded-2xl p-6">
            Loading evaluation dashboard...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          <div className="glass-card rounded-2xl p-6 text-red-300">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="glass rounded-2xl p-5 border border-white/10">
          <h1 className="text-2xl font-bold text-cyan-300">
            RAG Evaluation Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Accuracy, faithfulness, hallucination, relevance, latency, and
            confidence analytics.
          </p>
        </header>

        <MetricCards metrics={metrics} />

        <AccuracyChart metrics={metrics} />
        <HallucinationTrend points={trend} />
        <ModelComparison models={comparison} />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <LatencyChart buckets={latencyBuckets} />
          <ConfidenceChart points={confidencePoints} />
        </div>
      </div>
    </div>
  );
}

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface ChatApiResponse {
    answer: string;
    context: string[];
    pipeline: 'naive' | 'improved';
    model_version: string;
    confidence: number;
    latency_seconds: number;
    metrics: Record<string, number>;
    timestamp: string;
}

export interface MetricsSummary {
    accuracy: number;
    faithfulness: number;
    hallucination_rate: number;
    context_relevance: number;
    avg_latency: number;
    confidence: number;
    total_queries: number;
}

export interface HallucinationPoint {
    timestamp: string;
    hallucination_rate: number;
}

export interface ModelComparisonItem {
    model_version: string;
    accuracy: number;
    faithfulness: number;
    hallucination_rate: number;
    context_relevance: number;
    confidence: number;
    avg_latency: number;
    total_queries: number;
}

export interface LatencyBucket {
    bucket: string;
    count: number;
}

export interface ConfidencePoint {
    timestamp: string;
    confidence: number;
}

export const chatWithBot = async (
    message: string,
    pipeline: 'naive' | 'improved' = 'improved',
): Promise<ChatApiResponse> => {
    const response = await axios.post<ChatApiResponse>(`${API_URL}/chat`, { message, pipeline });
    return response.data;
};

export const fetchMetrics = async (): Promise<MetricsSummary> => {
    const response = await axios.get<MetricsSummary>(`${API_URL}/evaluation/metrics`);
    return response.data;
};

export const fetchLogs = async (limit = 100, offset = 0): Promise<{ logs: unknown[]; limit: number; offset: number }> => {
    const response = await axios.get(`${API_URL}/evaluation/logs`, { params: { limit, offset } });
    return response.data;
};

export const fetchHallucinationTrend = async (): Promise<{ points: HallucinationPoint[] }> => {
    const response = await axios.get<{ points: HallucinationPoint[] }>(`${API_URL}/evaluation/hallucination-trend`);
    return response.data;
};

export const fetchModelComparison = async (): Promise<{ models: ModelComparisonItem[] }> => {
    const response = await axios.get<{ models: ModelComparisonItem[] }>(`${API_URL}/evaluation/model-comparison`);
    return response.data;
};

export const fetchLatencyDistribution = async (): Promise<{ buckets: LatencyBucket[] }> => {
    const response = await axios.get<{ buckets: LatencyBucket[] }>(`${API_URL}/evaluation/latency-distribution`);
    return response.data;
};

export const fetchConfidenceScores = async (): Promise<{ points: ConfidencePoint[] }> => {
    const response = await axios.get<{ points: ConfidencePoint[] }>(`${API_URL}/evaluation/confidence-scores`);
    return response.data;
};

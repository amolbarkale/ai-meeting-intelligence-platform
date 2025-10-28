"use client"

import { useEffect, useState } from "react"
import { ArrowLeft, Loader2 } from "lucide-react"
import Link from "next/link"
import OverviewCards from "@/components/analytics/overview-cards"
import SentimentChart from "@/components/analytics/sentiment-chart"
import TopicsChart from "@/components/analytics/topics-chart"
import SentimentTimeline from "@/components/analytics/sentiment-timeline"
import ProcessingStats from "@/components/analytics/processing-stats"
import KnowledgeGraph from "@/components/analytics/knowledge-graph"

export default function AnalyticsPage() {
  const [overview, setOverview] = useState(null)
  const [sentiment, setSentiment] = useState(null)
  const [topics, setTopics] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [processing, setProcessing] = useState(null)
  const [graph, setGraph] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [overviewRes, sentimentRes, topicsRes, timelineRes, processingRes, graphRes] = await Promise.all([
          fetch("http://localhost:8000/analytics/overview"),
          fetch("http://localhost:8000/analytics/sentiment-distribution"),
          fetch("http://localhost:8000/analytics/top-topics?limit=8"),
          fetch("http://localhost:8000/analytics/sentiment-timeline?days=30"),
          fetch("http://localhost:8000/analytics/processing-stats"),
          fetch("http://localhost:8000/analytics/knowledge-graph"),
        ])

        if (overviewRes.ok) setOverview(await overviewRes.json())
        if (sentimentRes.ok) setSentiment(await sentimentRes.json())
        if (topicsRes.ok) setTopics(await topicsRes.json())
        if (timelineRes.ok) setTimeline(await timelineRes.json())
        if (processingRes.ok) setProcessing(await processingRes.json())
        if (graphRes.ok) setGraph(await graphRes.json())
      } catch (err) {
        console.error("Failed to fetch analytics:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <Link href="/" className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Meetings
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Analytics Dashboard</h1>
          <p className="text-lg text-slate-600">Insights from your meeting intelligence platform</p>
        </div>

        {/* Overview Cards */}
        {overview && <OverviewCards data={overview} />}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {sentiment && <SentimentChart data={sentiment} />}
          {processing && <ProcessingStats data={processing} />}
        </div>

        {/* Timeline */}
        {timeline && <SentimentTimeline data={timeline.timeline} />}

        {/* Topics */}
        {topics && <TopicsChart data={topics.topics} />}

        {/* Knowledge Graph */}
        {graph && <KnowledgeGraph data={graph} />}
      </div>
    </main>
  )
}

"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface ProcessingStatsProps {
  data: {
    transcribed: number
    summarized: number
    sentiment_analyzed: number
    topics_extracted: number
    total_meetings: number
    transcription_rate: number
    analysis_rate: number
  }
}

export default function ProcessingStats({ data }: ProcessingStatsProps) {
  const stats = [
    { label: "Transcribed", value: data.transcribed, rate: data.transcription_rate },
    { label: "Summarized", value: data.summarized, rate: data.analysis_rate },
    {
      label: "Sentiment Analyzed",
      value: data.sentiment_analyzed,
      rate: Math.round((data.sentiment_analyzed / data.total_meetings) * 100),
    },
    {
      label: "Topics Extracted",
      value: data.topics_extracted,
      rate: Math.round((data.topics_extracted / data.total_meetings) * 100),
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Processing Status</CardTitle>
        <CardDescription>Analysis completion rates</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {stats.map((stat, idx) => (
            <div key={idx}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">{stat.label}</span>
                <span className="text-sm font-bold text-slate-900">
                  {stat.value} ({stat.rate}%)
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-blue-500 transition-all" style={{ width: `${stat.rate}%` }} />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

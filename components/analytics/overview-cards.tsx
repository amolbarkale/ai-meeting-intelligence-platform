"use client"

import { Card, CardContent } from "@/components/ui/card"
import { BarChart3, CheckCircle2, Clock, AlertCircle, TrendingUp } from "lucide-react"

interface OverviewCardsProps {
  data: {
    total_meetings: number
    completed_meetings: number
    processing_meetings: number
    error_meetings: number
    completion_rate: number
    average_sentiment_score: number
  }
}

export default function OverviewCards({ data }: OverviewCardsProps) {
  const cards = [
    {
      icon: BarChart3,
      label: "Total Meetings",
      value: data.total_meetings,
      color: "bg-blue-50 text-blue-600",
    },
    {
      icon: CheckCircle2,
      label: "Completed",
      value: data.completed_meetings,
      color: "bg-green-50 text-green-600",
    },
    {
      icon: Clock,
      label: "Processing",
      value: data.processing_meetings,
      color: "bg-yellow-50 text-yellow-600",
    },
    {
      icon: AlertCircle,
      label: "Errors",
      value: data.error_meetings,
      color: "bg-red-50 text-red-600",
    },
    {
      icon: TrendingUp,
      label: "Completion Rate",
      value: `${data.completion_rate}%`,
      color: "bg-purple-50 text-purple-600",
    },
    {
      icon: TrendingUp,
      label: "Avg Sentiment",
      value: `${data.average_sentiment_score}/100`,
      color: "bg-indigo-50 text-indigo-600",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <Card key={idx}>
            <CardContent className="p-6">
              <div className={`w-12 h-12 rounded-lg ${card.color} flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6" />
              </div>
              <p className="text-sm text-slate-600 mb-1">{card.label}</p>
              <p className="text-2xl font-bold text-slate-900">{card.value}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

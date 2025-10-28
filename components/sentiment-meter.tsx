"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface SentimentMeterProps {
  overall: number
  positive: number
  neutral: number
  negative: number
}

export default function SentimentMeter({ overall, positive, neutral, negative }: SentimentMeterProps) {
  const getSentimentColor = (score: number) => {
    if (score >= 0.6) return "bg-green-500"
    if (score >= 0.4) return "bg-amber-500"
    return "bg-red-500"
  }

  const getSentimentLabel = (score: number) => {
    if (score >= 0.6) return "Positive"
    if (score >= 0.4) return "Neutral"
    return "Negative"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Overall Sentiment</CardTitle>
        <CardDescription>Meeting tone analysis</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-4xl font-bold text-slate-900">{(overall * 100).toFixed(0)}%</p>
            <p className="text-sm text-slate-600 mt-1">{getSentimentLabel(overall)}</p>
          </div>
          <div className={`w-24 h-24 rounded-full ${getSentimentColor(overall)} opacity-20`} />
        </div>

        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-600">Positive</span>
              <span className="font-medium text-slate-900">{(positive * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: `${positive * 100}%` }} />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-600">Neutral</span>
              <span className="font-medium text-slate-900">{(neutral * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${neutral * 100}%` }} />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-600">Negative</span>
              <span className="font-medium text-slate-900">{(negative * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: `${negative * 100}%` }} />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

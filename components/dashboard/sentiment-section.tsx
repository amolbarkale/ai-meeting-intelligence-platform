"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, Smile, Meh, Frown } from "lucide-react"

interface SentimentSectionProps {
  meeting: {
    sentiment?: {
      overall_sentiment: string
      sentiment_score: number
      explanation: string
    }
    status: string
  }
}

export default function SentimentSection({ meeting }: SentimentSectionProps) {
  if (!meeting.sentiment) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <AlertCircle className="w-5 h-5" />
            <p>Sentiment analysis not yet available. Processing in progress...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const sentiment = meeting.sentiment
  const score = sentiment.sentiment_score || 0
  const sentimentType = sentiment.overall_sentiment.toLowerCase()

  const getSentimentIcon = () => {
    if (sentimentType === "positive") return <Smile className="w-12 h-12 text-green-600" />
    if (sentimentType === "negative") return <Frown className="w-12 h-12 text-red-600" />
    return <Meh className="w-12 h-12 text-yellow-600" />
  }

  const getSentimentColor = () => {
    if (sentimentType === "positive") return "bg-green-50 border-green-200"
    if (sentimentType === "negative") return "bg-red-50 border-red-200"
    return "bg-yellow-50 border-yellow-200"
  }

  const getSentimentTextColor = () => {
    if (sentimentType === "positive") return "text-green-900"
    if (sentimentType === "negative") return "text-red-900"
    return "text-yellow-900"
  }

  return (
    <div className="space-y-6">
      {/* Overall Sentiment */}
      <Card className={`border-2 ${getSentimentColor()}`}>
        <CardContent className="py-12">
          <div className="flex flex-col items-center gap-4">
            {getSentimentIcon()}
            <div className="text-center">
              <p className={`text-2xl font-bold ${getSentimentTextColor()}`}>
                {sentimentType.charAt(0).toUpperCase() + sentimentType.slice(1)}
              </p>
              <p className="text-sm text-slate-600 mt-1">Overall Meeting Sentiment</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sentiment Score */}
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Score</CardTitle>
          <CardDescription>0 = Very Negative, 100 = Very Positive</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Score</span>
              <span className="text-2xl font-bold text-slate-900">{score}</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full transition-all ${
                  score > 60 ? "bg-green-500" : score > 40 ? "bg-yellow-500" : "bg-red-500"
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Explanation */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-700 leading-relaxed">{sentiment.explanation}</p>
        </CardContent>
      </Card>
    </div>
  )
}

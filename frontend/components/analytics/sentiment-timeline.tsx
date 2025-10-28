"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface SentimentTimelineProps {
  data: Array<{
    date: string
    sentiment_score: number
    meeting_count: number
  }>
}

export default function SentimentTimeline({ data }: SentimentTimelineProps) {
  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle>Sentiment Trend</CardTitle>
        <CardDescription>Average sentiment score over the last 30 days</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="sentiment_score" stroke="#10b981" name="Sentiment Score" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

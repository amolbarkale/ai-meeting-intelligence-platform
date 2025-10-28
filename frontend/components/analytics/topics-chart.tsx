"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface TopicsChartProps {
  data: Array<{
    name: string
    frequency: number
    avg_relevance: number
  }>
}

export default function TopicsChart({ data }: TopicsChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Discussion Topics</CardTitle>
        <CardDescription>Most frequently discussed topics across meetings</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="frequency" fill="#3b82f6" name="Frequency" />
            <Bar dataKey="avg_relevance" fill="#8b5cf6" name="Avg Relevance" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

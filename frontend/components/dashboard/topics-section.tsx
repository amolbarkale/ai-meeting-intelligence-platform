"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, Tag } from "lucide-react"

interface TopicsSectionProps {
  meeting: {
    topics?: Array<{
      topic_name: string
      relevance_score: number
      mentions: number
    }>
    status: string
  }
}

export default function TopicsSection({ meeting }: TopicsSectionProps) {
  if (!meeting.topics || meeting.topics.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <AlertCircle className="w-5 h-5" />
            <p>Topics not yet available. Processing in progress...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const sortedTopics = [...meeting.topics].sort((a, b) => b.relevance_score - a.relevance_score)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Discussion Topics</CardTitle>
        <CardDescription>{meeting.topics.length} topics identified</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedTopics.map((topic, idx) => (
            <div key={idx} className="border border-slate-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Tag className="w-4 h-4 text-slate-400" />
                  <h3 className="font-medium text-slate-900">{topic.topic_name}</h3>
                </div>
                <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded">
                  {topic.mentions} mention{topic.mentions !== 1 ? "s" : ""}
                </span>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Relevance</span>
                  <span className="font-medium text-slate-900">{topic.relevance_score}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div className="h-full bg-blue-500 transition-all" style={{ width: `${topic.relevance_score}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

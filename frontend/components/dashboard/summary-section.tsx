"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle2, AlertCircle } from "lucide-react"

interface SummarySectionProps {
  meeting: {
    summary?: {
      summary: string
      key_points: string[]
      action_items: string[]
    }
    status: string
  }
}

export default function SummarySection({ meeting }: SummarySectionProps) {
  if (!meeting.summary) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <AlertCircle className="w-5 h-5" />
            <p>Summary not yet available. Processing in progress...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Meeting Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-700 leading-relaxed">{meeting.summary.summary}</p>
        </CardContent>
      </Card>

      {/* Key Points */}
      <Card>
        <CardHeader>
          <CardTitle>Key Points</CardTitle>
          <CardDescription>{meeting.summary.key_points.length} points identified</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {meeting.summary.key_points.map((point, idx) => (
              <li key={idx} className="flex gap-3">
                <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span className="text-slate-700">{point}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Action Items */}
      <Card>
        <CardHeader>
          <CardTitle>Action Items</CardTitle>
          <CardDescription>{meeting.summary.action_items.length} items to follow up</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {meeting.summary.action_items.map((item, idx) => (
              <li key={idx} className="flex gap-3">
                <div className="w-5 h-5 rounded border-2 border-slate-300 flex-shrink-0 mt-0.5" />
                <span className="text-slate-700">{item}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

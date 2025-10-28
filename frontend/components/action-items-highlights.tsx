"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle2, AlertCircle, Quote, Clock } from "lucide-react"

interface ActionItem {
  id: string
  type: "action" | "decision" | "highlight"
  content: string
  timestamp: string
  speaker?: string
}

interface ActionItemsHighlightsProps {
  items: ActionItem[]
}

export default function ActionItemsHighlights({ items }: ActionItemsHighlightsProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case "action":
        return <CheckCircle2 className="w-5 h-5 text-blue-600" />
      case "decision":
        return <AlertCircle className="w-5 h-5 text-purple-600" />
      case "highlight":
        return <Quote className="w-5 h-5 text-amber-600" />
      default:
        return <Clock className="w-5 h-5 text-slate-600" />
    }
  }

  const getTypeLabel = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Action Items & Highlights</CardTitle>
        <CardDescription>{items.length} items extracted</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex gap-4 p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition"
            >
              <div className="flex-shrink-0 mt-1">{getIcon(item.type)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <span className="text-xs font-semibold text-slate-600 uppercase">{getTypeLabel(item.type)}</span>
                  <span className="text-xs text-slate-500 flex-shrink-0">{item.timestamp}</span>
                </div>
                <p className="text-slate-700 text-sm">{item.content}</p>
                {item.speaker && <p className="text-xs text-slate-500 mt-2">— {item.speaker}</p>}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

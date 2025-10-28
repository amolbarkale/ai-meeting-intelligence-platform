"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Users } from "lucide-react"

interface Speaker {
  name: string
  talkTime: number
  sentiment: "positive" | "neutral" | "negative"
  wordCount: number
}

interface SpeakerStatsPanelProps {
  speakers: Speaker[]
}

export default function SpeakerStatsPanel({ speakers }: SpeakerStatsPanelProps) {
  const sentimentColors = {
    positive: "bg-green-50 text-green-700",
    neutral: "bg-slate-50 text-slate-700",
    negative: "bg-red-50 text-red-700",
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="w-5 h-5" />
          Speaker Statistics
        </CardTitle>
        <CardDescription>{speakers.length} speakers identified</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {speakers.map((speaker) => (
            <div key={speaker.name} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-slate-900">{speaker.name}</p>
                <p className="text-sm text-slate-600">{speaker.wordCount} words</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="font-semibold text-slate-900">{speaker.talkTime}%</p>
                  <p className="text-xs text-slate-500">talk time</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${sentimentColors[speaker.sentiment]}`}>
                  {speaker.sentiment}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

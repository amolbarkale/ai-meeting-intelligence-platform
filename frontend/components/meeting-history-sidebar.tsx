"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { ChevronLeft, ChevronRight, FileAudio } from "lucide-react"

interface Meeting {
  id: string
  title: string
  date: string
  tags: string[]
  sentiment: "positive" | "neutral" | "negative"
}

interface MeetingHistorySidebarProps {
  meetings: Meeting[]
  onSelectMeeting?: (id: string) => void
}

export default function MeetingHistorySidebar({ meetings, onSelectMeeting }: MeetingHistorySidebarProps) {
  const [isOpen, setIsOpen] = useState(false)

  const sentimentColors = {
    positive: "text-green-600",
    neutral: "text-slate-600",
    negative: "text-red-600",
  }

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-0 top-1/2 -translate-y-1/2 z-40 bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-r-lg transition"
      >
        {isOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
      </button>

      {/* Sidebar */}
      {isOpen && (
        <div className="fixed left-0 top-0 h-screen w-80 bg-white border-r border-slate-200 shadow-lg z-30 overflow-y-auto">
          <div className="p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Meeting History</h2>

            <div className="space-y-3">
              {meetings.map((meeting) => (
                <Card
                  key={meeting.id}
                  className="p-3 cursor-pointer hover:shadow-md transition"
                  onClick={() => {
                    onSelectMeeting?.(meeting.id)
                    setIsOpen(false)
                  }}
                >
                  <div className="flex items-start gap-3">
                    <FileAudio className="w-4 h-4 text-slate-400 mt-1 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-900 text-sm truncate">{meeting.title}</p>
                      <p className="text-xs text-slate-500">{meeting.date}</p>
                      <div className="flex gap-1 mt-2 flex-wrap">
                        {meeting.tags.map((tag) => (
                          <span key={tag} className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className={`text-lg ${sentimentColors[meeting.sentiment]}`}>●</div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

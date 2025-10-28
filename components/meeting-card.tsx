"use client"

import { Card } from "@/components/ui/card"
import { FileAudio, CheckCircle, AlertCircle, Loader2, Zap } from "lucide-react"
import Link from "next/link"
import { useEffect, useState } from "react"

interface MeetingCardProps {
  meeting: {
    id: string
    filename: string
    upload_date: string
    status: string
  }
}

export default function MeetingCard({ meeting }: MeetingCardProps) {
  const [status, setStatus] = useState(meeting.status)
  const [isPolling, setIsPolling] = useState(meeting.status === "processing" || meeting.status === "transcribed")

  useEffect(() => {
    if (!isPolling) return

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/meetings/${meeting.id}/status`)
        if (response.ok) {
          const data = await response.json()
          setStatus(data.status)
          if (data.status === "completed" || data.status === "error") {
            setIsPolling(false)
          }
        }
      } catch (err) {
        console.error("Failed to fetch status:", err)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [isPolling, meeting.id])

  const statusConfig = {
    processing: { icon: Loader2, color: "text-blue-600", bg: "bg-blue-50", label: "Transcribing", animate: true },
    transcribed: { icon: Zap, color: "text-purple-600", bg: "bg-purple-50", label: "Analyzing", animate: true },
    completed: { icon: CheckCircle, color: "text-green-600", bg: "bg-green-50", label: "Complete" },
    error: { icon: AlertCircle, color: "text-red-600", bg: "bg-red-50", label: "Error" },
  }

  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.processing
  const StatusIcon = config.icon

  return (
    <Link href={`/meeting/${meeting.id}`}>
      <Card className="p-4 hover:shadow-md transition cursor-pointer">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <FileAudio className="w-5 h-5 text-slate-400 mt-1 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-slate-900 truncate">{meeting.filename}</p>
              <p className="text-sm text-slate-500">{new Date(meeting.upload_date).toLocaleDateString()}</p>
            </div>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${config.bg}`}>
            <StatusIcon className={`w-4 h-4 ${config.color} ${config.animate ? "animate-spin" : ""}`} />
            <span className={`text-xs font-medium ${config.color}`}>{config.label}</span>
          </div>
        </div>
      </Card>
    </Link>
  )
}

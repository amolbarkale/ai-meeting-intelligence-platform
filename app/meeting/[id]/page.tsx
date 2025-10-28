"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, ArrowLeft } from "lucide-react"
import SummarySection from "@/components/dashboard/summary-section"
import TranscriptSection from "@/components/dashboard/transcript-section"
import SentimentSection from "@/components/dashboard/sentiment-section"
import TopicsSection from "@/components/dashboard/topics-section"

interface Meeting {
  id: string
  filename: string
  upload_date: string
  status: string
  transcript?: string
  summary?: {
    summary: string
    key_points: string[]
    action_items: string[]
  }
  sentiment?: {
    overall_sentiment: string
    sentiment_score: number
    explanation: string
  }
  topics?: Array<{
    topic_name: string
    relevance_score: number
    mentions: number
  }>
}

export default function MeetingDetailPage() {
  const params = useParams()
  const router = useRouter()
  const meetingId = params.id as string

  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("summary")

  useEffect(() => {
    const fetchMeeting = async () => {
      try {
        setIsLoading(true)
        const response = await fetch(`http://localhost:8000/meetings/${meetingId}`)
        if (!response.ok) throw new Error("Failed to fetch meeting")
        const data = await response.json()
        setMeeting(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load meeting")
      } finally {
        setIsLoading(false)
      }
    }

    fetchMeeting()
    const interval = setInterval(fetchMeeting, 3000)
    return () => clearInterval(interval)
  }, [meetingId])

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
          </div>
        </div>
      </main>
    )
  }

  if (error || !meeting) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Meetings
          </button>
          <Card>
            <CardContent className="py-12">
              <p className="text-center text-red-600">{error || "Meeting not found"}</p>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  const tabs = [
    { id: "summary", label: "Summary" },
    { id: "sentiment", label: "Sentiment" },
    { id: "topics", label: "Topics" },
    { id: "transcript", label: "Transcript" },
  ]

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Meetings
        </button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">{meeting.filename}</h1>
          <p className="text-slate-600">
            Uploaded {new Date(meeting.upload_date).toLocaleDateString()} • Status:{" "}
            <span className="font-medium">{meeting.status}</span>
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 font-medium text-sm transition ${
                activeTab === tab.id
                  ? "text-slate-900 border-b-2 border-slate-900"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === "summary" && <SummarySection meeting={meeting} />}
          {activeTab === "sentiment" && <SentimentSection meeting={meeting} />}
          {activeTab === "topics" && <TopicsSection meeting={meeting} />}
          {activeTab === "transcript" && <TranscriptSection meeting={meeting} />}
        </div>
      </div>
    </main>
  )
}

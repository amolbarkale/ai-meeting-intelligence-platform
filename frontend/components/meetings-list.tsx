"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import MeetingCard from "./meeting-card"

interface Meeting {
  id: string
  filename: string
  upload_date: string
  status: string
}

interface MeetingsListProps {
  refreshTrigger: number
}

export default function MeetingsList({ refreshTrigger }: MeetingsListProps) {
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        setIsLoading(true)
        const response = await fetch("http://localhost:8000/meetings")
        if (!response.ok) throw new Error("Failed to fetch meetings")
        const data = await response.json()
        setMeetings(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load meetings")
      } finally {
        setIsLoading(false)
      }
    }

    fetchMeetings()
  }, [refreshTrigger])

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-12">
          <p className="text-center text-red-600">{error}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Meetings</CardTitle>
        <CardDescription>{meetings.length} meetings uploaded</CardDescription>
      </CardHeader>
      <CardContent>
        {meetings.length === 0 ? (
          <p className="text-center text-slate-500 py-8">No meetings yet. Upload one to get started.</p>
        ) : (
          <div className="space-y-3">
            {meetings.map((meeting) => (
              <MeetingCard key={meeting.id} meeting={meeting} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, Calendar, FileText, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import { useMeetingStatus } from "@/lib/hooks"
import Link from "next/link"

interface Meeting {
  id: string
  original_filename: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  created_at: string
}

interface MeetingsListProps {
  meetings: Meeting[]
  isLoading: boolean
  error: string | null
}

function MeetingCard({ meeting }: { meeting: Meeting }) {
  const { status: statusData } = useMeetingStatus(meeting.id)
  
  const getStatusIcon = () => {
    switch (meeting.status) {
      case 'COMPLETED':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'FAILED':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'PROCESSING':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />
    }
  }

  const getStatusColor = () => {
    switch (meeting.status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800'
      case 'FAILED':
        return 'bg-red-100 text-red-800'
      case 'PROCESSING':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Link href={`/meeting/${meeting.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-slate-500 flex-shrink-0" />
                <h3 className="font-medium text-slate-900 truncate">
                  {meeting.original_filename}
                </h3>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(meeting.created_at)}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 ml-4">
              {getStatusIcon()}
              <Badge className={getStatusColor()}>
                {meeting.status.toLowerCase()}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

export default function MeetingsList({ meetings, isLoading, error }: MeetingsListProps) {
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
          <div className="flex items-center justify-center gap-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <p>{error}</p>
          </div>
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
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No meetings yet. Upload one to get started.</p>
          </div>
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

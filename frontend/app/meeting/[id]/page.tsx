"use client"

import { useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, ArrowLeft, AlertCircle, CheckCircle, Clock, XCircle } from "lucide-react"
import { useMeetingDetails, useMeetingStatus, useMeetingGraphContext } from "@/lib/hooks"
import ChatBox from "@/components/chat-box"

export default function MeetingDetailPage() {
  const params = useParams()
  const router = useRouter()
  const meetingId = params.id as string

  const { meeting, isLoading, error, refetch } = useMeetingDetails(meetingId)
  const { status } = useMeetingStatus(meetingId)
  const { context: graphContext, isLoading: graphLoading, error: graphError } = useMeetingGraphContext(meetingId)
  const currentStatus = status?.status || meeting?.status

  useEffect(() => {
    if (!status?.status || !meeting) return

    if ((status.status === 'COMPLETED' || status.status === 'FAILED') && meeting.status !== status.status) {
      refetch()
    }
  }, [status?.status, meeting?.status, refetch])

  const getStatusIcon = () => {
    switch (currentStatus) {
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
    switch (currentStatus) {
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
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

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
              <div className="flex items-center justify-center gap-2 text-red-600">
                <AlertCircle className="w-5 h-5" />
                <p>{error || "Meeting not found"}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  const isProcessing = currentStatus === 'PROCESSING' || currentStatus === 'PENDING'
  const isCompleted = currentStatus === 'COMPLETED'
  const isFailed = currentStatus === 'FAILED'

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
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">{meeting.original_filename}</h1>
          <p className="text-slate-600">
                Uploaded {formatDate(meeting.created_at)}
          </p>
        </div>
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              <Badge className={getStatusColor()}>
                {(currentStatus || 'unknown').toLowerCase()}
              </Badge>
            </div>
          </div>

          {status?.message && (
            <Card className="mb-6">
              <CardContent className="py-3">
                <p className="text-sm text-slate-600">{status.message}</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Content based on status */}
        {isProcessing && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-slate-900 mb-2">Processing Meeting</h2>
                <p className="text-slate-600 mb-4">
                  Your meeting is being analyzed. This may take a few minutes.
                </p>
                <div className="text-sm text-slate-500">
                  <p>• Converting audio to text</p>
                  <p>• Identifying speakers</p>
                  <p>• Generating insights</p>
                  <p>• Creating searchable content</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {isFailed && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-slate-900 mb-2">Processing Failed</h2>
                <p className="text-slate-600 mb-4">
                  There was an error processing your meeting. Please try uploading again.
                </p>
            <button
                  onClick={() => router.push("/")}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Upload Another Meeting
            </button>
              </div>
            </CardContent>
          </Card>
        )}

        {isCompleted && (
          <div className="space-y-8">
            {graphLoading && (
              <Card>
                <CardContent className="py-6 flex items-center gap-3 text-slate-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Loading knowledge graph context…</span>
                </CardContent>
              </Card>
            )}

            {graphError && (
              <Card>
                <CardContent className="py-6 flex items-center gap-3 text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>{graphError}</span>
                </CardContent>
              </Card>
            )}

            {graphContext && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Knowledge Graph Highlights</h2>
                  <p className="text-sm text-slate-500">
                    Participants, decisions, and timeline events extracted from the meeting graph.
                  </p>
                </CardHeader>
                <CardContent className="grid gap-6 md:grid-cols-2">
                  {graphContext.participants.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-700 mb-2">Participants</h3>
                      <ul className="space-y-1 text-sm text-slate-600">
                        {graphContext.participants.map((participant) => (
                          <li key={participant.id ?? participant.name}>
                            <span className="font-medium text-slate-700">{participant.name}</span>
                            {participant.role && <span className="ml-1">({participant.role})</span>}
                            {participant.organization && <span className="ml-1 text-slate-500">· {participant.organization}</span>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {graphContext.decisions.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-700 mb-2">Decisions</h3>
                      <ul className="space-y-1 text-sm text-slate-600">
                        {graphContext.decisions.map((decision) => (
                          <li key={decision.id ?? decision.title}>
                            <span className="font-medium text-slate-700">{decision.title}</span>
                            {decision.owner && <span className="ml-1">· Owner: {decision.owner}</span>}
                            {decision.due_date && <span className="ml-1">· Due: {decision.due_date}</span>}
                            {decision.description && <p className="text-slate-500 text-xs">{decision.description}</p>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {graphContext.timeline.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-700 mb-2">Timeline Highlights</h3>
                      <ul className="space-y-1 text-sm text-slate-600">
                        {graphContext.timeline.map((entry) => (
                          <li key={entry.id ?? entry.label}>
                            <span className="font-medium text-slate-700">
                              {entry.start_time ? `${entry.start_time} · ` : ""}
                              {entry.label}
                            </span>
                            {entry.summary && <p className="text-slate-500 text-xs">{entry.summary}</p>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {graphContext.topics.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-700 mb-2">Topics</h3>
                      <div className="flex flex-wrap gap-2">
                        {graphContext.topics.map((topic) => (
                          <Badge key={topic} variant="secondary" className="bg-slate-200 text-slate-700">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Summary */}
            {meeting.summary && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Summary</h2>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 leading-relaxed">{meeting.summary}</p>
                </CardContent>
              </Card>
            )}

            {/* Key Points */}
            {meeting.key_points && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Key Points</h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{ __html: meeting.key_points.replace(/\n/g, '<br>') }} />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Items */}
            {meeting.action_items && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Action Items</h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{ __html: meeting.action_items.replace(/\n/g, '<br>') }} />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Sentiment */}
            {meeting.sentiment && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Sentiment Analysis</h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{ __html: meeting.sentiment.replace(/\n/g, '<br>') }} />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tags */}
            {meeting.tags && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Topics & Tags</h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{ __html: meeting.tags.replace(/\n/g, '<br>') }} />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Transcript */}
            {meeting.transcript && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Transcript</h2>
                </CardHeader>
                <CardContent>
                  <div className="bg-slate-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                    <pre className="text-sm text-slate-700 whitespace-pre-wrap font-mono">
                      {meeting.transcript}
                    </pre>
        </div>
                </CardContent>
              </Card>
            )}

            {/* Knowledge Graph */}
            {meeting.knowledge_graph && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-slate-900">Knowledge Graph</h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{ __html: meeting.knowledge_graph.replace(/\n/g, '<br>') }} />
                  </div>
                </CardContent>
              </Card>
            )}
        </div>
        )}
      </div>

      <ChatBox meetingId={meetingId} />
    </main>
  )
}

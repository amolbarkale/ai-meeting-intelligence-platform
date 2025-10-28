"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Menu, Plus } from "lucide-react"
import MeetingUpload from "@/components/meeting-upload"
import MeetingsList from "@/components/meetings-list"
import SearchBar from "@/components/search-bar"
import { api, MeetingResponse } from "@/lib/api"

export default function Home() {
  const [meetings, setMeetings] = useState<MeetingResponse[]>([])
  const [isLoadingMeetings, setIsLoadingMeetings] = useState(true)
  const [meetingsError, setMeetingsError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Mock data for demonstration (when no real meetings exist)
  const mockMeeting = {
    id: "demo",
    filename: "Q4 Planning Meeting.mp4",
    upload_date: "2024-10-28",
    status: "completed",
    summary: {
      summary: "The Q4 planning meeting covered budget allocation, team expansion, and product roadmap priorities. Key decisions were made regarding resource allocation and timeline adjustments.",
      key_points: [
        "Budget increased by 15% for Q4 initiatives",
        "New marketing team to be hired by November",
        "Product launch delayed to January for quality assurance",
        "Customer feedback integration prioritized",
      ],
      action_items: [
        "Prepare detailed budget breakdown by Friday",
        "Schedule interviews with marketing candidates",
        "Update product roadmap documentation",
        "Send customer survey to top 50 clients",
      ],
    },
    sentiment: {
      overall: 0.72,
      positive: 0.65,
      neutral: 0.25,
      negative: 0.1,
    },
    topics: ["Budget", "Hiring", "Product Launch", "Customer Feedback", "Timeline"],
    speakers: [
      { name: "Sarah Chen", talkTime: 35, sentiment: "positive", wordCount: 2840 },
      { name: "Mike Johnson", talkTime: 28, sentiment: "positive", wordCount: 2156 },
      { name: "Lisa Park", talkTime: 22, sentiment: "neutral", wordCount: 1680 },
      { name: "David Brown", talkTime: 15, sentiment: "positive", wordCount: 1024 },
    ],
    actionItems: [
      {
        id: "1",
        type: "action" as const,
        content: "Prepare detailed budget breakdown",
        timestamp: "00:12:34",
        speaker: "Sarah Chen",
      },
      {
        id: "2",
        type: "decision" as const,
        content: "Product launch delayed to January",
        timestamp: "00:28:15",
        speaker: "Mike Johnson",
      },
      {
        id: "3",
        type: "action" as const,
        content: "Schedule interviews with marketing candidates",
        timestamp: "00:35:42",
        speaker: "Sarah Chen",
      },
      {
        id: "4",
        type: "highlight" as const,
        content: "Customer feedback integration is our top priority",
        timestamp: "00:42:18",
        speaker: "Lisa Park",
      },
    ],
    knowledgeGraph: {
      nodes: [
        { id: "1", label: "Budget", size: 30, frequency: 12 },
        { id: "2", label: "Hiring", size: 25, frequency: 8 },
        { id: "3", label: "Product", size: 28, frequency: 10 },
        { id: "4", label: "Timeline", size: 20, frequency: 6 },
        { id: "5", label: "Customers", size: 22, frequency: 7 },
        { id: "6", label: "Q4", size: 18, frequency: 5 },
      ],
      edges: [
        { source: "Budget", target: "Hiring", weight: 5 },
        { source: "Budget", target: "Product", weight: 4 },
        { source: "Product", target: "Timeline", weight: 6 },
        { source: "Customers", target: "Product", weight: 5 },
        { source: "Hiring", target: "Q4", weight: 3 },
      ],
    },
  }

  const fetchMeetings = async () => {
    try {
      setIsLoadingMeetings(true)
      setMeetingsError(null)
      
      // For now, we'll use mock data since we don't have a list endpoint
      // In a real implementation, you'd call: const data = await api.getMeetings()
      setMeetings([])
    } catch (err) {
      setMeetingsError(err instanceof Error ? err.message : "Failed to load meetings")
    } finally {
      setIsLoadingMeetings(false)
    }
  }

  useEffect(() => {
    fetchMeetings()
  }, [refreshTrigger])

  const handleUploadSuccess = (meetingId: string) => {
    setRefreshTrigger(prev => prev + 1)
  }

  const hasRealMeetings = meetings.length > 0

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Top Navbar */}
      <nav className="sticky top-0 z-20 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Menu className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">Meeting Intelligence</h1>
          </div>

          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            New Meeting
          </Button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8 pb-32">
        {/* Upload Section */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Upload Meeting</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <MeetingUpload onUploadSuccess={handleUploadSuccess} />
            <div className="lg:col-span-2">
              <MeetingsList 
                meetings={meetings}
                isLoading={isLoadingMeetings}
                error={meetingsError}
              />
            </div>
          </div>
        </section>

        {/* Search Section */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Search Meetings</h2>
          <SearchBar />
        </section>

        {/* Demo Content (shown when no real meetings) */}
        {!hasRealMeetings && (
          <>
            {/* Summary & Insights Section */}
            <section className="mb-12">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Meeting Summary & Insights (Demo)</h2>
              <Card>
                <CardHeader>
                  <CardTitle>Demo Meeting Analysis</CardTitle>
                  <CardDescription>
                    This is a demonstration of the AI meeting analysis capabilities. 
                    Upload a real meeting to see your own analysis.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium text-slate-900 mb-2">Summary</h3>
                      <p className="text-slate-600 text-sm leading-relaxed">
                        {mockMeeting.summary.summary}
                      </p>
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-900 mb-2">Key Points</h3>
                      <ul className="text-slate-600 text-sm space-y-1">
                        {mockMeeting.summary.key_points.map((point, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-blue-500 mt-1">•</span>
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-900 mb-2">Action Items</h3>
                      <ul className="text-slate-600 text-sm space-y-1">
                        {mockMeeting.summary.action_items.map((item, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-green-500 mt-1">✓</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* Action Items & Highlights */}
            <section className="mb-12">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Action Items & Highlights (Demo)</h2>
              <Card>
                <CardHeader>
                  <CardTitle>Meeting Highlights</CardTitle>
                  <CardDescription>Key moments and decisions from the meeting</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {mockMeeting.actionItems.map((item) => (
                      <div key={item.id} className="flex items-start gap-3 p-3 border border-slate-200 rounded-lg">
                        <div className="flex-shrink-0">
                          {item.type === 'action' && <span className="text-green-500 text-sm">📝</span>}
                          {item.type === 'decision' && <span className="text-blue-500 text-sm">⚖️</span>}
                          {item.type === 'highlight' && <span className="text-yellow-500 text-sm">⭐</span>}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-slate-900">{item.content}</p>
                          <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                            <span>{item.timestamp}</span>
                            <span>•</span>
                            <span>{item.speaker}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </section>
          </>
        )}
      </div>
    </main>
  )
}

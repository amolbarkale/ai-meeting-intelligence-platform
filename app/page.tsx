"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, Menu } from "lucide-react"
import MeetingUpload from "@/components/meeting-upload"
import TopicTagsBar from "@/components/topic-tags-bar"
import SpeakerStatsPanel from "@/components/speaker-stats-panel"
import SentimentMeter from "@/components/sentiment-meter"
import ActionItemsHighlights from "@/components/action-items-highlights"
import KnowledgeGraph from "@/components/analytics/knowledge-graph"
import ChatBox from "@/components/chat-box"
import MeetingHistorySidebar from "@/components/meeting-history-sidebar"
import ShareExportButtons from "@/components/share-export-buttons"
import SummarySection from "@/components/dashboard/summary-section"
import SentimentChart from "@/components/analytics/sentiment-chart"

// Mock data
const mockMeeting = {
  id: "1",
  filename: "Q4 Planning Meeting.mp4",
  upload_date: "2024-10-28",
  status: "completed",
  summary: {
    summary:
      "The Q4 planning meeting covered budget allocation, team expansion, and product roadmap priorities. Key decisions were made regarding resource allocation and timeline adjustments.",
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

const mockMeetingHistory = [
  {
    id: "1",
    title: "Q4 Planning Meeting",
    date: "Oct 28, 2024",
    tags: ["Planning", "Budget"],
    sentiment: "positive" as const,
  },
  {
    id: "2",
    title: "Product Review",
    date: "Oct 27, 2024",
    tags: ["Product", "Review"],
    sentiment: "neutral" as const,
  },
  {
    id: "3",
    title: "Client Call",
    date: "Oct 26, 2024",
    tags: ["Client", "Sales"],
    sentiment: "positive" as const,
  },
]

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTag, setSelectedTag] = useState<string | null>(null)

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Top Navbar */}
      <nav className="sticky top-0 z-20 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Menu className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">Meeting Intelligence</h1>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search meetings, topics, or transcripts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-slate-50 border-slate-200"
              />
            </div>
          </div>

          <Button className="bg-blue-600 hover:bg-blue-700">New Meeting</Button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8 pb-32">
        {/* Upload Section */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Upload Meeting</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <MeetingUpload onUploadSuccess={() => {}} />
            <div className="lg:col-span-2">
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Recent Uploads</CardTitle>
                  <CardDescription>Your latest meeting recordings</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 text-sm">No recent uploads. Upload a meeting to get started.</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Summary & Insights Section */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Meeting Summary & Insights</h2>

          <Tabs defaultValue="summary" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
              <TabsTrigger value="speakers">Speakers</TabsTrigger>
              <TabsTrigger value="topics">Topics</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="space-y-6">
              <SummarySection meeting={mockMeeting} />
            </TabsContent>

            <TabsContent value="sentiment" className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SentimentMeter
                overall={mockMeeting.sentiment.overall}
                positive={mockMeeting.sentiment.positive}
                neutral={mockMeeting.sentiment.neutral}
                negative={mockMeeting.sentiment.negative}
              />
              <SentimentChart data={[]} />
            </TabsContent>

            <TabsContent value="speakers">
              <SpeakerStatsPanel speakers={mockMeeting.speakers} />
            </TabsContent>

            <TabsContent value="topics" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Detected Topics</CardTitle>
                  <CardDescription>Key topics discussed in the meeting</CardDescription>
                </CardHeader>
                <CardContent>
                  <TopicTagsBar tags={mockMeeting.topics} onTagClick={setSelectedTag} />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </section>

        {/* Action Items & Highlights */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Action Items & Highlights</h2>
          <ActionItemsHighlights items={mockMeeting.actionItems} />
        </section>

        {/* Knowledge Graph */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Topic Network</h2>
          <KnowledgeGraph data={mockMeeting.knowledgeGraph} />
        </section>
      </div>

      {/* Floating Components */}
      <ChatBox />
      <ShareExportButtons />
      <MeetingHistorySidebar meetings={mockMeetingHistory} />
    </main>
  )
}

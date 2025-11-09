"use client"

import { useEffect, useMemo, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Send, Loader2, ChevronDown, ChevronUp, AlertCircle, Info } from "lucide-react"
import { useMeetingChat, useMeetingGraphContext } from "@/lib/hooks"

interface ChatBoxProps {
  meetingId: string | null
  disabled?: boolean
}

export default function ChatBox({ meetingId, disabled = false }: ChatBoxProps) {
  const [input, setInput] = useState("")
  const [isExpanded, setIsExpanded] = useState(true)
  const [showContext, setShowContext] = useState(true)

  const { messages, isLoading, error, sendMessage, context: chatContext } = useMeetingChat(meetingId)
  const {
    context: graphContext,
    isLoading: graphLoading,
    error: graphError,
  } = useMeetingGraphContext(meetingId)

  useEffect(() => {
    setInput("")
  }, [meetingId])

  const examplePrompts = useMemo(() => {
    if (!graphContext) {
      return [
        "Summarize the key decisions.",
        "List the follow-up items with owners.",
        "When did we discuss the budget topic?",
      ]
    }

    const prompts: string[] = []
    if (graphContext.decisions.length > 0) {
      prompts.push("Summarize the decisions made in this meeting.")
    }
    if (graphContext.action_items_structured.length > 0) {
      prompts.push("What follow-up items were assigned and to whom?")
    }
    if (graphContext.timeline.length > 0) {
      const firstEvent = graphContext.timeline[0]
      const label = firstEvent.label || "this point"
      prompts.push(`What was discussed around ${label.toLowerCase()}?`)
    }
    if (graphContext.participants.length > 0) {
      const participant = graphContext.participants[0]
      if (participant.name) {
        prompts.push(`What topics involved ${participant.name}?`)
      }
    }
    const uniquePrompts = Array.from(new Set(prompts))
    if (uniquePrompts.length < 3) {
      uniquePrompts.push("Give me a recap of the major themes.")
    }
    return uniquePrompts.slice(0, 3)
  }, [graphContext])

  const handleSendMessage = async () => {
    if (!input.trim() || !meetingId || disabled) return
    const message = input.trim()
    setInput("")
    await sendMessage(message)
  }

  const renderContextPanel = () => {
    if (!meetingId) return null

    return (
      <div className="rounded-md border border-slate-200 bg-slate-50 p-3 space-y-2 text-xs text-slate-600">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-slate-500" />
          <span className="font-semibold text-slate-700">Graph Snapshot</span>
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto h-6 px-2 text-xs"
            onClick={() => setShowContext((prev) => !prev)}
          >
            {showContext ? "Hide" : "Show"}
          </Button>
        </div>

        {graphLoading && (
          <div className="flex items-center gap-2 text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading meeting knowledge graph...
          </div>
        )}

        {graphError && (
          <div className="flex items-center gap-2 text-red-600 border border-red-200 bg-red-50 rounded px-3 py-2">
            <AlertCircle className="w-4 h-4" />
            {graphError}
          </div>
        )}

        {showContext && graphContext && (
          <div className="space-y-3">
            {graphContext.topics.length > 0 && (
              <div>
                <p className="font-semibold text-slate-700 mb-1">Topics</p>
                <div className="flex flex-wrap gap-1">
                  {graphContext.topics.map((topic) => (
                    <Badge key={topic} variant="secondary" className="bg-slate-200 text-slate-700">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {graphContext.participants.length > 0 && (
              <div>
                <p className="font-semibold text-slate-700 mb-1">Participants</p>
                <ul className="space-y-1">
                  {graphContext.participants.map((participant) => (
                    <li key={participant.id ?? participant.name}>
                      <span className="font-medium text-slate-700">{participant.name}</span>
                      {participant.role && <span className="ml-1 text-slate-500">({participant.role})</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {graphContext.decisions.length > 0 && (
              <div>
                <p className="font-semibold text-slate-700 mb-1">Decisions</p>
                <ul className="space-y-1">
                  {graphContext.decisions.slice(0, 3).map((decision) => (
                    <li key={decision.id ?? decision.title} className="text-slate-600">
                      <span className="font-medium text-slate-700">{decision.title}</span>
                      {decision.owner && <span className="ml-1">· Owner: {decision.owner}</span>}
                      {decision.due_date && <span className="ml-1">· Due: {decision.due_date}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {graphContext.timeline.length > 0 && (
              <div>
                <p className="font-semibold text-slate-700 mb-1">Timeline Highlights</p>
                <ul className="space-y-1">
                  {graphContext.timeline.slice(0, 3).map((entry) => (
                    <li key={entry.id ?? entry.label}>
                      <span className="font-medium text-slate-700">
                        {entry.start_time ? `${entry.start_time} · ` : ""}
                        {entry.label}
                      </span>
                      {entry.summary && <span className="ml-1 text-slate-500">— {entry.summary}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <Card
      className={`fixed bottom-6 right-6 flex flex-col shadow-lg transition-all duration-300 ease-in-out ${
        isExpanded ? "w-96 max-h-[32rem]" : "w-80 h-16"
      }`}
    >
      <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900">Meeting Assistant</h3>
          {isExpanded && (
            <p className="text-xs text-slate-600">
              {meetingId ? "Ask questions about this meeting" : "Select a meeting to start chatting"}
            </p>
          )}
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-2 h-8 w-8 p-0 hover:bg-slate-200"
        >
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-slate-600" />
          ) : (
            <ChevronUp className="w-4 h-4 text-slate-600" />
          )}
        </Button>
      </div>

      {isExpanded && (
        <>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {renderContextPanel()}

            {messages.length === 0 ? (
              <div className="space-y-2">
                <p className="text-xs font-medium text-slate-600 mb-3">Example prompts:</p>
                {examplePrompts.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setInput(prompt)}
                    className="w-full text-left text-xs p-2 rounded border border-slate-200 hover:bg-slate-50 transition text-slate-700 disabled:text-slate-400"
                    disabled={!meetingId || disabled}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-br-none"
                        : "bg-slate-100 text-slate-900 rounded-bl-none"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-100 text-slate-900 px-3 py-2 rounded-lg rounded-bl-none">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
              </div>
            )}
            {error && (
              <div className="flex items-center gap-2 text-sm text-red-600 border border-red-200 bg-red-50 rounded px-3 py-2">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
          </div>

          {chatContext && (
            <div className="px-4 pb-2 text-xs text-slate-500 border-t border-slate-100 bg-slate-50 space-y-1">
              {chatContext.title && <p className="font-semibold text-slate-700">{chatContext.title}</p>}
              {Array.isArray(chatContext.tags) && chatContext.tags.length > 0 && (
                <p>Tags: {chatContext.tags.join(", ")}</p>
              )}
              {Array.isArray(chatContext.topics) && chatContext.topics.length > 0 && (
                <p>Topics: {chatContext.topics.join(", ")}</p>
              )}
              {chatContext.created_at && <p>Recorded: {new Date(chatContext.created_at).toLocaleString()}</p>}
            </div>
          )}

          <div className="p-4 border-t border-slate-200 flex gap-2">
            <Input
              placeholder="Ask about the meeting..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={isLoading || !meetingId || disabled}
              className="text-sm"
            />
            <Button
              size="sm"
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim() || !meetingId || disabled}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </>
      )}
    </Card>
  )
}

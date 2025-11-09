"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Loader2, ChevronDown, ChevronUp, AlertCircle } from "lucide-react"
import { useMeetingChat } from "@/lib/hooks"

interface ChatBoxProps {
  meetingId: string | null
  disabled?: boolean
}

export default function ChatBox({ meetingId, disabled = false }: ChatBoxProps) {
  const [input, setInput] = useState("")
  const [isExpanded, setIsExpanded] = useState(true)
  const { messages, isLoading, error, sendMessage, context } = useMeetingChat(meetingId)

  useEffect(() => {
    setInput("")
  }, [meetingId])

  const examplePrompts = [
    "Summarize the key decisions.",
    "List the follow-up items with owners.",
    "When did we discuss the budget topic?",
  ]

  const handleSendMessage = async () => {
    if (!input.trim() || !meetingId || disabled) return
    const message = input.trim()
    setInput("")
    await sendMessage(message)
  }

  return (
    <Card
      className={`fixed bottom-6 right-6 flex flex-col shadow-lg transition-all duration-300 ease-in-out ${
        isExpanded ? "w-96 max-h-[28rem]" : "w-80 h-16"
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

          {context && (
            <div className="px-4 pb-2 text-xs text-slate-500 border-t border-slate-100 bg-slate-50">
              {context.title && <p className="font-semibold text-slate-700 mb-1">{context.title}</p>}
              {context.tags && Array.isArray(context.tags) && context.tags.length > 0 && (
                <p className="mb-1">Tags: {context.tags.join(", ")}</p>
              )}
              {context.created_at && <p>Recorded: {new Date(context.created_at).toLocaleString()}</p>}
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

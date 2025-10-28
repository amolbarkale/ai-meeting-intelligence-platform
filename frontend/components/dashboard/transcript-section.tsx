"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, Copy, Check } from "lucide-react"
import { useState } from "react"

interface TranscriptSectionProps {
  meeting: {
    transcript?: string
    status: string
  }
}

export default function TranscriptSection({ meeting }: TranscriptSectionProps) {
  const [copied, setCopied] = useState(false)

  if (!meeting.transcript) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <AlertCircle className="w-5 h-5" />
            <p>Transcript not yet available. Processing in progress...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(meeting.transcript || "")
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Full Transcript</CardTitle>
            <CardDescription>Complete meeting transcription</CardDescription>
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded transition"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                Copied
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy
              </>
            )}
          </button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-slate-50 rounded-lg p-6 max-h-96 overflow-y-auto">
          <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{meeting.transcript}</p>
        </div>
      </CardContent>
    </Card>
  )
}

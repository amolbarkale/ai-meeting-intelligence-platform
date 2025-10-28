"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload } from "lucide-react"
import Link from "next/link"
import ProcessingIndicator from "./processing-indicator"

interface MeetingUploadProps {
  onUploadSuccess: () => void
}

export default function MeetingUpload({ onUploadSuccess }: MeetingUploadProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setFileName(file.name)
    setError(null)
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      const data = await response.json()
      console.log("Upload successful:", data)
      onUploadSuccess()
      setFileName(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <ProcessingIndicator fileName={fileName || ""} isVisible={isLoading} />

      <Card className="h-full">
        <CardHeader>
          <CardTitle>Upload Meeting</CardTitle>
          <CardDescription>Audio or video file</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex flex-col items-center justify-center w-full p-6 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-slate-400 transition">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Upload className="w-8 h-8 text-slate-400 mb-2" />
              <p className="text-sm text-slate-600">{fileName ? fileName : "Click to upload or drag and drop"}</p>
              <p className="text-xs text-slate-500 mt-1">MP3, WAV, M4A, MP4, WebM</p>
            </div>
            <input
              type="file"
              className="hidden"
              accept=".mp3,.wav,.m4a,.mp4,.webm"
              onChange={handleFileChange}
              disabled={isLoading}
            />
          </label>

          {error && <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">{error}</div>}

          <Link
            href="/analytics"
            className="block w-full text-center px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition font-medium text-sm"
          >
            View Analytics
          </Link>
        </CardContent>
      </Card>
    </>
  )
}

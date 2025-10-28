"use client"

import type React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, Loader2, CheckCircle, AlertCircle } from "lucide-react"
import { useMeetingUpload } from "@/lib/hooks"
import { useState } from "react"

interface MeetingUploadProps {
  onUploadSuccess: (meetingId: string) => void
}

export default function MeetingUpload({ onUploadSuccess }: MeetingUploadProps) {
  const { uploadFile, isLoading, error, uploadedMeeting, reset } = useMeetingUpload()
  const [fileName, setFileName] = useState<string | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setFileName(file.name)
    reset()

    try {
      const result = await uploadFile(file)
      onUploadSuccess(result.id)
    } catch (err) {
      // Error is handled by the hook
    }
  }

  const getStatusIcon = () => {
    if (isLoading) return <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    if (uploadedMeeting) return <CheckCircle className="w-8 h-8 text-green-500" />
    if (error) return <AlertCircle className="w-8 h-8 text-red-500" />
    return <Upload className="w-8 h-8 text-slate-400" />
  }

  const getStatusText = () => {
    if (isLoading) return "Uploading..."
    if (uploadedMeeting) return "Upload successful!"
    if (error) return "Upload failed"
    return fileName ? fileName : "Click to upload or drag and drop"
  }

  const getStatusColor = () => {
    if (isLoading) return "text-blue-600"
    if (uploadedMeeting) return "text-green-600"
    if (error) return "text-red-600"
    return "text-slate-600"
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Upload Meeting</CardTitle>
        <CardDescription>Audio or video file (MP3, WAV, M4A, MP4, AVI, MOV, MKV)</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <label className="flex flex-col items-center justify-center w-full p-6 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-slate-400 transition">
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            {getStatusIcon()}
            <p className={`text-sm mt-2 ${getStatusColor()}`}>{getStatusText()}</p>
            <p className="text-xs text-slate-500 mt-1">Max size: 100MB</p>
          </div>
          <input
            type="file"
            className="hidden"
            accept=".mp3,.wav,.m4a,.mp4,.avi,.mov,.mkv"
            onChange={handleFileChange}
            disabled={isLoading}
          />
        </label>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        {uploadedMeeting && (
          <div className="p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700">
            Meeting uploaded successfully! Processing will begin shortly.
          </div>
        )}
      </CardContent>
    </Card>
  )
}

"use client"

import { useState, useEffect } from "react"
import { CheckCircle2, Circle, Loader2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ProcessingStep {
  id: string
  label: string
  status: "pending" | "processing" | "completed"
}

interface ProcessingIndicatorProps {
  fileName: string
  isVisible: boolean
}

export default function ProcessingIndicator({ fileName, isVisible }: ProcessingIndicatorProps) {
  const [steps, setSteps] = useState<ProcessingStep[]>([
    { id: "upload", label: "Uploading file", status: "processing" },
    { id: "transcribe", label: "Transcribing audio", status: "pending" },
    { id: "sentiment", label: "Analyzing sentiment", status: "pending" },
    { id: "topics", label: "Extracting topics", status: "pending" },
    { id: "summary", label: "Generating summary", status: "pending" },
    { id: "graph", label: "Creating knowledge graph", status: "pending" },
  ])

  useEffect(() => {
    if (!isVisible) return

    const timings = [1000, 3000, 2000, 2000, 2500, 1500]
    let currentStep = 0

    const interval = setInterval(
      () => {
        if (currentStep < steps.length) {
          setSteps((prev) => {
            const updated = [...prev]
            if (currentStep > 0) {
              updated[currentStep - 1].status = "completed"
            }
            if (currentStep < updated.length) {
              updated[currentStep].status = "processing"
            }
            return updated
          })
          currentStep++
        } else {
          clearInterval(interval)
        }
      },
      timings[Math.min(currentStep, timings.length - 1)],
    )

    return () => clearInterval(interval)
  }, [isVisible, steps.length])

  if (!isVisible) return null

  return (
    <Card className="border-blue-200 bg-blue-50">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          Processing: {fileName}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-start gap-3">
            <div className="mt-1">
              {step.status === "completed" && <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />}
              {step.status === "processing" && <Loader2 className="w-5 h-5 text-blue-600 animate-spin flex-shrink-0" />}
              {step.status === "pending" && <Circle className="w-5 h-5 text-slate-300 flex-shrink-0" />}
            </div>
            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  step.status === "completed"
                    ? "text-green-700"
                    : step.status === "processing"
                      ? "text-blue-700"
                      : "text-slate-500"
                }`}
              >
                {step.label}
              </p>
              {step.status === "processing" && (
                <div className="mt-1 h-1 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 rounded-full animate-pulse" style={{ width: "60%" }} />
                </div>
              )}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

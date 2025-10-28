"use client"

import { Button } from "@/components/ui/button"
import { Share2, Download } from "lucide-react"
import { useState } from "react"

export default function ShareExportButtons() {
  const [copied, setCopied] = useState(false)

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleExport = () => {
    // Mock export functionality
    alert("Export to PDF functionality would be implemented here")
  }

  return (
    <div className="fixed bottom-6 left-6 flex gap-2">
      <Button
        onClick={handleShare}
        variant="outline"
        size="sm"
        className="gap-2 bg-transparent"
        title="Copy link to clipboard"
      >
        <Share2 className="w-4 h-4" />
        {copied ? "Copied!" : "Share"}
      </Button>
      <Button
        onClick={handleExport}
        variant="outline"
        size="sm"
        className="gap-2 bg-transparent"
        title="Download as PDF"
      >
        <Download className="w-4 h-4" />
        Export
      </Button>
    </div>
  )
}

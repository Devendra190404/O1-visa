"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, FileText, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface PDFViewerProps {
  file: File
  isProcessing: boolean
}

export function PDFViewer({ file, isProcessing }: PDFViewerProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [highlightPosition, setHighlightPosition] = useState({ top: 0, left: 0, width: 100, height: 20 })

  useEffect(() => {
    // Create a URL for the PDF file
    const url = URL.createObjectURL(file)
    setPdfUrl(url)
    setLoading(false)

    // Clean up the URL when the component unmounts
    return () => {
      URL.revokeObjectURL(url)
    }
  }, [file])

  // Animation for highlighting different parts of the PDF
  useEffect(() => {
    if (!isProcessing) return

    const interval = setInterval(() => {
      // Get the iframe dimensions
      const iframe = document.querySelector("iframe")
      if (!iframe) return

      const iframeHeight = iframe.clientHeight
      const iframeWidth = iframe.clientWidth

      // Randomly position the highlight within the iframe
      setHighlightPosition({
        top: Math.random() * (iframeHeight - 40),
        left: Math.random() * (iframeWidth - 200),
        width: 150 + Math.random() * 200,
        height: 15 + Math.random() * 20,
      })
    }, 1500)

    return () => clearInterval(interval)
  }, [isProcessing])

  if (loading) {
    return (
      <Card className="w-full border-dashed">
        <CardContent className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full border-dashed">
        <CardContent className="p-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>Error loading PDF: {error}</AlertDescription>
          </Alert>
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <FileText className="h-16 w-16 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">PDF Preview Not Available</p>
            <p className="text-xs text-muted-foreground mt-2">Your PDF is still being processed</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full border-dashed overflow-hidden">
      <CardContent className="p-0 relative">
        <div className="relative" style={{ height: "500px" }}>
          {pdfUrl && <iframe src={`${pdfUrl}#toolbar=0`} className="w-full h-full border-none" title="PDF Preview" />}

          {isProcessing && (
            <div
              className="absolute bg-primary/20 border border-primary/30 transition-all duration-1000 ease-in-out rounded-sm pointer-events-none"
              style={{
                top: highlightPosition.top,
                left: highlightPosition.left,
                width: highlightPosition.width,
                height: highlightPosition.height,
                zIndex: 10,
              }}
            />
          )}
        </div>
      </CardContent>
    </Card>
  )
}


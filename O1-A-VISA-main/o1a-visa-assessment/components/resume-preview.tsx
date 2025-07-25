"use client"

import { useEffect, useState, useRef } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { FileText } from "lucide-react"
import { PDFViewer } from "./pdf-viewer"

interface ResumePreviewProps {
  file: File | null
  isProcessing: boolean
}

export function ResumePreview({ file, isProcessing }: ResumePreviewProps) {
  const [content, setContent] = useState<string>("")
  const [isPdf, setIsPdf] = useState(false)
  const [isDocx, setIsDocx] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)
  const [highlightPosition, setHighlightPosition] = useState({ top: 0, width: 0, height: 0 })

  useEffect(() => {
    if (!file) {
      setContent("")
      setIsPdf(false)
      setIsDocx(false)
      return
    }

    const fileType = file.name.split(".").pop()?.toLowerCase()
    setIsPdf(fileType === "pdf")
    setIsDocx(fileType === "docx")

    if (fileType === "txt") {
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        setContent(text || "")
      }
      reader.readAsText(file)
    } else if (fileType === "docx") {
      setContent("[Word Document Content]")
    }
  }, [file])

  // Animation effect for highlighting different parts of the resume
  useEffect(() => {
    if (!isProcessing || !contentRef.current || !content) return

    const contentElement = contentRef.current
    const paragraphs = contentElement.querySelectorAll("p")
    if (paragraphs.length === 0) return

    let currentIndex = 0
    const interval = setInterval(() => {
      if (currentIndex >= paragraphs.length) {
        currentIndex = 0
      }

      const paragraph = paragraphs[currentIndex]
      const rect = paragraph.getBoundingClientRect()
      const parentRect = contentElement.getBoundingClientRect()

      setHighlightPosition({
        top: paragraph.offsetTop,
        width: rect.width,
        height: rect.height,
      })

      currentIndex++
    }, 2000)

    return () => clearInterval(interval)
  }, [isProcessing, content])

  if (!file) return null

  if (isPdf) {
    return <PDFViewer file={file} isProcessing={isProcessing} />
  }

  if (isDocx) {
    return (
      <Card className="w-full border-dashed">
        <CardContent className="flex flex-col items-center justify-center p-8 text-center">
          <FileText className="h-16 w-16 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Word Document Preview Not Available</p>
          <p className="text-xs text-muted-foreground mt-2">Your document is being processed</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full border-dashed">
      <CardContent className="p-0">
        <div ref={contentRef} className="relative font-mono text-xs p-4 max-h-[400px] overflow-auto">
          {isProcessing && (
            <div
              className="absolute bg-primary/10 transition-all duration-1000 ease-in-out"
              style={{
                top: highlightPosition.top,
                height: highlightPosition.height,
                width: "100%",
                left: 0,
              }}
            />
          )}
          {content.split("\n").map((line, i) => (
            <p key={i} className="mb-1 leading-relaxed">
              {line || " "}
            </p>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


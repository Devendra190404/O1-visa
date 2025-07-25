"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, FileText, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AssessmentResult } from "./assessment-result"
import { ProcessingNotification } from "./processing-notification"
import { ResumePreview } from "./resume-preview"
import { ResumeAnalyzerAnimation } from "./resume-analyzer-animation"

export function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [apiUrl, setApiUrl] = useState("https://09c9-38-242-232-192.ngrok-free.app")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      const fileExt = selectedFile.name.split(".").pop()?.toLowerCase()

      if (!fileExt || !["pdf", "docx", "txt"].includes(fileExt)) {
        setError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
        setFile(null)
        return
      }

      setFile(selectedFile)
      setError(null)
      setResult(null) // Clear previous results when a new file is selected
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      setError("Please select a file to upload")
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append("cv_file", file)

      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Upload CV for Assessment</CardTitle>
        <CardDescription>Upload your CV to analyze your eligibility for an O-1A visa</CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-url">API URL</Label>
            <Input
              id="api-url"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8000"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cv-file">CV File (PDF, DOCX, or TXT)</Label>
            <div className="flex items-center gap-2">
              <Input
                id="cv-file"
                type="file"
                onChange={handleFileChange}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                accept=".pdf,.docx,.txt"
              />
            </div>
            {file && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span>{file.name}</span>
              </div>
            )}
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? (
              <>Analyzing...</>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Analyze CV
              </>
            )}
          </Button>
        </form>
      </CardContent>

      <CardFooter className="flex flex-col w-full gap-4">
        {file && <ResumePreview file={file} isProcessing={isLoading} />}
        <ResumeAnalyzerAnimation isVisible={isLoading} />
        <ProcessingNotification isVisible={isLoading} />
        {result && <AssessmentResult result={result} />}
      </CardFooter>
    </Card>
  )
}


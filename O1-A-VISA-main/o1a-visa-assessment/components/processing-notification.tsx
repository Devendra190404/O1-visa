"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useState, useEffect } from "react"
import { Clock, FileSearch, CheckCircle } from "lucide-react"

interface ProcessingNotificationProps {
  isVisible: boolean
}

export function ProcessingNotification({ isVisible }: ProcessingNotificationProps) {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState(0)

  const stages = [
    { icon: FileSearch, text: "Extracting information from your CV..." },
    { icon: Clock, text: "Analyzing against O-1A criteria..." },
    { icon: CheckCircle, text: "Finalizing assessment..." },
  ]

  useEffect(() => {
    if (!isVisible) {
      setProgress(0)
      setStage(0)
      return
    }

    const totalDuration = 120 * 1000 // 2 minutes in milliseconds
    const interval = 500 // Update every 500ms
    const incrementAmount = (interval / totalDuration) * 100

    const timer = setInterval(() => {
      setProgress((prev) => Math.min(prev + incrementAmount, 100))
    }, interval)

    return () => clearInterval(timer)
  }, [isVisible])

  useEffect(() => {
    if (progress > 75) {
      setStage(2)
    } else if (progress > 30) {
      setStage(1)
    }
  }, [progress])

  if (!isVisible) return null

  const CurrentIcon = stages[stage].icon

  return (
    <Card className="w-full border-primary/20 bg-primary/5">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center text-primary">
          <CurrentIcon className="mr-2 h-5 w-5" />
          Processing Your CV
        </CardTitle>
        <CardDescription>Please wait approximately 2 minutes while we analyze your CV</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Progress value={progress} className="h-2" />
          <p className="text-sm text-muted-foreground animate-in fade-in">{stages[stage].text}</p>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Started</span>
            <span>~2 minutes</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


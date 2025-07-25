"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Cpu, CheckCircle, XCircle, AlertTriangle } from "lucide-react"

interface ResumeAnalyzerAnimationProps {
  isVisible: boolean
}

export function ResumeAnalyzerAnimation({ isVisible }: ResumeAnalyzerAnimationProps) {
  const [currentCriteria, setCurrentCriteria] = useState(0)

  const criteria = [
    { name: "Awards", status: "positive" },
    { name: "Publications", status: "neutral" },
    { name: "Leadership", status: "positive" },
    { name: "Salary", status: "negative" },
    { name: "Judging", status: "neutral" },
    { name: "Critical Employment", status: "positive" },
  ]

  useEffect(() => {
    if (!isVisible) return

    const interval = setInterval(() => {
      setCurrentCriteria((prev) => (prev + 1) % criteria.length)
    }, 1500)

    return () => clearInterval(interval)
  }, [isVisible, criteria.length])

  if (!isVisible) return null

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "positive":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "negative":
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    }
  }

  return (
    <Card className="w-full mt-4 mb-4 bg-background/50 border-dashed">
      <CardContent className="p-4">
        <div className="flex items-center space-x-2 mb-2">
          <Cpu className="h-4 w-4 text-primary animate-pulse" />
          <span className="text-sm font-medium">AI Analysis in Progress</span>
        </div>

        <div className="space-y-2">
          {criteria.map((criterion, index) => (
            <div
              key={index}
              className={`flex items-center justify-between p-2 rounded-md transition-all duration-300 ${
                index === currentCriteria ? "bg-primary/10 scale-105" : ""
              }`}
            >
              <span className="text-xs">{criterion.name}</span>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-muted-foreground">
                  {index === currentCriteria ? "Analyzing..." : index < currentCriteria ? "Analyzed" : "Pending"}
                </span>
                {index < currentCriteria && getStatusIcon(criterion.status)}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


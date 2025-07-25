"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RefreshCw, CheckCircle, XCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function ApiStatus() {
  const [apiUrl, setApiUrl] = useState("https://09c9-38-242-232-192.ngrok-free.app")
  const [status, setStatus] = useState<"online" | "offline" | "checking">("checking")
  const [lastChecked, setLastChecked] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const checkApiStatus = async () => {
    setIsLoading(true)
    setStatus("checking")

    try {
      const response = await fetch(`${apiUrl}/api/health`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      })

      if (response.ok) {
        setStatus("online")
      } else {
        setStatus("offline")
      }
    } catch (error) {
      setStatus("offline")
    } finally {
      setIsLoading(false)
      setLastChecked(new Date().toLocaleTimeString())
    }
  }

  useEffect(() => {
    checkApiStatus()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          API Status
          <Badge variant={status === "online" ? "default" : status === "checking" ? "outline" : "destructive"}>
            {status === "online" ? (
              <span className="flex items-center">
                <CheckCircle className="mr-1 h-3 w-3" />
                Online
              </span>
            ) : status === "checking" ? (
              "Checking..."
            ) : (
              <span className="flex items-center">
                <XCircle className="mr-1 h-3 w-3" />
                Offline
              </span>
            )}
          </Badge>
        </CardTitle>
        <CardDescription>
          Check if the O-1A API is operational
          {lastChecked && <span className="block text-xs">Last checked: {lastChecked}</span>}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="status-api-url">API URL</Label>
            <div className="flex gap-2">
              <Input
                id="status-api-url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
              />
              <Button variant="outline" size="icon" onClick={checkApiStatus} disabled={isLoading}>
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { RefreshCw, Info } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export function CriteriaInfo() {
  const [apiUrl, setApiUrl] = useState("https://09c9-38-242-232-192.ngrok-free.app")
  const [criteria, setCriteria] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchCriteria = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/api/criteria`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch criteria: ${response.status}`)
      }

      const data = await response.json()
      setCriteria(data)
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to fetch criteria")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCriteria()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>O-1A Criteria</CardTitle>
        <CardDescription>Learn about the criteria used for O-1A visa assessment</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="criteria-api-url">API URL</Label>
            <div className="flex gap-2">
              <Input
                id="criteria-api-url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
              />
              <Button variant="outline" size="icon" onClick={fetchCriteria} disabled={isLoading}>
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              </Button>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {isLoading ? (
            <div className="text-center py-4 text-muted-foreground">Loading criteria...</div>
          ) : criteria ? (
            <Accordion type="single" collapsible className="w-full">
              {Object.entries(criteria.criteria || {}).map(([key, value]: [string, any]) => (
                <AccordionItem key={key} value={key}>
                  <AccordionTrigger className="text-sm font-medium">{value.name || key}</AccordionTrigger>
                  <AccordionContent>
                    <div className="text-sm space-y-2">
                      <p>{value.description}</p>
                      {value.examples && value.examples.length > 0 && (
                        <div>
                          <p className="font-medium text-xs mt-2">Examples:</p>
                          <ul className="list-disc pl-5 text-xs text-muted-foreground">
                            {value.examples.map((example: string, i: number) => (
                              <li key={i}>{example}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <div className="flex items-center justify-center py-4 text-muted-foreground">
              <Info className="mr-2 h-4 w-4" />
              <span>No criteria information available</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


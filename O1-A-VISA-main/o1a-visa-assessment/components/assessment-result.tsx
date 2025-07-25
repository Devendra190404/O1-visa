import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Award,
  BookOpen,
  Trophy,
  DollarSign,
  Gavel,
  Briefcase,
  Users,
  Newspaper,
  Lightbulb,
  FileText,
} from "lucide-react"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

interface AssessmentResultProps {
  result: any
}

export function AssessmentResult({ result }: AssessmentResultProps) {
  if (!result || result.status !== "success") {
    return (
      <Card className="w-full border-destructive">
        <CardHeader className="pb-2">
          <CardTitle className="text-destructive flex items-center">
            <XCircle className="mr-2 h-5 w-5" />
            Analysis Failed
          </CardTitle>
          <CardDescription>{result?.message || "Unable to process the CV file"}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const assessment = result.assessment
  console.log(assessment)
  const rating = assessment.qualification_rating?.toLowerCase() || "unknown"
  const approvalChance = assessment.approval_chance || "Unknown"
  const profileType =
    assessment.profile_type
  const fieldType = assessment.field_type?.replace(/\b\w/g, (c: string) => c.toUpperCase()) || "Unknown"
  const criteriaMet = assessment.criteria_met_count || 0
  const detailedAssessment = assessment.detailed_assessment || {}
  const recommendations = assessment.application_recommendations || []
  const redFlags = assessment.red_flags || []
  const visaRequirements = assessment.visa_requirements || {}
  const matchesByCriterion = assessment.matches_by_criterion || {}

  // Sort criteria by confidence
  const sortedCriteria = Object.entries(detailedAssessment).sort((a: any, b: any) => b[1].confidence - a[1].confidence)

  const getBadgeVariant = (rating: string) => {
    switch (rating) {
      case "high":
      case "excellent":
        return "default"
      case "good":
        return "secondary"
      case "moderate":
        return "outline"
      default:
        return "destructive"
    }
  }

  const getIcon = (rating: string) => {
    switch (rating) {
      case "high":
      case "excellent":
      case "good":
        return <CheckCircle2 className="mr-2 h-5 w-5" />
      case "moderate":
        return <AlertCircle className="mr-2 h-5 w-5" />
      default:
        return <XCircle className="mr-2 h-5 w-5" />
    }
  }

  const getCriterionIcon = (name: string) => {
    const lowerName = name.toLowerCase()
    if (lowerName.includes("award")) return <Award className="h-4 w-4" />
    if (lowerName.includes("publication") || lowerName.includes("scholarly")) return <BookOpen className="h-4 w-4" />
    if (lowerName.includes("prize") || lowerName.includes("trophy")) return <Trophy className="h-4 w-4" />
    if (lowerName.includes("salary") || lowerName.includes("remuneration")) return <DollarSign className="h-4 w-4" />
    if (lowerName.includes("judg")) return <Gavel className="h-4 w-4" />
    if (lowerName.includes("employment") || lowerName.includes("critical")) return <Briefcase className="h-4 w-4" />
    if (lowerName.includes("membership")) return <Users className="h-4 w-4" />
    if (lowerName.includes("press")) return <Newspaper className="h-4 w-4" />
    if (lowerName.includes("original") || lowerName.includes("contribution")) return <Lightbulb className="h-4 w-4" />
    if (lowerName.includes("article")) return <FileText className="h-4 w-4" />
    return <CheckCircle2 className="h-4 w-4" />
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "bg-green-500"
    if (confidence >= 0.5) return "bg-yellow-500"
    return "bg-red-500"
  }

  // Extract approval chance percentage for progress bar
  const getApprovalPercentage = (approvalChance: string) => {
    const percentageMatch = approvalChance.match(/(\d+)-(\d+)%/)
    if (percentageMatch) {
      const [_, min, max] = percentageMatch
      return (Number.parseInt(min) + Number.parseInt(max)) / 2
    }

    if (approvalChance.includes("High")) return 90
    if (approvalChance.includes("Medium")) return 60
    if (approvalChance.includes("Low")) return 30
    return 50
  }

  return (
    <div className="space-y-6">
      <Card className="w-full">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              {getIcon(rating)}
              O-1A Assessment Results
            </CardTitle>
            <Badge variant={getBadgeVariant(rating)} className="capitalize">
              {assessment.qualification_rating}
            </Badge>
          </div>
          <CardDescription>{assessment.rating_explanation}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-muted/50 p-3 rounded-md">
              <div className="text-xs text-muted-foreground">Profile Type</div>
              <div className="font-medium">{profileType}</div>
            </div>
            <div className="bg-muted/50 p-3 rounded-md">
              <div className="text-xs text-muted-foreground">Field</div>
              <div className="font-medium">{fieldType}</div>
            </div>
            <div className="bg-muted/50 p-3 rounded-md">
              <div className="text-xs text-muted-foreground">Criteria Met</div>
              <div className="font-medium">{criteriaMet} of 8</div>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Approval Chance</span>
              <span className="text-sm font-medium">{approvalChance}</span>
            </div>
            <Progress value={getApprovalPercentage(approvalChance)} className="h-2" />
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="criteria" className="w-full">
        <TabsList className="grid grid-cols-4 mb-4">
          <TabsTrigger value="criteria">Criteria</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="redflags">Red Flags</TabsTrigger>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
        </TabsList>

        <TabsContent value="criteria" className="space-y-4">
          {sortedCriteria.map(([name, criterion]: [string, any], index) => {
            const confidence = criterion.confidence || 0
            const confidencePct = Math.round(confidence * 100)
            const weight = criterion.weight || 1.0
            const matches = criterion.matches || []

            return (
              <Card
                key={index}
                className={`w-full ${confidence >= 0.7 ? "border-green-200" : confidence >= 0.5 ? "border-yellow-200" : ""}`}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base flex items-center gap-2">
                      {getCriterionIcon(name)}
                      {name}
                      {weight > 1 && (
                        <Badge variant="outline" className="ml-2 text-xs">
                          Weight: {weight}x
                        </Badge>
                      )}
                    </CardTitle>
                    <Badge variant={confidence >= 0.7 ? "default" : confidence >= 0.5 ? "secondary" : "outline"}>
                      {confidencePct}% Confidence
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="mb-2">
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full ${getConfidenceColor(confidence)}`}
                        style={{ width: `${confidencePct}%` }}
                      />
                    </div>
                  </div>

                  <p className="text-sm mb-2">{criterion.evaluation}</p>

                  {matches && matches.length > 0 && (
                    <Accordion type="single" collapsible className="w-full">
                      <AccordionItem value="evidence">
                        <AccordionTrigger className="text-sm">View Evidence ({matches.length})</AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-2 text-sm">
                            {matches.slice(0, 3).map((match: string, i: number) => (
                              <div key={i} className="p-2 bg-muted/50 rounded-md">
                                <div className="text-xs font-medium mb-1">Evidence {i + 1}</div>
                                <div className="whitespace-pre-wrap text-xs">
                                  {match.length > 300 ? `${match.substring(0, 300)}...` : match}
                                </div>
                              </div>
                            ))}
                            {matches.length > 3 && (
                              <div className="text-xs text-muted-foreground">
                                + {matches.length - 3} more evidence items
                              </div>
                            )}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  )}

                  {criterion.strong_examples_matched && criterion.strong_examples_matched.length > 0 && (
                    <div className="mt-2 text-sm">
                      <div className="font-medium text-xs mb-1">Strong Examples Matched:</div>
                      <div className="flex flex-wrap gap-1">
                        {criterion.strong_examples_matched.map((example: string, i: number) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {example}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </TabsContent>

        <TabsContent value="recommendations">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Application Recommendations</CardTitle>
              <CardDescription>Follow these recommendations to strengthen your O-1A visa application</CardDescription>
            </CardHeader>
            <CardContent>
              {recommendations.length > 0 ? (
                <ol className="list-decimal pl-5 space-y-2">
                  {recommendations.map((rec: string, index: number) => (
                    <li key={index} className="text-sm">
                      {rec}
                    </li>
                  ))}
                </ol>
              ) : (
                <div className="text-muted-foreground text-sm">No specific recommendations available.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="redflags">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <AlertCircle className="mr-2 h-5 w-5 text-destructive" />
                Potential Red Flags
              </CardTitle>
              <CardDescription>Issues that might negatively impact your O-1A visa application</CardDescription>
            </CardHeader>
            <CardContent>
              {redFlags.length > 0 ? (
                <div className="space-y-2">
                  {redFlags.map((flag: any, index: number) => {
                    const flagText = typeof flag === "object" ? flag.flag : flag
                    return (
                      <Alert key={index} variant="destructive" className="text-sm">
                        <AlertDescription>{flagText}</AlertDescription>
                      </Alert>
                    )
                  })}
                </div>
              ) : (
                <div className="text-muted-foreground text-sm">No red flags identified.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requirements">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Visa Requirements</CardTitle>
              <CardDescription>O-1A visa requirements and eligibility information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {visaRequirements.eligibility_threshold && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Eligibility Threshold</h3>
                  <p className="text-sm">{visaRequirements.eligibility_threshold}</p>
                </div>
              )}

              {visaRequirements.exception && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Exception</h3>
                  <p className="text-sm">{visaRequirements.exception}</p>
                </div>
              )}

              {visaRequirements.petition_requirements && visaRequirements.petition_requirements.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Petition Requirements</h3>
                  <ul className="list-disc pl-5 text-sm">
                    {visaRequirements.petition_requirements.map((req: string, index: number) => (
                      <li key={index}>{req}</li>
                    ))}
                  </ul>
                </div>
              )}

              {visaRequirements.fees && Object.keys(visaRequirements.fees).length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Fees</h3>
                  <ul className="list-disc pl-5 text-sm">
                    {Object.entries(visaRequirements.fees).map(([name, amount]: [string, any], index: number) => (
                      <li key={index}>
                        {name.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}: {amount}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {visaRequirements.visa_duration && Object.keys(visaRequirements.visa_duration).length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Visa Duration</h3>
                  <ul className="list-disc pl-5 text-sm">
                    {Object.entries(visaRequirements.visa_duration).map(
                      ([type, duration]: [string, any], index: number) => (
                        <li key={index}>
                          {type.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}: {duration}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}
            </CardContent>
            <CardFooter className="text-xs text-muted-foreground border-t pt-4">
              This assessment is for informational purposes only and does not constitute legal advice. Please consult
              with an immigration attorney for professional guidance.
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}


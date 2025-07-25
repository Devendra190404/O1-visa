import { UploadForm } from "@/components/upload-form"
import { ApiStatus } from "@/components/api-status"
import { CriteriaInfo } from "@/components/criteria-info"

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8 bg-background">
      <div className="container mx-auto space-y-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">O-1A Visa Assessment Tool</h1>
          <p className="text-muted-foreground">Upload your CV to assess your eligibility for an O-1A visa</p>
        </header>

        <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
          <div className="space-y-6">
            <UploadForm />
          </div>
          <div className="space-y-6">
            <ApiStatus />
            <CriteriaInfo />
          </div>
        </div>
      </div>
    </main>
  )
}


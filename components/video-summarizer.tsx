"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent } from "@/components/ui/card"
import { VideoSummary } from "@/components/video-summary"
import { Flashcards } from "@/components/flashcards"
import { Quiz } from "@/components/quiz"
import { YoutubeIcon, FileText, BookOpen, HelpCircle, Loader2, AlertCircle } from "lucide-react"
import { extractVideoId } from "@/lib/utils"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function VideoSummarizer() {
  const [url, setUrl] = useState("")
  const [videoId, setVideoId] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [summary, setSummary] = useState("")
  const [activeTab, setActiveTab] = useState("summary")
  const [error, setError] = useState<string | null>(null)
  const [errorDetails, setErrorDetails] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const extractedId = extractVideoId(url)
    if (!extractedId) {
      setError("Please enter a valid YouTube URL")
      setErrorDetails(null)
      return
    }

    setVideoId(extractedId)
    setIsLoading(true)
    setError(null)
    setErrorDetails(null)

    try {
      // Call the real summarize API
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          language: 'en', // Default to English, could add language selector
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to summarize video', { 
          cause: errorData.details 
        })
      }

      const data = await response.json()
      setSummary(data.summary)
      setActiveTab("summary")
    } catch (error) {
      console.error("Error summarizing video:", error)
      if (error instanceof Error) {
        setError(error.message)
        // Check if error has details
        if ('cause' in error && typeof error.cause === 'string') {
          setErrorDetails(error.cause)
        }
      } else {
        setError('Failed to summarize video. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="mb-8">
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <YoutubeIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 dark:text-slate-500" />
              <Input
                type="text"
                placeholder="Paste YouTube URL here..."
                className="pl-10"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <Button type="submit" disabled={isLoading || !url}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing
                </>
              ) : (
                "Summarize"
              )}
            </Button>
          </form>
          
          {error && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                {error}
                {errorDetails && (
                  <p className="mt-2 text-sm opacity-80">{errorDetails}</p>
                )}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {isLoading && (
        <div className="text-center py-12">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
          <p className="mt-4 text-slate-600 dark:text-slate-400">Analyzing video content and generating summary...</p>
        </div>
      )}

      {!isLoading && summary && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-8">
          <TabsList className="grid grid-cols-3 mb-8">
            <TabsTrigger value="summary" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>Summary</span>
            </TabsTrigger>
            <TabsTrigger value="flashcards" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              <span>Flashcards</span>
            </TabsTrigger>
            <TabsTrigger value="quiz" className="flex items-center gap-2">
              <HelpCircle className="h-4 w-4" />
              <span>Quiz</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="summary">
            <VideoSummary videoId={videoId} summary={summary} />
          </TabsContent>

          <TabsContent value="flashcards">
            <Flashcards summary={summary} />
          </TabsContent>

          <TabsContent value="quiz">
            <Quiz summary={summary} />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}


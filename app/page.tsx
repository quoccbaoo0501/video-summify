import { VideoSummarizer } from "@/components/video-summarizer"
import { ThemeToggle } from "@/components/theme-toggle"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 flex flex-col items-center">
          <div className="w-full flex justify-end mb-4">
            <ThemeToggle />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-50 mb-2">Video Summify</h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-center">
            Transform YouTube videos into concise summaries, flashcards, and quizzes to enhance your learning
            experience.
          </p>
        </header>

        <main>
          <VideoSummarizer />
        </main>

        <footer className="mt-16 text-center text-sm text-slate-500 dark:text-slate-400">
          <p>© {new Date().getFullYear()} Video Summify. All rights reserved.</p>
        </footer>
      </div>
    </div>
  )
}


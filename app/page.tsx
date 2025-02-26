import Header from "@/components/Header"
import VideoSummary from "@/components/VideoSummary"
import Footer from "@/components/Footer"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        <VideoSummary />
      </main>
      <Footer />
    </div>
  )
}


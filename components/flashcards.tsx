"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, RotateCcw, AlertCircle, Loader2 } from "lucide-react"

interface FlashcardItem {
  id?: number
  front: string
  back: string
}

interface FlashcardsProps {
  summary: string
}

export function Flashcards({ summary }: FlashcardsProps) {
  const [flashcards, setFlashcards] = useState<FlashcardItem[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Generate flashcards from the summary using our API
    const generateFlashcards = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch('/api/generate-flashcards', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            summary,
            numCards: 10
          }),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to generate flashcards');
        }
        
        const data = await response.json();
        console.log("Flashcards data:", data); // Debug logging
        
        // Add IDs to the flashcards if they don't have them
        const flashcardsWithIds = data.flashcards.map((card: FlashcardItem, index: number) => ({
          ...card,
          id: card.id || index + 1
        }));
        
        setFlashcards(flashcardsWithIds);
      } catch (err) {
        console.error('Error generating flashcards:', err);
        setError(err instanceof Error ? err.message : 'Failed to generate flashcards. Please try again.');
        
        // Fallback to no flashcards if the API call fails
        setFlashcards([]);
      } finally {
        setLoading(false);
      }
    }

    if (summary) {
      generateFlashcards();
    }
  }, [summary]);

  const nextCard = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setFlipped(false);
    }
  };

  const prevCard = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setFlipped(false);
    }
  };

  const flipCard = () => {
    setFlipped(!flipped);
  };

  const resetCards = () => {
    setCurrentIndex(0);
    setFlipped(false);
  };

  // If there's an error
  if (error) {
    return (
      <Card className="p-6 text-center">
        <div className="flex flex-col items-center justify-center p-6 text-red-500">
          <AlertCircle className="h-12 w-12 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Error Loading Flashcards</h3>
          <p className="text-slate-600 dark:text-slate-400 mb-4">{error}</p>
          <Button 
            variant="outline" 
            onClick={() => window.location.reload()}
            className="mt-2"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </div>
      </Card>
    );
  }

  // Loading state
  if (loading) {
    return (
      <Card className="p-6 text-center">
        <div className="flex flex-col items-center justify-center p-6">
          <Loader2 className="h-12 w-12 animate-spin mb-4 text-primary" />
          <p className="text-slate-600 dark:text-slate-400">Generating flashcards...</p>
        </div>
      </Card>
    );
  }

  // If there are no flashcards
  if (flashcards.length === 0) {
    return (
      <Card className="p-6 text-center">
        <div className="flex flex-col items-center justify-center p-6">
          <AlertCircle className="h-12 w-12 mb-4 text-amber-500" />
          <h3 className="text-lg font-semibold mb-2">No Flashcards Available</h3>
          <p className="text-slate-600 dark:text-slate-400">Unable to generate flashcards for this summary.</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold">Study Flashcards</h3>
        <div className="text-sm text-slate-500">
          Card {currentIndex + 1} of {flashcards.length}
        </div>
      </div>
      
      {/* Simple card with toggle instead of 3D flip */}
      <Card 
        className="h-64 cursor-pointer"
        onClick={flipCard}
      >
        {!flipped ? (
          <CardContent className="p-6 h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-xl font-medium">{flashcards[currentIndex]?.front}</p>
              <p className="mt-4 text-sm text-slate-500">Click to reveal answer</p>
            </div>
          </CardContent>
        ) : (
          <CardContent className="p-6 h-full flex items-center justify-center bg-slate-50 dark:bg-slate-900">
            <div className="text-center">
              <p className="text-xl">{flashcards[currentIndex]?.back}</p>
              <p className="mt-4 text-sm text-slate-500">Click to see question</p>
            </div>
          </CardContent>
        )}
      </Card>
      
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={prevCard}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>
        
        <Button
          variant="outline"
          onClick={resetCards}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset
        </Button>
        
        <Button
          variant="outline"
          onClick={nextCard}
          disabled={currentIndex === flashcards.length - 1}
        >
          Next
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}


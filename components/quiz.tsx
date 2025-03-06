"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { CheckCircle, XCircle, RefreshCw, AlertCircle, Loader2 } from "lucide-react"

interface QuizQuestion {
  id?: number
  question: string
  options: string[]
  correctAnswer: number
}

interface QuizProps {
  summary: string
}

export function Quiz({ summary }: QuizProps) {
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const [isAnswered, setIsAnswered] = useState(false)
  const [score, setScore] = useState(0)
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Generate quiz questions from the summary using our API
    const generateQuiz = async () => {
      setLoading(true)
      setError(null)
      
      try {
        console.log("Generating quiz for summary:", summary.substring(0, 50) + "...");
        
        const response = await fetch('/api/generate-quiz', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            summary,
            numQuestions: 5
          }),
        });
        
        console.log("Quiz API response status:", response.status);
        
        if (!response.ok) {
          const errorData = await response.json();
          console.error("Quiz API error:", errorData);
          throw new Error(errorData.error || 'Failed to generate quiz questions');
        }
        
        const data = await response.json();
        console.log("Quiz data received:", data);
        
        if (!data.questions || !Array.isArray(data.questions) || data.questions.length === 0) {
          console.error("Invalid quiz data format:", data);
          throw new Error('Received invalid quiz data format');
        }
        
        // Add IDs to the questions if they don't have them
        const questionsWithIds = data.questions.map((q: QuizQuestion, index: number) => ({
          ...q,
          id: q.id || index + 1
        }));
        
        setQuestions(questionsWithIds);
      } catch (err) {
        console.error('Error generating quiz:', err);
        setError(err instanceof Error ? err.message : 'Failed to generate quiz. Please try again.');
        
        // Fallback to no questions if the API call fails
        setQuestions([]);
      } finally {
        setLoading(false);
      }
    }

    if (summary) {
      generateQuiz();
    }
  }, [summary]);

  const handleOptionSelect = (index: number) => {
    if (!isAnswered) {
      setSelectedOption(index);
    }
  };

  const checkAnswer = () => {
    if (selectedOption !== null) {
      setIsAnswered(true);
      if (selectedOption === questions[currentQuestion].correctAnswer) {
        setScore(score + 1);
      }
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedOption(null);
      setIsAnswered(false);
    } else {
      setQuizCompleted(true);
    }
  };

  const restartQuiz = () => {
    setCurrentQuestion(0);
    setSelectedOption(null);
    setIsAnswered(false);
    setScore(0);
    setQuizCompleted(false);
  };

  // If there's an error
  if (error) {
    return (
      <Card className="p-6 text-center">
        <div className="flex flex-col items-center justify-center p-6 text-red-500">
          <AlertCircle className="h-12 w-12 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Error Loading Quiz</h3>
          <p className="text-slate-600 dark:text-slate-400 mb-4">{error}</p>
          <Button 
            variant="outline" 
            onClick={() => window.location.reload()}
            className="mt-2"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
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
          <p className="text-slate-600 dark:text-slate-400">Generating quiz questions...</p>
        </div>
      </Card>
    );
  }

  // If there are no questions
  if (questions.length === 0) {
    return (
      <Card className="p-6 text-center">
        <div className="flex flex-col items-center justify-center p-6">
          <AlertCircle className="h-12 w-12 mb-4 text-amber-500" />
          <h3 className="text-lg font-semibold mb-2">No Questions Available</h3>
          <p className="text-slate-600 dark:text-slate-400">Unable to generate quiz questions for this summary.</p>
        </div>
      </Card>
    );
  }

  // Quiz completed view
  if (quizCompleted) {
    const percentage = Math.round((score / questions.length) * 100);
    
    return (
      <Card>
        <CardContent className="pt-6 flex flex-col items-center text-center">
          {percentage >= 70 ? (
            <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
          ) : (
            <XCircle className="h-12 w-12 text-amber-500 mb-4" />
          )}
          
          <h3 className="text-xl font-bold mb-2">Quiz Completed!</h3>
          <p className="text-3xl font-bold mb-2 text-primary">
            {score} / {questions.length}
          </p>
          <p className="text-lg mb-6">{percentage}% Correct</p>
          
          {percentage >= 90 ? (
            <p className="mb-6">Excellent! You have a strong understanding of the content.</p>
          ) : percentage >= 70 ? (
            <p className="mb-6">Good job! You understood most of the key concepts.</p>
          ) : percentage >= 50 ? (
            <p className="mb-6">You're on the right track, but might want to review some concepts.</p>
          ) : (
            <p className="mb-6">You should review the summary again to better understand the material.</p>
          )}
          
          <Button onClick={restartQuiz}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Restart Quiz
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Current question view
  const currentQ = questions[currentQuestion];
  
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="mb-4 text-sm font-medium text-slate-500 dark:text-slate-400">
          Question {currentQuestion + 1} of {questions.length}
        </div>
        
        <h3 className="text-xl font-semibold mb-6">{currentQ.question}</h3>
        
        <RadioGroup value={selectedOption?.toString()} className="space-y-3">
          {currentQ.options.map((option, index) => (
            <div
              key={index}
              className={`flex items-start space-x-2 p-3 border rounded-md cursor-pointer transition-colors ${
                isAnswered
                  ? index === currentQ.correctAnswer
                    ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                    : index === selectedOption
                    ? "border-red-500 bg-red-50 dark:bg-red-900/20"
                    : "border-slate-200 dark:border-slate-800"
                  : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
              }`}
              onClick={() => handleOptionSelect(index)}
            >
              <RadioGroupItem
                value={index.toString()}
                id={`option-${index}`}
                disabled={isAnswered}
                className="mt-1"
              />
              <div className="flex-1">
                <Label
                  htmlFor={`option-${index}`}
                  className={`font-medium ${
                    isAnswered && index === currentQ.correctAnswer
                      ? "text-green-700 dark:text-green-400"
                      : isAnswered && index === selectedOption
                      ? "text-red-700 dark:text-red-400"
                      : ""
                  }`}
                >
                  {option}
                </Label>
              </div>
              {isAnswered && index === currentQ.correctAnswer && (
                <CheckCircle className="h-5 w-5 text-green-500 shrink-0" />
              )}
              {isAnswered && index === selectedOption && index !== currentQ.correctAnswer && (
                <XCircle className="h-5 w-5 text-red-500 shrink-0" />
              )}
            </div>
          ))}
        </RadioGroup>
      </CardContent>
      
      <CardFooter className="flex justify-between border-t p-4">
        <div className="flex-1">
          {isAnswered && (
            <div className={selectedOption === currentQ.correctAnswer ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}>
              {selectedOption === currentQ.correctAnswer ? (
                <span className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Correct!
                </span>
              ) : (
                <span className="flex items-center">
                  <XCircle className="h-4 w-4 mr-2" />
                  Incorrect
                </span>
              )}
            </div>
          )}
        </div>
        
        <div>
          {!isAnswered ? (
            <Button 
              onClick={checkAnswer} 
              disabled={selectedOption === null}
            >
              Check Answer
            </Button>
          ) : (
            <Button onClick={nextQuestion}>
              {currentQuestion < questions.length - 1 ? "Next Question" : "Finish Quiz"}
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}


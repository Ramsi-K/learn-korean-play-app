import React, { useState, useEffect } from 'react';
import { Gamepad2, Play, RotateCcw, Trophy, Clock, Target, Loader2, AlertCircle } from 'lucide-react';
import { getWords, type WordResponse } from '../../services/api';

interface GameStats {
  score: number;
  correct: number;
  incorrect: number;
  timeRemaining: number;
}

interface GameState {
  isPlaying: boolean;
  currentWordIndex: number;
  userAnswer: string;
  showResult: boolean;
  resultCorrect: boolean;
  gameWords: WordResponse[];
  stats: GameStats;
  gameComplete: boolean;
}

const GAME_DURATION = 60; // 60 seconds
const WORDS_PER_GAME = 10;

const Arcade: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<GameState>({
    isPlaying: false,
    currentWordIndex: 0,
    userAnswer: '',
    showResult: false,
    resultCorrect: false,
    gameWords: [],
    stats: {
      score: 0,
      correct: 0,
      incorrect: 0,
      timeRemaining: GAME_DURATION,
    },
    gameComplete: false,
  });

  // Timer effect
  useEffect(() => {
    let timer: NodeJS.Timeout;
    
    if (gameState.isPlaying && gameState.stats.timeRemaining > 0 && !gameState.gameComplete) {
      timer = setInterval(() => {
        setGameState(prev => {
          const newTimeRemaining = prev.stats.timeRemaining - 1;
          if (newTimeRemaining <= 0) {
            return {
              ...prev,
              isPlaying: false,
              gameComplete: true,
              stats: { ...prev.stats, timeRemaining: 0 }
            };
          }
          return {
            ...prev,
            stats: { ...prev.stats, timeRemaining: newTimeRemaining }
          };
        });
      }, 1000);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [gameState.isPlaying, gameState.stats.timeRemaining, gameState.gameComplete]);

  const startGame = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch random words for the game
      const allWords = await getWords(0, 100); // Get more words to randomize from
      
      if (allWords.length === 0) {
        setError('No words available. Make sure the database is seeded.');
        return;
      }

      // Shuffle and select words for the game
      const shuffled = [...allWords].sort(() => Math.random() - 0.5);
      const gameWords = shuffled.slice(0, Math.min(WORDS_PER_GAME, shuffled.length));

      setGameState({
        isPlaying: true,
        currentWordIndex: 0,
        userAnswer: '',
        showResult: false,
        resultCorrect: false,
        gameWords,
        stats: {
          score: 0,
          correct: 0,
          incorrect: 0,
          timeRemaining: GAME_DURATION,
        },
        gameComplete: false,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start game');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = () => {
    if (!gameState.userAnswer.trim()) return;

    const currentWord = gameState.gameWords[gameState.currentWordIndex];
    const userAnswerLower = gameState.userAnswer.toLowerCase().trim();
    const correctAnswerLower = currentWord.english.toLowerCase();
    
    // Check if the answer is correct (allow partial matches)
    const isCorrect = correctAnswerLower.includes(userAnswerLower) || 
                     userAnswerLower.includes(correctAnswerLower);

    const newScore = isCorrect ? gameState.stats.score + 10 : gameState.stats.score;
    const newCorrect = isCorrect ? gameState.stats.correct + 1 : gameState.stats.correct;
    const newIncorrect = isCorrect ? gameState.stats.incorrect : gameState.stats.incorrect + 1;

    setGameState(prev => ({
      ...prev,
      showResult: true,
      resultCorrect: isCorrect,
      stats: {
        ...prev.stats,
        score: newScore,
        correct: newCorrect,
        incorrect: newIncorrect,
      }
    }));

    // Auto-advance after showing result
    setTimeout(() => {
      nextWord();
    }, 2000);
  };

  const nextWord = () => {
    const nextIndex = gameState.currentWordIndex + 1;
    
    if (nextIndex >= gameState.gameWords.length) {
      // Game complete
      setGameState(prev => ({
        ...prev,
        isPlaying: false,
        gameComplete: true,
        showResult: false,
      }));
    } else {
      setGameState(prev => ({
        ...prev,
        currentWordIndex: nextIndex,
        userAnswer: '',
        showResult: false,
        resultCorrect: false,
      }));
    }
  };

  const resetGame = () => {
    setGameState({
      isPlaying: false,
      currentWordIndex: 0,
      userAnswer: '',
      showResult: false,
      resultCorrect: false,
      gameWords: [],
      stats: {
        score: 0,
        correct: 0,
        incorrect: 0,
        timeRemaining: GAME_DURATION,
      },
      gameComplete: false,
    });
    setError(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !gameState.showResult) {
      submitAnswer();
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };

  const currentWord = gameState.gameWords[gameState.currentWordIndex];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Gamepad2 className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Arcade</h1>
          <p className="text-muted-foreground">Play games to learn Korean in a fun way</p>
        </div>
      </div>

      {error && (
        <div className="flex items-center p-4 bg-destructive/20 text-destructive rounded-lg">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {!gameState.isPlaying && !gameState.gameComplete && (
        <div className="text-center space-y-6">
          <div className="p-8 border border-border rounded-lg">
            <h2 className="text-2xl font-bold mb-4">Guess the Word</h2>
            <p className="text-muted-foreground mb-6">
              You'll see Korean words and need to type their English translation. 
              You have {GAME_DURATION} seconds to answer as many as possible!
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-sm">
              <div className="flex items-center justify-center space-x-2 p-3 bg-accent/20 rounded-lg">
                <Clock className="h-4 w-4" />
                <span>{GAME_DURATION} seconds</span>
              </div>
              <div className="flex items-center justify-center space-x-2 p-3 bg-accent/20 rounded-lg">
                <Target className="h-4 w-4" />
                <span>Up to {WORDS_PER_GAME} words</span>
              </div>
              <div className="flex items-center justify-center space-x-2 p-3 bg-accent/20 rounded-lg">
                <Trophy className="h-4 w-4" />
                <span>10 points per correct answer</span>
              </div>
            </div>

            <button
              onClick={startGame}
              disabled={loading}
              className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center space-x-2 mx-auto"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Loading...</span>
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  <span>Start Game</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {gameState.isPlaying && currentWord && (
        <div className="space-y-6">
          {/* Game Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-accent/20 rounded-lg text-center">
              <div className="text-2xl font-bold">{gameState.stats.score}</div>
              <div className="text-sm text-muted-foreground">Score</div>
            </div>
            <div className="p-3 bg-accent/20 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-500">{gameState.stats.correct}</div>
              <div className="text-sm text-muted-foreground">Correct</div>
            </div>
            <div className="p-3 bg-accent/20 rounded-lg text-center">
              <div className="text-2xl font-bold text-red-500">{gameState.stats.incorrect}</div>
              <div className="text-sm text-muted-foreground">Incorrect</div>
            </div>
            <div className="p-3 bg-accent/20 rounded-lg text-center">
              <div className={`text-2xl font-bold ${gameState.stats.timeRemaining <= 10 ? 'text-red-500' : ''}`}>
                {formatTime(gameState.stats.timeRemaining)}
              </div>
              <div className="text-sm text-muted-foreground">Time</div>
            </div>
          </div>

          {/* Game Area */}
          <div className="text-center space-y-6 p-8 border border-border rounded-lg">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Word {gameState.currentWordIndex + 1} of {gameState.gameWords.length}
              </p>
              <h2 className="text-6xl font-bold">{currentWord.korean}</h2>
              {currentWord.romanization && (
                <p className="text-xl text-muted-foreground">{currentWord.romanization}</p>
              )}
            </div>

            {gameState.showResult ? (
              <div className={`p-4 rounded-lg ${gameState.resultCorrect ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                <p className="text-xl font-bold">
                  {gameState.resultCorrect ? 'Correct!' : 'Incorrect'}
                </p>
                <p className="text-lg">Answer: {currentWord.english}</p>
              </div>
            ) : (
              <div className="space-y-4">
                <input
                  type="text"
                  value={gameState.userAnswer}
                  onChange={(e) => setGameState(prev => ({ ...prev, userAnswer: e.target.value }))}
                  onKeyPress={handleKeyPress}
                  placeholder="Type the English translation..."
                  className="w-full max-w-md mx-auto px-4 py-3 text-lg text-center border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  autoFocus
                />
                <button
                  onClick={submitAnswer}
                  disabled={!gameState.userAnswer.trim()}
                  className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  Submit Answer
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {gameState.gameComplete && (
        <div className="text-center space-y-6">
          <div className="p-8 border border-border rounded-lg">
            <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Game Complete!</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-accent/20 rounded-lg">
                <div className="text-3xl font-bold text-primary">{gameState.stats.score}</div>
                <div className="text-muted-foreground">Final Score</div>
              </div>
              <div className="p-4 bg-accent/20 rounded-lg">
                <div className="text-3xl font-bold text-green-500">{gameState.stats.correct}</div>
                <div className="text-muted-foreground">Correct Answers</div>
              </div>
              <div className="p-4 bg-accent/20 rounded-lg">
                <div className="text-3xl font-bold">
                  {gameState.stats.correct > 0 ? Math.round((gameState.stats.correct / (gameState.stats.correct + gameState.stats.incorrect)) * 100) : 0}%
                </div>
                <div className="text-muted-foreground">Accuracy</div>
              </div>
            </div>

            <button
              onClick={resetGame}
              className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center space-x-2 mx-auto"
            >
              <RotateCcw className="h-5 w-5" />
              <span>Play Again</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Arcade;
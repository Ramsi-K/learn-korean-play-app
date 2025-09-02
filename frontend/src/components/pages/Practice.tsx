import React, { useState, useEffect } from 'react';
import { Book, Play, Loader2, AlertCircle, ChevronRight, X } from 'lucide-react';
import { getWords, generatePracticeContent, type WordResponse, type PracticeResponse } from '../../services/api';

interface PracticeModalProps {
  word: WordResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

const PracticeModal: React.FC<PracticeModalProps> = ({ word, isOpen, onClose }) => {
  const [practiceContent, setPracticeContent] = useState<PracticeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && word) {
      generatePractice();
    }
  }, [isOpen, word]);

  const generatePractice = async () => {
    if (!word) return;
    
    setLoading(true);
    setError(null);
    setPracticeContent(null);

    try {
      const response = await generatePracticeContent(word.id);
      setPracticeContent(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate practice content');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-background border border-border rounded-lg w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">AI Practice</h2>
            <button 
              onClick={onClose}
              className="p-2 rounded-full hover:bg-accent/30 transition-colors"
              aria-label="Close practice modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          {word && (
            <div className="mb-6 p-4 bg-accent/20 rounded-lg">
              <h3 className="text-xl font-bold mb-2">{word.korean}</h3>
              {word.romanization && (
                <p className="text-sm text-muted-foreground mb-1">{word.romanization}</p>
              )}
              <p className="text-lg">{word.english}</p>
              {word.topik_level && (
                <p className="text-sm text-muted-foreground mt-2">TOPIK Level: {word.topik_level}</p>
              )}
            </div>
          )}

          <div className="space-y-4">
            {loading && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin mr-2" />
                <span>Generating practice content...</span>
              </div>
            )}

            {error && (
              <div className="flex items-center p-4 bg-destructive/20 text-destructive rounded-lg">
                <AlertCircle className="h-5 w-5 mr-2" />
                <span>{error}</span>
              </div>
            )}

            {practiceContent && (
              <div className="space-y-4">
                <div className="p-4 bg-primary/10 rounded-lg">
                  <h4 className="font-semibold mb-2 capitalize">{practiceContent.type} Practice</h4>
                  <div className="prose prose-sm max-w-none">
                    <p className="whitespace-pre-wrap">{practiceContent.content}</p>
                  </div>
                </div>
                
                <button
                  onClick={generatePractice}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  Generate New Practice Content
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const Practice: React.FC = () => {
  const [words, setWords] = useState<WordResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    loadWords();
  }, []);

  const loadWords = async () => {
    try {
      setLoading(true);
      setError(null);
      const wordsData = await getWords(0, 50); // Load first 50 words
      setWords(wordsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load words');
    } finally {
      setLoading(false);
    }
  };

  const handlePracticeClick = (word: WordResponse) => {
    setSelectedWord(word);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedWord(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Book className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Word Practice</h1>
          <p className="text-muted-foreground">Practice Korean words with AI-powered exercises</p>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin mr-2" />
          <span>Loading words...</span>
        </div>
      )}

      {error && (
        <div className="flex items-center p-4 bg-destructive/20 text-destructive rounded-lg">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
          <button 
            onClick={loadWords}
            className="ml-auto px-3 py-1 bg-destructive text-destructive-foreground rounded text-sm hover:bg-destructive/90"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && words.length === 0 && (
        <div className="text-center py-12">
          <Book className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No words found. Make sure the database is seeded.</p>
        </div>
      )}

      {!loading && !error && words.length > 0 && (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Found {words.length} words. Click "Practice" to generate AI-powered exercises.
          </p>
          
          <div className="grid gap-4">
            {words.map((word) => (
              <div 
                key={word.id} 
                className="p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-bold">{word.korean}</h3>
                      {word.topik_level && (
                        <span className="px-2 py-1 bg-primary/20 text-primary text-xs rounded-full">
                          TOPIK {word.topik_level}
                        </span>
                      )}
                    </div>
                    {word.romanization && (
                      <p className="text-sm text-muted-foreground mb-1">{word.romanization}</p>
                    )}
                    <p className="text-lg mb-2">{word.english}</p>
                    {word.part_of_speech && (
                      <p className="text-sm text-muted-foreground">
                        Part of speech: {word.part_of_speech}
                      </p>
                    )}
                  </div>
                  
                  <button
                    onClick={() => handlePracticeClick(word)}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                  >
                    <Play className="h-4 w-4" />
                    <span>Practice</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <PracticeModal 
        word={selectedWord}
        isOpen={modalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default Practice;
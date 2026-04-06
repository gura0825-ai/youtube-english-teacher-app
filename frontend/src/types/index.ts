export interface QuizOptions {
  A: string;
  B: string;
  C: string;
  D: string;
}

export interface QuizItem {
  id: number;
  question: string;
  options: QuizOptions;
  answer: string;
}

export interface ProcessResponse {
  video_id: string;
  title: string;
  transcript: string;
  summary: string;
  insights: string[];
  quiz: QuizItem[];
}

export type AppPhase = 'idle' | 'loading' | 'done' | 'error';

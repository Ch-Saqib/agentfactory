export interface QuizSubmitRequest {
  chapter_slug: string;
  score_pct: number;
  questions_correct: number;
  questions_total: number;
  duration_secs?: number;
}

export interface BadgeEarned {
  id: string;
  name: string;
  earned_at: string;
}

export interface StreakInfo {
  current: number;
  longest: number;
}

export interface QuizSubmitResponse {
  xp_earned: number;
  total_xp: number;
  attempt_number: number;
  best_score: number;
  new_badges: BadgeEarned[];
  streak: StreakInfo;
}

export interface LessonCompleteRequest {
  chapter_slug: string;
  lesson_slug: string;
  active_duration_secs?: number;
}

export interface LessonCompleteResponse {
  completed: boolean;
  active_duration_secs: number;
  streak: StreakInfo;
  already_completed: boolean;
  xp_earned: number;
}

export interface FlashcardCompleteRequest {
  deck_id: string;
  chapter_slug: string;
  cards_correct: number;
  cards_total: number;
}

export interface FlashcardCompleteResponse {
  xp_earned: number;
  total_xp: number;
  is_first_completion: boolean;
  score_pct: number;
  streak: StreakInfo;
  new_badges: BadgeEarned[];
}

export interface ProgressResponse {
  user: { display_name: string; avatar_url: string | null };
  stats: {
    total_xp: number;
    rank: number | null;
    current_streak: number;
    longest_streak: number;
    quizzes_completed: number;
    perfect_scores: number;
    lessons_completed: number;
    flashcards_completed: number;
    badge_count: number;
  };
  badges: BadgeEarned[];
  chapters: Array<{
    slug: string;
    title: string;
    best_score: number | null;
    attempts: number;
    xp_earned: number;
    lessons_completed: Array<{
      lesson_slug: string;
      active_duration_secs: number;
      completed_at: string;
    }>;
  }>;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  total_xp: number;
  badge_count: number;
  badge_ids: string[];
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
  current_user_rank: number | null;
  total_users: number;
}

export interface BadgeDefinition {
  id: string;
  name: string;
  description: string;
  icon: string;
}

// Daily Challenges
export interface ChallengeProgress {
  current: number;
  target: number;
  unit: string;
}

export interface ChallengeResponse {
  id: number;
  challenge_date: string;
  challenge_type: string;
  title: string;
  description: string;
  config: Record<string, unknown>;
  xp_bonus: number;
  progress: ChallengeProgress;
  completed: boolean;
  started_at: string | null;
}

export interface ChallengeHistoryItem {
  id: number;
  challenge_date: string;
  title: string;
  completed: boolean;
  xp_awarded: number;
  completed_at: string | null;
}

export interface ChallengeHistoryResponse {
  challenges: ChallengeHistoryItem[];
}

export interface ChallengeProgressUpdate {
  progress_delta: number;
}

export interface ChallengeCompleteResponse {
  xp_earned: number;
  total_xp: number;
  new_badges: Array<Record<string, unknown>>;
  streak: Record<string, number>;
}

// Achievement Roadmap
export interface RoadmapNodeResponse {
  id: string;
  parent_id: string | null;
  node_type: string; // 'part', 'chapter', 'milestone'
  title: string;
  description: string | null;
  position_x: number;
  position_y: number;
  config: Record<string, unknown>;
  required_xp: number;
  icon: string | null;
  unlocked: boolean;
  unlocked_at: string | null;
  locked: boolean;
}

export interface RoadmapEdge {
  id: string;
  source: string;
  target: string;
  animated: boolean;
}

export interface RoadmapResponse {
  nodes: RoadmapNodeResponse[];
  edges: RoadmapEdge[];
  user_xp: number;
  unlocked_count: number;
  total_count: number;
}

export interface RoadmapSyncResponse {
  new_unlocks: string[];
  total_unlocked: number;
  total_nodes: number;
}

// Study Buddies (Friends)
export interface FriendActivity {
  activity_type: string;
  activity_ref: string;
  completed_at: string;
}

export interface FriendInfo {
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  total_xp: number;
  current_streak: number;
  last_activity: FriendActivity | null;
  friendship_status: "accepted";
}

export interface FriendListResponse {
  friends: FriendInfo[];
  pending_requests: FriendInfo[];
  sent_requests: FriendInfo[];
}

export interface FriendsLeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  total_xp: number;
  badge_count: number;
  current_streak: number;
  is_you: boolean;
}

export interface FriendsLeaderboardResponse {
  entries: FriendsLeaderboardEntry[];
  your_rank: number | null;
}

export interface BuddyXpCheckResponse {
  eligible: boolean;
  buddy_xp: number;
  friend_names: string[];
}

// Knowledge Checkpoints
export interface CheckpointQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

export interface CheckpointResponse {
  id: number;
  lesson_slug: string;
  position_pct: number;
  question: CheckpointQuestion;
  xp_bonus: number;
}

export interface CheckpointAnswerRequest {
  checkpoint_id: number;
  answer: number;
}

export interface CheckpointAnswerResponse {
  correct: boolean;
  explanation: string;
  correct_answer: number;
  xp_awarded: number;
  total_xp: number;
}

// Smart Review
export interface ReviewItem {
  id: number;
  chapter_slug: string;
  priority: string; // 'high', 'medium', 'low'
  reason: string; // 'weak_area', 'spaced_repetition', 'prerequisite'
  due_date: string;
  interval_days: number;
}

export interface ReviewQueueResponse {
  items: ReviewItem[];
  total_count: number;
  high_priority_count: number;
}

export interface ReviewCompleteRequest {
  score_pct: number;
}

export interface ReviewCompleteResponse {
  interval_days: number;
  next_due_date: string;
  message: string;
}

/** All badge definitions (mirrors backend BADGE_DEFINITIONS). */
export const BADGE_DEFINITIONS: Record<string, BadgeDefinition> = {
  "first-steps": {
    id: "first-steps",
    name: "First Steps",
    description: "Complete your first quiz",
    icon: "\uD83C\uDFAF",
  },
  "perfect-score": {
    id: "perfect-score",
    name: "Perfect Score",
    description: "Score 100% on any quiz",
    icon: "\u2B50",
  },
  ace: {
    id: "ace",
    name: "Ace",
    description: "Score 100% on your first attempt",
    icon: "\uD83C\uDFC6",
  },
  "on-fire": {
    id: "on-fire",
    name: "On Fire",
    description: "3-day learning streak",
    icon: "\uD83D\uDD25",
  },
  "week-warrior": {
    id: "week-warrior",
    name: "Week Warrior",
    description: "7-day learning streak",
    icon: "\uD83D\uDCAA",
  },
  dedicated: {
    id: "dedicated",
    name: "Dedicated",
    description: "30-day learning streak",
    icon: "\uD83C\uDF96\uFE0F",
  },
  "foundations-complete": {
    id: "foundations-complete",
    name: "Foundations",
    description: "Complete all Part 1 quizzes",
    icon: "\uD83D\uDCDA",
  },
  "workflows-complete": {
    id: "workflows-complete",
    name: "Applied",
    description: "Complete all Part 2 quizzes",
    icon: "\uD83D\uDEE0\uFE0F",
  },
  "sdd-complete": {
    id: "sdd-complete",
    name: "SDD Master",
    description: "Complete all Part 3 quizzes",
    icon: "\uD83D\uDCCB",
  },
  "coding-complete": {
    id: "coding-complete",
    name: "Coder",
    description: "Complete all Part 4 quizzes",
    icon: "\uD83D\uDCBB",
  },
  "deployment-complete": {
    id: "deployment-complete",
    name: "Agent Builder",
    description: "Complete all Part 5 quizzes",
    icon: "\uD83E\uDD16",
  },
  "cloud-native-complete": {
    id: "cloud-native-complete",
    name: "Cloud Native",
    description: "Complete all Part 6 quizzes",
    icon: "\u2601\uFE0F",
  },
  "agent-factory-graduate": {
    id: "agent-factory-graduate",
    name: "Agent Factory Graduate",
    description: "Complete all quizzes in the book",
    icon: "\uD83C\uDF93",
  },
  elite: {
    id: "elite",
    name: "Elite",
    description: "Reach top 100 on leaderboard",
    icon: "\uD83D\uDC51",
  },
  "first-deck": {
    id: "first-deck",
    name: "Memory Lane",
    description: "Complete your first flashcard deck",
    icon: "\uD83C\uDCCF",
  },
  "deck-master-10": {
    id: "deck-master-10",
    name: "Deck Master",
    description: "Complete 10 unique flashcard decks",
    icon: "\uD83C\uDFC5",
  },
  "perfect-recall": {
    id: "perfect-recall",
    name: "Total Recall",
    description: "Score 100% on any flashcard deck",
    icon: "\uD83E\uDDE0",
  },
};

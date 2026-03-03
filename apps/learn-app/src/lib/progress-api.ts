import type {
  BuddyXpCheckResponse,
  ChallengeCompleteResponse,
  ChallengeHistoryResponse,
  ChallengeProgressUpdate,
  ChallengeResponse,
  CheckpointAnswerRequest,
  CheckpointAnswerResponse,
  CheckpointResponse,
  FlashcardCompleteRequest,
  FlashcardCompleteResponse,
  FriendListResponse,
  FriendsLeaderboardResponse,
  LeaderboardResponse,
  LessonCompleteRequest,
  LessonCompleteResponse,
  ProgressResponse,
  QuizSubmitRequest,
  QuizSubmitResponse,
  ReviewCompleteRequest,
  ReviewCompleteResponse,
  ReviewQueueResponse,
  RoadmapResponse,
  RoadmapSyncResponse,
} from "./progress-types";
import { getAuthHeaders } from "./api-utils";

export async function submitQuizScore(
  baseUrl: string,
  data: QuizSubmitRequest,
): Promise<QuizSubmitResponse> {
  const response = await fetch(`${baseUrl}/api/v1/quiz/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Quiz submit failed: ${response.status}`);
  }
  return response.json();
}

export async function completeLesson(
  baseUrl: string,
  data: LessonCompleteRequest,
): Promise<LessonCompleteResponse> {
  const response = await fetch(`${baseUrl}/api/v1/lesson/complete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Lesson complete failed: ${response.status}`);
  }
  return response.json();
}

export async function completeFlashcardSession(
  baseUrl: string,
  data: FlashcardCompleteRequest,
): Promise<FlashcardCompleteResponse> {
  const response = await fetch(`${baseUrl}/api/v1/flashcard/complete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Flashcard complete failed: ${response.status}`);
  }
  return response.json();
}

export async function getProgress(baseUrl: string): Promise<ProgressResponse> {
  const response = await fetch(`${baseUrl}/api/v1/progress/me`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get progress failed: ${response.status}`);
  }
  return response.json();
}

export async function getLeaderboard(
  baseUrl: string,
): Promise<LeaderboardResponse> {
  const response = await fetch(`${baseUrl}/api/v1/leaderboard`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get leaderboard failed: ${response.status}`);
  }
  return response.json();
}

export async function updatePreferences(
  baseUrl: string,
  data: { show_on_leaderboard: boolean },
): Promise<void> {
  const response = await fetch(`${baseUrl}/api/v1/progress/me/preferences`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Update preferences failed: ${response.status}`);
  }
}

// Daily Challenges
export async function getTodayChallenge(
  baseUrl: string,
): Promise<ChallengeResponse> {
  const response = await fetch(`${baseUrl}/api/v1/challenges/today`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get today challenge failed: ${response.status}`);
  }
  return response.json();
}

export async function updateChallengeProgress(
  baseUrl: string,
  challengeId: number,
  data: ChallengeProgressUpdate,
): Promise<ChallengeResponse | ChallengeCompleteResponse> {
  const response = await fetch(`${baseUrl}/api/v1/challenges/${challengeId}/progress`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Update challenge progress failed: ${response.status}`);
  }
  return response.json();
}

export async function getChallengeHistory(
  baseUrl: string,
  days: number = 7,
): Promise<ChallengeHistoryResponse> {
  const response = await fetch(`${baseUrl}/api/v1/challenges/history?days=${days}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get challenge history failed: ${response.status}`);
  }
  return response.json();
}

// Achievement Roadmap
export async function getRoadmap(
  baseUrl: string,
): Promise<RoadmapResponse> {
  const response = await fetch(`${baseUrl}/api/v1/roadmap`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get roadmap failed: ${response.status}`);
  }
  return response.json();
}

export async function syncRoadmap(
  baseUrl: string,
): Promise<RoadmapSyncResponse> {
  const response = await fetch(`${baseUrl}/api/v1/roadmap/sync`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Sync roadmap failed: ${response.status}`);
  }
  return response.json();
}

// Study Buddies (Friends)
export async function sendFriendRequest(
  baseUrl: string,
  username: string,
): Promise<{ message: string }> {
  const response = await fetch(`${baseUrl}/api/v1/friends/request`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ username }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Send friend request failed: ${response.status}`);
  }
  return response.json();
}

export async function acceptFriendRequest(
  baseUrl: string,
  requesterId: string,
): Promise<{ message: string }> {
  const response = await fetch(`${baseUrl}/api/v1/friends/accept`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ requester_id: requesterId }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Accept friend request failed: ${response.status}`);
  }
  return response.json();
}

export async function getFriends(
  baseUrl: string,
): Promise<FriendListResponse> {
  const response = await fetch(`${baseUrl}/api/v1/friends`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get friends failed: ${response.status}`);
  }
  return response.json();
}

export async function getFriendsLeaderboard(
  baseUrl: string,
): Promise<FriendsLeaderboardResponse> {
  const response = await fetch(`${baseUrl}/api/v1/friends/leaderboard`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get friends leaderboard failed: ${response.status}`);
  }
  return response.json();
}

export async function checkBuddyXp(
  baseUrl: string,
  activityType: string,
  activityRef: string,
): Promise<BuddyXpCheckResponse> {
  const params = new URLSearchParams({
    activity_type: activityType,
    activity_ref: activityRef,
  });
  const response = await fetch(`${baseUrl}/api/v1/friends/buddy-xp-check?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Check buddy XP failed: ${response.status}`);
  }
  return response.json();
}

// Knowledge Checkpoints
export async function getCheckpoint(
  baseUrl: string,
  lessonSlug: string,
  positionPct: number,
): Promise<CheckpointResponse> {
  const params = new URLSearchParams({
    lesson_slug: lessonSlug,
    position_pct: positionPct.toString(),
  });
  const response = await fetch(`${baseUrl}/api/v1/checkpoints?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get checkpoint failed: ${response.status}`);
  }
  return response.json();
}

export async function submitCheckpointAnswer(
  baseUrl: string,
  data: CheckpointAnswerRequest,
): Promise<CheckpointAnswerResponse> {
  const response = await fetch(`${baseUrl}/api/v1/checkpoints/answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Submit checkpoint answer failed: ${response.status}`);
  }
  return response.json();
}

// Smart Review
export async function getReviewQueue(
  baseUrl: string,
): Promise<ReviewQueueResponse> {
  const response = await fetch(`${baseUrl}/api/v1/review/queue`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Get review queue failed: ${response.status}`);
  }
  return response.json();
}

export async function completeReview(
  baseUrl: string,
  reviewId: number,
  data: ReviewCompleteRequest,
): Promise<ReviewCompleteResponse> {
  const response = await fetch(`${baseUrl}/api/v1/review/${reviewId}/complete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Complete review failed: ${response.status}`);
  }
  return response.json();
}

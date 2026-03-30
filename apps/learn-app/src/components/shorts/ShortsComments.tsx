/**
 * ShortsComments - Slide-up panel for video comments
 *
 * Features:
 * - Slide-up panel from bottom
 * - Threaded replies support
 * - Real-time updates (optional)
 * - Add new comments
 */

import React, { useState, useCallback, useEffect, useRef } from "react";
import { useVideoComments } from "./hooks/useShortsFeed";

interface ShortsCommentsProps {
  /** Video ID to fetch comments for */
  videoId: string;
  /** Whether panel is open */
  isOpen: boolean;
  /** Callback when panel closes */
  onClose: () => void;
}

interface Comment {
  id: string;
  userId: string;
  videoId: string;
  text: string;
  parentId?: string;
  createdAt: string;
  replies?: Comment[];
}

interface CommentItemProps {
  comment: Comment;
  depth?: number;
  onReply?: (commentId: string) => void;
}

function CommentItem({ comment, depth = 0, onReply }: CommentItemProps) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleReply = useCallback(async () => {
    if (!replyText.trim()) return;

    setIsSubmitting(true);
    try {
      // TODO: Submit reply via API
      console.log("Reply:", comment.id, replyText);
      setReplyText("");
      setShowReplyForm(false);
    } finally {
      setIsSubmitting(false);
    }
  }, [comment.id, replyText]);

  const formatDate = useCallback((dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }, []);

  return (
    <div
      className="mb-4"
      style={{ marginLeft: depth > 0 ? `${depth * 1.5}rem` : "0" }}
    >
      {/* Comment Header */}
      <div className="mb-2 flex items-start gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-sm font-semibold text-white">
          {comment.userId[0].toUpperCase()}
        </div>
        <div className="flex-1">
          <div className="mb-1 flex items-center gap-2">
            <span className="text-sm font-semibold text-white">
              {comment.userId}
            </span>
            <span className="text-xs text-gray-400">
              {formatDate(comment.createdAt)}
            </span>
          </div>
          <p className="text-sm text-gray-200">{comment.text}</p>

          {/* Reply Button */}
          {depth < 2 && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="mt-2 text-xs text-gray-400 hover:text-white transition-colors"
            >
              {showReplyForm ? "Cancel" : "Reply"}
            </button>
          )}
        </div>
      </div>

      {/* Reply Form */}
      {showReplyForm && (
        <div className="mt-2 rounded-lg bg-gray-800/50 p-2">
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Write a reply..."
            className="w-full rounded border border-gray-700 bg-transparent px-2 py-1 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            rows={2}
          />
          <div className="mt-2 flex justify-end gap-2">
            <button
              onClick={() => setShowReplyForm(false)}
              className="rounded px-3 py-1 text-xs text-gray-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              onClick={handleReply}
              disabled={!replyText.trim() || isSubmitting}
              className="rounded bg-blue-500 px-3 py-1 text-xs text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? "Sending..." : "Reply"}
            </button>
          </div>
        </div>
      )}

      {/* Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-2 space-y-3">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              depth={depth + 1}
              onReply={onReply}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function ShortsComments({
  videoId,
  isOpen,
  onClose,
}: ShortsCommentsProps) {
  const [newCommentText, setNewCommentText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { comments, loading, error, addComment, loadComments, totalCount } =
    useVideoComments(videoId);

  // Load comments when panel opens
  useEffect(() => {
    if (isOpen && comments.length === 0) {
      loadComments();
    }
  }, [isOpen, videoId, comments.length, loadComments]);

  // Handle adding a new top-level comment
  const handleAddComment = useCallback(async () => {
    if (!newCommentText.trim()) return;

    setIsSubmitting(true);
    try {
      await addComment(newCommentText);
      setNewCommentText("");
    } catch (err) {
      console.error("Failed to add comment:", err);
    } finally {
      setIsSubmitting(false);
    }
  }, [newCommentText, addComment]);

  // Handle escape key to close
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  // Don't render if not open (performance)
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="absolute bottom-0 left-0 right-0 max-h-[70vh] rounded-t-2xl bg-gray-900 shadow-xl transition-all">
        {/* Handle for drag gesture */}
        <div className="flex justify-center py-3">
          <div className="h-1 w-12 rounded-full bg-gray-600" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
          <h2 className="text-lg font-semibold text-white">
            Comments {totalCount > 0 && `(${totalCount})`}
          </h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-800 text-white hover:bg-gray-700"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-4" style={{ maxHeight: "calc(70vh - 120px)" }}>
          {/* Loading State */}
          {loading && comments.length === 0 && (
            <div className="flex justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-white border-t-transparent" />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="mb-4 rounded-lg bg-red-500/20 p-3 text-center text-red-200">
              Failed to load comments.{" "}
              <button onClick={loadComments} className="underline">
                Retry
              </button>
            </div>
          )}

          {/* Comments List */}
          {comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              onReply={(commentId) => {
                console.log("Reply to:", commentId);
                // TODO: Scroll to reply form
              }}
            />
          ))}

          {/* Empty State */}
          {!loading && comments.length === 0 && (
            <div className="py-8 text-center text-gray-400">
              <p className="text-lg">No comments yet</p>
              <p className="text-sm">Be the first to comment!</p>
            </div>
          )}
        </div>

        {/* Add Comment Form */}
        <div className="border-t border-gray-800 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={newCommentText}
              onChange={(e) => setNewCommentText(e.target.value)}
              placeholder="Add a comment..."
              className="flex-1 rounded-full border border-gray-700 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAddComment();
                }
              }}
            />
            <button
              onClick={handleAddComment}
              disabled={!newCommentText.trim() || isSubmitting}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500 text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                "↑"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from "react";
import {
  deleteMyProfile,
  gdprEraseMyProfile,
} from "@/lib/learner-profile-api";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

export function DangerZone() {
  const { siteConfig } = useDocusaurusContext();
  const apiUrl =
    (siteConfig.customFields?.learnerProfileApiUrl as string) ||
    "http://localhost:8004";
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showGdprConfirm, setShowGdprConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteMyProfile(apiUrl);
      window.location.href = "/";
    } catch (err) {
      console.error("Delete failed:", err);
      setIsDeleting(false);
    }
  };

  const handleGdprErase = async () => {
    setIsDeleting(true);
    try {
      await gdprEraseMyProfile(apiUrl);
      window.location.href = "/";
    } catch (err) {
      console.error("GDPR erase failed:", err);
      setIsDeleting(false);
    }
  };

  return (
    <div className="rounded-lg border border-destructive/30 bg-card p-6 mt-8">
      <h3 className="text-lg font-semibold text-destructive mb-2">
        Danger Zone
      </h3>
      <p className="text-sm text-muted-foreground mb-4">
        These actions cannot be undone.
      </p>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">Delete Profile</div>
            <div className="text-xs text-muted-foreground">
              Soft delete — can be recovered within 30 days
            </div>
          </div>
          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-3 py-1.5 text-sm rounded-md border border-destructive text-destructive hover:bg-destructive/10"
            >
              Delete
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-3 py-1.5 text-sm rounded-md border border-border text-muted-foreground hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-3 py-1.5 text-sm rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isDeleting ? "Deleting..." : "Confirm Delete"}
              </button>
            </div>
          )}
        </div>
        <div className="border-t border-border pt-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium">Erase All Data (GDPR)</div>
              <div className="text-xs text-muted-foreground">
                Permanently erase all profile data. This cannot be undone.
              </div>
            </div>
            {!showGdprConfirm ? (
              <button
                onClick={() => setShowGdprConfirm(true)}
                className="px-3 py-1.5 text-sm rounded-md border border-destructive text-destructive hover:bg-destructive/10"
              >
                GDPR Erase
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => setShowGdprConfirm(false)}
                  disabled={isDeleting}
                  className="px-3 py-1.5 text-sm rounded-md border border-border text-muted-foreground hover:bg-accent"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGdprErase}
                  disabled={isDeleting}
                  className="px-3 py-1.5 text-sm rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  {isDeleting ? "Erasing..." : "Confirm Erase"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

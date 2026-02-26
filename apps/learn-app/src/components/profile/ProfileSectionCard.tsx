import React, { useState } from "react";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";
import type { SectionName, ProfileResponse } from "@/lib/learner-profile-types";
import { SECTION_CONFIGS } from "@/lib/learner-profile-types";

interface ProfileSectionCardProps {
  section: SectionName;
  ViewComponent: React.ComponentType<{ data: unknown }>;
  EditComponent: React.ComponentType<{
    data: unknown;
    onChange: (data: unknown) => void;
  }>;
}

export function ProfileSectionCard({
  section,
  ViewComponent,
  EditComponent,
}: ProfileSectionCardProps) {
  const { profile, updateSection } = useLearnerProfile();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<unknown>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const config = SECTION_CONFIGS[section];
  const sectionData = profile?.[section as keyof ProfileResponse];

  const handleEdit = () => {
    setEditData(JSON.parse(JSON.stringify(sectionData)));
    setIsEditing(true);
    setError(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData(null);
    setError(null);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    try {
      await updateSection(section, editData);
      setIsEditing(false);
      setEditData(null);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to save changes";
      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold">{config.label}</h3>
          <p className="text-sm text-muted-foreground">{config.description}</p>
        </div>
        {!isEditing ? (
          <button
            onClick={handleEdit}
            className="text-sm text-primary hover:underline"
            aria-label={`Edit ${config.label}`}
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleCancel}
              disabled={isSaving}
              className="text-sm text-muted-foreground hover:underline"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="text-sm font-medium text-primary hover:underline"
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        )}
      </div>
      {error && (
        <div className="text-sm text-destructive mb-4" role="alert">
          {error}
        </div>
      )}
      {isEditing ? (
        <EditComponent data={editData} onChange={setEditData} />
      ) : (
        <ViewComponent data={sectionData} />
      )}
    </div>
  );
}

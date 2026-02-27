import React, { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { X, UserPlus, Sparkles } from "lucide-react";

export function ProfileNudgeBanner() {
    const { session } = useAuth();
    const { profile, needsOnboarding, isLoading } = useLearnerProfile();
    const [isDismissed, setIsDismissed] = useState(false);

    // Don't show if loading, no session, explicitly dismissed, or already on the onboarding page
    if (
        isLoading ||
        !session?.user ||
        isDismissed ||
        (typeof window !== "undefined" && window.location.pathname.includes("/onboarding"))
    ) {
        return null;
    }

    // Determine State
    const hasNoProfile = !profile && needsOnboarding;
    const hasIncompleteProfile = profile && !profile.onboarding_completed;

    if (!hasNoProfile && !hasIncompleteProfile) {
        return null; // Profile is fully complete
    }

    const navigateToOnboarding = () => {
        window.location.href = "/onboarding";
    };

    return (
        <AnimatePresence>
            <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="w-full bg-primary/10 border-b border-primary/20 overflow-hidden"
            >
                <div className="container mx-auto px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">

                    {/* Content Area */}
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/20 rounded-full text-primary">
                            {hasNoProfile ? <UserPlus size={18} /> : <Sparkles size={18} />}
                        </div>
                        <div>
                            <p className="text-sm font-semibold text-foreground">
                                {hasNoProfile
                                    ? "Create your Learner Profile"
                                    : "Level up your learning experience"}
                            </p>
                            <p className="text-xs text-muted-foreground mt-0.5">
                                {hasNoProfile
                                    ? "Get deeply personalized content tailored to your goals and expertise."
                                    : "Your profile is incomplete. Finish setting it up for better personalization."}
                            </p>
                        </div>
                    </div>

                    {/* Action Area */}
                    <div className="flex items-center gap-2 self-end sm:self-auto min-w-max">
                        {hasNoProfile && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsDismissed(true)}
                                className="text-muted-foreground hover:text-foreground h-8 text-xs"
                            >
                                Not Now
                            </Button>
                        )}
                        <Button
                            size="sm"
                            onClick={navigateToOnboarding}
                            className="h-8 text-xs font-medium shadow-sm"
                        >
                            {hasNoProfile ? "Create Profile" : "Continue Profile"}
                        </Button>
                        <button
                            onClick={() => setIsDismissed(true)}
                            className="ml-2 p-1 text-muted-foreground hover:text-foreground rounded-full hover:bg-black/5"
                            aria-label="Dismiss banner"
                        >
                            <X size={16} />
                        </button>
                    </div>

                </div>
            </motion.div>
        </AnimatePresence>
    );
}

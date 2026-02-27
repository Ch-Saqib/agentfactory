import { UrgencyRadio } from "@/components/profile/fields";
import type { GoalsSection } from "@/lib/learner-profile-types";
import { motion } from "framer-motion";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

interface GoalsStepProps {
  data: GoalsSection;
  onChange: (data: GoalsSection) => void;
  autoAdvance?: () => void;
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
};

const GOAL_EXAMPLES = [
  "Build an AI agent I can sell as a SaaS product",
  "Automate repetitive tasks at work using AI agents",
  "Understand AI agents well enough to lead a team building them",
  "Transition my career into AI product development",
];

export function GoalsStep({ data, onChange, autoAdvance }: GoalsStepProps) {
  return (
    <motion.div
      className="space-y-12 max-w-2xl mx-auto"
      initial="hidden"
      animate="visible"
      variants={{
        visible: { transition: { staggerChildren: 0.1 } }
      }}
    >
      <motion.div variants={itemVariants} className="space-y-3">
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-foreground">
          What brings you here?
        </h2>
        <p className="text-lg text-muted-foreground font-medium max-w-xl">
          Your goal shapes every lesson — we'll emphasize what matters to you and skip what doesn't.
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="space-y-4">
        <div className="flex justify-between items-baseline mb-2">
          <Label htmlFor="onboarding-primary-goal" className="font-semibold text-lg">
            What do you want to achieve?
          </Label>
          <span className="text-xs text-muted-foreground font-medium shadow-sm px-2 py-0.5 rounded-md bg-accent/50">
            {data.primary_learning_goal?.length || 0} / 500
          </span>
        </div>
        <div className="relative group">
          <Textarea
            id="onboarding-primary-goal"
            value={data.primary_learning_goal || ""}
            onChange={(e) =>
              onChange({
                ...data,
                primary_learning_goal: e.target.value.substring(0, 500) || null,
              })
            }
            placeholder="Be specific — the more detail, the better we can personalize. e.g., 'Build a customer support AI agent for my e-commerce store that handles returns and order tracking'"
            className="w-full text-base min-h-[120px] rounded-xl border-2 border-border/50 bg-background/50 px-4 py-4 text-foreground placeholder:text-muted-foreground/50 shadow-sm focus-visible:ring-2 focus-visible:ring-primary/20 transition-all font-medium resize-y"
            maxLength={500}
            autoFocus
          />
        </div>
        <div className="space-y-2 pt-2">
          <p className="text-xs text-muted-foreground pl-1">Or pick one to start:</p>
          <div className="flex flex-wrap gap-2">
            {GOAL_EXAMPLES.map(example => (
              <Badge
                key={example}
                variant="secondary"
                className="cursor-pointer font-normal hover:bg-primary/20 transition-colors py-1.5 px-3"
                onClick={() => {
                  onChange({
                    ...data,
                    primary_learning_goal: example,
                  });
                }}
              >
                {example}
              </Badge>
            ))}
          </div>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="space-y-4 pt-6">
        <label className="text-lg font-semibold block">
          How urgent is this?
        </label>
        <p className="text-sm text-muted-foreground -mt-2">
          High urgency = practical shortcuts first. Low urgency = deeper conceptual foundations.
        </p>
        <div className="bg-transparent border-0 rounded-2xl p-0 shadow-none">
          <UrgencyRadio
            value={data.urgency}
            onChange={(value) => {
              onChange({ ...data, urgency: value as GoalsSection["urgency"] });
              if (autoAdvance && data.primary_learning_goal) {
                setTimeout(autoAdvance, 400);
              }
            }}
            name="onboarding-urgency"
          />
        </div>
      </motion.div>
    </motion.div>
  );
}

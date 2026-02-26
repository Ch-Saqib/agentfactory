import React from "react";
import type { DeliverySection } from "@/lib/learner-profile-types";

export function DeliveryView({ data }: { data: unknown }) {
  const delivery = data as DeliverySection;
  return (
    <dl className="space-y-3 text-sm">
      <div>
        <dt className="font-medium text-muted-foreground">Output Format</dt>
        <dd className="capitalize">
          {delivery?.output_format?.replace(/-/g, " ") || "Not set"}
        </dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Target Length</dt>
        <dd className="capitalize">
          {delivery?.target_length?.replace(/-/g, " ") || "Not set"}
        </dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Code Verbosity</dt>
        <dd className="capitalize">
          {delivery?.code_verbosity?.replace(/-/g, " ") || "Not set"}
        </dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Language</dt>
        <dd>{delivery?.language || "Not set"}</dd>
      </div>
      {delivery?.language_proficiency && (
        <div>
          <dt className="font-medium text-muted-foreground">
            Language Proficiency
          </dt>
          <dd className="capitalize">{delivery.language_proficiency}</dd>
        </div>
      )}
    </dl>
  );
}

# Minutes of Meeting

## Meeting

- Title: Offline Utility Test
- Recording date: March 13, 2026
- Duration reviewed: about 58 minutes
- Primary topics: depart-by rollout, NXP/transfer handling, SLA and reporting rules, route UX gaps, next-sprint planning

## Summary

The discussion centered on finalizing requirement details for depart-by and related routing scenarios, with heavy focus on how `NXP` transfers should behave in the UI, backend, and reporting flows. The team also separated confirmed phase-one work from unresolved UX questions, identified risks tied to service-level dependencies and screen constraints, and outlined the next cards and follow-up meetings needed to keep delivery moving.

## Decisions

- No additional API calls should be introduced; existing `whiteboard` and `route window` APIs should be leveraged.
- The initial rollout should be gated by the `auto dispatch` flag and treated as part of the `COS` phase-one pilot.
- Customer-management or similar unsupported flows should not be pulled into the current phase because service-level support is missing.
- `Transfer` is a display-only front-end concept; the backend should continue to store the underlying status as `invoice`.
- For `NXP` standard deliveries, the system should ignore anticipated delivery time and derive timing from SLA instead.
- The optimizer should remain generic; route-specific logic belongs in upstream auto-dispatch handling rather than in the optimizer itself.
- The route-window/header changes and `hide map` / `show map` control were treated as sufficiently confirmed for card creation, while drill-down UX remains open.
- Dispatch work should be considered `1024`-pixel compatible by default, with that requirement captured in delivery expectations.
- Near-term team focus should be on logout scenarios, `FR6` backend work, and refreshing or expanding `FR9` cards.

## Open Items

- The requirement still appears inconsistent on whether transfer orders may be marked ready before all parts are available.
- Reporting rules for `NXP` and partial-delivery cases still need explicit confirmation.
- Several UX items remain unconfirmed, including route drill-downs, some dispatch-card behavior, and broader whiteboard coverage.
- The exact rule for driver route counts, pending routes, and dispatcher cancellation capability still needs final confirmation.
- Final screen-resolution guidance and detailed Figma references are still needed for smaller in-store devices.

## Action Items

- Team to mark unresolved requirement items clearly so open points are easier to identify in the working document.
- Madison and product leads to confirm remaining UX decisions with Chuck and provide the approved designs or prototypes.
- Team to update requirements with the discussed notes on transfer handling, `NXP`, SLA calculation, and reporting expectations.
- Team to create or refine cards for logout scenarios, `FR6`, and `FR9`.
- Owners to capture `1024`-pixel compatibility in acceptance criteria or the PR checklist for dispatch-related changes.
- Team to hold separate follow-up sessions for `no rush` behavior, design review, and estimation alignment.
- Leads to sequence pod onboarding carefully so auto-dispatch work is expanded without creating unnecessary overlap or confusion.

## Risks / Blockers

- Lack of service-level data blocks wider support for domains outside the current pilot scope.
- Requirement ambiguity around transfer readiness and related edge cases could lead to rework.
- Reporting and SLA outputs may be wrong if `NXP` logic is not implemented consistently across services.
- Unconfirmed UX and small-screen limitations may slow front-end execution.
- Expanding the work across multiple pods too quickly could introduce coordination and delivery risk.

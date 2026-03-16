# Minutes of Meeting

## Meeting

- Title: Quick MoM Test
- Recording date: March 13, 2026
- Duration reviewed: about 59 minutes
- Primary topics: depart-by rollout, NXP/transfer handling, SLA and reporting rules, route UX gaps, next-sprint planning

## Summary

The discussion focused on clarifying functional requirements for depart-by and related routing behavior, especially for NXP or transfer scenarios, SLA handling, and reporting implications. The team also reviewed what UX is confirmed versus still pending, agreed on a few implementation boundaries for phase one, and aligned on the next set of cards and backend work to prepare for upcoming sprint planning.

## Decisions

- No new API calls should be added; existing `whiteboard` and `route window` endpoints should be reused where possible.
- The pilot scope should be driven by the `auto dispatch` flag for the `COS` phase-one rollout.
- Customer-management and similar non-supported domains should stay out of the current phase until the required service-level inputs exist.
- `Transfer` should remain a front-end display status only; the backend status should still remain `invoice`.
- For `NXP` standard deliveries, anticipated delivery time should be ignored and SLA-based timing should be used instead.
- Route-type logic should stay outside the optimizer; `auto dispatch` should provide the priorities and windows the optimizer needs.
- The route-window/header rework and `hide map` / `show map` changes were treated as confirmed enough to create cards, but drill-down behavior is still not finalized.
- Going forward, dispatch work should be treated as needing `1024`-pixel compatibility, with that expectation captured in acceptance criteria or the PR checklist.
- For the next planning cycle, the team should prioritize logout scenarios, `FR6` backend work, and updates to existing `FR9` cards.

## Open Items

- There is still a contradiction around whether transfer orders can be marked ready before all parts arrive.
- Reporting behavior for `NXP` orders still needs clearer rules so downstream consumers know when to use SLA timing versus anticipated delivery time.
- Some UX remains unconfirmed, including drill-down behavior, parts of the dispatch-card experience, and some whiteboard or route-detail views.
- Driver route-limit rules and cancellation behavior for ad-hoc routes still need final confirmation.
- Final design guidance is still needed for smaller store screens, especially around `1024`-pixel layouts.

## Action Items

- Team to annotate open items more clearly in the requirements and keep unresolved items visibly marked.
- Madison to confirm the remaining UX gaps and signed-off designs with Chuck and share the needed Figma or prototype references.
- Team to update the functional requirements with the `NXP`, transfer, SLA, and reporting notes discussed in the meeting.
- Team to create or update cards for logout scenarios, `FR6`, and `FR9`.
- Product and UX to define the final small-screen expectations and make `1024`-pixel compatibility explicit.
- Team to schedule separate follow-up discussion for `no rush` scenarios and other edge cases that were deferred from this call.
- Leads to review pod planning and sequencing so additional pods are brought into auto-dispatch work gradually.

## Risks / Blockers

- Missing service-level support blocks broader rollout for domains that do not yet have the required data.
- Contradictory requirement wording around transfer readiness could cause implementation churn or rework.
- Reporting accuracy may be affected if `NXP` and partial-delivery cases are not handled consistently.
- Unconfirmed UX and small-screen constraints could delay front-end implementation and card readiness.
- Bringing too many pods into the same auto-dispatch area too quickly may create coordination and dependency issues.

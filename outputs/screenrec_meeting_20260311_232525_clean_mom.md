# ScreenRec Meeting - Clean MoM

- Meeting date: March 11, 2026
- Source: ScreenRec recording
- Duration: about 48 minutes

## Decisions

- Force logout should be handled first as backend/API work, with mobile listening for the notification and logging the user out.
- Force logout and related driver actions should capture metadata such as who performed the action and when.
- Route and dispatcher actions should move toward a shared audit trail instead of multiple fragmented audit tables.
- The audit table design is a technical requirement and should not block the current functional requirements.
- For now, invoice flow should remain simple, with `ready` as the main backend status used by optimizer-related logic.
- A separate `routed` status is not clearly needed yet; the team will avoid adding it until a stronger reporting or debugging case appears.
- Visual indicators and alerts are the preferred short-term approach for delayed departures and possible SLA misses, rather than building full ETA recalculation or re-optimization immediately.
- Auto-dispatch is a near-term high-priority deliverable and should be completed around mid-March.
- Auto-dispatch work should initially stay concentrated across the current pods, with additional team involvement phased in later.

## Action Items

- Hermita to take or help drive the force logout work.
- Add backend endpoints and metadata support for force logout and release-vehicle related actions.
- Define how mobile should react to force logout notifications.
- Add or refine a route and action audit trail covering dispatcher actions, optimizer triggers, and auto-dispatch decisions.
- Create or update cards before refinement so the backlog reflects the latest decisions.
- Review all created cards again and fill in missing implementation details.
- Confirm with Madison whether extra integration, automation, and performance testing tickets are needed.
- Create or review integration testing, automation, and performance testing work as part of the effort.
- Add clearer flow diagrams and detailed card descriptions so offshore contributors can follow the workflow and decisions.
- Have the team review the work in the next refinement meeting.

## Open Questions

- How should mobile behave in every force logout edge case, especially when the driver is in-route or mid-flow?
- Should force logout be denied in some pending or active route states?
- What is the final ownership split between driver behavior, dispatcher follow-up, and system behavior when departures are delayed?
- Should delayed departures only show visual warnings, or should route service / optimizer logic also adjust ETA handling?
- How should auto-dispatch behave for no-rush orders and other cases where optimizer is intentionally not triggered?
- What UX should dispatchers see when optimizer or auto-dispatch decides not to create a route?
- Is a dedicated `routed` invoice status needed later for reporting, debugging, or audit visibility?
- What trigger mechanism should be used for auto-dispatch and no-rush flows, especially given open questions around pub/sub and cloud tasks?
- Which release items can go out before pilot, and which must wait until pilot-specific flows are available?


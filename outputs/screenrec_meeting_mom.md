# Meeting Minutes

## Meeting

- Title: ScreenRec Meeting Review
- Date: March 11, 2026
- Source: ScreenRec shared recording
- Duration: Approximately 1 hour 19 minutes

## Attendees

- Madison
- Chuck
- Bonnie
- Jason
- Anusha
- Hermita
- Prince

Note: attendee names are inferred from the meeting audio and may be incomplete.

## Objective

- Review dispatch and optimizer workflows around `force log out`, `release vehicle`, route finalization, and late-day optimizer behavior.
- Align functional requirements before implementation work starts.

## Executive Summary

The meeting focused on preventing dispatchers from using `force log out` or `release vehicle` while a route is already in progress, because those actions can create optimizer, driver-availability, and vehicle-tracking issues. The team agreed that these actions should remain available only for pending routes that have not yet departed. For in-progress routes, the preferred path is route finalization rather than forcibly releasing the driver or vehicle.

The group also revisited a functional requirement that blocked optimizer usage near store closing time. That requirement is being changed. Instead of blocking the optimizer, the current direction is to allow it to run with clear warnings when the route may extend beyond normal store hours.

The main unresolved areas are exception handling when the driver device fails mid-route, the exact UX flow for warnings and edge cases, and ownership of Figma/UX design support.

## Discussed Points

- APAC has seen misuse of `release vehicle` and `force log out`, causing active routes to lose correct vehicle/user state.
- In USAG, the same behavior would be more harmful because the optimizer could incorrectly treat drivers and vehicles as available.
- A hidden `mark route as complete` capability already exists in production behind a flag and depends on mobile app version alignment.
- The team needs a safe way to deal with routes where the driver did not finalize correctly or the device stopped syncing.
- The optimizer behavior near store closing time needs a warning-based flow rather than a hard block.
- Confirmed functional requirements should be signed off quickly so cards can be created and sprint work can begin.

## Decisions

- Do not allow `force log out` for routes that are already in progress.
- Do not allow `release vehicle` for routes that are already in progress.
- Allow those actions only for pending routes that have not departed.
- Use route finalization or `mark route as complete` as the preferred resolution path for eligible end-of-route cases.
- Change the requirement that said the optimizer should not run close to store closing time.
- Allow the optimizer to run near closing time, but show a warning/disclaimer to the store user.
- Treat driver/vehicle availability as a prerequisite for optimizer execution.

## Open Questions

- What is the exact fallback process when a route is in progress and the driver cannot finalize through the mobile app?
- How should the system handle mid-route device failure without losing control of the route, vehicle, and proof-of-delivery state?
- What exact UX copy and confirmation flow should be shown for optimizer warnings near store closing?
- Who will provide the design support: a UX designer, Figma designs, or internal design work?
- Which functional requirements are pilot-only and which are intended for general rollout?

## Risks And Blockers

- Mid-route logout or vehicle release can make optimizer decisions incorrect.
- Missing proof-of-delivery or signatures cannot be reconstructed reliably after device failure.
- Mixed mobile app versions are delaying broader rollout of route-completion support.
- UX/Figma ownership is currently a blocker for finalizing flows.

## Action Items

- Madison to update the functional requirements based on the discussion.
- Chuck and Madison to mark confirmed FRs and provide sign-off on answered items.
- Start creating implementation cards for confirmed requirements.
- Update FRs related to logout scenarios, part status handling, and optimizer no-route-found notifications.
- Resolve the Figma / UX support gap.
- Send the deployment communication to Stratix for the two pilot stores.
- Continue optimizer-related implementation planning for the sprint starting March 12, 2026.

## Outcome

- The team aligned on restricting risky mid-route dispatcher actions.
- The optimizer requirement near store closing will be revised.
- Requirement cleanup, sign-off, and UX clarification are the immediate next steps before broader implementation continues.

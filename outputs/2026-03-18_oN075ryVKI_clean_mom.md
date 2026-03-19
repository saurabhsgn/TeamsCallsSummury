# Clean Minutes of Meeting

## Meeting

- Recording: `https://screenrec.com/share/oN075ryVKI`
- Date processed: 2026-03-18
- Working title: Q2 Planning and ProTracker Dependency Review
- Note: This MOM is based on an automated transcript and cleaned manually. A few speaker names and product terms may need final validation.

## Executive Summary

The discussion focused on Q2 scope, dependencies, and functional clarifications for ProTracker-related work. The team aligned that `inventory domain item availability` is not a Q2 or July dependency and should be removed from the current dependency list. They also clarified that the current auto-hold behavior should not continue as a core design assumption for phase one; instead, the functional specification should capture the future-state automation approach around ETA-driven flows, automated routing optimization, and NXP-driven events.

The other major Q2 dependencies called out were `wheels.com` and `catalog`. Catalog documentation has already been received and discussions are underway. `wheels.com` remains the larger uncertainty because required attributes such as store number mapping and related operational data may not be readily available. The team also discussed TAMS dependencies including confirmed delivery address support, geocode/date-time needs, and whether return-service work should stay in scope.

## Key Discussion Points

- The team reviewed whether inventory domain availability is truly needed for phase one and agreed it is not.
- The longer-term vision is to move away from manual or event-driven "ready to go" handling toward more automated routing and pick/dispatch behavior.
- Current holds exist largely because ETA information is not always reliably propagated through the flow from ProLink to TAMS to ProTracker.
- With the broader CDE direction, ETA information should flow more accurately, reducing the need for manual or automatic holds.
- Q2 dependency focus was narrowed primarily to `wheels.com` and `catalog`.
- `wheels.com` data quality and attribute availability remain a concern, especially around store mapping and logistics-related data.
- TAMS-related items were reviewed, especially confirmed delivery address, customer address ID / lat-long support, return service timing, and testing dependencies.
- A barcode scanner dependency tied to ESB replacement was identified as a follow-up item that still needs clarification.

## Decisions

- Remove `inventory domain item availability` as a Q2 / July dependency.
- Capture the future automation behavior in the functional spec instead of treating inventory-domain integration as an immediate dependency.
- Keep the requirement that orders should not be automatically held in the current phase-one design.
- Continue Q2 dependency tracking primarily around `wheels.com` and `catalog`.
- Remove `return service` from the immediate dependency list if the actual work is moving out of Q2 and into a later quarter.
- Treat current external asks from other teams as mostly testing dependencies unless new implementation work is confirmed.

## Dependencies

### Confirmed / Active

- `catalog`
  - Documentation is available.
  - Conversations have already started.
  - Team will review available attributes for Q2 usage.

- `wheels.com`
  - Still an active dependency and the largest open concern.
  - Team needs to validate whether the available fields are sufficient for Q2 needs.
  - Specific concern: store number mapping is not directly available; there may be an `OU` field that could potentially be mapped.

- `TAMS`
  - Confirmed delivery address / customer address ID still needs clarification and prioritization.
  - Date-time, SLA, and geocode-related support must be prioritized for end-to-end delivery strategy in Q2.

### Removed / Deferred

- `inventory domain item availability`
  - Removed as a Q2 dependency.

- `return service`
  - Likely deferred from Q2; remove from near-term dependencies unless TAMS-side work must still happen in Q2.

## Risks and Open Questions

- `wheels.com` may not provide all required attributes for Q2 use.
- It is unclear whether `wheels.com` can add or expose fields needed for clean store-level mapping.
- Confirmed delivery address support in TAMS needs prioritization confirmation.
- Barcode scanner behavior may be impacted by the ESB replacement timeline in Q3.
- Ownership and implementation path for the ESB-related barcode scanner replacement/integration are still unclear.
- Functional specification sign-off is still pending for some areas, especially routing optimization / auto-dispatch.

## Action Items

- Anusha to update the functional spec with future-state automation notes, especially around:
  - no automatic holds in phase one
  - automated routing optimization
  - handling of events when inventory is unavailable or becomes available
  - NXP notification/event expectations

- Ryan to update the dependency notes and spreadsheet/roadmap entries:
  - remove inventory-domain dependency
  - add notes to revisit when later architecture pieces are ready
  - annotate TAMS dependency items based on follow-up conversations

- Team to get final confirmation and sign-off on the functional spec content from Chuck and Madison.

- Team to create / verify Jira dependency stories for external teams and include sufficient schedule buffer for testing.

- Owner to create a spike / follow-up card for `wheels.com` to validate:
  - available fields
  - store mapping approach
  - cost-related data definitions
  - whether additional columns or changes can be requested

- Chuck / team to share or validate the current delivery cost-per-mile assumptions and how store-level reporting can be sourced going forward.

- TAMS owner to confirm whether `confirm delivery address` remains in the current quarter or should move to a later quarter after discussion with Colette.

- Madison to follow up on the barcode scanner and ESB replacement dependency and bring back the required details.

- Functional spec draft for routing optimization / auto-dispatch to be circulated more broadly by the next day so reviewers have time to digest it.

## Notes for Follow-Up Review

- Validate speaker names and owners before sharing externally.
- Confirm whether `Q2`, `July`, and `phase one` references all map to the same planning window in the project tracker.
- Recheck the `wheels.com` dependency after the next follow-up meeting because it appears to be the most likely scope risk.

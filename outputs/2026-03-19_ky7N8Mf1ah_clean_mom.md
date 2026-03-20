# Clean Minutes of Meeting

## Meeting

- Recording: `https://screenrec.com/share/ky7N8Mf1ah`
- Date processed: 2026-03-19
- Working title: Driver Reassignment, Depart-By, and Force Logout Requirement Review
- Note: This MOM is based on an automated transcript and then cleaned manually. A few names and terms may need final validation before wider circulation.

## Executive Summary

The meeting focused on clarifying functional behavior for driver reassignment, `Depart By`, route status colors, and force-logout handling. The team aligned on several important phase-one behaviors: `Depart By` should turn red exactly when the threshold is violated, not five minutes later; `Depart By` should not be shown for route types that do not have meaningful SLA support such as custom stops, DoorDash, ISOs, and store-to-store transfers; and force logout should be treated as a strong administrative action that can release the driver from assigned work.

The largest discussion area was how to represent driver availability during reassignment. The team moved toward a clearer status model where color should reflect operational meaning for the dispatcher, and where selecting a driver with a pending auto-generated route can trigger follow-on system actions such as breaking that route back into invoices and returning them to the queue. Some edge cases were still debated and should be finalized in a simple scenario matrix.

## Key Discussion Points

- Confirmed timing and display rules for `Depart By`.
- Reviewed which route types should not display `Depart By` because they do not currently carry usable SLA logic.
- Clarified the intended behavior of driver reassignment when a driver already has pending or in-progress work.
- Discussed the difference between dispatcher-created ad hoc routes and optimizer-created auto-generated routes.
- Reviewed whether the `Ready to Go` button should be disabled when no drivers are logged in.
- Discussed force-logout consequences, especially how it affects pending routes and route cancellation.
- Reviewed whether `Release Vehicle` is still needed in the active-driver modal.
- Discussed ambiguity around the meaning of `Active` time in the driver UI.
- Briefly noted pending UI considerations around mobile design and user-management placement.

## Decisions

- `Depart By` should turn red at the exact violation time, not with a five-minute grace buffer, unless future feedback changes that behavior.
- `Depart By` should not be shown for:
  - custom stops
  - DoorDash routes
  - ISOs
  - store-to-store transfers

- For phase one, dispatcher-created ad hoc routes and optimizer-created routes should be treated differently:
  - ad hoc routes do not by themselves imply optimizer-driven cancellation behavior
  - pending auto-generated routes do carry special consequences when reassignment happens

- If a driver with a pending auto-generated route is selected during reassignment, that auto-generated route can be broken down and its invoices returned to the queue.

- `Release Vehicle` should be removed from the active-driver modal because:
  - force logout already releases the vehicle
  - the same action can be handled through `My Fleet`
  - the team did not identify a strong standalone scenario requiring it in this modal

- The active-driver time metric should represent accumulated logged-in time, not a single uninterrupted session.

## Confirmed Functional Behavior

### Depart By

- `Depart By` is a confirmed requirement for supported SLA-based routes.
- It should not appear on route types where SLA handling is absent or not meaningful today.
- Current excluded route types are custom stops, DoorDash, ISOs, and store-to-store transfers.

### Driver Reassignment Status Logic

- The team wants driver status colors to communicate practical availability to dispatchers.
- A driver with only ad hoc routes should not automatically be treated the same as a driver with pending optimizer-created work.
- A pending auto-generated route is the key trigger for special system behavior during reassignment.
- Reassigning a route to a driver who already has pending auto-generated work can cause the previously auto-generated route to be broken apart and returned to the queue.

### Route Reassignment vs Optimization

- If a dispatcher manually reassigns an optimizer-created route, that route should effectively become locked and no longer be re-optimized in the same way.
- If the dispatcher does not intervene, an optimizer-created route may still remain a candidate for further optimization or invoice reordering.

### Force Logout

- Force logout is treated as a high-impact admin action.
- The working direction is that force logout can cancel or release associated routes so the driver is fully detached from active/pending work.
- The team explicitly noted the risk that dispatchers may abuse this function if the behavior is not clear.

## Open Questions

- Final color-state model still needs a clean matrix for edge cases:
  - when should a driver be `green`
  - when should a driver be `red`
  - whether `amber` should be introduced as a better status for drivers with pending auto-generated routes

- If no drivers are logged in, should `Ready to Go` be disabled outright, or should the system allow the action and then return an explanatory error?

- Exact cancellation scope on force logout still needs final confirmation:
  - cancel only auto-generated routes
  - or cancel all routes, including ad hoc routes

- The team should validate whether the reassignment list should simply show all drivers with status colors, rather than hiding or disabling some of them.

- The wording of `Active` in the UI may be misleading, since users may read it as active on-route time rather than total logged-in time for the day.

- User-management placement and alignment with the mobile design were mentioned as still-open UI items.

## Risks and Concerns

- Without a final scenario matrix, the reassignment logic is easy to misinterpret.
- Force logout may be overused if dispatchers are not clearly warned about its consequences.
- Incorrect status-color semantics could cause dispatchers to make poor route-assignment decisions.
- Breaking down optimizer-created routes during reassignment may create SLA risk if the rules are not explicit.
- Custom stops remain a visibility gap and were described as a current blind spot.

## Action Items

- Anusha / Prince to convert the reassignment discussion into a simple scenario matrix covering:
  - driver has pending auto-generated route
  - driver is en route
  - driver has only ad hoc routes
  - reassignment outcome
  - status color shown

- Team to finalize whether the UI will use `green/red` only or `green/amber/red`.

- Team to confirm the exact force-logout cancellation behavior and document it in the functional requirements.

- Team to confirm the final handling for `Ready to Go` when no drivers are logged in.

- Team to remove `Release Vehicle` from the active-driver modal.

- Team to rename or clarify the `Active` metric if needed so it is not confused with on-route utilization.

- Team to revisit custom-stop visibility in a later design pass, even if it stays out of current phase-one scope.

- Team to review pending UI items around mobile design consistency and moving user management.

## Notes for Follow-Up Review

- Validate final owner names before circulation.
- Review the raw transcript for the later force-logout section if an implementation spec is being written from this MOM.
- Use this MOM together with the transcript to build the scenario matrix before any UI or backend changes are finalized.

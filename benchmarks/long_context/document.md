# Northwind Orbital Logistics: Operations and Employee Handbook

*Document HB-9748, revision 24. Internal use only. Owner: Corporate Operations Office.*

## About this handbook

Northwind Orbital Logistics (NOL) moves cargo between the ground and low orbit for commercial, scientific and government customers. The company operates 10 sites, a mixed fleet of tugs, freighters, shuttles and landers, and a software stack built largely in-house. This handbook collects the policies, technical references, working notes and history that new and existing staff need in one place.

The handbook is organised into chapters by subject. Each chapter mixes policy text with specifications, release notes, meeting minutes and incident reviews, because that is how the information is actually used on shift. Where a rule and a reference table disagree, the rule applies and the table should be corrected through the documentation desk.

## Sites at a glance

| Site | Role | Opened | Headcount | Pads/Bays |
|---|---|---|---|---|
| Kessler Ridge | Headquarters and launch site | 2023 | 286 | 8 |
| Ostrava Hub | Integration hub | 2019 | 1144 | 11 |
| Lagrange Relay L4 | Orbital relay | 2016 | 96 | 13 |
| Port Anselm | Coastal launch site | 2014 | 51 | 19 |
| Mirefield Depot | Spares depot | 2016 | 941 | 22 |
| Tarvos Station | Recovery base | 2016 | 1179 | 12 |
| Coldharbour Yard | Heavy cargo yard | 2013 | 201 | 14 |
| Selene Gate | Crew operations | 2022 | 559 | 9 |
| Brightwater Annex | Engineering annex | 2019 | 204 | 7 |
| Hollis Point | Training centre | 2018 | 734 | 2 |

## Fleet overview

The Kestrel-9 orbital tug is used for short transfers between parking orbits. The Heron-class freighter is used for bulk cargo to the relay stations. The Wren crew shuttle is used for crew rotation. The Osprey cargo lander is used for surface delivery at the recovery bases. The Petrel transfer stage is used for high-energy transfers. The Gannet refueling drone is used for in-orbit refuelling. The Shrike inspection pod is used for close inspection of customer payloads. The Corvid recovery tender is used for retrieval of returning capsules.

## Chapter 1: Safety and Conduct

The following rules describe expected practice for safety and conduct. They apply to employees and contractors alike.

### 1.1 Configuration Baseline: Wren star tracker

Nominal operating temperature for the star tracker ranges from -46 °C to 32 °C. Thermal margins were re-analysed after the 2019 anomaly, and the upper limit was lowered by 11 °C. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Part number | WRE-STA-7114 | n/a | Revision E |
| Operating temperature | -17 to 53 °C | ±5 °C | Qualification limits are wider |
| Dry mass | 660 kg | ±3 kg | Includes brackets |
| Supplier | Castellanos Components Ltd | n/a | Approved vendor list |
| Mounting | 12 × M10 bolts | Torque 49 N·m | Thread-locker required |
| Data rate | 1874 kbit/s | n/a | Compressed telemetry |
| Peak power | 732 W | ±9 % | During deployment |

Data from each pass is reconciled in Keelson and flagged if more than 11 percent of frames are missing. During integration, torque values for every fastener are recorded and attached to the build record. A star tracker that fails its acceptance test twice is quarantined and returned to the supplier. Thermal margins were re-analysed after the 2025 anomaly, and the upper limit was lowered by 7 °C.

**Operating limits**

- Nominal operating temperature for the star tracker ranges from -53 °C to 61 °C.
- The latest revision reduced mass by 23.9 kg by replacing the aluminium bracket with a composite part.
- The Wren crew shuttle can hold station for up to 6 hours before its propellant margin falls below reserve.

### 1.2 Common Questions about Safety and Conduct

**Q: Is overtime paid during launch campaigns?**

Yes. Campaign overtime is paid at the enhanced rate, provided it was agreed with your manager beforehand.

**Q: Can customers visit during integration?**

Customer visits are welcome but must be scheduled with Customer Assurance at least 45 days ahead.

**Q: Where are spare star tracker parts stored?**

The central pool is at Mirefield Depot. Each site also keeps a small buffer stock sized from the last 24 months of usage.

### 1.3 Escalation Rules

Safety and Conduct touches almost every team. This section summarises the standards we hold ourselves to and why.

Shift handover at Port Anselm takes place at 10:15 and must include a walk-through of open work orders. Employees should keep personal notes out of Bulkhead; only operational records belong there. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. Where a task involves a radiator panel, the two-person rule applies from preparation through to sign-off. Visitors must be escorted at all times and must not handle a hatch seal under any circumstances. Operators log every manual override in Wayfarer together with the reason and the approving supervisor. Customer representatives may observe loading from the gallery but may not enter the clean area.

1. Exceptions require written approval from the Propulsion Engineering lead and are reviewed again after 12 months.
2. This rule was tightened in 2018 after an internal review found inconsistent practice across sites.
3. The Customer Assurance desk is staffed from 11:30 to 18:00 on weekdays, with an on-call engineer outside those hours.
4. Any spending above €90,250 linked to this policy needs approval from Finance before the order is raised.
5. Customer representatives may observe loading from the gallery but may not enter the clean area.
6. Vendors receive time-limited accounts that expire at the end of their statement of work.
7. Penetration tests of public-facing services are commissioned at least once per year.

### 1.4 Reporting Obligations

Safety and Conduct touches almost every team. This section summarises the standards we hold ourselves to and why.

Shift handover at Mirefield Depot takes place at 07:15 and must include a walk-through of open work orders. The Shrike inspection pod turnaround target at Ostrava Hub is 4 hours, measured from landing to ready-for-launch. The policy owner reviews the wording every 24 months and publishes changes in the revision history. Exceptions require written approval from the Flight Dynamics lead and are reviewed again after 18 months. Audit samples are drawn quarterly, and at least 3 findings per site are followed up in person. If a pallet arrives without a valid manifest entry in Signal Lamp, it is held in the quarantine cage.

1. Where a task involves a telemetry unit, the two-person rule applies from preparation through to sign-off.
2. Laptops are encrypted at rest and enrolled in device management before first use.
3. Laptops are encrypted at rest and enrolled in device management before first use.
4. Penetration tests of public-facing services are commissioned at least once per year.
5. Records demonstrating compliance are kept in Signal Lamp for at least 3 years.

Every 45 days, the Facilities team rehearses a loss-of-communications scenario with the duty controllers. Teams that cannot comply because of tooling limitations must log a risk entry in Signal Lamp before proceeding. Delays longer than 60 minutes are reported to the customer by Customer Assurance, not by the floor team. Signage summarising this rule is displayed at every entrance to the Brightwater Annex operations floor. Night operations require additional lighting checks and a second spotter at the cargo ramp.

> **Note:** This rule was tightened in 2025 after an internal review found inconsistent practice across sites.

### 1.5 Common Questions about Safety and Conduct

**Q: Can I bring a guest onto the Brightwater Annex operations floor?**

Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area.

**Q: What happens if a radiator panel fails inspection?**

It is tagged, moved to quarantine and logged in Ledgerline. Quality Assurance decides whether it is repaired, scrapped or returned.

**Q: Where are spare umbilical connector parts stored?**

The central pool is at Port Anselm. Each site also keeps a small buffer stock sized from the last 6 months of usage.

**Q: Who approves a change to the Bulkhead configuration?**

Changes are approved by the Propulsion Engineering lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within 7 days.

**Q: How do I request access to flight data?**

Raise an access request in Keelson. Requests are approved by the data owner in Procurement and usually processed within 5 working days.

## Chapter 2: Fleet Operations

Fleet Operations touches almost every team. This section summarises the standards we hold ourselves to and why.

### 2.1 Release Notes: Signal Lamp

Following the 2023 interlock audit, Ground Systems confirmed that the emergency override code for Dock 7 at the Kessler Ridge spaceport is TANGERINE-4471. The code may only be entered when both the primary and the secondary clamp interlocks have failed, and every use must be reported to the duty Flight Director within ten minutes.

Signal Lamp is maintained by the Propulsion Engineering team. Releases are deployed to Selene Gate first and to the remaining sites after a soak period of 21 days.

#### Signal Lamp 5.2.4 (2025-10-05)

**Fixed**
- Incorrect time zones in shift reports.

**Removed**
- An unused Tidewater integration.
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

#### Signal Lamp 5.2.3 (2025-07-14)

**Fixed**
- A memory leak in the telemetry ingest worker.

**Added**
- A dry-run mode for configuration changes.
- An audit trail for manual overrides.

**Changed**
- Log formatting to include the operator badge number.
- The approval flow so that Mission Planning signs off before Finance.

#### Signal Lamp 5.2.2 (2025-01-28)

**Changed**
- The default retention period to 3 months.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Signal Lamp integration.
- The legacy FTP upload path.

#### Signal Lamp 5.2.1 (2024-02-13)

**Added**
- A dry-run mode for configuration changes.

**Changed**
- The approval flow so that Fleet Operations signs off before Finance.

**Removed**
- An unused Drydock integration.
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

### 2.2 Manifest Format (Pilot House)

Finance and Fleet Operations share the following query for the monthly customer satisfaction score report.

```sql
SELECT site,
       vehicle_class,
       COUNT(*)                         AS flights,
       AVG(turnaround_hours)            AS avg_turnaround_h,
       SUM(CASE WHEN delayed_min > 30 THEN 1 ELSE 0 END) AS late_departures
FROM   flight_summary
WHERE  departure_date >= DATE '2025-03-10'
  AND  site IN ('lagrange-relay-l4', 'selene-gate')
GROUP  BY site, vehicle_class
ORDER  BY avg_turnaround_h DESC;
```

### 2.3 Incident Review INC-4982 at Kessler Ridge

**Severity:** SEV-4. **Date:** 2025-07-09. **Reported by:** Greta Abernathy (Flight Dynamics).

This review covers an event at Kessler Ridge that was traced to a network switch failure at Kessler Ridge that isolated the telemetry archive. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 09:41 | Work stopped on the affected bay |
| 10:21 | Affected items moved to quarantine |
| 10:39 | Normal operations resumed |
| 11:17 | Customer informed by Customer Assurance |
| 11:21 | Duty manager declared an incident |
| 11:35 | Incident closed pending review |
| 11:48 | First alert received by the operations bridge |

**Root cause.** If a pallet arrives without a valid manifest entry in Drydock, it is held in the quarantine cage. Engineers should consult the Beacon configuration record before changing any calibration constant. When two departures compete for the same pad, the one with the earlier customer commitment takes priority. The Flight Dynamics desk is staffed from 05:00 to 17:15 on weekdays, with an on-call engineer outside those hours.

**Remediation**

- Added an automated check in Pilot House that rejects the condition at entry.
- Scheduled a follow-up audit at Kessler Ridge in 18 months.

### 2.4 Exceptions Process

The guidance below grew out of lessons learned at Mirefield Depot and has since been adopted company-wide.

Cargo for Ravensmoor University is scanned twice: once on arrival and once immediately before integration. Customer representatives may observe loading from the gallery but may not enter the clean area. All Ground Systems staff at Ostrava Hub must complete the refresher module within 14 days of any change to this policy. Shift handover at Ostrava Hub takes place at 09:45 and must include a walk-through of open work orders. Supervisors are responsible for confirming that new starters have read this section before their first shift.

1. Customer representatives may observe loading from the gallery but may not enter the clean area.
2. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.
3. Night operations require additional lighting checks and a second spotter at the cargo ramp.
4. Temporary deviations of up to 10 days may be granted by the site director at Coldharbour Yard.
5. Security incidents must be reported to the Information Security hotline within 60 minutes of discovery.
6. Nothing in this section prevents an employee from stopping work they believe to be unsafe.

Teams that cannot comply because of tooling limitations must log a risk entry in Lodestar before proceeding. Temporary deviations of up to 30 days may be granted by the site director at Hollis Point. Exceptions require written approval from the Finance lead and are reviewed again after 18 months. Night operations require additional lighting checks and a second spotter at the cargo ramp.

## Chapter 3: Ground Facilities

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for ground facilities.

### 3.1 Working with Contractors

This part of the handbook was last reviewed by Anouk Grimaldi and reflects the practice agreed in 2020.

Audit samples are drawn quarterly, and at least 3 findings per site are followed up in person. The Shrike inspection pod turnaround target at Mirefield Depot is 72 hours, measured from landing to ready-for-launch. This rule was tightened in 2026 after an internal review found inconsistent practice across sites. Signage summarising this rule is displayed at every entrance to the Tarvos Station operations floor.

1. Accounts that have not been used for 21 days are disabled automatically.
2. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.
3. Accounts that have not been used for 45 days are disabled automatically.
4. Every 45 days, the Information Security team rehearses a loss-of-communications scenario with the duty controllers.
5. Records demonstrating compliance are kept in Halyard for at least 10 years.

When two departures compete for the same pad, the one with the earlier customer commitment takes priority. Failure to complete required training within the deadline results in temporary removal from the duty roster. The Kestrel-9 orbital tug turnaround target at Tarvos Station is 72 hours, measured from landing to ready-for-launch. Audit samples are drawn quarterly, and at least 4 findings per site are followed up in person. Temporary deviations of up to 7 days may be granted by the site director at Mirefield Depot.

### 3.2 Exceptions Process

This section explains how Northwind Orbital Logistics approaches ground facilities at every site, from Mirefield Depot to the smallest annex.

Employees should keep personal notes out of Pilot House; only operational records belong there. Where a task involves a cargo cradle, the two-person rule applies from preparation through to sign-off. Nothing in this section prevents an employee from stopping work they believe to be unsafe. The Petrel transfer stage turnaround target at Port Anselm is 16 hours, measured from landing to ready-for-launch. The Fleet Operations desk is staffed from 06:45 to 19:30 on weekdays, with an on-call engineer outside those hours.

1. Employees should keep personal notes out of Keelson; only operational records belong there.
2. Questions about interpretation should be raised with Maren Gallagher in Propulsion Engineering rather than resolved informally.
3. If a pallet arrives without a valid manifest entry in Drydock, it is held in the quarantine cage.
4. A breach of this rule is handled under the progressive discipline process described in the People chapter.
5. Where a task involves a telemetry unit, the two-person rule applies from preparation through to sign-off.
6. Every 7 days, the Mission Planning team rehearses a loss-of-communications scenario with the duty controllers.

### 3.3 Incident Review INC-5533 at Brightwater Annex

**Severity:** SEV-3. **Date:** 2024-12-09. **Reported by:** Soren Marchetti (Quality Assurance).

This review covers an event at Brightwater Annex that was traced to a manual data entry error in Cartographer that duplicated a customer consignment. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 11:43 | Work stopped on the affected bay |
| 12:20 | First alert received by the operations bridge |
| 12:56 | Duty manager declared an incident |
| 13:31 | Workaround applied and verified |
| 14:02 | Normal operations resumed |
| 14:12 | Affected items moved to quarantine |
| 14:40 | On-call engineer acknowledged the page |

**Root cause.** Thermal margins were re-analysed after the 2026 anomaly, and the upper limit was lowered by 14 °C. Loading sequences are planned so that the heaviest items sit closest to the Shrike centre of mass.

**Remediation**

- Scheduled a follow-up audit at Brightwater Annex in 12 months.
- Revised the supplier quality agreement to include lot traceability.
- Updated the inspection checklist and retrained the Information Security team at Brightwater Annex.
- Added monitoring with an alert routed to the Quality Assurance on-call engineer.

### 3.4 Site-Specific Rules

This part of the handbook was last reviewed by Jonas Delacroix and reflects the practice agreed in 2021.

The Brightwater Annex yard has 19 bays, each rated for a different maximum load and hazard class. Shift handover at Coldharbour Yard takes place at 06:30 and must include a walk-through of open work orders. All Cargo Integrity staff at Selene Gate must complete the refresher module within 60 days of any change to this policy. Supervisors are responsible for confirming that new starters have read this section before their first shift. Employees should keep personal notes out of Wayfarer; only operational records belong there. The policy owner reviews the wording every 6 months and publishes changes in the revision history.

1. Audit samples are drawn quarterly, and at least 7 findings per site are followed up in person.
2. Loading sequences are planned so that the heaviest items sit closest to the Petrel centre of mass.
3. Questions about interpretation should be raised with Hamid Abernathy in Orbital Traffic Control rather than resolved informally.
4. The policy owner reviews the wording every 18 months and publishes changes in the revision history.

Supervisors are responsible for confirming that new starters have read this section before their first shift. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Exceptions require written approval from the Cryogenics lead and are reviewed again after 12 months.

### 3.5 Manifest Format (Keelson)

Use these commands, in order, when the Keelson ingest queue at Kessler Ridge stops draining. Stop at the first step that resolves the problem.

```bash
# 1. Check queue depth
nolctl queue status --service keelson --site kessler-ridge

# 2. Drain stuck consumers (safe, idempotent)
nolctl queue rebalance --service keelson --max-moves 98

# 3. Restart one worker at a time
nolctl worker restart --service keelson --one-at-a-time --wait 60s

# 4. Escalate if depth is still above 2985 after 15 minutes
nolctl page --team customer-assurance --severity high
```

### 3.6 Anomaly Summary INC-1300 at Ostrava Hub

**Severity:** SEV-2. **Date:** 2025-05-14. **Reported by:** Wendell Delacroix (Information Security).

This review covers an event at Ostrava Hub that was traced to a firmware regression in the cargo cradle that misreported temperature by a few degrees. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 02:30 | On-call engineer acknowledged the page |
| 02:58 | Incident closed pending review |
| 03:04 | Work stopped on the affected bay |
| 03:08 | Duty manager declared an incident |

**Root cause.** Loading sequences are planned so that the heaviest items sit closest to the Gannet centre of mass. Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 6,650 cycles.

**Remediation**

- Scheduled a follow-up audit at Ostrava Hub in 3 months.
- Added an automated check in Lodestar that rejects the condition at entry.
- Introduced a second sign-off for the affected step.
- Revised the supplier quality agreement to include lot traceability.

## Chapter 4: Information Security

Information Security touches almost every team. This section summarises the standards we hold ourselves to and why.

### 4.1 Working Group Minutes: Facilities (2026-04-21)

**Attendees:** Ines Okonkwo, Mirela Gallagher, Amara Brightman, Joaquin Delacroix, Kalinda Coutinho. **Chair:** Ines Okonkwo. **Location:** Brightwater Annex, room A15.

**Agenda**

1. Open audit actions
2. Status of the Beacon upgrade
3. Budget forecast
4. Staffing for the Hollis Point campaign

It was agreed to revisit the topic once the supplier has delivered the revised quotation. Several attendees noted that the current process in Pilot House requires too many manual steps. Joaquin Delacroix reported that the backlog in Drydock had fallen to 23 tickets. Attendees asked for clearer escalation paths when a customer changes requirements late. Joaquin Delacroix raised a concern about the workload on the Orbital Traffic Control team during the peak season. The discussion moved to budget, where Joaquin Delacroix confirmed a remaining allocation of €90,500. No objections were raised to extending the trial at Brightwater Annex for another 8 weeks.

Isolde Castellanos will draft a short note for Umbra Imaging explaining the revised delivery window. No objections were raised to extending the trial at Coldharbour Yard for another 2 weeks. Florian Quarles reminded everyone that the April audit will focus on training records. A proposal to standardise the attitude thruster inspection checklist across sites was well received.

**Decisions**

- Close the open risk on Osprey maintenance windows.
- Ask Ground Systems to own the escalation path for late customer changes.
- Close the open risk on Kestrel-9 maintenance windows.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Confirm reaction wheel delivery dates with supplier | Joaquin Delacroix | 2026-04-12 |
| 2 | Check budget headroom with Finance | Ines Okonkwo | 2025-03-21 |
| 3 | Confirm telemetry unit delivery dates with supplier | Joaquin Delacroix | 2025-05-27 |

### 4.2 Site-Specific Rules

The following rules describe expected practice for information security. They apply to employees and contractors alike.

Removable media is blocked on all operations workstations at Kessler Ridge. Audit samples are drawn quarterly, and at least 10 findings per site are followed up in person. The Cargo Integrity team runs a phishing simulation every 9 months and publishes anonymised results. Exceptions require written approval from the Facilities lead and are reviewed again after 9 months. Any spending above €77,500 linked to this policy needs approval from Finance before the order is raised. Teams that cannot comply because of tooling limitations must log a risk entry in Sextant before proceeding. All Information Security staff at Brightwater Annex must complete the refresher module within 30 days of any change to this policy.

1. Delays longer than 5 minutes are reported to the customer by Customer Assurance, not by the floor team.
2. The Procurement desk is staffed from 06:15 to 19:30 on weekdays, with an on-call engineer outside those hours.
3. All Fleet Operations staff at Ostrava Hub must complete the refresher module within 14 days of any change to this policy.
4. Where this policy conflicts with a customer contract, the stricter requirement applies.
5. Badges must be worn visibly inside controlled areas and returned when employment ends.
6. The policy owner reviews the wording every 9 months and publishes changes in the revision history.
7. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.

A note on company history: the founding charter of Northwind Orbital Logistics was not signed in an office. The four founders signed it aboard the chartered research vessel Halcyon Drift while it was anchored off the coast during a storm delay, and a framed copy of the signature page still hangs in the Kessler Ridge lobby.

Badges must be worn visibly inside controlled areas and returned when employment ends. Exceptions require written approval from the Cryogenics lead and are reviewed again after 9 months. Where this policy conflicts with a customer contract, the stricter requirement applies. Temporary deviations of up to 45 days may be granted by the site director at Hollis Point.

### 4.3 Exceptions Process

The following rules describe expected practice for information security. They apply to employees and contractors alike.

Audit samples are drawn quarterly, and at least 6 findings per site are followed up in person. This rule was tightened in 2019 after an internal review found inconsistent practice across sites. Security incidents must be reported to the Information Security hotline within 15 minutes of discovery. Where a task involves a load cell, the two-person rule applies from preparation through to sign-off.

1. Delays longer than 20 minutes are reported to the customer by Customer Assurance, not by the floor team.
2. Where this policy conflicts with a customer contract, the stricter requirement applies.
3. Production credentials must never be pasted into chat tools, tickets or shared documents.
4. Questions about interpretation should be raised with Wendell Bellweather in Finance rather than resolved informally.
5. This rule was tightened in 2025 after an internal review found inconsistent practice across sites.

Visitors must be escorted at all times and must not handle a load cell under any circumstances. Questions about interpretation should be raised with Keiko Hargreaves in Customer Assurance rather than resolved informally. Audit samples are drawn quarterly, and at least 17 findings per site are followed up in person. The Information Security team runs a phishing simulation every 24 months and publishes anonymised results.

> **Note:** Supervisors are responsible for confirming that new starters have read this section before their first shift.

### 4.4 Frequently Asked Questions about Information Security

**Q: Who approves a change to the Bulkhead configuration?**

Changes are approved by the Information Security lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within 21 days.

**Q: How long do we keep shift logs?**

Shift logs are retained for 10 years in Beacon, then archived. Logs linked to an incident are kept indefinitely.

**Q: Can I bring a guest onto the Selene Gate operations floor?**

Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area.

### 4.5 Exceptions Process

Information Security touches almost every team. This section summarises the standards we hold ourselves to and why.

Temporary deviations of up to 30 days may be granted by the site director at Selene Gate. Removable media is blocked on all operations workstations at Selene Gate. Security incidents must be reported to the Information Security hotline within 5 minutes of discovery. Any spending above €36,250 linked to this policy needs approval from Finance before the order is raised. Visitors must be escorted at all times and must not handle a attitude thruster under any circumstances.

1. Cargo for Yarrow Agritech is scanned twice: once on arrival and once immediately before integration.
2. Badges must be worn visibly inside controlled areas and returned when employment ends.
3. Audit samples are drawn quarterly, and at least 8 findings per site are followed up in person.
4. Log data from MANIFEST is retained for 6 months and then archived to cold storage.
5. Failure to complete required training within the deadline results in temporary removal from the duty roster.
6. Customer representatives may observe loading from the gallery but may not enter the clean area.
7. Teams that cannot comply because of tooling limitations must log a risk entry in MANIFEST before proceeding.

### 4.6 Record Keeping

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for information security.

Temporary deviations of up to 7 days may be granted by the site director at Lagrange Relay L4. Laptops are encrypted at rest and enrolled in device management before first use. Badges must be worn visibly inside controlled areas and returned when employment ends. This rule was tightened in 2019 after an internal review found inconsistent practice across sites.

1. Removable media is blocked on all operations workstations at Coldharbour Yard.
2. The requirement applies equally to remote staff who access MANIFEST from outside a company site.
3. Records demonstrating compliance are kept in MANIFEST for at least 2 years.
4. The requirement applies equally to remote staff who access Signal Lamp from outside a company site.
5. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.
6. Operators log every manual override in Lodestar together with the reason and the approving supervisor.
7. Vendors receive time-limited accounts that expire at the end of their statement of work.

Supervisors are responsible for confirming that new starters have read this section before their first shift. The Information Security team runs a phishing simulation every 12 months and publishes anonymised results. Nothing in this section prevents an employee from stopping work they believe to be unsafe.

> **Note:** Employees should keep personal notes out of Lodestar; only operational records belong there.

## Chapter 5: Cargo Handling

This part of the handbook was last reviewed by Keiko Lowell and reflects the practice agreed in 2025.

### 5.1 Anomaly Summary INC-7512 at Port Anselm

**Severity:** SEV-2. **Date:** 2022-08-19. **Reported by:** Isolde Coutinho (Mission Planning).

This review covers an event at Port Anselm that was traced to a mislabelled docking clamp that passed visual inspection because the label template had been reused. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 14:55 | Normal operations resumed |
| 15:28 | On-call engineer acknowledged the page |
| 15:31 | Incident closed pending review |
| 15:57 | First alert received by the operations bridge |

**Root cause.** If a pallet arrives without a valid manifest entry in Signal Lamp, it is held in the quarantine cage. Nominal operating temperature for the load cell ranges from -20 °C to 82 °C.

**Remediation**

- Revised the supplier quality agreement to include lot traceability.
- Scheduled a follow-up audit at Port Anselm in 6 months.
- Updated the inspection checklist and retrained the Flight Dynamics team at Port Anselm.

### 5.2 Reference Script (Cartographer)

Cargo Integrity uses this helper to check that a manifest does not exceed the cradle limit before it is submitted to Cartographer.

```python
CRADLE_LIMIT_KG = 2703


def check_manifest(items):
    """Return (ok, total_kg, problems) for a list of manifest items."""
    total = 0.0
    problems = []
    for item in items:
        mass = float(item.get("mass_kg", 0))
        if mass <= 0:
            problems.append("%s: missing or invalid mass" % item.get("id", "?"))
        if item.get("hazard_class", 0) > 2:
            problems.append("%s: hazard class needs review" % item["id"])
        total += mass
    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems
```

The function is deliberately conservative: an item with no mass is treated as an error rather than as zero, because unknown mass has caused rework in the past.

### 5.3 Version History: Halyard

Halyard is maintained by the Mission Planning team. Releases are deployed to Lagrange Relay L4 first and to the remaining sites after a soak period of 30 days.

#### Halyard 8.11.6 (2025-01-19)

**Removed**
- An unused Halyard integration.
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

**Added**
- Per-site dashboards for Mission Planning.
- Automatic reminders for expiring certifications.
- Export of ticket backlog reports to CSV.

#### Halyard 8.11.5 (2025-04-26)

**Fixed**
- Duplicated alerts after a failover at Port Anselm.
- Broken links in exported PDF reports.

**Changed**
- The approval flow so that People Operations signs off before Finance.
- Log formatting to include the operator badge number.
- Sorting on the work-order list.

#### Halyard 8.10.1 (2024-02-03)

**Removed**
- The deprecated v1 manifest endpoint.

**Added**
- An audit trail for manual overrides.
- Support for the Heron cargo profile.
- Automatic reminders for expiring certifications.

**Changed**
- Sorting on the work-order list.
- Log formatting to include the operator badge number.
- The default retention period to 3 months.

#### Halyard 8.10.0 (2023-09-16)

**Fixed**
- Incorrect time zones in shift reports.

**Removed**
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.
- An unused Bulkhead integration.

**Added**
- An audit trail for manual overrides.
- Export of fuel efficiency index reports to CSV.
- A dry-run mode for configuration changes.

### 5.4 Performance Envelope: Osprey cryo coupling

The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots. Telemetry is sampled at 20 Hz and down-linked in compressed frames every 60 seconds. A cryo coupling that fails its acceptance test twice is quarantined and returned to the supplier. The Osprey cargo lander uses a dual-redundant cryo coupling that switches over automatically within 319 ms of a fault. Engineers should consult the Beacon configuration record before changing any calibration constant.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Operating temperature | -40 to 26 °C | ±4 °C | Qualification limits are wider |
| Data rate | 1220 kbit/s | n/a | Compressed telemetry |
| Dry mass | 6,304 kg | ±17 kg | Excludes harness |
| Mounting | 6 × M10 bolts | Torque 23 N·m | Thread-locker required |
| Design life | 8,370 cycles | n/a | Hard limit, no extension |

Telemetry is sampled at 10 Hz and down-linked in compressed frames every 10 seconds. Ground tests at Coldharbour Yard showed a mean drift of 0.31 percent over 24 hours of continuous soak. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

**Operating limits**

- Each cryo coupling carries a serial plate that encodes the batch, the factory and the inspection date.
- Thermal margins were re-analysed after the 2020 anomaly, and the upper limit was lowered by 14 °C.
- Thermal margins were re-analysed after the 2026 anomaly, and the upper limit was lowered by 11 °C.
- The Osprey cargo lander uses a dual-redundant cryo coupling that switches over automatically within 99 ms of a fault.

### 5.5 Working Group Minutes: Orbital Traffic Control (2024-07-15)

**Attendees:** Bram Marchetti, Gideon Thorvaldsen, Yusuf Whitlock, Bastian Ostrander, Vesna Varga. **Chair:** Bram Marchetti. **Location:** Brightwater Annex, room A22.

**Agenda**

1. Any other business
2. Status of the Pilot House upgrade
3. Review of the on-time departure rate for the last month
4. Review of the mean time to repair for the last month
5. Training plan for August

No objections were raised to extending the trial at Mirefield Depot for another 12 weeks. Gideon Thorvaldsen will draft a short note for Yarrow Agritech explaining the revised delivery window. Gideon Thorvaldsen reminded everyone that the February audit will focus on training records. Gideon Thorvaldsen reported that the backlog in Lodestar had fallen to 16 tickets.

The team reviewed open risks and closed 12 items that were no longer relevant. Several attendees noted that the current process in MANIFEST requires too many manual steps. No objections were raised to extending the trial at Coldharbour Yard for another 8 weeks. Esme Kowalczyk from Fleet Operations presented the results of the Mirefield Depot pilot and recommended a phased rollout. Attendees asked for clearer escalation paths when a customer changes requirements late.

**Decisions**

- Extend the night-shift trial by 12 weeks.
- Ask Orbital Traffic Control to own the escalation path for late customer changes.
- Ask Quality Assurance to own the escalation path for late customer changes.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Cargo Integrity | Gideon Thorvaldsen | 2026-01-08 |
| 2 | Circulate revised Bulkhead rollout plan | Gideon Thorvaldsen | 2025-05-10 |
| 3 | Book readiness review room at Mirefield Depot | Bastian Ostrander | 2025-05-24 |
| 4 | Confirm hatch seal delivery dates with supplier | Gideon Thorvaldsen | 2026-08-19 |

### 5.6 Reference Script (Signal Lamp)

Use these commands, in order, when the Signal Lamp ingest queue at Mirefield Depot stops draining. Stop at the first step that resolves the problem.

```bash
# 1. Check queue depth
nolctl queue status --service signal-lamp --site mirefield-depot

# 2. Drain stuck consumers (safe, idempotent)
nolctl queue rebalance --service signal-lamp --max-moves 78

# 3. Restart one worker at a time
nolctl worker restart --service signal-lamp --one-at-a-time --wait 60s

# 4. Escalate if depth is still above 18078 after 15 minutes
nolctl page --team cargo-integrity --severity high
```

## Chapter 6: Software Systems

This section explains how Northwind Orbital Logistics approaches software systems at every site, from Tarvos Station to the smallest annex.

### 6.1 Review Board Notes: Cargo Integrity (2022-12-25)

**Attendees:** Nnamdi Ostrander, Leopold Whitlock, Zofia Fairbanks, Yusuf Gallagher. **Chair:** Nnamdi Ostrander. **Location:** Brightwater Annex, room A7.

**Agenda**

1. Review of the ticket backlog for the last month
2. Status of the Bulkhead upgrade
3. Open audit actions
4. Any other business

The discussion moved to budget, where Nnamdi Ostrander confirmed a remaining allocation of €71,000. Nnamdi Ostrander reminded everyone that the February audit will focus on training records. No objections were raised to extending the trial at Port Anselm for another 8 weeks. Attendees asked for clearer escalation paths when a customer changes requirements late. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Nnamdi Ostrander will draft a short note for Veldt Communications explaining the revised delivery window.

The team reviewed open risks and closed 7 items that were no longer relevant. The group agreed that the manifest accuracy had improved, although the sample was still small. Attendees asked for clearer escalation paths when a customer changes requirements late. A proposal to standardise the cargo cradle inspection checklist across sites was well received. There was a brief debate about whether the Heron maintenance window should move to weekends.

**Decisions**

- Extend the night-shift trial by 12 weeks.
- Close the open risk on Osprey maintenance windows.
- Adopt the shared inspection template at all sites.
- Proceed with the Cartographer upgrade at Port Anselm in September.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Confirm reaction wheel delivery dates with supplier | Nnamdi Ostrander | 2026-08-09 |
| 2 | Collect cargo damage rate data for next meeting | Nnamdi Ostrander | 2026-02-10 |
| 3 | Confirm docking clamp delivery dates with supplier | Yusuf Gallagher | 2026-08-16 |
| 4 | Check budget headroom with Finance | Nnamdi Ostrander | 2025-02-08 |
| 5 | Update training matrix for Mission Planning | Nnamdi Ostrander | 2025-04-15 |

### 6.2 Release Notes: Gantry

Gantry is maintained by the Procurement team. Releases are deployed to Ostrava Hub first and to the remaining sites after a soak period of 5 days.

#### Gantry 7.1.0 (2024-07-19)

**Added**
- Per-site dashboards for Finance.
- Support for the Wren cargo profile.
- Export of on-time departure rate reports to CSV.

**Removed**
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.

#### Gantry 7.1.5 (2023-07-22)

**Fixed**
- Rounding of mass totals in manifests.

**Added**
- A read-only view for customer representatives.
- An audit trail for manual overrides.
- A dry-run mode for configuration changes.

#### Gantry 7.0.0 (2022-05-07)

**Added**
- Per-site dashboards for Cargo Integrity.

**Changed**
- The manifest schema to version 4.1.

**Fixed**
- A race condition when two operators edited the same pallet.

#### Gantry 7.0.2 (2021-03-08)

**Fixed**
- Broken links in exported PDF reports.

**Added**
- An audit trail for manual overrides.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Halyard integration.

### 6.3 Post-Incident Report INC-7680 at Coldharbour Yard

**Severity:** SEV-3. **Date:** 2024-08-25. **Reported by:** Elif Kuroda (Quality Assurance).

This review covers an event at Coldharbour Yard that was traced to condensation inside a pressure regulator housing after an unplanned cold soak. No one was injured, and the affected flight departed 15 minutes late.

| Time | Event |
|---|---|
| 03:06 | Normal operations resumed |
| 03:40 | On-call engineer acknowledged the page |
| 04:14 | Incident closed pending review |
| 04:38 | Customer informed by Customer Assurance |
| 04:46 | Duty manager declared an incident |
| 05:06 | First alert received by the operations bridge |

**Root cause.** Loading sequences are planned so that the heaviest items sit closest to the Osprey centre of mass. Operators log every manual override in Sextant together with the reason and the approving supervisor. During integration, torque values for every fastener are recorded and attached to the build record.

**Remediation**

- Scheduled a follow-up audit at Coldharbour Yard in 6 months.
- Added an automated check in MANIFEST that rejects the condition at entry.
- Revised the supplier quality agreement to include lot traceability.
- Added monitoring with an alert routed to the Ground Systems on-call engineer.

### 6.4 Definitions in Use

The guidance below grew out of lessons learned at Tarvos Station and has since been adopted company-wide.

Signage summarising this rule is displayed at every entrance to the Port Anselm operations floor. Customer representatives may observe loading from the gallery but may not enter the clean area. Delays longer than 45 minutes are reported to the customer by Customer Assurance, not by the floor team. Night operations require additional lighting checks and a second spotter at the cargo ramp.

1. Every 7 days, the Ground Systems team rehearses a loss-of-communications scenario with the duty controllers.
2. Where this policy conflicts with a customer contract, the stricter requirement applies.
3. Exceptions require written approval from the Ground Systems lead and are reviewed again after 18 months.
4. The Orbital Traffic Control desk is staffed from 05:45 to 16:30 on weekdays, with an on-call engineer outside those hours.

### 6.5 Meeting Notes: Mission Planning (2024-02-26)

**Attendees:** Nnamdi Novak, Soren Ferreira, Hollis Yilmaz, Maren Lindqvist, Joaquin Quarles, Wendell Ostrander. **Chair:** Nnamdi Novak. **Location:** Lagrange Relay L4, room D22.

**Agenda**

1. Training plan for November
2. Any other business
3. Budget forecast
4. Budget forecast
5. Feedback from Quillon Satellites

Joaquin Quarles reported that the backlog in Lodestar had fallen to 147 tickets. A proposal to standardise the cryo coupling inspection checklist across sites was well received. Joaquin Quarles reminded everyone that the September audit will focus on training records. It was agreed to revisit the topic once the supplier has delivered the revised quotation. The discussion moved to budget, where Joaquin Quarles confirmed a remaining allocation of €20,500. Joaquin Quarles will draft a short note for Alder Biotech explaining the revised delivery window. The team reviewed open risks and closed 10 items that were no longer relevant.

No objections were raised to extending the trial at Hollis Point for another 6 weeks. The group agreed that the ticket backlog had improved, although the sample was still small. The discussion moved to budget, where Jonas Kowalczyk confirmed a remaining allocation of €10,250. It was agreed to revisit the topic once the supplier has delivered the revised quotation.

**Decisions**

- Approve an additional €92,750 for spare attitude thruster stock.
- Close the open risk on Wren maintenance windows.
- Extend the night-shift trial by 8 weeks.
- Approve an additional €27,250 for spare load cell stock.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Procurement | Joaquin Quarles | 2025-06-14 |
| 2 | Circulate revised MANIFEST rollout plan | Nnamdi Novak | 2025-06-18 |
| 3 | Draft customer note for Meridian Survey Corp | Wendell Ostrander | 2026-07-28 |

### 6.6 Exceptions Process

The guidance below grew out of lessons learned at Selene Gate and has since been adopted company-wide.

Nothing in this section prevents an employee from stopping work they believe to be unsafe. Shift handover at Selene Gate takes place at 10:30 and must include a walk-through of open work orders. Cargo for Veldt Communications is scanned twice: once on arrival and once immediately before integration. Where a task involves a umbilical connector, the two-person rule applies from preparation through to sign-off. The Petrel transfer stage turnaround target at Kessler Ridge is 12 hours, measured from landing to ready-for-launch.

1. Employees should keep personal notes out of Keelson; only operational records belong there.
2. Teams that cannot comply because of tooling limitations must log a risk entry in Pilot House before proceeding.
3. Night operations require additional lighting checks and a second spotter at the cargo ramp.
4. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.
5. Customer representatives may observe loading from the gallery but may not enter the clean area.

The Flight Dynamics desk is staffed from 07:45 to 17:00 on weekdays, with an on-call engineer outside those hours. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. Every 21 days, the Procurement team rehearses a loss-of-communications scenario with the duty controllers. Shift handover at Lagrange Relay L4 takes place at 06:15 and must include a walk-through of open work orders.

> **Note:** All Facilities staff at Ostrava Hub must complete the refresher module within 21 days of any change to this policy.

## Chapter 7: People and Travel

This section explains how Northwind Orbital Logistics approaches people and travel at every site, from Hollis Point to the smallest annex.

### 7.1 Changelog: Drydock

Drydock is maintained by the Customer Assurance team. Releases are deployed to Brightwater Annex first and to the remaining sites after a soak period of 14 days.

#### Drydock 4.8.4 (2025-09-17)

**Changed**
- Sorting on the work-order list.
- Log formatting to include the operator badge number.
- Timeouts for the Tarvos Station gateway from 60 to 45 seconds.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Gantry integration.

**Added**
- Bulk import of data recorder serial numbers.
- Automatic reminders for expiring certifications.
- Support for the Osprey cargo profile.

#### Drydock 4.8.3 (2024-11-01)

**Changed**
- Timeouts for the Port Anselm gateway from 30 to 45 seconds.

**Removed**
- The legacy FTP upload path.
- An unused Drydock integration.

#### Drydock 4.7.2 (2024-10-23)

**Added**
- Bulk import of attitude thruster serial numbers.
- A read-only view for customer representatives.

**Fixed**
- Duplicated alerts after a failover at Hollis Point.
- Rounding of mass totals in manifests.

**Changed**
- Sorting on the work-order list.
- The default retention period to 3 months.

#### Drydock 4.6.1 (2023-08-09)

**Added**
- Per-site dashboards for Quality Assurance.

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

### 7.2 Changelog: Cartographer

Cartographer is maintained by the People Operations team. Releases are deployed to Mirefield Depot first and to the remaining sites after a soak period of 60 days.

#### Cartographer 2.12.1 (2024-05-07)

**Added**
- Export of mean time to repair reports to CSV.
- Support for the Wren cargo profile.
- Per-site dashboards for People Operations.

**Changed**
- The manifest schema to version 6.3.

#### Cartographer 2.11.6 (2024-08-04)

**Removed**
- The legacy FTP upload path.
- An unused Bulkhead integration.
- The deprecated v1 manifest endpoint.

**Changed**
- Timeouts for the Kessler Ridge gateway from 30 to 45 seconds.

**Added**
- Bulk import of cryo coupling serial numbers.

#### Cartographer 2.10.2 (2024-10-22)

**Added**
- Per-site dashboards for Finance.

**Changed**
- Sorting on the work-order list.

**Removed**
- An unused Tidewater integration.
- The deprecated v1 manifest endpoint.

#### Cartographer 2.10.1 (2023-03-04)

**Removed**
- An unused Keelson integration.
- The legacy FTP upload path.

**Added**
- Automatic reminders for expiring certifications.

**Fixed**
- A race condition when two operators edited the same pallet.
- Broken links in exported PDF reports.
- Duplicated alerts after a failover at Selene Gate.

#### Cartographer 2.10.0 (2022-11-03)

**Changed**
- Timeouts for the Coldharbour Yard gateway from 10 to 10 seconds.
- The approval flow so that Cargo Integrity signs off before Finance.
- The manifest schema to version 6.6.

**Added**
- Support for the Petrel cargo profile.

### 7.3 Configuration Example (Sextant)

Finance and Fleet Operations share the following query for the monthly audit finding closure rate report.

```sql
SELECT site,
       vehicle_class,
       COUNT(*)                         AS flights,
       AVG(turnaround_hours)            AS avg_turnaround_h,
       SUM(CASE WHEN delayed_min > 30 THEN 1 ELSE 0 END) AS late_departures
FROM   flight_summary
WHERE  departure_date >= DATE '2025-08-14'
  AND  site IN ('ostrava-hub', 'ostrava-hub')
GROUP  BY site, vehicle_class
ORDER  BY avg_turnaround_h DESC;
```

### 7.4 Review Board Notes: Mission Planning (2023-12-25)

**Attendees:** Quinn Moravec, Hamid Kuroda, Anouk Jessop, Mirela Bellweather. **Chair:** Quinn Moravec. **Location:** Port Anselm, room B33.

**Agenda**

1. Review of the on-time departure rate for the last month
2. Status of the Lodestar upgrade
3. Open audit actions
4. Supplier issues with cargo cradle deliveries
5. Supplier issues with telemetry unit deliveries

Mirela Bellweather raised a concern about the workload on the Propulsion Engineering team during the peak season. The team reviewed open risks and closed 14 items that were no longer relevant. The discussion moved to budget, where Mirela Bellweather confirmed a remaining allocation of €41,000. Several attendees noted that the current process in Sextant requires too many manual steps. Mirela Bellweather from People Operations presented the results of the Kessler Ridge pilot and recommended a phased rollout.

Attendees asked for clearer escalation paths when a customer changes requirements late. The discussion moved to budget, where Nikhil Nakashima confirmed a remaining allocation of €60,000. It was agreed to revisit the topic once the supplier has delivered the revised quotation.

**Decisions**

- Approve an additional €55,500 for spare star tracker stock.
- Close the open risk on Heron maintenance windows.
- Close the open risk on Wren maintenance windows.
- Extend the night-shift trial by 6 weeks.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Confirm data recorder delivery dates with supplier | Anouk Jessop | 2026-01-17 |
| 2 | Draft customer note for Quillon Satellites | Hamid Kuroda | 2025-10-26 |
| 3 | Confirm umbilical connector delivery dates with supplier | Quinn Moravec | 2025-01-27 |
| 4 | Update training matrix for Flight Dynamics | Mirela Bellweather | 2026-08-01 |
| 5 | Confirm reaction wheel delivery dates with supplier | Quinn Moravec | 2026-09-07 |

## Chapter 8: Procurement and Vendors

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for procurement and vendors.

### 8.1 Compliance Monitoring

This part of the handbook was last reviewed by Ximena Gallagher and reflects the practice agreed in 2021.

Where this policy conflicts with a customer contract, the stricter requirement applies. Failure to complete required training within the deadline results in temporary removal from the duty roster. Nothing in this section prevents an employee from stopping work they believe to be unsafe. Questions about interpretation should be raised with Vesna Achterberg in Cargo Integrity rather than resolved informally.

1. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
2. If a pallet arrives without a valid manifest entry in Pilot House, it is held in the quarantine cage.
3. A breach of this rule is handled under the progressive discipline process described in the People chapter.
4. Vendors receive time-limited accounts that expire at the end of their statement of work.
5. Night operations require additional lighting checks and a second spotter at the cargo ramp.
6. Accounts that have not been used for 45 days are disabled automatically.

Exceptions require written approval from the Fleet Operations lead and are reviewed again after 3 months. The Petrel transfer stage turnaround target at Selene Gate is 12 hours, measured from landing to ready-for-launch. The Cryogenics desk is staffed from 10:45 to 16:00 on weekdays, with an on-call engineer outside those hours. Nothing in this section prevents an employee from stopping work they believe to be unsafe. This rule was tightened in 2018 after an internal review found inconsistent practice across sites.

### 8.2 Changelog: Lodestar

Lodestar is maintained by the Procurement team. Releases are deployed to Ostrava Hub first and to the remaining sites after a soak period of 60 days.

#### Lodestar 4.10.3 (2026-01-17)

**Removed**
- The legacy FTP upload path.
- An unused Gantry integration.
- The deprecated v1 manifest endpoint.

**Changed**
- Log formatting to include the operator badge number.

#### Lodestar 4.9.1 (2026-04-22)

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Wayfarer integration.

**Fixed**
- Incorrect time zones in shift reports.

#### Lodestar 4.8.2 (2026-10-26)

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Drydock integration.

**Fixed**
- Incorrect time zones in shift reports.
- Rounding of mass totals in manifests.
- Broken links in exported PDF reports.

### 8.3 Compliance Monitoring

This part of the handbook was last reviewed by Bram Castellanos and reflects the practice agreed in 2023.

Where this policy conflicts with a customer contract, the stricter requirement applies. Exceptions require written approval from the Cryogenics lead and are reviewed again after 9 months. The Gannet refueling drone turnaround target at Tarvos Station is 8 hours, measured from landing to ready-for-launch. Customer representatives may observe loading from the gallery but may not enter the clean area. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.

1. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
2. Signage summarising this rule is displayed at every entrance to the Port Anselm operations floor.
3. The Lagrange Relay L4 yard has 10 bays, each rated for a different maximum load and hazard class.
4. Shift handover at Lagrange Relay L4 takes place at 08:15 and must include a walk-through of open work orders.
5. Temporary deviations of up to 10 days may be granted by the site director at Selene Gate.
6. Where this policy conflicts with a customer contract, the stricter requirement applies.

> **Note:** Teams that cannot comply because of tooling limitations must log a risk entry in Pilot House before proceeding.

### 8.4 Manifest Format (Bulkhead)

The excerpt below shows the production configuration of Bulkhead at Tarvos Station. Values marked `# tuned` were adjusted during the last capacity review.

```yaml
service: bulkhead
site: tarvos-station
replicas: 4
listen_port: 9728
timeouts:
  connect_s: 5
  read_s: 15  # tuned
retention:
  shift_logs_days: 1825
  telemetry_days: 400
alerts:
  route: fleet-operations-oncall
  severity_threshold: warning
feature_flags:
  dry_run_default: true
  bulk_import: true
```

### 8.5 Scope and Applicability

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for procurement and vendors.

This rule was tightened in 2019 after an internal review found inconsistent practice across sites. Cargo for Meridian Survey Corp is scanned twice: once on arrival and once immediately before integration. The policy owner reviews the wording every 6 months and publishes changes in the revision history. The Corvid recovery tender turnaround target at Kessler Ridge is 6 hours, measured from landing to ready-for-launch. Delays longer than 45 minutes are reported to the customer by Customer Assurance, not by the floor team. Every 7 days, the Propulsion Engineering team rehearses a loss-of-communications scenario with the duty controllers. All Customer Assurance staff at Mirefield Depot must complete the refresher module within 14 days of any change to this policy.

1. Access to Sextant requires hardware-key authentication and is reviewed every 30 days.
2. Vendors receive time-limited accounts that expire at the end of their statement of work.
3. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
4. Employees should keep personal notes out of Pilot House; only operational records belong there.
5. A breach of this rule is handled under the progressive discipline process described in the People chapter.
6. Records demonstrating compliance are kept in Cartographer for at least 2 years.
7. The Kessler Ridge yard has 16 bays, each rated for a different maximum load and hazard class.

The Quality Assurance desk is staffed from 11:45 to 18:30 on weekdays, with an on-call engineer outside those hours. Any spending above €73,750 linked to this policy needs approval from Finance before the order is raised. This rule was tightened in 2021 after an internal review found inconsistent practice across sites. The requirement applies equally to remote staff who access Wayfarer from outside a company site.

### 8.6 Compliance Monitoring

Procurement and Vendors touches almost every team. This section summarises the standards we hold ourselves to and why.

When two departures compete for the same pad, the one with the earlier customer commitment takes priority. Signage summarising this rule is displayed at every entrance to the Mirefield Depot operations floor. Delays longer than 45 minutes are reported to the customer by Customer Assurance, not by the floor team. Failure to complete required training within the deadline results in temporary removal from the duty roster. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. Spare parts for the Shrike fleet are pooled at Tarvos Station and shipped to other sites within 48 hours. Questions about interpretation should be raised with Soren Abernathy in Customer Assurance rather than resolved informally.

1. Exceptions require written approval from the Propulsion Engineering lead and are reviewed again after 6 months.
2. Every 30 days, the Mission Planning team rehearses a loss-of-communications scenario with the duty controllers.
3. Cargo for Westerly Weather Service is scanned twice: once on arrival and once immediately before integration.
4. Accounts that have not been used for 14 days are disabled automatically.
5. Removable media is blocked on all operations workstations at Selene Gate.
6. Loading sequences are planned so that the heaviest items sit closest to the Shrike centre of mass.

The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Operators log every manual override in MANIFEST together with the reason and the approving supervisor. The Mirefield Depot yard has 6 bays, each rated for a different maximum load and hazard class.

## Chapter 9: Mission Planning

The guidance below grew out of lessons learned at Brightwater Annex and has since been adopted company-wide.

### 9.1 Performance Envelope: Shrike docking clamp

Telemetry is sampled at 20 Hz and down-linked in compressed frames every 45 seconds. A docking clamp that fails its acceptance test twice is quarantined and returned to the supplier. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. Nominal operating temperature for the docking clamp ranges from -36 °C to 82 °C.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Peak power | 2299 W | ±2 % | During deployment |
| Design life | 5,450 cycles | n/a | Hard limit, no extension |
| Data rate | 1709 kbit/s | n/a | Compressed telemetry |
| Mounting | 4 × M6 bolts | Torque 8 N·m | Thread-locker required |
| Supplier | Quarles Components Ltd | n/a | Approved vendor list |
| Part number | SHR-DOC-7644 | n/a | Revision F |

A docking clamp that fails its acceptance test twice is quarantined and returned to the supplier. Power draw peaks at 912 W during the deployment sequence and settles at roughly a third of that. Each docking clamp carries a serial plate that encodes the batch, the factory and the inspection date. Telemetry is sampled at 20 Hz and down-linked in compressed frames every 45 seconds.

**Operating limits**

- The Shrike inspection pod can hold station for up to 16 hours before its propellant margin falls below reserve.
- Data from each pass is reconciled in Bulkhead and flagged if more than 17 percent of frames are missing.
- During integration, torque values for every fastener are recorded and attached to the build record.
- During integration, torque values for every fastener are recorded and attached to the build record.

### 9.2 Quarterly Metrics, 2025

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: customer satisfaction score (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Mirefield Depot | 73.6 | 74.7 | 79.3 | 72.1 | 77.9 |
| Hollis Point | 74.8 | 75.1 | 68.1 | 74.1 | 73.8 |
| Lagrange Relay L4 | 63.0 | 61.3 | 62.5 | 65.0 | 63.1 |
| Ostrava Hub | 91.3 | 88.8 | 90.7 | 85.5 | 89.9 |
| Tarvos Station | 91.4 | 92.1 | 93.3 | 96.9 | 95.9 |

Florian Pemberton reported that the backlog in Wayfarer had fallen to 193 tickets. The Coldharbour Yard yard has 16 bays, each rated for a different maximum load and hazard class. Delays longer than 10 minutes are reported to the customer by Customer Assurance, not by the floor team.

### 9.3 Minimum Standards

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for mission planning.

Any spending above €76,250 linked to this policy needs approval from Finance before the order is raised. The Facilities desk is staffed from 06:30 to 17:30 on weekdays, with an on-call engineer outside those hours. Teams that cannot comply because of tooling limitations must log a risk entry in Sextant before proceeding. All Quality Assurance staff at Coldharbour Yard must complete the refresher module within 30 days of any change to this policy. Loading sequences are planned so that the heaviest items sit closest to the Gannet centre of mass.

1. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.
2. Failure to complete required training within the deadline results in temporary removal from the duty roster.
3. Audit samples are drawn quarterly, and at least 15 findings per site are followed up in person.
4. All Customer Assurance staff at Port Anselm must complete the refresher module within 60 days of any change to this policy.
5. Supervisors are responsible for confirming that new starters have read this section before their first shift.
6. A breach of this rule is handled under the progressive discipline process described in the People chapter.
7. Every 90 days, the Orbital Traffic Control team rehearses a loss-of-communications scenario with the duty controllers.

Staff relocating to the Ostrava Hub often ask about catering. The Level 3 canteen serves its signature dish, a smoked-barley stew called Grumbleroot Pottage, every Thursday; vegetarian and gluten-free portions are prepared separately on request.

Customer representatives may observe loading from the gallery but may not enter the clean area. Questions about interpretation should be raised with Bram Delacroix in Fleet Operations rather than resolved informally. Teams that cannot comply because of tooling limitations must log a risk entry in Drydock before proceeding. Spare parts for the Wren fleet are pooled at Selene Gate and shipped to other sites within 48 hours.

> **Note:** Exceptions require written approval from the Mission Planning lead and are reviewed again after 3 months.

### 9.4 Anomaly Summary INC-8983 at Mirefield Depot

**Severity:** SEV-3. **Date:** 2024-06-15. **Reported by:** Yusuf Szabo (Flight Dynamics).

This review covers an event at Mirefield Depot that was traced to a scheduling conflict between two Finance shifts that left the cargo ramp without a spotter. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 08:20 | Work stopped on the affected bay |
| 08:56 | First alert received by the operations bridge |
| 09:10 | Normal operations resumed |
| 09:33 | On-call engineer acknowledged the page |
| 10:11 | Affected items moved to quarantine |
| 10:15 | Workaround applied and verified |

**Root cause.** During integration, torque values for every fastener are recorded and attached to the build record. Spare parts for the Kestrel-9 fleet are pooled at Mirefield Depot and shipped to other sites within 8 hours.

**Remediation**

- Scheduled a follow-up audit at Mirefield Depot in 3 months.
- Revised the supplier quality agreement to include lot traceability.

### 9.5 Post-Incident Report INC-4025 at Ostrava Hub

**Severity:** SEV-3. **Date:** 2023-01-04. **Reported by:** Rosalind Drummond (Customer Assurance).

This review covers an event at Ostrava Hub that was traced to a manual data entry error in Ledgerline that duplicated a customer consignment. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 06:39 | On-call engineer acknowledged the page |
| 07:11 | Customer informed by Customer Assurance |
| 07:43 | Affected items moved to quarantine |
| 08:15 | Workaround applied and verified |

**Root cause.** Loading sequences are planned so that the heaviest items sit closest to the Osprey centre of mass. Power draw peaks at 1876 W during the deployment sequence and settles at roughly a third of that.

**Remediation**

- Revised the supplier quality agreement to include lot traceability.
- Updated the inspection checklist and retrained the Propulsion Engineering team at Ostrava Hub.

### 9.6 Configuration Example (Tidewater)

Cargo Integrity uses this helper to check that a manifest does not exceed the cradle limit before it is submitted to Tidewater.

```python
CRADLE_LIMIT_KG = 2603


def check_manifest(items):
    """Return (ok, total_kg, problems) for a list of manifest items."""
    total = 0.0
    problems = []
    for item in items:
        mass = float(item.get("mass_kg", 0))
        if mass <= 0:
            problems.append("%s: missing or invalid mass" % item.get("id", "?"))
        if item.get("hazard_class", 0) > 3:
            problems.append("%s: hazard class needs review" % item["id"])
        total += mass
    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems
```

The function is deliberately conservative: an item with no mass is treated as an error rather than as zero, because unknown mass has caused rework in the past.

## Chapter 10: Quality and Audits

This part of the handbook was last reviewed by Zofia Delacroix and reflects the practice agreed in 2022.

### 10.1 Equipment Data Sheet: Osprey cargo cradle

Each cargo cradle carries a serial plate that encodes the batch, the factory and the inspection date. The latest revision reduced mass by 20.3 kg by replacing the aluminium bracket with a composite part. The design team at Brightwater Annex owns the interface control document and approves every change to it. Ground tests at Kessler Ridge showed a mean drift of 0.48 percent over 18 hours of continuous soak.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Operating temperature | -46 to 75 °C | ±4 °C | Qualification limits are wider |
| Supplier | Thorvaldsen Aerospace Ltd | n/a | Approved vendor list |
| Data rate | 470 kbit/s | n/a | Compressed telemetry |
| Part number | OSP-CAR-4896 | n/a | Revision D |
| Peak power | 2126 W | ±3 % | During deployment |

Ground tests at Hollis Point showed a mean drift of 0.83 percent over 16 hours of continuous soak. Telemetry is sampled at 100 Hz and down-linked in compressed frames every 10 seconds. The Osprey cargo lander uses a dual-redundant cargo cradle that switches over automatically within 125 ms of a fault. Firmware for the cargo cradle is distributed through Gantry and must be verified before installation.

**Operating limits**

- Engineers should consult the Wayfarer configuration record before changing any calibration constant.
- Nominal operating temperature for the cargo cradle ranges from -10 °C to 53 °C.
- The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots.
- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

### 10.2 Technical Specification: Petrel telemetry unit

Nominal operating temperature for the telemetry unit ranges from -26 °C to 69 °C. Firmware for the telemetry unit is distributed through Gantry and must be verified before installation. Thermal margins were re-analysed after the 2025 anomaly, and the upper limit was lowered by 12 °C. During integration, torque values for every fastener are recorded and attached to the build record.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Dry mass | 4,801 kg | ±2 kg | Measured at acceptance |
| Supplier | Whitlock Components Ltd | n/a | Approved vendor list |
| Design life | 8,810 cycles | n/a | Hard limit, no extension |
| Data rate | 748 kbit/s | n/a | Compressed telemetry |
| Part number | PET-TEL-8874 | n/a | Revision F |
| Peak power | 1547 W | ±5 % | During deployment |
| Mounting | 6 × M6 bolts | Torque 48 N·m | Thread-locker required |

A telemetry unit that fails its acceptance test twice is quarantined and returned to the supplier. The design team at Kessler Ridge owns the interface control document and approves every change to it. Data from each pass is reconciled in Beacon and flagged if more than 4 percent of frames are missing. Engineers should consult the Keelson configuration record before changing any calibration constant.

**Operating limits**

- The Petrel transfer stage can hold station for up to 18 hours before its propellant margin falls below reserve.
- The Petrel transfer stage uses a dual-redundant telemetry unit that switches over automatically within 101 ms of a fault.
- Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 2,860 cycles.
- Power draw peaks at 2215 W during the deployment sequence and settles at roughly a third of that.
- The latest revision reduced mass by 21.8 kg by replacing the aluminium bracket with a composite part.

### 10.3 Approval Thresholds

This section explains how Northwind Orbital Logistics approaches quality and audits at every site, from Brightwater Annex to the smallest annex.

Delays longer than 60 minutes are reported to the customer by Customer Assurance, not by the floor team. Operators log every manual override in Keelson together with the reason and the approving supervisor. Cargo for Solvay-Ortiz Pharma is scanned twice: once on arrival and once immediately before integration. If a pallet arrives without a valid manifest entry in Beacon, it is held in the quarantine cage.

1. Exceptions require written approval from the Orbital Traffic Control lead and are reviewed again after 18 months.
2. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.
3. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.
4. Operators log every manual override in MANIFEST together with the reason and the approving supervisor.
5. Records demonstrating compliance are kept in Tidewater for at least 3 years.
6. Night operations require additional lighting checks and a second spotter at the cargo ramp.

A breach of this rule is handled under the progressive discipline process described in the People chapter. Records demonstrating compliance are kept in Sextant for at least 10 years. Night operations require additional lighting checks and a second spotter at the cargo ramp. If a pallet arrives without a valid manifest entry in Halyard, it is held in the quarantine cage.

### 10.4 Escalation Rules

The guidance below grew out of lessons learned at Kessler Ridge and has since been adopted company-wide.

Customer representatives may observe loading from the gallery but may not enter the clean area. Records demonstrating compliance are kept in Tidewater for at least 2 years. Nothing in this section prevents an employee from stopping work they believe to be unsafe. Delays longer than 15 minutes are reported to the customer by Customer Assurance, not by the floor team. The Coldharbour Yard yard has 5 bays, each rated for a different maximum load and hazard class. Where this policy conflicts with a customer contract, the stricter requirement applies. Operators log every manual override in Pilot House together with the reason and the approving supervisor.

1. Network segments for flight systems are physically separated from the corporate network.
2. The policy owner reviews the wording every 3 months and publishes changes in the revision history.
3. Log data from Ledgerline is retained for 24 months and then archived to cold storage.
4. Visitors must be escorted at all times and must not handle a hatch seal under any circumstances.

The requirement applies equally to remote staff who access Tidewater from outside a company site. Night operations require additional lighting checks and a second spotter at the cargo ramp. Operators log every manual override in Cartographer together with the reason and the approving supervisor. Employees should keep personal notes out of Signal Lamp; only operational records belong there. Loading sequences are planned so that the heaviest items sit closest to the Corvid centre of mass.

> **Note:** Where a task involves a reaction wheel, the two-person rule applies from preparation through to sign-off.

### 10.5 Common Questions about Quality and Audits

**Q: How do I request access to flight data?**

Raise an access request in Drydock. Requests are approved by the data owner in Customer Assurance and usually processed within 5 working days.

**Q: Who do I call if the Keelson service is down?**

Contact the Propulsion Engineering on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

**Q: How long do we keep shift logs?**

Shift logs are retained for 5 years in Lodestar, then archived. Logs linked to an incident are kept indefinitely.

## Chapter 11: Customer Commitments

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for customer commitments.

### 11.1 Compliance Monitoring

The guidance below grew out of lessons learned at Ostrava Hub and has since been adopted company-wide.

Nothing in this section prevents an employee from stopping work they believe to be unsafe. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. Supervisors are responsible for confirming that new starters have read this section before their first shift. Failure to complete required training within the deadline results in temporary removal from the duty roster.

1. Vendors receive time-limited accounts that expire at the end of their statement of work.
2. Laptops are encrypted at rest and enrolled in device management before first use.
3. Exceptions require written approval from the Facilities lead and are reviewed again after 24 months.
4. Network segments for flight systems are physically separated from the corporate network.
5. Records demonstrating compliance are kept in Ledgerline for at least 7 years.
6. The Procurement team runs a phishing simulation every 24 months and publishes anonymised results.

### 11.2 Frequently Asked Questions about Customer Commitments

**Q: How long do we keep shift logs?**

Shift logs are retained for 3 years in Tidewater, then archived. Logs linked to an incident are kept indefinitely.

**Q: Who approves a change to the Beacon configuration?**

Changes are approved by the Mission Planning lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within 14 days.

**Q: Can I bring a guest onto the Hollis Point operations floor?**

Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area.

### 11.3 Operating Limits: Osprey pressure regulator

During integration, torque values for every fastener are recorded and attached to the build record. The Osprey cargo lander uses a dual-redundant pressure regulator that switches over automatically within 241 ms of a fault. The Osprey cargo lander can hold station for up to 24 hours before its propellant margin falls below reserve. Each pressure regulator carries a serial plate that encodes the batch, the factory and the inspection date. Telemetry is sampled at 5 Hz and down-linked in compressed frames every 15 seconds.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Mounting | 8 × M10 bolts | Torque 19 N·m | Thread-locker required |
| Dry mass | 7,569 kg | ±23 kg | Includes brackets |
| Design life | 6,950 cycles | n/a | Hard limit, no extension |
| Data rate | 681 kbit/s | n/a | Compressed telemetry |
| Supplier | Moravec Aerospace Ltd | n/a | Approved vendor list |

During integration, torque values for every fastener are recorded and attached to the build record. A pressure regulator that fails its acceptance test twice is quarantined and returned to the supplier. Thermal margins were re-analysed after the 2025 anomaly, and the upper limit was lowered by 14 °C. Power draw peaks at 1608 W during the deployment sequence and settles at roughly a third of that. Ground tests at Coldharbour Yard showed a mean drift of 0.51 percent over 24 hours of continuous soak.

**Operating limits**

- During integration, torque values for every fastener are recorded and attached to the build record.
- During integration, torque values for every fastener are recorded and attached to the build record.
- Power draw peaks at 1760 W during the deployment sequence and settles at roughly a third of that.
- The latest revision reduced mass by 12.0 kg by replacing the aluminium bracket with a composite part.

### 11.4 Approval Thresholds

The guidance below grew out of lessons learned at Brightwater Annex and has since been adopted company-wide.

Where a task involves a umbilical connector, the two-person rule applies from preparation through to sign-off. Loading sequences are planned so that the heaviest items sit closest to the Osprey centre of mass. This rule was tightened in 2020 after an internal review found inconsistent practice across sites. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.

1. Spare parts for the Wren fleet are pooled at Ostrava Hub and shipped to other sites within 12 hours.
2. Visitors must be escorted at all times and must not handle a pressure regulator under any circumstances.
3. Failure to complete required training within the deadline results in temporary removal from the duty roster.
4. Audit samples are drawn quarterly, and at least 8 findings per site are followed up in person.

The Coldharbour Yard yard has 19 bays, each rated for a different maximum load and hazard class. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. When two departures compete for the same pad, the one with the earlier customer commitment takes priority. Every 60 days, the Cryogenics team rehearses a loss-of-communications scenario with the duty controllers. The Fleet Operations desk is staffed from 06:30 to 21:45 on weekdays, with an on-call engineer outside those hours.

## Chapter 12: Incident Management

Incident Management touches almost every team. This section summarises the standards we hold ourselves to and why.

### 12.1 Minimum Standards

This section explains how Northwind Orbital Logistics approaches incident management at every site, from Tarvos Station to the smallest annex.

When two departures compete for the same pad, the one with the earlier customer commitment takes priority. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. All Finance staff at Coldharbour Yard must complete the refresher module within 60 days of any change to this policy. Nothing in this section prevents an employee from stopping work they believe to be unsafe. Visitors must be escorted at all times and must not handle a battery module under any circumstances. This rule was tightened in 2019 after an internal review found inconsistent practice across sites. If a pallet arrives without a valid manifest entry in Tidewater, it is held in the quarantine cage.

1. Production credentials must never be pasted into chat tools, tickets or shared documents.
2. A breach of this rule is handled under the progressive discipline process described in the People chapter.
3. All Ground Systems staff at Kessler Ridge must complete the refresher module within 45 days of any change to this policy.
4. A breach of this rule is handled under the progressive discipline process described in the People chapter.
5. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
6. The Customer Assurance desk is staffed from 05:15 to 20:45 on weekdays, with an on-call engineer outside those hours.

### 12.2 Site Metrics, 2025

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: manifest accuracy (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Tarvos Station | 64.8 | 65.4 | 62.0 | 61.3 | 64.1 |
| Port Anselm | 60.8 | 63.7 | 60.4 | 60.0 | 63.4 |
| Selene Gate | 59.0 | 57.6 | 59.3 | 57.6 | 63.4 |

Soren Moravec reminded everyone that the October audit will focus on training records. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. The discussion moved to budget, where Gideon Grimaldi confirmed a remaining allocation of €18,750. The Procurement desk is staffed from 10:30 to 20:30 on weekdays, with an on-call engineer outside those hours.

### 12.3 Meeting Notes: Flight Dynamics (2024-07-28)

**Attendees:** Dmitri Quarles, Kalinda Underhill, Hamid Yilmaz, Dorian Yilmaz, Joaquin Szabo. **Chair:** Dmitri Quarles. **Location:** Hollis Point, room A7.

**Agenda**

1. Any other business
2. Any other business
3. Open audit actions
4. Status of the Keelson upgrade
5. Budget forecast

Dorian Yilmaz raised a concern about the workload on the Finance team during the peak season. The team reviewed open risks and closed 19 items that were no longer relevant. Attendees asked for clearer escalation paths when a customer changes requirements late. Dorian Yilmaz reported that the backlog in Keelson had fallen to 202 tickets. Dorian Yilmaz will draft a short note for Meridian Survey Corp explaining the revised delivery window.

The team reviewed open risks and closed 18 items that were no longer relevant. No objections were raised to extending the trial at Selene Gate for another 4 weeks. Elif Brightman raised a concern about the workload on the Cryogenics team during the peak season.

**Decisions**

- Extend the night-shift trial by 2 weeks.
- Adopt the shared inspection template at all sites.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Book readiness review room at Mirefield Depot | Kalinda Underhill | 2025-02-12 |
| 2 | Check budget headroom with Finance | Hamid Yilmaz | 2026-10-09 |
| 3 | Update training matrix for Procurement | Joaquin Szabo | 2025-04-16 |
| 4 | Book readiness review room at Hollis Point | Kalinda Underhill | 2025-01-02 |

### 12.4 Incident Review INC-9173 at Ostrava Hub

**Severity:** SEV-3. **Date:** 2024-07-22. **Reported by:** Keiko Eskildsen (Quality Assurance).

This review covers an event at Ostrava Hub that was traced to a mislabelled umbilical connector that passed visual inspection because the label template had been reused. No one was injured, and no customer cargo was damaged.

| Time | Event |
|---|---|
| 07:29 | Workaround applied and verified |
| 08:06 | On-call engineer acknowledged the page |
| 08:15 | Work stopped on the affected bay |
| 08:49 | First alert received by the operations bridge |
| 09:17 | Affected items moved to quarantine |
| 09:43 | Normal operations resumed |

**Root cause.** Cargo for Meridian Survey Corp is scanned twice: once on arrival and once immediately before integration. Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 1,200 cycles. The Ostrava Hub yard has 10 bays, each rated for a different maximum load and hazard class.

**Remediation**

- Scheduled a follow-up audit at Ostrava Hub in 18 months.
- Replaced the affected data recorder stock and quarantined the remaining batch.
- Revised the supplier quality agreement to include lot traceability.

## Chapter 13: Propulsion and Cryogenics

This section explains how Northwind Orbital Logistics approaches propulsion and cryogenics at every site, from Brightwater Annex to the smallest annex.

### 13.1 Incident Review INC-3777 at Coldharbour Yard

**Severity:** SEV-2. **Date:** 2021-04-19. **Reported by:** Elif Zelenko (Orbital Traffic Control).

This review covers an event at Coldharbour Yard that was traced to a mislabelled attitude thruster that passed visual inspection because the label template had been reused. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 14:48 | Work stopped on the affected bay |
| 14:51 | Customer informed by Customer Assurance |
| 15:27 | Normal operations resumed |
| 15:44 | On-call engineer acknowledged the page |
| 16:24 | Workaround applied and verified |
| 17:04 | Incident closed pending review |

**Root cause.** Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. Night operations require additional lighting checks and a second spotter at the cargo ramp. Nominal operating temperature for the docking clamp ranges from -28 °C to 44 °C. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.

**Remediation**

- Added monitoring with an alert routed to the Finance on-call engineer.
- Scheduled a follow-up audit at Coldharbour Yard in 24 months.
- Introduced a second sign-off for the affected step.

### 13.2 Compliance Monitoring

Propulsion and Cryogenics touches almost every team. This section summarises the standards we hold ourselves to and why.

A breach of this rule is handled under the progressive discipline process described in the People chapter. Visitors must be escorted at all times and must not handle a telemetry unit under any circumstances. Records demonstrating compliance are kept in Halyard for at least 10 years. Shift handover at Lagrange Relay L4 takes place at 08:15 and must include a walk-through of open work orders. The Kestrel-9 orbital tug turnaround target at Tarvos Station is 24 hours, measured from landing to ready-for-launch.

1. Temporary deviations of up to 14 days may be granted by the site director at Selene Gate.
2. Employees should keep personal notes out of Pilot House; only operational records belong there.
3. Every 14 days, the Finance team rehearses a loss-of-communications scenario with the duty controllers.
4. Penetration tests of public-facing services are commissioned at least once per year.
5. Temporary deviations of up to 5 days may be granted by the site director at Brightwater Annex.

> **Note:** Temporary deviations of up to 60 days may be granted by the site director at Lagrange Relay L4.

### 13.3 Operating Limits: Gannet reaction wheel

Nominal operating temperature for the reaction wheel ranges from -29 °C to 72 °C. Firmware for the reaction wheel is distributed through Lodestar and must be verified before installation. The Gannet refueling drone can hold station for up to 12 hours before its propellant margin falls below reserve.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Data rate | 1652 kbit/s | n/a | Compressed telemetry |
| Peak power | 535 W | ±4 % | During deployment |
| Dry mass | 3,241 kg | ±36 kg | Includes brackets |
| Part number | GAN-REA-5803 | n/a | Revision F |
| Design life | 5,760 cycles | n/a | Hard limit, no extension |
| Supplier | Marchetti Precision Ltd | n/a | Approved vendor list |
| Operating temperature | -46 to 25 °C | ±2 °C | Qualification limits are wider |
| Mounting | 6 × M10 bolts | Torque 34 N·m | Thread-locker required |

The design team at Selene Gate owns the interface control document and approves every change to it. Firmware for the reaction wheel is distributed through Lodestar and must be verified before installation. Nominal operating temperature for the reaction wheel ranges from -58 °C to 45 °C. Engineers should consult the Wayfarer configuration record before changing any calibration constant. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

**Operating limits**

- The Gannet refueling drone uses a dual-redundant reaction wheel that switches over automatically within 81 ms of a fault.
- Power draw peaks at 1110 W during the deployment sequence and settles at roughly a third of that.
- A reaction wheel that fails its acceptance test twice is quarantined and returned to the supplier.
- The Gannet refueling drone can hold station for up to 72 hours before its propellant margin falls below reserve.
- The Gannet refueling drone supports both automated and manual docking, although manual mode is reserved for certified pilots.

### 13.4 Post-Incident Report INC-1579 at Hollis Point

**Severity:** SEV-2. **Date:** 2021-04-28. **Reported by:** Ines Underhill (Flight Dynamics).

This review covers an event at Hollis Point that was traced to a manual data entry error in Beacon that duplicated a customer consignment. No one was injured, and no customer cargo was damaged.

| Time | Event |
|---|---|
| 19:18 | On-call engineer acknowledged the page |
| 19:21 | First alert received by the operations bridge |
| 19:55 | Normal operations resumed |
| 20:17 | Affected items moved to quarantine |

**Root cause.** Nominal operating temperature for the pressure regulator ranges from -12 °C to 64 °C. A attitude thruster that fails its acceptance test twice is quarantined and returned to the supplier. Every 14 days, the Ground Systems team rehearses a loss-of-communications scenario with the duty controllers. Thermal margins were re-analysed after the 2024 anomaly, and the upper limit was lowered by 18 °C.

**Remediation**

- Added an automated check in Gantry that rejects the condition at entry.
- Added monitoring with an alert routed to the Customer Assurance on-call engineer.

## Chapter 14: Data Retention

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for data retention.

### 14.1 Meeting Notes: Procurement (2023-12-19)

**Attendees:** Zofia Whitlock, Oona Kowalczyk, Bram Kowalczyk, Soren Iwasaki, Nnamdi Bellweather. **Chair:** Zofia Whitlock. **Location:** Mirefield Depot, room C24.

**Agenda**

1. Any other business
2. Training plan for July
3. Open audit actions
4. Staffing for the Mirefield Depot campaign
5. Budget forecast

The team reviewed open risks and closed 18 items that were no longer relevant. A proposal to standardise the pressure regulator inspection checklist across sites was well received. Attendees asked for clearer escalation paths when a customer changes requirements late. The group agreed that the manifest accuracy had improved, although the sample was still small. Zofia Whitlock reported that the backlog in Sextant had fallen to 181 tickets.

Kalinda Gallagher reported that the backlog in Cartographer had fallen to 198 tickets. Vesna Castellanos from Quality Assurance presented the results of the Mirefield Depot pilot and recommended a phased rollout. No objections were raised to extending the trial at Hollis Point for another 3 weeks. Vesna Iwasaki raised a concern about the workload on the Customer Assurance team during the peak season.

**Decisions**

- Ask Ground Systems to own the escalation path for late customer changes.
- Close the open risk on Kestrel-9 maintenance windows.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Draft customer note for Talisker Mining | Soren Iwasaki | 2025-03-20 |
| 2 | Confirm data recorder delivery dates with supplier | Soren Iwasaki | 2025-09-09 |
| 3 | Draft customer note for Umbra Imaging | Nnamdi Bellweather | 2025-05-28 |
| 4 | Book readiness review room at Selene Gate | Nnamdi Bellweather | 2025-12-16 |
| 5 | Circulate revised MANIFEST rollout plan | Soren Iwasaki | 2026-01-01 |

### 14.2 Incident Review INC-1610 at Lagrange Relay L4

**Severity:** SEV-4. **Date:** 2025-08-03. **Reported by:** Zofia Iwasaki (People Operations).

This review covers an event at Lagrange Relay L4 that was traced to a manual data entry error in Cartographer that duplicated a customer consignment. No one was injured, and no customer cargo was damaged.

| Time | Event |
|---|---|
| 16:41 | Normal operations resumed |
| 16:57 | Customer informed by Customer Assurance |
| 17:15 | Duty manager declared an incident |
| 17:49 | Workaround applied and verified |

**Root cause.** Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.

**Remediation**

- Added an automated check in Keelson that rejects the condition at entry.
- Scheduled a follow-up audit at Lagrange Relay L4 in 12 months.
- Added monitoring with an alert routed to the Quality Assurance on-call engineer.

### 14.3 Performance Envelope: Petrel pressure regulator

Engineers should consult the MANIFEST configuration record before changing any calibration constant. The Petrel transfer stage uses a dual-redundant pressure regulator that switches over automatically within 134 ms of a fault. Firmware for the pressure regulator is distributed through Drydock and must be verified before installation. Each pressure regulator carries a serial plate that encodes the batch, the factory and the inspection date.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Mounting | 4 × M8 bolts | Torque 31 N·m | Thread-locker required |
| Part number | PET-PRE-1930 | n/a | Revision A |
| Peak power | 2215 W | ±6 % | During deployment |
| Supplier | Eskildsen Precision Ltd | n/a | Approved vendor list |
| Operating temperature | -49 to 79 °C | ±5 °C | Qualification limits are wider |

Telemetry is sampled at 1 Hz and down-linked in compressed frames every 45 seconds. The Petrel transfer stage uses a dual-redundant pressure regulator that switches over automatically within 44 ms of a fault. Thermal margins were re-analysed after the 2025 anomaly, and the upper limit was lowered by 17 °C.

**Operating limits**

- The Petrel transfer stage can hold station for up to 6 hours before its propellant margin falls below reserve.
- Ground tests at Selene Gate showed a mean drift of 0.60 percent over 36 hours of continuous soak.
- Each pressure regulator carries a serial plate that encodes the batch, the factory and the inspection date.

### 14.4 Release Notes: MANIFEST

MANIFEST is maintained by the Information Security team. Releases are deployed to Tarvos Station first and to the remaining sites after a soak period of 60 days.

#### MANIFEST 8.1.0 (2023-03-09)

**Removed**
- The deprecated v1 manifest endpoint.
- An unused MANIFEST integration.

**Fixed**
- Rounding of mass totals in manifests.
- A race condition when two operators edited the same pallet.

**Added**
- Export of on-time departure rate reports to CSV.
- Support for the Heron cargo profile.
- A read-only view for customer representatives.

#### MANIFEST 8.0.5 (2022-11-05)

**Fixed**
- Duplicated alerts after a failover at Selene Gate.
- A race condition when two operators edited the same pallet.

**Added**
- Support for the Petrel cargo profile.
- A dry-run mode for configuration changes.
- Per-site dashboards for Cargo Integrity.

**Removed**
- An unused Halyard integration.
- The deprecated v1 manifest endpoint.

#### MANIFEST 8.0.4 (2021-09-18)

**Removed**
- An unused Tidewater integration.
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.

**Changed**
- The default retention period to 18 months.
- Log formatting to include the operator badge number.

**Added**
- Bulk import of cargo cradle serial numbers.
- Support for the Wren cargo profile.

### 14.5 Performance Envelope: Petrel radiator panel

The firmware signing key for the Pathfinder telemetry units is held in the hardware security vault designated BLUE-HERON-82. Requests to use that vault require two approvers from Information Security and are logged permanently.

Engineers should consult the Keelson configuration record before changing any calibration constant. Thermal margins were re-analysed after the 2019 anomaly, and the upper limit was lowered by 5 °C. Data from each pass is reconciled in Halyard and flagged if more than 16 percent of frames are missing.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Data rate | 83 kbit/s | n/a | Compressed telemetry |
| Mounting | 12 × M8 bolts | Torque 8 N·m | Thread-locker required |
| Supplier | Halvorsen Precision Ltd | n/a | Approved vendor list |
| Part number | PET-RAD-9755 | n/a | Revision B |
| Operating temperature | -18 to 65 °C | ±2 °C | Qualification limits are wider |

Each radiator panel carries a serial plate that encodes the batch, the factory and the inspection date. A radiator panel that fails its acceptance test twice is quarantined and returned to the supplier. Ground tests at Brightwater Annex showed a mean drift of 0.92 percent over 8 hours of continuous soak.

**Operating limits**

- The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots.
- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.
- Firmware for the radiator panel is distributed through Drydock and must be verified before installation.
- The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots.
- The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots.

### 14.6 Approval Thresholds

This section explains how Northwind Orbital Logistics approaches data retention at every site, from Hollis Point to the smallest annex.

The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Temporary deviations of up to 14 days may be granted by the site director at Mirefield Depot. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. Loading sequences are planned so that the heaviest items sit closest to the Shrike centre of mass. Supervisors are responsible for confirming that new starters have read this section before their first shift. The Shrike inspection pod turnaround target at Mirefield Depot is 18 hours, measured from landing to ready-for-launch.

1. Delays longer than 10 minutes are reported to the customer by Customer Assurance, not by the floor team.
2. All Procurement staff at Kessler Ridge must complete the refresher module within 10 days of any change to this policy.
3. This rule was tightened in 2025 after an internal review found inconsistent practice across sites.
4. Shift handover at Brightwater Annex takes place at 09:00 and must include a walk-through of open work orders.
5. Badges must be worn visibly inside controlled areas and returned when employment ends.

## Chapter 15: Environmental Practices

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for environmental practices.

### 15.1 Quarterly Metrics, 2024

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: on-time departure rate (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Tarvos Station | 64.5 | 65.4 | 69.3 | 65.8 | 68.6 |
| Hollis Point | 84.0 | 89.2 | 82.6 | 84.6 | 88.1 |
| Ostrava Hub | 88.1 | 88.5 | 90.1 | 89.4 | 89.6 |
| Selene Gate | 71.3 | 71.6 | 73.5 | 72.3 | 74.9 |
| Brightwater Annex | 93.5 | 94.5 | 93.2 | 98.5 | 98.0 |

The team reviewed open risks and closed 5 items that were no longer relevant. The Kessler Ridge yard has 16 bays, each rated for a different maximum load and hazard class. The discussion moved to budget, where Nikhil Pemberton confirmed a remaining allocation of €5,500. Several attendees noted that the current process in Sextant requires too many manual steps.

### 15.2 Version History: Tidewater

Tidewater is maintained by the Fleet Operations team. Releases are deployed to Port Anselm first and to the remaining sites after a soak period of 45 days.

#### Tidewater 9.6.1 (2022-01-08)

**Removed**
- An unused Gantry integration.
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

**Fixed**
- A crash when a battery module record had no serial number.
- Broken links in exported PDF reports.

**Changed**
- Timeouts for the Lagrange Relay L4 gateway from 120 to 60 seconds.
- The manifest schema to version 2.7.
- Log formatting to include the operator badge number.

#### Tidewater 9.5.6 (2022-10-12)

**Fixed**
- Rounding of mass totals in manifests.
- A crash when a radiator panel record had no serial number.
- Broken links in exported PDF reports.

**Changed**
- Sorting on the work-order list.
- The default retention period to 3 months.

#### Tidewater 9.4.1 (2022-07-08)

**Fixed**
- A crash when a reaction wheel record had no serial number.

**Added**
- Bulk import of docking clamp serial numbers.

**Removed**
- The deprecated v1 manifest endpoint.

#### Tidewater 9.4.0 (2021-04-02)

**Added**
- Per-site dashboards for Quality Assurance.
- Support for the Petrel cargo profile.

**Changed**
- The manifest schema to version 5.8.
- The approval flow so that Facilities signs off before Finance.

**Fixed**
- Incorrect time zones in shift reports.
- Duplicated alerts after a failover at Selene Gate.
- Broken links in exported PDF reports.

#### Tidewater 9.4.3 (2021-05-13)

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Signal Lamp integration.

**Fixed**
- Incorrect time zones in shift reports.
- A memory leak in the telemetry ingest worker.
- Broken links in exported PDF reports.

**Added**
- Automatic reminders for expiring certifications.
- Bulk import of cargo cradle serial numbers.
- An audit trail for manual overrides.

### 15.3 Post-Incident Report INC-4582 at Selene Gate

**Severity:** SEV-4. **Date:** 2021-09-08. **Reported by:** Bastian Kuroda (Facilities).

This review covers an event at Selene Gate that was traced to condensation inside a telemetry unit housing after an unplanned cold soak. No one was injured, and the affected flight departed 5 minutes late.

| Time | Event |
|---|---|
| 13:31 | On-call engineer acknowledged the page |
| 13:47 | Affected items moved to quarantine |
| 14:07 | Incident closed pending review |
| 14:15 | Work stopped on the affected bay |
| 14:34 | Customer informed by Customer Assurance |
| 14:54 | Workaround applied and verified |

**Root cause.** Engineers should consult the MANIFEST configuration record before changing any calibration constant. Thermal margins were re-analysed after the 2022 anomaly, and the upper limit was lowered by 2 °C. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.

**Remediation**

- Scheduled a follow-up audit at Selene Gate in 3 months.
- Added monitoring with an alert routed to the Cargo Integrity on-call engineer.
- Revised the supplier quality agreement to include lot traceability.
- Updated the inspection checklist and retrained the Ground Systems team at Selene Gate.

### 15.4 Version History: Pilot House

Pilot House is maintained by the Procurement team. Releases are deployed to Selene Gate first and to the remaining sites after a soak period of 90 days.

#### Pilot House 4.7.1 (2025-10-27)

**Fixed**
- A race condition when two operators edited the same pallet.
- Duplicated alerts after a failover at Port Anselm.

**Changed**
- Timeouts for the Port Anselm gateway from 120 to 45 seconds.
- Log formatting to include the operator badge number.

#### Pilot House 4.7.0 (2025-05-23)

**Changed**
- The manifest schema to version 2.6.
- Log formatting to include the operator badge number.
- The default retention period to 3 months.

**Fixed**
- A crash when a load cell record had no serial number.
- Broken links in exported PDF reports.

#### Pilot House 4.6.3 (2024-06-18)

**Fixed**
- Broken links in exported PDF reports.
- A race condition when two operators edited the same pallet.

**Removed**
- An unused MANIFEST integration.

### 15.5 Reference Script (Drydock)

Finance and Fleet Operations share the following query for the monthly fuel efficiency index report.

```sql
SELECT site,
       vehicle_class,
       COUNT(*)                         AS flights,
       AVG(turnaround_hours)            AS avg_turnaround_h,
       SUM(CASE WHEN delayed_min > 5 THEN 1 ELSE 0 END) AS late_departures
FROM   flight_summary
WHERE  departure_date >= DATE '2024-06-19'
  AND  site IN ('kessler-ridge', 'brightwater-annex')
GROUP  BY site, vehicle_class
ORDER  BY avg_turnaround_h DESC;
```

## Chapter 16: Training and Certification

The guidance below grew out of lessons learned at Tarvos Station and has since been adopted company-wide.

### 16.1 Manifest Format (Signal Lamp)

Cargo Integrity uses this helper to check that a manifest does not exceed the cradle limit before it is submitted to Signal Lamp.

```python
CRADLE_LIMIT_KG = 2620


def check_manifest(items):
    """Return (ok, total_kg, problems) for a list of manifest items."""
    total = 0.0
    problems = []
    for item in items:
        mass = float(item.get("mass_kg", 0))
        if mass <= 0:
            problems.append("%s: missing or invalid mass" % item.get("id", "?"))
        if item.get("hazard_class", 0) > 3:
            problems.append("%s: hazard class needs review" % item["id"])
        total += mass
    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems
```

The function is deliberately conservative: an item with no mass is treated as an error rather than as zero, because unknown mass has caused rework in the past.

### 16.2 Compliance Monitoring

The guidance below grew out of lessons learned at Kessler Ridge and has since been adopted company-wide.

Contractors working on site are bound by the same obligations as employees for the duration of their engagement. A breach of this rule is handled under the progressive discipline process described in the People chapter. Supervisors are responsible for confirming that new starters have read this section before their first shift. The requirement applies equally to remote staff who access Bulkhead from outside a company site. Exceptions require written approval from the Facilities lead and are reviewed again after 18 months. The Petrel transfer stage turnaround target at Port Anselm is 24 hours, measured from landing to ready-for-launch.

1. Badges must be worn visibly inside controlled areas and returned when employment ends.
2. Cargo for Westerly Weather Service is scanned twice: once on arrival and once immediately before integration.
3. The Mission Planning desk is staffed from 10:30 to 20:00 on weekdays, with an on-call engineer outside those hours.
4. Where a task involves a umbilical connector, the two-person rule applies from preparation through to sign-off.
5. Questions about interpretation should be raised with Esme Yilmaz in Cryogenics rather than resolved informally.
6. Where this policy conflicts with a customer contract, the stricter requirement applies.

### 16.3 Scope and Applicability

The guidance below grew out of lessons learned at Coldharbour Yard and has since been adopted company-wide.

Shift handover at Coldharbour Yard takes place at 11:15 and must include a walk-through of open work orders. Spare parts for the Kestrel-9 fleet are pooled at Brightwater Annex and shipped to other sites within 72 hours. Delays longer than 5 minutes are reported to the customer by Customer Assurance, not by the floor team. All Finance staff at Tarvos Station must complete the refresher module within 7 days of any change to this policy. Loading sequences are planned so that the heaviest items sit closest to the Osprey centre of mass.

1. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
2. Questions about interpretation should be raised with Ximena Underhill in Flight Dynamics rather than resolved informally.
3. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
4. Questions about interpretation should be raised with Ines Marchetti in People Operations rather than resolved informally.
5. Records demonstrating compliance are kept in Halyard for at least 2 years.

Audit samples are drawn quarterly, and at least 9 findings per site are followed up in person. Every 10 days, the Quality Assurance team rehearses a loss-of-communications scenario with the duty controllers. If a pallet arrives without a valid manifest entry in Halyard, it is held in the quarantine cage. Teams that cannot comply because of tooling limitations must log a risk entry in Halyard before proceeding.

> **Note:** Employees should keep personal notes out of Cartographer; only operational records belong there.

### 16.4 Record Keeping

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for training and certification.

Shift handover at Ostrava Hub takes place at 07:30 and must include a walk-through of open work orders. Delays longer than 15 minutes are reported to the customer by Customer Assurance, not by the floor team. The Propulsion Engineering desk is staffed from 08:15 to 17:00 on weekdays, with an on-call engineer outside those hours. Teams that cannot comply because of tooling limitations must log a risk entry in Drydock before proceeding. Where a task involves a telemetry unit, the two-person rule applies from preparation through to sign-off. Supervisors are responsible for confirming that new starters have read this section before their first shift. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.

1. Audit samples are drawn quarterly, and at least 6 findings per site are followed up in person.
2. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
3. Accounts that have not been used for 7 days are disabled automatically.
4. The requirement applies equally to remote staff who access Beacon from outside a company site.
5. The Heron-class freighter turnaround target at Hollis Point is 18 hours, measured from landing to ready-for-launch.
6. Operators log every manual override in Drydock together with the reason and the approving supervisor.
7. Log data from Sextant is retained for 6 months and then archived to cold storage.

### 16.5 Working with Contractors

The following rules describe expected practice for training and certification. They apply to employees and contractors alike.

Shift handover at Port Anselm takes place at 10:45 and must include a walk-through of open work orders. Where this policy conflicts with a customer contract, the stricter requirement applies. All Propulsion Engineering staff at Lagrange Relay L4 must complete the refresher module within 21 days of any change to this policy. Supervisors are responsible for confirming that new starters have read this section before their first shift. Signage summarising this rule is displayed at every entrance to the Lagrange Relay L4 operations floor. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.

1. Loading sequences are planned so that the heaviest items sit closest to the Petrel centre of mass.
2. Any spending above €94,750 linked to this policy needs approval from Finance before the order is raised.
3. The Customer Assurance desk is staffed from 08:30 to 18:15 on weekdays, with an on-call engineer outside those hours.
4. Laptops are encrypted at rest and enrolled in device management before first use.

Shift handover at Mirefield Depot takes place at 05:30 and must include a walk-through of open work orders. The Osprey cargo lander turnaround target at Ostrava Hub is 4 hours, measured from landing to ready-for-launch. The Tarvos Station yard has 8 bays, each rated for a different maximum load and hazard class. Records demonstrating compliance are kept in Halyard for at least 2 years.

## Chapter 17: Safety and Conduct, Part II

This part of the handbook was last reviewed by Wendell Grimaldi and reflects the practice agreed in 2025.

### 17.1 Review Board Notes: Facilities (2022-05-16)

**Attendees:** Leopold Fairbanks, Ines Kuroda, Tamsin Ibarra, Greta Grimaldi, Esme Okonkwo, Mirela Fairbanks. **Chair:** Leopold Fairbanks. **Location:** Ostrava Hub, room B38.

**Agenda**

1. Review of the fuel efficiency index for the last month
2. Any other business
3. Any other business
4. Staffing for the Mirefield Depot campaign

Esme Okonkwo from Orbital Traffic Control presented the results of the Lagrange Relay L4 pilot and recommended a phased rollout. The group agreed that the ticket backlog had improved, although the sample was still small. The team reviewed open risks and closed 12 items that were no longer relevant. Esme Okonkwo reminded everyone that the November audit will focus on training records. Esme Okonkwo reported that the backlog in Drydock had fallen to 56 tickets.

Several attendees noted that the current process in Pilot House requires too many manual steps. Leopold Moravec will draft a short note for Quillon Satellites explaining the revised delivery window. Hollis Eskildsen reminded everyone that the June audit will focus on training records. Hamid Yilmaz from Flight Dynamics presented the results of the Selene Gate pilot and recommended a phased rollout.

**Decisions**

- Extend the night-shift trial by 3 weeks.
- Close the open risk on Petrel maintenance windows.
- Proceed with the Keelson upgrade at Tarvos Station in October.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Confirm cargo cradle delivery dates with supplier | Tamsin Ibarra | 2025-03-09 |
| 2 | Collect manifest accuracy data for next meeting | Leopold Fairbanks | 2025-10-22 |
| 3 | Circulate revised Lodestar rollout plan | Mirela Fairbanks | 2025-12-02 |
| 4 | Circulate revised Signal Lamp rollout plan | Leopold Fairbanks | 2026-06-14 |

### 17.2 Site-Specific Rules

The guidance below grew out of lessons learned at Tarvos Station and has since been adopted company-wide.

Shift handover at Selene Gate takes place at 06:45 and must include a walk-through of open work orders. A breach of this rule is handled under the progressive discipline process described in the People chapter. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. The policy owner reviews the wording every 3 months and publishes changes in the revision history.

1. The People Operations desk is staffed from 08:30 to 22:30 on weekdays, with an on-call engineer outside those hours.
2. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.
3. A breach of this rule is handled under the progressive discipline process described in the People chapter.
4. Signage summarising this rule is displayed at every entrance to the Selene Gate operations floor.
5. Badges must be worn visibly inside controlled areas and returned when employment ends.

Visitors must be escorted at all times and must not handle a docking clamp under any circumstances. Shift handover at Tarvos Station takes place at 06:00 and must include a walk-through of open work orders. Every 30 days, the Propulsion Engineering team rehearses a loss-of-communications scenario with the duty controllers. If a pallet arrives without a valid manifest entry in Drydock, it is held in the quarantine cage. Delays longer than 60 minutes are reported to the customer by Customer Assurance, not by the floor team.

### 17.3 Technical Specification: Shrike load cell

Telemetry is sampled at 50 Hz and down-linked in compressed frames every 15 seconds. Data from each pass is reconciled in Drydock and flagged if more than 19 percent of frames are missing. Nominal operating temperature for the load cell ranges from -15 °C to 29 °C.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Design life | 2,500 cycles | n/a | Hard limit, no extension |
| Peak power | 1286 W | ±3 % | During deployment |
| Part number | SHR-LOA-2126 | n/a | Revision B |
| Mounting | 8 × M6 bolts | Torque 10 N·m | Thread-locker required |
| Operating temperature | -16 to 58 °C | ±2 °C | Qualification limits are wider |
| Data rate | 552 kbit/s | n/a | Compressed telemetry |

Engineers should consult the Cartographer configuration record before changing any calibration constant. Power draw peaks at 965 W during the deployment sequence and settles at roughly a third of that. The Shrike inspection pod can hold station for up to 72 hours before its propellant margin falls below reserve. A load cell that fails its acceptance test twice is quarantined and returned to the supplier. The latest revision reduced mass by 11.3 kg by replacing the aluminium bracket with a composite part.

**Operating limits**

- Nominal operating temperature for the load cell ranges from -37 °C to 30 °C.
- Engineers should consult the Sextant configuration record before changing any calibration constant.
- Each load cell carries a serial plate that encodes the batch, the factory and the inspection date.

### 17.4 Escalation Rules

Safety and Conduct touches almost every team. This section summarises the standards we hold ourselves to and why.

When two departures compete for the same pad, the one with the earlier customer commitment takes priority. Where a task involves a hatch seal, the two-person rule applies from preparation through to sign-off. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. Signage summarising this rule is displayed at every entrance to the Lagrange Relay L4 operations floor. Operators log every manual override in Wayfarer together with the reason and the approving supervisor. The Lagrange Relay L4 yard has 15 bays, each rated for a different maximum load and hazard class.

1. The policy owner reviews the wording every 3 months and publishes changes in the revision history.
2. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.
3. Night operations require additional lighting checks and a second spotter at the cargo ramp.
4. Removable media is blocked on all operations workstations at Kessler Ridge.
5. Shift handover at Mirefield Depot takes place at 11:15 and must include a walk-through of open work orders.
6. Temporary deviations of up to 60 days may be granted by the site director at Ostrava Hub.
7. Spare parts for the Gannet fleet are pooled at Mirefield Depot and shipped to other sites within 18 hours.

Operators log every manual override in Lodestar together with the reason and the approving supervisor. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Cargo for Talisker Mining is scanned twice: once on arrival and once immediately before integration.

### 17.5 Version History: Wayfarer

Wayfarer is maintained by the Cargo Integrity team. Releases are deployed to Ostrava Hub first and to the remaining sites after a soak period of 14 days.

#### Wayfarer 3.11.3 (2026-06-26)

**Fixed**
- Rounding of mass totals in manifests.
- Duplicated alerts after a failover at Selene Gate.
- Broken links in exported PDF reports.

**Changed**
- Log formatting to include the operator badge number.
- The approval flow so that Facilities signs off before Finance.

#### Wayfarer 3.10.5 (2026-09-07)

**Added**
- Export of customer satisfaction score reports to CSV.
- Automatic reminders for expiring certifications.
- An audit trail for manual overrides.

**Fixed**
- A memory leak in the telemetry ingest worker.
- Broken links in exported PDF reports.
- A crash when a radiator panel record had no serial number.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused MANIFEST integration.
- The legacy FTP upload path.

#### Wayfarer 3.10.4 (2025-09-14)

**Added**
- An audit trail for manual overrides.
- Per-site dashboards for Customer Assurance.
- Bulk import of battery module serial numbers.

**Changed**
- The default retention period to 24 months.
- The manifest schema to version 6.0.
- Log formatting to include the operator badge number.

### 17.6 Data Query Example (Gantry)

Cargo Integrity uses this helper to check that a manifest does not exceed the cradle limit before it is submitted to Gantry.

```python
CRADLE_LIMIT_KG = 3376


def check_manifest(items):
    """Return (ok, total_kg, problems) for a list of manifest items."""
    total = 0.0
    problems = []
    for item in items:
        mass = float(item.get("mass_kg", 0))
        if mass <= 0:
            problems.append("%s: missing or invalid mass" % item.get("id", "?"))
        if item.get("hazard_class", 0) > 2:
            problems.append("%s: hazard class needs review" % item["id"])
        total += mass
    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems
```

The function is deliberately conservative: an item with no mass is treated as an error rather than as zero, because unknown mass has caused rework in the past.

## Chapter 18: Fleet Operations, Part II

The following rules describe expected practice for fleet operations. They apply to employees and contractors alike.

### 18.1 Version History: MANIFEST

MANIFEST is maintained by the Customer Assurance team. Releases are deployed to Brightwater Annex first and to the remaining sites after a soak period of 21 days.

#### MANIFEST 3.1.6 (2024-04-09)

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

**Changed**
- Sorting on the work-order list.
- The manifest schema to version 3.0.
- Timeouts for the Coldharbour Yard gateway from 15 to 30 seconds.

#### MANIFEST 3.0.0 (2023-11-12)

**Added**
- Support for the Kestrel-9 cargo profile.

**Removed**
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.
- An unused Keelson integration.

#### MANIFEST 3.0.1 (2022-05-24)

**Fixed**
- A race condition when two operators edited the same pallet.
- Incorrect time zones in shift reports.
- Broken links in exported PDF reports.

**Changed**
- Sorting on the work-order list.
- Timeouts for the Lagrange Relay L4 gateway from 30 to 120 seconds.
- The manifest schema to version 2.2.

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.
- An unused Ledgerline integration.

#### MANIFEST 3.0.5 (2021-09-27)

**Changed**
- The default retention period to 9 months.

**Fixed**
- Duplicated alerts after a failover at Lagrange Relay L4.
- A crash when a docking clamp record had no serial number.
- A memory leak in the telemetry ingest worker.

#### MANIFEST 3.0.4 (2021-10-16)

**Removed**
- An unused Sextant integration.

**Added**
- Per-site dashboards for Flight Dynamics.
- Bulk import of hatch seal serial numbers.
- Export of on-time departure rate reports to CSV.

**Changed**
- Log formatting to include the operator badge number.
- The default retention period to 3 months.
- The manifest schema to version 5.2.

### 18.2 Configuration Baseline: Osprey thermal blanket

Ground tests at Port Anselm showed a mean drift of 0.90 percent over 24 hours of continuous soak. The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots. The Osprey cargo lander can hold station for up to 72 hours before its propellant margin falls below reserve.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Design life | 3,830 cycles | n/a | Hard limit, no extension |
| Dry mass | 5,660 kg | ±29 kg | Excludes harness |
| Part number | OSP-THE-7468 | n/a | Revision B |
| Operating temperature | -59 to 81 °C | ±3 °C | Qualification limits are wider |
| Peak power | 1932 W | ±8 % | During deployment |

Engineers should consult the MANIFEST configuration record before changing any calibration constant. Each thermal blanket carries a serial plate that encodes the batch, the factory and the inspection date. The latest revision reduced mass by 4.5 kg by replacing the aluminium bracket with a composite part. Thermal margins were re-analysed after the 2022 anomaly, and the upper limit was lowered by 5 °C.

**Operating limits**

- Engineers should consult the MANIFEST configuration record before changing any calibration constant.
- The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots.
- The Osprey cargo lander can hold station for up to 24 hours before its propellant margin falls below reserve.

### 18.3 Incident Review INC-3080 at Kessler Ridge

**Severity:** SEV-2. **Date:** 2024-02-01. **Reported by:** Maren Quarles (Finance).

This review covers an event at Kessler Ridge that was traced to a scheduling conflict between two Propulsion Engineering shifts that left the cargo ramp without a spotter. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 01:52 | Duty manager declared an incident |
| 02:19 | Normal operations resumed |
| 02:47 | First alert received by the operations bridge |
| 03:24 | Customer informed by Customer Assurance |
| 03:42 | Workaround applied and verified |
| 04:13 | On-call engineer acknowledged the page |

**Root cause.** Operators log every manual override in MANIFEST together with the reason and the approving supervisor. Delays longer than 45 minutes are reported to the customer by Customer Assurance, not by the floor team.

**Remediation**

- Replaced the affected reaction wheel stock and quarantined the remaining batch.
- Scheduled a follow-up audit at Kessler Ridge in 24 months.
- Added an automated check in MANIFEST that rejects the condition at entry.
- Added monitoring with an alert routed to the Finance on-call engineer.

### 18.4 Technical Specification: Heron cargo cradle

The latest revision reduced mass by 22.6 kg by replacing the aluminium bracket with a composite part. Ground tests at Mirefield Depot showed a mean drift of 0.18 percent over 36 hours of continuous soak. Engineers should consult the Drydock configuration record before changing any calibration constant. During integration, torque values for every fastener are recorded and attached to the build record. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Mounting | 8 × M10 bolts | Torque 19 N·m | Thread-locker required |
| Design life | 6,390 cycles | n/a | Hard limit, no extension |
| Operating temperature | -48 to 66 °C | ±1 °C | Qualification limits are wider |
| Part number | HER-CAR-6311 | n/a | Revision D |
| Supplier | Kuroda Aerospace Ltd | n/a | Approved vendor list |
| Data rate | 1830 kbit/s | n/a | Compressed telemetry |
| Dry mass | 2,863 kg | ±35 kg | Excludes harness |

The Heron-class freighter supports both automated and manual docking, although manual mode is reserved for certified pilots. Each cargo cradle carries a serial plate that encodes the batch, the factory and the inspection date. Nominal operating temperature for the cargo cradle ranges from -28 °C to 52 °C. The design team at Hollis Point owns the interface control document and approves every change to it. During integration, torque values for every fastener are recorded and attached to the build record.

**Operating limits**

- A cargo cradle that fails its acceptance test twice is quarantined and returned to the supplier.
- Firmware for the cargo cradle is distributed through MANIFEST and must be verified before installation.
- Thermal margins were re-analysed after the 2024 anomaly, and the upper limit was lowered by 18 °C.

## Chapter 19: Ground Facilities, Part II

Any hot-fire test of the Mk-IV maneuvering thruster requires written sign-off from Dr. Ingrid Valtameri, the Chief Propulsion Safety Officer; no deputy may substitute for this signature, even during a declared schedule emergency.

This part of the handbook was last reviewed by Mirela Whitlock and reflects the practice agreed in 2018.

### 19.1 Performance Dashboard Snapshot, 2024

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: on-time departure rate (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Kessler Ridge | 75.1 | 72.1 | 76.7 | 75.1 | 77.4 |
| Selene Gate | 64.9 | 61.7 | 65.8 | 62.6 | 64.6 |
| Brightwater Annex | 87.7 | 81.8 | 83.4 | 89.3 | 87.3 |
| Coldharbour Yard | 61.2 | 62.1 | 61.1 | 66.9 | 66.0 |

Rosalind Ibarra raised a concern about the workload on the Customer Assurance team during the peak season. Operators log every manual override in Signal Lamp together with the reason and the approving supervisor. If a pallet arrives without a valid manifest entry in Gantry, it is held in the quarantine cage. Shift handover at Ostrava Hub takes place at 11:00 and must include a walk-through of open work orders.

### 19.2 Reference Script (Signal Lamp)

Cargo Integrity uses this helper to check that a manifest does not exceed the cradle limit before it is submitted to Signal Lamp.

```python
CRADLE_LIMIT_KG = 2079


def check_manifest(items):
    """Return (ok, total_kg, problems) for a list of manifest items."""
    total = 0.0
    problems = []
    for item in items:
        mass = float(item.get("mass_kg", 0))
        if mass <= 0:
            problems.append("%s: missing or invalid mass" % item.get("id", "?"))
        if item.get("hazard_class", 0) > 4:
            problems.append("%s: hazard class needs review" % item["id"])
        total += mass
    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems
```

The function is deliberately conservative: an item with no mass is treated as an error rather than as zero, because unknown mass has caused rework in the past.

### 19.3 Frequently Asked Questions about Ground Facilities

**Q: Who do I call if the Drydock service is down?**

Contact the Customer Assurance on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

**Q: Can customers visit during integration?**

Customer visits are welcome but must be scheduled with Customer Assurance at least 14 days ahead.

**Q: Where are spare umbilical connector parts stored?**

The central pool is at Tarvos Station. Each site also keeps a small buffer stock sized from the last 3 months of usage.

### 19.4 Performance Envelope: Osprey radiator panel

Data from each pass is reconciled in Tidewater and flagged if more than 14 percent of frames are missing. Nominal operating temperature for the radiator panel ranges from -10 °C to 35 °C. The Osprey cargo lander can hold station for up to 12 hours before its propellant margin falls below reserve. Each radiator panel carries a serial plate that encodes the batch, the factory and the inspection date.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Operating temperature | -25 to 51 °C | ±3 °C | Qualification limits are wider |
| Dry mass | 7,393 kg | ±5 kg | Includes brackets |
| Mounting | 12 × M6 bolts | Torque 6 N·m | Thread-locker required |
| Design life | 6,590 cycles | n/a | Hard limit, no extension |
| Part number | OSP-RAD-7107 | n/a | Revision C |
| Peak power | 1890 W | ±2 % | During deployment |

The design team at Tarvos Station owns the interface control document and approves every change to it. Power draw peaks at 798 W during the deployment sequence and settles at roughly a third of that. Thermal margins were re-analysed after the 2018 anomaly, and the upper limit was lowered by 7 °C. Firmware for the radiator panel is distributed through Ledgerline and must be verified before installation.

**Operating limits**

- Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 8,590 cycles.
- The Osprey cargo lander uses a dual-redundant radiator panel that switches over automatically within 171 ms of a fault.
- Nominal operating temperature for the radiator panel ranges from -44 °C to 26 °C.
- The design team at Selene Gate owns the interface control document and approves every change to it.

### 19.5 Scope and Applicability

This part of the handbook was last reviewed by Celeste Grimaldi and reflects the practice agreed in 2023.

Where a task involves a cargo cradle, the two-person rule applies from preparation through to sign-off. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. If a pallet arrives without a valid manifest entry in Halyard, it is held in the quarantine cage. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.

1. Signage summarising this rule is displayed at every entrance to the Tarvos Station operations floor.
2. Accounts that have not been used for 14 days are disabled automatically.
3. Production credentials must never be pasted into chat tools, tickets or shared documents.
4. Laptops are encrypted at rest and enrolled in device management before first use.
5. Delays longer than 15 minutes are reported to the customer by Customer Assurance, not by the floor team.
6. Questions about interpretation should be raised with Maren Halvorsen in Facilities rather than resolved informally.

> **Note:** Temporary deviations of up to 10 days may be granted by the site director at Kessler Ridge.

### 19.6 Meeting Notes: Customer Assurance (2022-07-08)

**Attendees:** Greta Halvorsen, Ximena Delacroix, Tamsin Fairbanks, Vesna Ostrander, Esme Quarles, Carys Nakashima, Celeste Zelenko. **Chair:** Greta Halvorsen. **Location:** Coldharbour Yard, room C11.

**Agenda**

1. Status of the Lodestar upgrade
2. Budget forecast
3. Review of the cargo damage rate for the last month
4. Any other business

Esme Quarles reported that the backlog in Cartographer had fallen to 47 tickets. The discussion moved to budget, where Esme Quarles confirmed a remaining allocation of €99,750. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Esme Quarles will draft a short note for Ravensmoor University explaining the revised delivery window. A proposal to standardise the cargo cradle inspection checklist across sites was well received. Several attendees noted that the current process in MANIFEST requires too many manual steps. Attendees asked for clearer escalation paths when a customer changes requirements late.

It was agreed to revisit the topic once the supplier has delivered the revised quotation. The group agreed that the manifest accuracy had improved, although the sample was still small. A proposal to standardise the star tracker inspection checklist across sites was well received.

**Decisions**

- Extend the night-shift trial by 3 weeks.
- Extend the night-shift trial by 8 weeks.
- Proceed with the Tidewater upgrade at Mirefield Depot in February.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Propulsion Engineering | Celeste Zelenko | 2025-06-11 |
| 2 | Draft customer note for Veldt Communications | Vesna Ostrander | 2025-01-13 |
| 3 | Check budget headroom with Finance | Tamsin Fairbanks | 2026-10-17 |

## Chapter 20: Information Security, Part II

The following rules describe expected practice for information security. They apply to employees and contractors alike.

### 20.1 Escalation Rules

This part of the handbook was last reviewed by Rosalind Nakashima and reflects the practice agreed in 2026.

This rule was tightened in 2020 after an internal review found inconsistent practice across sites. Temporary deviations of up to 10 days may be granted by the site director at Port Anselm. Teams that cannot comply because of tooling limitations must log a risk entry in Halyard before proceeding. Exceptions require written approval from the Cryogenics lead and are reviewed again after 9 months. Failure to complete required training within the deadline results in temporary removal from the duty roster. Network segments for flight systems are physically separated from the corporate network.

1. Customer representatives may observe loading from the gallery but may not enter the clean area.
2. Laptops are encrypted at rest and enrolled in device management before first use.
3. Signage summarising this rule is displayed at every entrance to the Mirefield Depot operations floor.
4. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
5. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.

Penetration tests of public-facing services are commissioned at least once per year. The Ground Systems team runs a phishing simulation every 3 months and publishes anonymised results. This rule was tightened in 2021 after an internal review found inconsistent practice across sites. Where a task involves a cryo coupling, the two-person rule applies from preparation through to sign-off.

> **Note:** Questions about interpretation should be raised with Tamsin Grimaldi in Procurement rather than resolved informally.

### 20.2 Equipment Data Sheet: Shrike star tracker

Nominal operating temperature for the star tracker ranges from -13 °C to 31 °C. Telemetry is sampled at 5 Hz and down-linked in compressed frames every 30 seconds. Thermal margins were re-analysed after the 2020 anomaly, and the upper limit was lowered by 3 °C. Engineers should consult the MANIFEST configuration record before changing any calibration constant.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Operating temperature | -41 to 35 °C | ±1 °C | Qualification limits are wider |
| Data rate | 1684 kbit/s | n/a | Compressed telemetry |
| Supplier | Ferreira Instruments Ltd | n/a | Approved vendor list |
| Part number | SHR-STA-2748 | n/a | Revision A |
| Mounting | 4 × M6 bolts | Torque 17 N·m | Thread-locker required |
| Peak power | 549 W | ±5 % | During deployment |
| Dry mass | 7,251 kg | ±28 kg | Excludes harness |
| Design life | 1,280 cycles | n/a | Hard limit, no extension |

Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 4,290 cycles. A star tracker that fails its acceptance test twice is quarantined and returned to the supplier. Engineers should consult the Signal Lamp configuration record before changing any calibration constant. Power draw peaks at 1813 W during the deployment sequence and settles at roughly a third of that.

**Operating limits**

- Thermal margins were re-analysed after the 2020 anomaly, and the upper limit was lowered by 11 °C.
- The Shrike inspection pod can hold station for up to 24 hours before its propellant margin falls below reserve.
- During integration, torque values for every fastener are recorded and attached to the build record.
- Data from each pass is reconciled in Wayfarer and flagged if more than 18 percent of frames are missing.

### 20.3 Configuration Example (Signal Lamp)

Use these commands, in order, when the Signal Lamp ingest queue at Hollis Point stops draining. Stop at the first step that resolves the problem.

```bash
# 1. Check queue depth
nolctl queue status --service signal-lamp --site hollis-point

# 2. Drain stuck consumers (safe, idempotent)
nolctl queue rebalance --service signal-lamp --max-moves 23

# 3. Restart one worker at a time
nolctl worker restart --service signal-lamp --one-at-a-time --wait 30s

# 4. Escalate if depth is still above 11914 after 15 minutes
nolctl page --team propulsion-engineering --severity high
```

### 20.4 Post-Incident Report INC-598 at Brightwater Annex

**Severity:** SEV-3. **Date:** 2021-01-05. **Reported by:** Vesna Jessop (Quality Assurance).

This review covers an event at Brightwater Annex that was traced to a network switch failure at Brightwater Annex that isolated the telemetry archive. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 04:03 | Work stopped on the affected bay |
| 04:20 | Workaround applied and verified |
| 04:44 | Normal operations resumed |
| 04:59 | Duty manager declared an incident |
| 05:12 | First alert received by the operations bridge |
| 05:19 | Incident closed pending review |

**Root cause.** The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots. Thermal margins were re-analysed after the 2021 anomaly, and the upper limit was lowered by 14 °C. Firmware for the hatch seal is distributed through Pilot House and must be verified before installation. Customer representatives may observe loading from the gallery but may not enter the clean area.

**Remediation**

- Scheduled a follow-up audit at Brightwater Annex in 24 months.
- Replaced the affected hatch seal stock and quarantined the remaining batch.
- Revised the supplier quality agreement to include lot traceability.

## Chapter 21: Cargo Handling, Part II

This part of the handbook was last reviewed by Oona Ibarra and reflects the practice agreed in 2021.

### 21.1 Review Board Notes: Procurement (2025-04-10)

**Attendees:** Hamid Gallagher, Ximena Novak, Kalinda Drummond, Hollis Yilmaz. **Chair:** Hamid Gallagher. **Location:** Lagrange Relay L4, room B11.

**Agenda**

1. Training plan for March
2. Feedback from Umbra Imaging
3. Review of the audit finding closure rate for the last month
4. Staffing for the Brightwater Annex campaign

Several attendees noted that the current process in Lodestar requires too many manual steps. Kalinda Drummond reported that the backlog in Gantry had fallen to 53 tickets. Attendees asked for clearer escalation paths when a customer changes requirements late. No objections were raised to extending the trial at Tarvos Station for another 4 weeks. The discussion moved to budget, where Kalinda Drummond confirmed a remaining allocation of €70,750. The group agreed that the mean time to repair had improved, although the sample was still small.

No objections were raised to extending the trial at Kessler Ridge for another 8 weeks. Ulrich Hargreaves from Propulsion Engineering presented the results of the Port Anselm pilot and recommended a phased rollout. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Jonas Pemberton reminded everyone that the April audit will focus on training records. Attendees asked for clearer escalation paths when a customer changes requirements late.

**Decisions**

- Defer the attitude thruster checklist change until the supplier responds.
- Ask Procurement to own the escalation path for late customer changes.
- Proceed with the Halyard upgrade at Port Anselm in October.
- Extend the night-shift trial by 3 weeks.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Ground Systems | Ximena Novak | 2025-11-25 |
| 2 | Update training matrix for Flight Dynamics | Hamid Gallagher | 2026-04-18 |
| 3 | Update training matrix for Ground Systems | Ximena Novak | 2025-07-07 |
| 4 | Update training matrix for Finance | Ximena Novak | 2025-01-07 |
| 5 | Book readiness review room at Kessler Ridge | Ximena Novak | 2025-04-03 |

### 21.2 Interface Summary: Corvid docking clamp

Power draw peaks at 527 W during the deployment sequence and settles at roughly a third of that. Each docking clamp carries a serial plate that encodes the batch, the factory and the inspection date. The Corvid recovery tender supports both automated and manual docking, although manual mode is reserved for certified pilots.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Dry mass | 1,911 kg | ±36 kg | Measured at acceptance |
| Peak power | 1723 W | ±9 % | During deployment |
| Design life | 3,130 cycles | n/a | Hard limit, no extension |
| Operating temperature | -24 to 71 °C | ±3 °C | Qualification limits are wider |
| Part number | COR-DOC-9843 | n/a | Revision B |
| Mounting | 8 × M5 bolts | Torque 36 N·m | Thread-locker required |

During integration, torque values for every fastener are recorded and attached to the build record. Data from each pass is reconciled in Gantry and flagged if more than 17 percent of frames are missing. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

**Operating limits**

- Ground tests at Hollis Point showed a mean drift of 0.87 percent over 72 hours of continuous soak.
- Ground tests at Ostrava Hub showed a mean drift of 0.24 percent over 48 hours of continuous soak.
- Nominal operating temperature for the docking clamp ranges from -32 °C to 81 °C.
- A docking clamp that fails its acceptance test twice is quarantined and returned to the supplier.

### 21.3 Release Notes: Wayfarer

Wayfarer is maintained by the Ground Systems team. Releases are deployed to Hollis Point first and to the remaining sites after a soak period of 21 days.

#### Wayfarer 8.7.0 (2023-07-26)

**Fixed**
- Incorrect time zones in shift reports.

**Removed**
- The legacy FTP upload path.
- An unused Cartographer integration.

#### Wayfarer 8.7.5 (2022-12-21)

**Removed**
- An unused Signal Lamp integration.
- The deprecated v1 manifest endpoint.

**Changed**
- Timeouts for the Tarvos Station gateway from 2 to 15 seconds.

**Fixed**
- A race condition when two operators edited the same pallet.

#### Wayfarer 8.7.4 (2022-01-26)

**Changed**
- The default retention period to 24 months.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Drydock integration.
- The legacy FTP upload path.

**Added**
- Support for the Kestrel-9 cargo profile.
- A read-only view for customer representatives.

### 21.4 Data Query Example (Lodestar)

Each December the company presents its highest internal honor for exceptional logistics work, the Copper Albatross Prize, to one employee nominated by peers from at least two different sites.

Finance and Fleet Operations share the following query for the monthly cargo damage rate report.

```sql
SELECT site,
       vehicle_class,
       COUNT(*)                         AS flights,
       AVG(turnaround_hours)            AS avg_turnaround_h,
       SUM(CASE WHEN delayed_min > 30 THEN 1 ELSE 0 END) AS late_departures
FROM   flight_summary
WHERE  departure_date >= DATE '2024-03-04'
  AND  site IN ('port-anselm', 'ostrava-hub')
GROUP  BY site, vehicle_class
ORDER  BY avg_turnaround_h DESC;
```

### 21.5 Changelog: Wayfarer

Wayfarer is maintained by the Ground Systems team. Releases are deployed to Brightwater Annex first and to the remaining sites after a soak period of 60 days.

#### Wayfarer 2.0.6 (2022-09-26)

**Fixed**
- Duplicated alerts after a failover at Coldharbour Yard.

**Removed**
- The legacy FTP upload path.

**Changed**
- The manifest schema to version 6.5.

#### Wayfarer 2.0.6 (2021-01-07)

**Fixed**
- Incorrect time zones in shift reports.

**Added**
- A dry-run mode for configuration changes.

**Removed**
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.

#### Wayfarer 2.0.4 (2021-05-04)

**Fixed**
- Broken links in exported PDF reports.
- Incorrect time zones in shift reports.
- A memory leak in the telemetry ingest worker.

**Added**
- Bulk import of umbilical connector serial numbers.
- Automatic reminders for expiring certifications.

#### Wayfarer 2.0.0 (2021-08-09)

**Added**
- A dry-run mode for configuration changes.

**Fixed**
- A memory leak in the telemetry ingest worker.
- A crash when a reaction wheel record had no serial number.

#### Wayfarer 2.0.4 (2021-07-18)

**Added**
- A dry-run mode for configuration changes.
- Per-site dashboards for Cryogenics.
- Support for the Shrike cargo profile.

**Changed**
- Timeouts for the Hollis Point gateway from 30 to 90 seconds.

### 21.6 Reference Script (Drydock)

A minimal manifest entry, as accepted by the Drydock API, looks like this:

```json
{
  "consignment_id": "CN-8496",
  "customer": "Veldt Communications",
  "site": "selene-gate",
  "items": [
    {"id": "IT-7881", "mass_kg": 789.8, "hazard_class": 0, "position": "B1"},
    {"id": "IT-2229", "mass_kg": 689.3, "hazard_class": 1, "position": "C1"}
  ],
  "requested_departure": "2026-03-10"
}
```

Positions refer to the cradle grid of the target vehicle. Items without a position are placed by the loading planner and confirmed during integration.

## Chapter 22: Software Systems, Part II

Software Systems touches almost every team. This section summarises the standards we hold ourselves to and why.

### 22.1 Escalation Rules

This section explains how Northwind Orbital Logistics approaches software systems at every site, from Mirefield Depot to the smallest annex.

Cargo for Ravensmoor University is scanned twice: once on arrival and once immediately before integration. If a pallet arrives without a valid manifest entry in Halyard, it is held in the quarantine cage. Operators log every manual override in Beacon together with the reason and the approving supervisor. Teams that cannot comply because of tooling limitations must log a risk entry in Lodestar before proceeding. Exceptions require written approval from the Mission Planning lead and are reviewed again after 24 months. The policy owner reviews the wording every 9 months and publishes changes in the revision history.

1. This rule was tightened in 2020 after an internal review found inconsistent practice across sites.
2. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
3. Any spending above €99,750 linked to this policy needs approval from Finance before the order is raised.
4. Teams that cannot comply because of tooling limitations must log a risk entry in Bulkhead before proceeding.

The Propulsion Engineering desk is staffed from 07:00 to 18:15 on weekdays, with an on-call engineer outside those hours. Audit samples are drawn quarterly, and at least 4 findings per site are followed up in person. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.

### 22.2 Configuration Baseline: Petrel cryo coupling

Engineers should consult the Drydock configuration record before changing any calibration constant. Power draw peaks at 1262 W during the deployment sequence and settles at roughly a third of that. During integration, torque values for every fastener are recorded and attached to the build record. The design team at Mirefield Depot owns the interface control document and approves every change to it.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Design life | 3,780 cycles | n/a | Hard limit, no extension |
| Operating temperature | -49 to 40 °C | ±2 °C | Qualification limits are wider |
| Dry mass | 2,424 kg | ±11 kg | Excludes harness |
| Mounting | 4 × M6 bolts | Torque 11 N·m | Thread-locker required |
| Peak power | 1510 W | ±5 % | During deployment |
| Part number | PET-CRY-9540 | n/a | Revision G |
| Data rate | 1782 kbit/s | n/a | Compressed telemetry |

The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots. Ground tests at Ostrava Hub showed a mean drift of 0.54 percent over 36 hours of continuous soak. The design team at Hollis Point owns the interface control document and approves every change to it.

**Operating limits**

- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.
- During integration, torque values for every fastener are recorded and attached to the build record.
- Ground tests at Hollis Point showed a mean drift of 0.64 percent over 8 hours of continuous soak.

### 22.3 Performance Envelope: Osprey reaction wheel

Data from each pass is reconciled in Bulkhead and flagged if more than 14 percent of frames are missing. The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots. The Osprey cargo lander can hold station for up to 72 hours before its propellant margin falls below reserve. A reaction wheel that fails its acceptance test twice is quarantined and returned to the supplier. Thermal margins were re-analysed after the 2022 anomaly, and the upper limit was lowered by 2 °C.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Operating temperature | -16 to 27 °C | ±5 °C | Qualification limits are wider |
| Supplier | Moravec Precision Ltd | n/a | Approved vendor list |
| Peak power | 1469 W | ±10 % | During deployment |
| Mounting | 6 × M10 bolts | Torque 51 N·m | Thread-locker required |
| Design life | 840 cycles | n/a | Hard limit, no extension |
| Part number | OSP-REA-4477 | n/a | Revision F |

The design team at Coldharbour Yard owns the interface control document and approves every change to it. Ground tests at Brightwater Annex showed a mean drift of 0.21 percent over 48 hours of continuous soak. Power draw peaks at 667 W during the deployment sequence and settles at roughly a third of that.

**Operating limits**

- The design team at Ostrava Hub owns the interface control document and approves every change to it.
- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.
- Thermal margins were re-analysed after the 2021 anomaly, and the upper limit was lowered by 9 °C.
- The Osprey cargo lander uses a dual-redundant reaction wheel that switches over automatically within 217 ms of a fault.

### 22.4 Reporting Obligations

This part of the handbook was last reviewed by Jonas Novak and reflects the practice agreed in 2026.

Delays longer than 10 minutes are reported to the customer by Customer Assurance, not by the floor team. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Records demonstrating compliance are kept in Beacon for at least 7 years. Signage summarising this rule is displayed at every entrance to the Hollis Point operations floor.

1. Questions about interpretation should be raised with Rosalind Szabo in Procurement rather than resolved informally.
2. Cargo for Alder Biotech is scanned twice: once on arrival and once immediately before integration.
3. If a pallet arrives without a valid manifest entry in Ledgerline, it is held in the quarantine cage.
4. Night operations require additional lighting checks and a second spotter at the cargo ramp.
5. Delays longer than 15 minutes are reported to the customer by Customer Assurance, not by the floor team.
6. Cargo for Meridian Survey Corp is scanned twice: once on arrival and once immediately before integration.

Loading sequences are planned so that the heaviest items sit closest to the Gannet centre of mass. Customer representatives may observe loading from the gallery but may not enter the clean area. Records demonstrating compliance are kept in Pilot House for at least 2 years. Any spending above €29,750 linked to this policy needs approval from Finance before the order is raised.

> **Note:** This rule was tightened in 2019 after an internal review found inconsistent practice across sites.

### 22.5 Configuration Baseline: Wren docking clamp

Power draw peaks at 729 W during the deployment sequence and settles at roughly a third of that. The design team at Lagrange Relay L4 owns the interface control document and approves every change to it. Telemetry is sampled at 2 Hz and down-linked in compressed frames every 60 seconds.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Part number | WRE-DOC-1976 | n/a | Revision B |
| Data rate | 1869 kbit/s | n/a | Compressed telemetry |
| Peak power | 1112 W | ±8 % | During deployment |
| Operating temperature | -35 to 81 °C | ±4 °C | Qualification limits are wider |
| Supplier | Quarles Components Ltd | n/a | Approved vendor list |
| Dry mass | 2,723 kg | ±38 kg | Excludes harness |

The Wren crew shuttle uses a dual-redundant docking clamp that switches over automatically within 145 ms of a fault. Each docking clamp carries a serial plate that encodes the batch, the factory and the inspection date. Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 6,320 cycles.

**Operating limits**

- Power draw peaks at 2200 W during the deployment sequence and settles at roughly a third of that.
- The latest revision reduced mass by 12.1 kg by replacing the aluminium bracket with a composite part.
- Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 3,450 cycles.
- Engineers should consult the Beacon configuration record before changing any calibration constant.

## Chapter 23: People and Travel, Part II

This section explains how Northwind Orbital Logistics approaches people and travel at every site, from Hollis Point to the smallest annex.

### 23.1 Anomaly Summary INC-8069 at Lagrange Relay L4

**Severity:** SEV-2. **Date:** 2026-04-09. **Reported by:** Greta Thorvaldsen (Propulsion Engineering).

This review covers an event at Lagrange Relay L4 that was traced to an expired certificate in Gantry that blocked manifest synchronisation for several hours. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 12:39 | Normal operations resumed |
| 13:04 | Workaround applied and verified |
| 13:32 | On-call engineer acknowledged the page |
| 13:40 | Affected items moved to quarantine |
| 13:59 | Customer informed by Customer Assurance |

**Root cause.** The Corvid recovery tender turnaround target at Lagrange Relay L4 is 18 hours, measured from landing to ready-for-launch. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. During integration, torque values for every fastener are recorded and attached to the build record.

**Remediation**

- Added monitoring with an alert routed to the Mission Planning on-call engineer.
- Scheduled a follow-up audit at Lagrange Relay L4 in 9 months.

### 23.2 Meeting Notes: Facilities (2024-07-06)

**Attendees:** Soren Ekwueme, Hamid Hargreaves, Kalinda Okonkwo, Quinn Bellweather, Ulrich Yilmaz. **Chair:** Soren Ekwueme. **Location:** Selene Gate, room B16.

**Agenda**

1. Status of the Lodestar upgrade
2. Feedback from Veldt Communications
3. Status of the Tidewater upgrade
4. Any other business

Kalinda Okonkwo reported that the backlog in Halyard had fallen to 92 tickets. The discussion moved to budget, where Kalinda Okonkwo confirmed a remaining allocation of €87,000. Kalinda Okonkwo reminded everyone that the June audit will focus on training records. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Kalinda Okonkwo will draft a short note for Meridian Survey Corp explaining the revised delivery window.

Bastian Thorvaldsen will draft a short note for Talisker Mining explaining the revised delivery window. A proposal to standardise the cryo coupling inspection checklist across sites was well received. It was agreed to revisit the topic once the supplier has delivered the revised quotation. No objections were raised to extending the trial at Ostrava Hub for another 8 weeks.

**Decisions**

- Adopt the shared inspection template at all sites.
- Proceed with the Bulkhead upgrade at Coldharbour Yard in February.
- Ask People Operations to own the escalation path for late customer changes.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Circulate revised MANIFEST rollout plan | Hamid Hargreaves | 2025-03-16 |
| 2 | Collect first-pass inspection yield data for next meeting | Quinn Bellweather | 2026-09-01 |
| 3 | Update training matrix for Procurement | Soren Ekwueme | 2025-03-26 |
| 4 | Update training matrix for Flight Dynamics | Hamid Hargreaves | 2025-05-28 |

### 23.3 Roles and Responsibilities

People and Travel touches almost every team. This section summarises the standards we hold ourselves to and why.

Employees should keep personal notes out of Ledgerline; only operational records belong there. Supervisors are responsible for confirming that new starters have read this section before their first shift. Signage summarising this rule is displayed at every entrance to the Kessler Ridge operations floor. Learning budgets of up to €77,000 per person per year can be spent on approved courses and conferences. Where a task involves a load cell, the two-person rule applies from preparation through to sign-off. The policy owner reviews the wording every 3 months and publishes changes in the revision history. Remote work is supported for roles that do not require hands-on access to flight hardware.

1. Customer representatives may observe loading from the gallery but may not enter the clean area.
2. Questions about interpretation should be raised with Maren Drummond in Quality Assurance rather than resolved informally.
3. Employees should keep personal notes out of Keelson; only operational records belong there.
4. Security incidents must be reported to the Information Security hotline within 30 minutes of discovery.
5. Cargo for Alder Biotech is scanned twice: once on arrival and once immediately before integration.
6. This rule was tightened in 2023 after an internal review found inconsistent practice across sites.

### 23.4 Reporting Obligations

The guidance below grew out of lessons learned at Coldharbour Yard and has since been adopted company-wide.

A breach of this rule is handled under the progressive discipline process described in the People chapter. Overtime above 12 hours per month must be agreed in advance with the line manager. Learning budgets of up to €75,500 per person per year can be spent on approved courses and conferences. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Exceptions require written approval from the Facilities lead and are reviewed again after 3 months. Failure to complete required training within the deadline results in temporary removal from the duty roster. Visitors must be escorted at all times and must not handle a battery module under any circumstances.

1. Night operations require additional lighting checks and a second spotter at the cargo ramp.
2. Supervisors are responsible for confirming that new starters have read this section before their first shift.
3. Questions about interpretation should be raised with Soren Drummond in Flight Dynamics rather than resolved informally.
4. Loading sequences are planned so that the heaviest items sit closest to the Shrike centre of mass.
5. Vendors receive time-limited accounts that expire at the end of their statement of work.
6. Security incidents must be reported to the Information Security hotline within 10 minutes of discovery.

Where this policy conflicts with a customer contract, the stricter requirement applies. This rule was tightened in 2022 after an internal review found inconsistent practice across sites. Records demonstrating compliance are kept in Bulkhead for at least 10 years. Signage summarising this rule is displayed at every entrance to the Hollis Point operations floor. Teams that cannot comply because of tooling limitations must log a risk entry in Lodestar before proceeding.

### 23.5 Roles and Responsibilities

The guidance below grew out of lessons learned at Tarvos Station and has since been adopted company-wide.

Exceptions require written approval from the Orbital Traffic Control lead and are reviewed again after 3 months. Temporary deviations of up to 10 days may be granted by the site director at Tarvos Station. This rule was tightened in 2023 after an internal review found inconsistent practice across sites. Visitors must be escorted at all times and must not handle a battery module under any circumstances. Employees at Brightwater Annex can use the on-site gym between 05:45 and 19:45, except during declared operations.

1. Temporary deviations of up to 90 days may be granted by the site director at Tarvos Station.
2. Where a task involves a load cell, the two-person rule applies from preparation through to sign-off.
3. Shift handover at Hollis Point takes place at 07:00 and must include a walk-through of open work orders.
4. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.
5. This rule was tightened in 2021 after an internal review found inconsistent practice across sites.

Employees should keep personal notes out of Wayfarer; only operational records belong there. Expense claims must be filed in Beacon within 5 days, with receipts attached. The policy owner reviews the wording every 6 months and publishes changes in the revision history.

> **Note:** Where this policy conflicts with a customer contract, the stricter requirement applies.

## Chapter 24: Procurement and Vendors, Part II

The following rules describe expected practice for procurement and vendors. They apply to employees and contractors alike.

### 24.1 Changelog: Cartographer

Cartographer is maintained by the Facilities team. Releases are deployed to Brightwater Annex first and to the remaining sites after a soak period of 30 days.

#### Cartographer 9.5.6 (2022-10-09)

**Added**
- A read-only view for customer representatives.
- Automatic reminders for expiring certifications.

**Fixed**
- Duplicated alerts after a failover at Lagrange Relay L4.
- A crash when a attitude thruster record had no serial number.
- Broken links in exported PDF reports.

#### Cartographer 9.5.5 (2021-08-17)

**Fixed**
- A memory leak in the telemetry ingest worker.

**Added**
- Support for the Petrel cargo profile.

#### Cartographer 9.4.5 (2021-02-11)

**Added**
- Export of on-time departure rate reports to CSV.

**Fixed**
- A memory leak in the telemetry ingest worker.
- Duplicated alerts after a failover at Brightwater Annex.

#### Cartographer 9.4.4 (2021-10-01)

**Removed**
- An unused Sextant integration.
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.

**Fixed**
- Rounding of mass totals in manifests.

#### Cartographer 9.3.0 (2021-03-12)

**Removed**
- The legacy FTP upload path.
- An unused MANIFEST integration.

**Fixed**
- Duplicated alerts after a failover at Selene Gate.
- Broken links in exported PDF reports.
- Incorrect time zones in shift reports.

### 24.2 Quarterly Metrics, 2023

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: cargo damage rate (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Ostrava Hub | 77.3 | 72.7 | 73.7 | 71.6 | 76.2 |
| Brightwater Annex | 90.2 | 85.6 | 90.3 | 84.7 | 90.2 |
| Port Anselm | 66.3 | 64.9 | 67.6 | 61.1 | 66.1 |
| Tarvos Station | 65.0 | 60.5 | 59.0 | 59.3 | 64.1 |

If the primary orbital traffic control center becomes unavailable, authority transfers to the backup ground station in the small town of Pellingford, which is staffed around the clock by a reduced crew of four controllers.

Bram Underhill will draft a short note for Solvay-Ortiz Pharma explaining the revised delivery window. Night operations require additional lighting checks and a second spotter at the cargo ramp. Celeste Gallagher reported that the backlog in Cartographer had fallen to 168 tickets. Celeste Ibarra from Fleet Operations presented the results of the Tarvos Station pilot and recommended a phased rollout.

### 24.3 Incident Review INC-1778 at Kessler Ridge

**Severity:** SEV-4. **Date:** 2025-04-20. **Reported by:** Maren Drummond (Orbital Traffic Control).

This review covers an event at Kessler Ridge that was traced to condensation inside a cryo coupling housing after an unplanned cold soak. No one was injured, and the affected flight departed 10 minutes late.

| Time | Event |
|---|---|
| 13:48 | Work stopped on the affected bay |
| 14:11 | Duty manager declared an incident |
| 14:18 | Customer informed by Customer Assurance |
| 14:41 | Incident closed pending review |
| 15:12 | Workaround applied and verified |

**Root cause.** A telemetry unit that fails its acceptance test twice is quarantined and returned to the supplier. The People Operations desk is staffed from 10:15 to 20:45 on weekdays, with an on-call engineer outside those hours.

**Remediation**

- Added an automated check in Halyard that rejects the condition at entry.
- Replaced the affected battery module stock and quarantined the remaining batch.

### 24.4 Working Group Minutes: Propulsion Engineering (2023-04-04)

**Attendees:** Ximena Yilmaz, Ines Iwasaki, Oona Gallagher, Tamsin Halvorsen, Greta Nakashima. **Chair:** Ximena Yilmaz. **Location:** Port Anselm, room C22.

**Agenda**

1. Budget forecast
2. Feedback from Westerly Weather Service
3. Any other business
4. Feedback from Umbra Imaging
5. Supplier issues with telemetry unit deliveries

Oona Gallagher raised a concern about the workload on the Information Security team during the peak season. Oona Gallagher reported that the backlog in Lodestar had fallen to 238 tickets. No objections were raised to extending the trial at Tarvos Station for another 2 weeks. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Attendees asked for clearer escalation paths when a customer changes requirements late. The team reviewed open risks and closed 6 items that were no longer relevant.

The group agreed that the manifest accuracy had improved, although the sample was still small. Isolde Grimaldi from Fleet Operations presented the results of the Ostrava Hub pilot and recommended a phased rollout. The team reviewed open risks and closed 5 items that were no longer relevant.

**Decisions**

- Ask People Operations to own the escalation path for late customer changes.
- Approve an additional €43,750 for spare attitude thruster stock.
- Extend the night-shift trial by 6 weeks.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Finance | Tamsin Halvorsen | 2026-01-02 |
| 2 | Book readiness review room at Kessler Ridge | Ines Iwasaki | 2025-03-18 |
| 3 | Update training matrix for People Operations | Tamsin Halvorsen | 2026-10-01 |
| 4 | Check budget headroom with Finance | Ximena Yilmaz | 2025-10-20 |

### 24.5 Meeting Notes: Procurement (2021-07-09)

**Attendees:** Celeste Fairbanks, Esme Szabo, Keiko Kuroda, Bram Marchetti. **Chair:** Celeste Fairbanks. **Location:** Tarvos Station, room D3.

**Agenda**

1. Any other business
2. Staffing for the Kessler Ridge campaign
3. Status of the Sextant upgrade
4. Staffing for the Mirefield Depot campaign

Several attendees noted that the current process in MANIFEST requires too many manual steps. The group agreed that the first-pass inspection yield had improved, although the sample was still small. No objections were raised to extending the trial at Brightwater Annex for another 6 weeks. Attendees asked for clearer escalation paths when a customer changes requirements late.

The discussion moved to budget, where Ulrich Quarles confirmed a remaining allocation of €86,750. Attendees asked for clearer escalation paths when a customer changes requirements late. There was a brief debate about whether the Kestrel-9 maintenance window should move to weekends.

**Decisions**

- Ask Cryogenics to own the escalation path for late customer changes.
- Approve an additional €84,000 for spare reaction wheel stock.
- Approve an additional €47,500 for spare reaction wheel stock.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Circulate revised Keelson rollout plan | Esme Szabo | 2026-07-23 |
| 2 | Draft customer note for Solvay-Ortiz Pharma | Bram Marchetti | 2025-02-03 |
| 3 | Collect cargo damage rate data for next meeting | Bram Marchetti | 2025-02-27 |
| 4 | Circulate revised Drydock rollout plan | Keiko Kuroda | 2025-09-01 |
| 5 | Check budget headroom with Finance | Keiko Kuroda | 2025-09-17 |

## Chapter 25: Mission Planning, Part II

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for mission planning.

### 25.1 Record Keeping

Mission Planning touches almost every team. This section summarises the standards we hold ourselves to and why.

Operators log every manual override in Keelson together with the reason and the approving supervisor. Any spending above €81,750 linked to this policy needs approval from Finance before the order is raised. This rule was tightened in 2018 after an internal review found inconsistent practice across sites. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. All Propulsion Engineering staff at Brightwater Annex must complete the refresher module within 5 days of any change to this policy. Night operations require additional lighting checks and a second spotter at the cargo ramp.

1. Questions about interpretation should be raised with Zofia Moravec in Orbital Traffic Control rather than resolved informally.
2. Badges must be worn visibly inside controlled areas and returned when employment ends.
3. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.
4. Temporary deviations of up to 10 days may be granted by the site director at Lagrange Relay L4.
5. Production credentials must never be pasted into chat tools, tickets or shared documents.

Records demonstrating compliance are kept in Sextant for at least 7 years. Where this policy conflicts with a customer contract, the stricter requirement applies. The Petrel transfer stage turnaround target at Lagrange Relay L4 is 6 hours, measured from landing to ready-for-launch.

> **Note:** Exceptions require written approval from the Facilities lead and are reviewed again after 12 months.

### 25.2 Review Board Notes: Quality Assurance (2025-07-11)

**Attendees:** Greta Castellanos, Lorcan Brightman, Ximena Grimaldi, Kalinda Ferreira, Leopold Lowell, Ulrich Rasmussen. **Chair:** Greta Castellanos. **Location:** Mirefield Depot, room D5.

**Agenda**

1. Staffing for the Hollis Point campaign
2. Open audit actions
3. Supplier issues with cryo coupling deliveries

Lorcan Brightman reminded everyone that the April audit will focus on training records. Lorcan Brightman reported that the backlog in Cartographer had fallen to 114 tickets. The team reviewed open risks and closed 15 items that were no longer relevant. The discussion moved to budget, where Lorcan Brightman confirmed a remaining allocation of €84,750. There was a brief debate about whether the Shrike maintenance window should move to weekends. Several attendees noted that the current process in Tidewater requires too many manual steps. Lorcan Brightman from Mission Planning presented the results of the Kessler Ridge pilot and recommended a phased rollout.

The team reviewed open risks and closed 12 items that were no longer relevant. There was a brief debate about whether the Heron maintenance window should move to weekends. Isolde Varga raised a concern about the workload on the Cryogenics team during the peak season. Greta Ekwueme will draft a short note for Westerly Weather Service explaining the revised delivery window. Attendees asked for clearer escalation paths when a customer changes requirements late.

**Decisions**

- Adopt the shared inspection template at all sites.
- Close the open risk on Wren maintenance windows.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Draft customer note for Meridian Survey Corp | Ulrich Rasmussen | 2026-04-26 |
| 2 | Draft customer note for Veldt Communications | Ximena Grimaldi | 2026-02-21 |
| 3 | Book readiness review room at Mirefield Depot | Leopold Lowell | 2025-11-21 |
| 4 | Confirm thermal blanket delivery dates with supplier | Ulrich Rasmussen | 2026-06-23 |

### 25.3 Data Query Example (Gantry)

Use these commands, in order, when the Gantry ingest queue at Selene Gate stops draining. Stop at the first step that resolves the problem.

```bash
# 1. Check queue depth
nolctl queue status --service gantry --site selene-gate

# 2. Drain stuck consumers (safe, idempotent)
nolctl queue rebalance --service gantry --max-moves 12

# 3. Restart one worker at a time
nolctl worker restart --service gantry --one-at-a-time --wait 90s

# 4. Escalate if depth is still above 16690 after 15 minutes
nolctl page --team cryogenics --severity high
```

### 25.4 Release Notes: Keelson

Keelson is maintained by the Fleet Operations team. Releases are deployed to Selene Gate first and to the remaining sites after a soak period of 7 days.

#### Keelson 9.1.2 (2025-06-04)

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

**Fixed**
- Incorrect time zones in shift reports.
- Rounding of mass totals in manifests.

**Changed**
- The approval flow so that Facilities signs off before Finance.
- Timeouts for the Hollis Point gateway from 2 to 60 seconds.

#### Keelson 9.0.1 (2025-06-08)

**Fixed**
- A crash when a telemetry unit record had no serial number.
- A race condition when two operators edited the same pallet.

**Changed**
- The default retention period to 18 months.
- Sorting on the work-order list.

#### Keelson 9.0.3 (2024-09-05)

**Changed**
- Sorting on the work-order list.
- The default retention period to 24 months.

**Fixed**
- A crash when a telemetry unit record had no serial number.
- Broken links in exported PDF reports.
- Duplicated alerts after a failover at Ostrava Hub.

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

#### Keelson 9.0.6 (2023-10-16)

**Added**
- A dry-run mode for configuration changes.
- Per-site dashboards for Quality Assurance.
- A read-only view for customer representatives.

**Fixed**
- Rounding of mass totals in manifests.

**Changed**
- Sorting on the work-order list.

#### Keelson 9.0.5 (2023-03-15)

**Changed**
- Log formatting to include the operator badge number.
- Timeouts for the Brightwater Annex gateway from 15 to 10 seconds.
- Sorting on the work-order list.

**Fixed**
- Broken links in exported PDF reports.
- A crash when a umbilical connector record had no serial number.
- A memory leak in the telemetry ingest worker.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Halyard integration.

### 25.5 Incident Review INC-7118 at Ostrava Hub

**Severity:** SEV-2. **Date:** 2024-09-02. **Reported by:** Anouk Zelenko (Facilities).

This review covers an event at Ostrava Hub that was traced to an expired certificate in Signal Lamp that blocked manifest synchronisation for several hours. No one was injured, and the affected flight departed 5 minutes late.

| Time | Event |
|---|---|
| 06:01 | First alert received by the operations bridge |
| 06:22 | Incident closed pending review |
| 06:30 | Work stopped on the affected bay |
| 06:55 | On-call engineer acknowledged the page |
| 07:35 | Customer informed by Customer Assurance |

**Root cause.** Loading sequences are planned so that the heaviest items sit closest to the Petrel centre of mass. A attitude thruster that fails its acceptance test twice is quarantined and returned to the supplier. Firmware for the thermal blanket is distributed through Signal Lamp and must be verified before installation. Engineers should consult the MANIFEST configuration record before changing any calibration constant.

**Remediation**

- Replaced the affected radiator panel stock and quarantined the remaining batch.
- Scheduled a follow-up audit at Ostrava Hub in 18 months.

## Chapter 26: Quality and Audits, Part II

This part of the handbook was last reviewed by Dorian Nakashima and reflects the practice agreed in 2018.

### 26.1 Escalation Rules

The following rules describe expected practice for quality and audits. They apply to employees and contractors alike.

Fuel loading is the last activity before closeout, and no other work may proceed in parallel. Night operations require additional lighting checks and a second spotter at the cargo ramp. Supervisors are responsible for confirming that new starters have read this section before their first shift. Failure to complete required training within the deadline results in temporary removal from the duty roster.

1. A breach of this rule is handled under the progressive discipline process described in the People chapter.
2. If a pallet arrives without a valid manifest entry in Lodestar, it is held in the quarantine cage.
3. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.
4. Any spending above €50,250 linked to this policy needs approval from Finance before the order is raised.
5. Audit samples are drawn quarterly, and at least 2 findings per site are followed up in person.
6. Signage summarising this rule is displayed at every entrance to the Kessler Ridge operations floor.

### 26.2 Compliance Monitoring

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for quality and audits.

This rule was tightened in 2020 after an internal review found inconsistent practice across sites. Exceptions require written approval from the Propulsion Engineering lead and are reviewed again after 24 months. Contractors working on site are bound by the same obligations as employees for the duration of their engagement. Teams that cannot comply because of tooling limitations must log a risk entry in Beacon before proceeding.

1. Spare parts for the Heron fleet are pooled at Lagrange Relay L4 and shipped to other sites within 48 hours.
2. Laptops are encrypted at rest and enrolled in device management before first use.
3. Badges must be worn visibly inside controlled areas and returned when employment ends.
4. The Shrike inspection pod turnaround target at Lagrange Relay L4 is 36 hours, measured from landing to ready-for-launch.
5. Where a task involves a hatch seal, the two-person rule applies from preparation through to sign-off.

The Heron-class freighter turnaround target at Coldharbour Yard is 72 hours, measured from landing to ready-for-launch. Supervisors are responsible for confirming that new starters have read this section before their first shift. Night operations require additional lighting checks and a second spotter at the cargo ramp.

> **Note:** Questions about interpretation should be raised with Celeste Achterberg in Cryogenics rather than resolved informally.

### 26.3 Common Questions about Quality and Audits

**Q: How do I request access to flight data?**

Raise an access request in Keelson. Requests are approved by the data owner in Ground Systems and usually processed within 60 working days.

**Q: Who approves a change to the Sextant configuration?**

Changes are approved by the Finance lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within 90 days.

**Q: Where are spare reaction wheel parts stored?**

The central pool is at Tarvos Station. Each site also keeps a small buffer stock sized from the last 24 months of usage.

**Q: Who do I call if the Pilot House service is down?**

Contact the Orbital Traffic Control on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

**Q: What counts as a near miss?**

Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents.

### 26.4 Configuration Baseline: Gannet radiator panel

The Gannet refueling drone supports both automated and manual docking, although manual mode is reserved for certified pilots. The Gannet refueling drone uses a dual-redundant radiator panel that switches over automatically within 210 ms of a fault. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. Data from each pass is reconciled in Ledgerline and flagged if more than 11 percent of frames are missing. Power draw peaks at 793 W during the deployment sequence and settles at roughly a third of that.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Design life | 7,100 cycles | n/a | Hard limit, no extension |
| Supplier | Ostrander Aerospace Ltd | n/a | Approved vendor list |
| Peak power | 1495 W | ±2 % | During deployment |
| Operating temperature | -54 to 57 °C | ±1 °C | Qualification limits are wider |
| Data rate | 554 kbit/s | n/a | Compressed telemetry |

The Gannet refueling drone can hold station for up to 16 hours before its propellant margin falls below reserve. Ground tests at Coldharbour Yard showed a mean drift of 0.87 percent over 36 hours of continuous soak. Thermal margins were re-analysed after the 2024 anomaly, and the upper limit was lowered by 7 °C.

**Operating limits**

- Thermal margins were re-analysed after the 2025 anomaly, and the upper limit was lowered by 9 °C.
- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.
- Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 3,330 cycles.

### 26.5 Definitions in Use

Quality and Audits touches almost every team. This section summarises the standards we hold ourselves to and why.

Spare parts for the Gannet fleet are pooled at Hollis Point and shipped to other sites within 4 hours. Night operations require additional lighting checks and a second spotter at the cargo ramp. Records demonstrating compliance are kept in Keelson for at least 2 years. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. The Ostrava Hub yard has 9 bays, each rated for a different maximum load and hazard class. The requirement applies equally to remote staff who access Gantry from outside a company site.

1. Exceptions require written approval from the Finance lead and are reviewed again after 6 months.
2. Customer representatives may observe loading from the gallery but may not enter the clean area.
3. Spare parts for the Corvid fleet are pooled at Mirefield Depot and shipped to other sites within 8 hours.
4. Operators log every manual override in Sextant together with the reason and the approving supervisor.
5. Failure to complete required training within the deadline results in temporary removal from the duty roster.

> **Note:** Supervisors are responsible for confirming that new starters have read this section before their first shift.

### 26.6 Meeting Notes: Ground Systems (2026-10-26)

**Attendees:** Lorcan Lindqvist, Bram Underhill, Kalinda Fairbanks, Elif Eskildsen. **Chair:** Lorcan Lindqvist. **Location:** Lagrange Relay L4, room D23.

**Agenda**

1. Feedback from Umbra Imaging
2. Budget forecast
3. Status of the Wayfarer upgrade
4. Supplier issues with radiator panel deliveries

No objections were raised to extending the trial at Tarvos Station for another 8 weeks. Elif Eskildsen reminded everyone that the February audit will focus on training records. The group agreed that the on-time departure rate had improved, although the sample was still small. There was a brief debate about whether the Petrel maintenance window should move to weekends. Elif Eskildsen reported that the backlog in Cartographer had fallen to 37 tickets. Elif Eskildsen will draft a short note for Quillon Satellites explaining the revised delivery window.

The group agreed that the planned maintenance compliance had improved, although the sample was still small. Oona Underhill from Orbital Traffic Control presented the results of the Lagrange Relay L4 pilot and recommended a phased rollout. Elif Bellweather will draft a short note for Westerly Weather Service explaining the revised delivery window. Tamsin Brightman reminded everyone that the July audit will focus on training records. The team reviewed open risks and closed 11 items that were no longer relevant.

**Decisions**

- Adopt the shared inspection template at all sites.
- Approve an additional €35,500 for spare reaction wheel stock.
- Ask Procurement to own the escalation path for late customer changes.
- Defer the cargo cradle checklist change until the supplier responds.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Quality Assurance | Lorcan Lindqvist | 2025-11-16 |
| 2 | Confirm thermal blanket delivery dates with supplier | Kalinda Fairbanks | 2025-05-01 |
| 3 | Book readiness review room at Hollis Point | Elif Eskildsen | 2026-08-18 |

## Chapter 27: Customer Commitments, Part II

The following rules describe expected practice for customer commitments. They apply to employees and contractors alike.

### 27.1 Changelog: Halyard

Halyard is maintained by the Cargo Integrity team. Releases are deployed to Port Anselm first and to the remaining sites after a soak period of 7 days.

#### Halyard 6.10.3 (2026-08-19)

**Fixed**
- A memory leak in the telemetry ingest worker.
- Broken links in exported PDF reports.

**Removed**
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.
- An unused Keelson integration.

#### Halyard 6.10.2 (2025-01-06)

**Added**
- Automatic reminders for expiring certifications.

**Fixed**
- Incorrect time zones in shift reports.
- Broken links in exported PDF reports.

#### Halyard 6.10.1 (2024-09-26)

**Added**
- Bulk import of attitude thruster serial numbers.

**Removed**
- The deprecated v1 manifest endpoint.

### 27.2 Quarterly Metrics, 2026

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: planned maintenance compliance (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Coldharbour Yard | 62.8 | 59.7 | 58.8 | 62.0 | 63.3 |
| Kessler Ridge | 72.2 | 77.6 | 73.9 | 77.2 | 76.9 |
| Ostrava Hub | 92.9 | 93.5 | 94.9 | 96.4 | 97.3 |

Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Delays longer than 5 minutes are reported to the customer by Customer Assurance, not by the floor team.

### 27.3 Definitions in Use

This part of the handbook was last reviewed by Kalinda Grimaldi and reflects the practice agreed in 2021.

A breach of this rule is handled under the progressive discipline process described in the People chapter. Records demonstrating compliance are kept in MANIFEST for at least 7 years. Where this policy conflicts with a customer contract, the stricter requirement applies. The Wren crew shuttle turnaround target at Ostrava Hub is 16 hours, measured from landing to ready-for-launch. The Selene Gate yard has 18 bays, each rated for a different maximum load and hazard class.

1. Accounts that have not been used for 5 days are disabled automatically.
2. Teams that cannot comply because of tooling limitations must log a risk entry in Lodestar before proceeding.
3. Operators log every manual override in MANIFEST together with the reason and the approving supervisor.
4. Employees should keep personal notes out of Bulkhead; only operational records belong there.
5. Access to Keelson requires hardware-key authentication and is reviewed every 90 days.
6. Shift handover at Ostrava Hub takes place at 07:00 and must include a walk-through of open work orders.

Visitors must be escorted at all times and must not handle a star tracker under any circumstances. Temporary deviations of up to 21 days may be granted by the site director at Lagrange Relay L4. The Information Security desk is staffed from 08:00 to 18:15 on weekdays, with an on-call engineer outside those hours. The Gannet refueling drone turnaround target at Coldharbour Yard is 8 hours, measured from landing to ready-for-launch.

### 27.4 Reporting Obligations

Customer Commitments touches almost every team. This section summarises the standards we hold ourselves to and why.

Night operations require additional lighting checks and a second spotter at the cargo ramp. Audit samples are drawn quarterly, and at least 5 findings per site are followed up in person. Shift handover at Brightwater Annex takes place at 09:00 and must include a walk-through of open work orders. Exceptions require written approval from the Cargo Integrity lead and are reviewed again after 24 months. Any spending above €55,000 linked to this policy needs approval from Finance before the order is raised.

1. Security incidents must be reported to the Information Security hotline within 15 minutes of discovery.
2. Laptops are encrypted at rest and enrolled in device management before first use.
3. Production credentials must never be pasted into chat tools, tickets or shared documents.
4. Supervisors are responsible for confirming that new starters have read this section before their first shift.
5. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.

If a pallet arrives without a valid manifest entry in Signal Lamp, it is held in the quarantine cage. Signage summarising this rule is displayed at every entrance to the Brightwater Annex operations floor. The policy owner reviews the wording every 3 months and publishes changes in the revision history. This rule was tightened in 2018 after an internal review found inconsistent practice across sites. Exceptions require written approval from the Cryogenics lead and are reviewed again after 18 months.

> **Note:** The policy owner reviews the wording every 6 months and publishes changes in the revision history.

## Chapter 28: Incident Management, Part II

This section explains how Northwind Orbital Logistics approaches incident management at every site, from Selene Gate to the smallest annex.

### 28.1 Roles and Responsibilities

The guidance below grew out of lessons learned at Brightwater Annex and has since been adopted company-wide.

Records demonstrating compliance are kept in Keelson for at least 10 years. Delays longer than 20 minutes are reported to the customer by Customer Assurance, not by the floor team. Signage summarising this rule is displayed at every entrance to the Tarvos Station operations floor. If a pallet arrives without a valid manifest entry in Lodestar, it is held in the quarantine cage. The Kessler Ridge yard has 4 bays, each rated for a different maximum load and hazard class. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision. Audit samples are drawn quarterly, and at least 17 findings per site are followed up in person.

1. Employees should keep personal notes out of Halyard; only operational records belong there.
2. Temporary deviations of up to 30 days may be granted by the site director at Brightwater Annex.
3. Loading sequences are planned so that the heaviest items sit closest to the Wren centre of mass.
4. Cargo for Talisker Mining is scanned twice: once on arrival and once immediately before integration.
5. Laptops are encrypted at rest and enrolled in device management before first use.

Contractors working on site are bound by the same obligations as employees for the duration of their engagement. Audit samples are drawn quarterly, and at least 12 findings per site are followed up in person. Night operations require additional lighting checks and a second spotter at the cargo ramp. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.

### 28.2 Minimum Standards

Incident Management touches almost every team. This section summarises the standards we hold ourselves to and why.

This rule was tightened in 2023 after an internal review found inconsistent practice across sites. Questions about interpretation should be raised with Ines Kuroda in Propulsion Engineering rather than resolved informally. Exceptions require written approval from the Finance lead and are reviewed again after 12 months. Supervisors are responsible for confirming that new starters have read this section before their first shift. Where a task involves a pressure regulator, the two-person rule applies from preparation through to sign-off. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.

1. Log data from Gantry is retained for 12 months and then archived to cold storage.
2. Any spending above €73,750 linked to this policy needs approval from Finance before the order is raised.
3. Where this policy conflicts with a customer contract, the stricter requirement applies.
4. Nothing in this section prevents an employee from stopping work they believe to be unsafe.

### 28.3 Definitions in Use

The guidance below grew out of lessons learned at Ostrava Hub and has since been adopted company-wide.

Customer representatives may observe loading from the gallery but may not enter the clean area. Where a task involves a radiator panel, the two-person rule applies from preparation through to sign-off. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. The requirement applies equally to remote staff who access Halyard from outside a company site. Shift handover at Coldharbour Yard takes place at 09:00 and must include a walk-through of open work orders.

1. Teams that cannot comply because of tooling limitations must log a risk entry in Drydock before proceeding.
2. The Lagrange Relay L4 yard has 17 bays, each rated for a different maximum load and hazard class.
3. Penetration tests of public-facing services are commissioned at least once per year.
4. Production credentials must never be pasted into chat tools, tickets or shared documents.
5. Signage summarising this rule is displayed at every entrance to the Tarvos Station operations floor.

> **Note:** The requirement applies equally to remote staff who access Signal Lamp from outside a company site.

### 28.4 Operating Limits: Shrike pressure regulator

Data from each pass is reconciled in Cartographer and flagged if more than 4 percent of frames are missing. Nominal operating temperature for the pressure regulator ranges from -50 °C to 45 °C. The latest revision reduced mass by 8.5 kg by replacing the aluminium bracket with a composite part. The Shrike inspection pod uses a dual-redundant pressure regulator that switches over automatically within 98 ms of a fault. The Shrike inspection pod supports both automated and manual docking, although manual mode is reserved for certified pilots.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Operating temperature | -42 to 59 °C | ±5 °C | Qualification limits are wider |
| Supplier | Hargreaves Precision Ltd | n/a | Approved vendor list |
| Peak power | 825 W | ±3 % | During deployment |
| Dry mass | 6,976 kg | ±3 kg | Includes brackets |
| Design life | 4,070 cycles | n/a | Hard limit, no extension |

Ground tests at Kessler Ridge showed a mean drift of 0.37 percent over 18 hours of continuous soak. The latest revision reduced mass by 23.0 kg by replacing the aluminium bracket with a composite part. Each pressure regulator carries a serial plate that encodes the batch, the factory and the inspection date. A pressure regulator that fails its acceptance test twice is quarantined and returned to the supplier. The design team at Hollis Point owns the interface control document and approves every change to it.

**Operating limits**

- During integration, torque values for every fastener are recorded and attached to the build record.
- Ground tests at Coldharbour Yard showed a mean drift of 0.93 percent over 6 hours of continuous soak.
- A pressure regulator that fails its acceptance test twice is quarantined and returned to the supplier.
- Data from each pass is reconciled in Tidewater and flagged if more than 14 percent of frames are missing.

### 28.5 Anomaly Summary INC-8828 at Mirefield Depot

**Severity:** SEV-2. **Date:** 2025-01-18. **Reported by:** Anouk Ekwueme (Flight Dynamics).

This review covers an event at Mirefield Depot that was traced to a network switch failure at Mirefield Depot that isolated the telemetry archive. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 20:18 | Customer informed by Customer Assurance |
| 20:29 | Incident closed pending review |
| 20:48 | Work stopped on the affected bay |
| 21:01 | Duty manager declared an incident |
| 21:40 | First alert received by the operations bridge |
| 21:59 | Affected items moved to quarantine |

**Root cause.** Ground tests at Mirefield Depot showed a mean drift of 0.62 percent over 36 hours of continuous soak. The Shrike inspection pod can hold station for up to 12 hours before its propellant margin falls below reserve. The design team at Mirefield Depot owns the interface control document and approves every change to it. Shift handover at Mirefield Depot takes place at 09:30 and must include a walk-through of open work orders.

**Remediation**

- Scheduled a follow-up audit at Mirefield Depot in 6 months.
- Introduced a second sign-off for the affected step.
- Replaced the affected star tracker stock and quarantined the remaining batch.
- Revised the supplier quality agreement to include lot traceability.

## Chapter 29: Propulsion and Cryogenics, Part II

This section explains how Northwind Orbital Logistics approaches propulsion and cryogenics at every site, from Port Anselm to the smallest annex.

### 29.1 Runbook Commands (Lodestar)

A minimal manifest entry, as accepted by the Lodestar API, looks like this:

```json
{
  "consignment_id": "CN-8317",
  "customer": "Alder Biotech",
  "site": "coldharbour-yard",
  "items": [
    {"id": "IT-8337", "mass_kg": 458.6, "hazard_class": 2, "position": "C2"},
    {"id": "IT-7258", "mass_kg": 284.2, "hazard_class": 0, "position": "C3"}
  ],
  "requested_departure": "2025-02-14"
}
```

Positions refer to the cradle grid of the target vehicle. Items without a position are placed by the loading planner and confirmed during integration.

### 29.2 Release Notes: Signal Lamp

Signal Lamp is maintained by the People Operations team. Releases are deployed to Selene Gate first and to the remaining sites after a soak period of 10 days.

#### Signal Lamp 5.0.0 (2022-11-14)

**Changed**
- The approval flow so that Cryogenics signs off before Finance.
- Log formatting to include the operator badge number.

**Removed**
- The legacy FTP upload path.

#### Signal Lamp 5.0.5 (2022-04-22)

**Removed**
- An unused Sextant integration.
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.

**Added**
- Support for the Wren cargo profile.

**Changed**
- Log formatting to include the operator badge number.
- Timeouts for the Tarvos Station gateway from 120 to 60 seconds.

#### Signal Lamp 5.0.4 (2021-07-05)

**Changed**
- Log formatting to include the operator badge number.
- The manifest schema to version 4.7.

**Added**
- Export of ticket backlog reports to CSV.
- Bulk import of load cell serial numbers.

**Fixed**
- A race condition when two operators edited the same pallet.
- Duplicated alerts after a failover at Coldharbour Yard.

#### Signal Lamp 5.0.3 (2021-04-27)

**Changed**
- The default retention period to 24 months.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Keelson integration.

#### Signal Lamp 5.0.0 (2021-01-20)

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Sextant integration.
- The legacy FTP upload path.

**Fixed**
- A memory leak in the telemetry ingest worker.
- Rounding of mass totals in manifests.

### 29.3 Reference Script (Wayfarer)

A minimal manifest entry, as accepted by the Wayfarer API, looks like this:

```json
{
  "consignment_id": "CN-1124",
  "customer": "Meridian Survey Corp",
  "site": "mirefield-depot",
  "items": [
    {"id": "IT-499", "mass_kg": 269.0, "hazard_class": 0, "position": "B3"},
    {"id": "IT-6808", "mass_kg": 517.9, "hazard_class": 4, "position": "C3"}
  ],
  "requested_departure": "2026-01-10"
}
```

Positions refer to the cradle grid of the target vehicle. Items without a position are placed by the loading planner and confirmed during integration.

### 29.4 Release Notes: Sextant

Sextant is maintained by the Flight Dynamics team. Releases are deployed to Tarvos Station first and to the remaining sites after a soak period of 60 days.

#### Sextant 6.3.1 (2022-10-08)

**Changed**
- The approval flow so that Cargo Integrity signs off before Finance.
- Sorting on the work-order list.
- Log formatting to include the operator badge number.

**Added**
- Per-site dashboards for Cargo Integrity.
- Bulk import of battery module serial numbers.

**Removed**
- An unused Sextant integration.

#### Sextant 6.2.6 (2022-12-16)

**Added**
- Per-site dashboards for Flight Dynamics.

**Removed**
- The legacy FTP upload path.
- An unused Drydock integration.
- The deprecated v1 manifest endpoint.

**Changed**
- Sorting on the work-order list.
- The approval flow so that Flight Dynamics signs off before Finance.

#### Sextant 6.1.2 (2022-11-25)

**Changed**
- Timeouts for the Mirefield Depot gateway from 30 to 45 seconds.
- Log formatting to include the operator badge number.
- The manifest schema to version 4.9.

**Added**
- Export of mean time to repair reports to CSV.
- Automatic reminders for expiring certifications.

**Fixed**
- Rounding of mass totals in manifests.
- Broken links in exported PDF reports.

#### Sextant 6.1.1 (2021-04-13)

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Beacon integration.
- The legacy FTP upload path.

**Added**
- Export of first-pass inspection yield reports to CSV.
- A read-only view for customer representatives.
- Automatic reminders for expiring certifications.

#### Sextant 6.1.0 (2021-10-15)

**Added**
- Automatic reminders for expiring certifications.
- Per-site dashboards for Flight Dynamics.
- Export of audit finding closure rate reports to CSV.

**Removed**
- An unused Drydock integration.

### 29.5 Roles and Responsibilities

Readers new to Northwind Orbital Logistics should treat this section as the authoritative reference for propulsion and cryogenics.

The Petrel transfer stage turnaround target at Tarvos Station is 4 hours, measured from landing to ready-for-launch. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. The People Operations desk is staffed from 10:45 to 17:15 on weekdays, with an on-call engineer outside those hours. If a pallet arrives without a valid manifest entry in Wayfarer, it is held in the quarantine cage. Failure to complete required training within the deadline results in temporary removal from the duty roster.

1. Operators log every manual override in Wayfarer together with the reason and the approving supervisor.
2. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
3. Visitors must be escorted at all times and must not handle a star tracker under any circumstances.
4. The Cryogenics team runs a phishing simulation every 24 months and publishes anonymised results.

Employees should keep personal notes out of Wayfarer; only operational records belong there. Operators log every manual override in Drydock together with the reason and the approving supervisor. Failure to complete required training within the deadline results in temporary removal from the duty roster. Temporary deviations of up to 10 days may be granted by the site director at Mirefield Depot.

> **Note:** The policy owner reviews the wording every 3 months and publishes changes in the revision history.

## Chapter 30: Data Retention, Part II

This part of the handbook was last reviewed by Gideon Marchetti and reflects the practice agreed in 2019.

### 30.1 Equipment Data Sheet: Petrel pressure regulator

Each pressure regulator carries a serial plate that encodes the batch, the factory and the inspection date. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. Nominal operating temperature for the pressure regulator ranges from -12 °C to 62 °C. Data from each pass is reconciled in Pilot House and flagged if more than 6 percent of frames are missing.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Dry mass | 5,598 kg | ±13 kg | Includes brackets |
| Part number | PET-PRE-9681 | n/a | Revision B |
| Supplier | Rasmussen Instruments Ltd | n/a | Approved vendor list |
| Peak power | 72 W | ±9 % | During deployment |
| Mounting | 4 × M6 bolts | Torque 4 N·m | Thread-locker required |

The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots. The Petrel transfer stage uses a dual-redundant pressure regulator that switches over automatically within 267 ms of a fault. Ground tests at Brightwater Annex showed a mean drift of 0.44 percent over 36 hours of continuous soak. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

**Operating limits**

- The design team at Tarvos Station owns the interface control document and approves every change to it.
- Ground tests at Hollis Point showed a mean drift of 0.64 percent over 18 hours of continuous soak.
- The Petrel transfer stage uses a dual-redundant pressure regulator that switches over automatically within 218 ms of a fault.

### 30.2 Review Board Notes: Procurement (2023-10-26)

**Attendees:** Bram Ekwueme, Ulrich Zelenko, Jonas Pemberton, Maren Zelenko, Yusuf Ferreira, Hollis Fairbanks, Pavel Drummond. **Chair:** Bram Ekwueme. **Location:** Tarvos Station, room B10.

**Agenda**

1. Supplier issues with cargo cradle deliveries
2. Open audit actions
3. Open audit actions

Attendees asked for clearer escalation paths when a customer changes requirements late. Several attendees noted that the current process in Beacon requires too many manual steps. The discussion moved to budget, where Hollis Fairbanks confirmed a remaining allocation of €98,500. There was a brief debate about whether the Heron maintenance window should move to weekends. Hollis Fairbanks reported that the backlog in MANIFEST had fallen to 212 tickets.

Nnamdi Jessop raised a concern about the workload on the Facilities team during the peak season. Elif Jessop reminded everyone that the December audit will focus on training records. The team reviewed open risks and closed 3 items that were no longer relevant. No objections were raised to extending the trial at Mirefield Depot for another 12 weeks.

**Decisions**

- Extend the night-shift trial by 8 weeks.
- Approve an additional €83,250 for spare data recorder stock.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Book readiness review room at Kessler Ridge | Ulrich Zelenko | 2026-10-21 |
| 2 | Check budget headroom with Finance | Maren Zelenko | 2026-06-08 |
| 3 | Draft customer note for Umbra Imaging | Maren Zelenko | 2025-06-22 |
| 4 | Confirm umbilical connector delivery dates with supplier | Hollis Fairbanks | 2026-06-15 |

### 30.3 Definitions in Use

The following rules describe expected practice for data retention. They apply to employees and contractors alike.

Exceptions require written approval from the Cargo Integrity lead and are reviewed again after 3 months. Nothing in this section prevents an employee from stopping work they believe to be unsafe. Questions about interpretation should be raised with Bastian Marchetti in Orbital Traffic Control rather than resolved informally. If a pallet arrives without a valid manifest entry in Signal Lamp, it is held in the quarantine cage. Operators log every manual override in Lodestar together with the reason and the approving supervisor.

1. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
2. The policy owner reviews the wording every 24 months and publishes changes in the revision history.
3. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
4. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.
5. A breach of this rule is handled under the progressive discipline process described in the People chapter.

The decommissioned relay satellite ND-Sentinel-3 was affectionately nicknamed "Old Biscuit" by the operations crew because of the beige thermal blankets that made it look, in early camera images, like a cracker floating in space.

Where this policy conflicts with a customer contract, the stricter requirement applies. Any spending above €25,500 linked to this policy needs approval from Finance before the order is raised. Teams that cannot comply because of tooling limitations must log a risk entry in MANIFEST before proceeding. Night operations require additional lighting checks and a second spotter at the cargo ramp. If a pallet arrives without a valid manifest entry in Bulkhead, it is held in the quarantine cage.

> **Note:** Teams that cannot comply because of tooling limitations must log a risk entry in Gantry before proceeding.

### 30.4 Meeting Notes: Facilities (2021-06-27)

**Attendees:** Soren Szabo, Ines Fairbanks, Ulrich Jessop, Zofia Szabo, Ines Kuroda. **Chair:** Soren Szabo. **Location:** Mirefield Depot, room D19.

**Agenda**

1. Status of the MANIFEST upgrade
2. Budget forecast
3. Status of the Lodestar upgrade
4. Budget forecast

There was a brief debate about whether the Osprey maintenance window should move to weekends. Several attendees noted that the current process in Gantry requires too many manual steps. Soren Szabo raised a concern about the workload on the Information Security team during the peak season. Soren Szabo from Fleet Operations presented the results of the Lagrange Relay L4 pilot and recommended a phased rollout. Attendees asked for clearer escalation paths when a customer changes requirements late. Soren Szabo reminded everyone that the April audit will focus on training records. The group agreed that the ticket backlog had improved, although the sample was still small.

The group agreed that the cargo damage rate had improved, although the sample was still small. Mirela Rasmussen from Information Security presented the results of the Mirefield Depot pilot and recommended a phased rollout. Several attendees noted that the current process in Bulkhead requires too many manual steps.

**Decisions**

- Ask Propulsion Engineering to own the escalation path for late customer changes.
- Ask People Operations to own the escalation path for late customer changes.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Circulate revised Wayfarer rollout plan | Soren Szabo | 2026-05-13 |
| 2 | Update training matrix for Information Security | Ulrich Jessop | 2025-01-22 |
| 3 | Draft customer note for Yarrow Agritech | Ulrich Jessop | 2025-11-17 |
| 4 | Update training matrix for Ground Systems | Zofia Szabo | 2025-05-22 |
| 5 | Update training matrix for Quality Assurance | Ulrich Jessop | 2026-05-20 |

### 30.5 Working with Contractors

The guidance below grew out of lessons learned at Coldharbour Yard and has since been adopted company-wide.

Records demonstrating compliance are kept in Pilot House for at least 10 years. Cargo for Yarrow Agritech is scanned twice: once on arrival and once immediately before integration. Customer representatives may observe loading from the gallery but may not enter the clean area. Nothing in this section prevents an employee from stopping work they believe to be unsafe. The policy owner reviews the wording every 24 months and publishes changes in the revision history.

1. A breach of this rule is handled under the progressive discipline process described in the People chapter.
2. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.
3. If a pallet arrives without a valid manifest entry in Cartographer, it is held in the quarantine cage.
4. Customer representatives may observe loading from the gallery but may not enter the clean area.
5. Accounts that have not been used for 21 days are disabled automatically.
6. Security incidents must be reported to the Information Security hotline within 15 minutes of discovery.

### 30.6 Review Board Notes: Cargo Integrity (2022-12-12)

**Attendees:** Isolde Jessop, Pavel Jessop, Joaquin Abernathy, Leopold Grimaldi, Lorcan Coutinho. **Chair:** Isolde Jessop. **Location:** Port Anselm, room C14.

**Agenda**

1. Staffing for the Brightwater Annex campaign
2. Staffing for the Brightwater Annex campaign
3. Staffing for the Coldharbour Yard campaign
4. Supplier issues with attitude thruster deliveries
5. Open audit actions

There was a brief debate about whether the Shrike maintenance window should move to weekends. The group agreed that the customer satisfaction score had improved, although the sample was still small. The team reviewed open risks and closed 18 items that were no longer relevant. It was agreed to revisit the topic once the supplier has delivered the revised quotation. Attendees asked for clearer escalation paths when a customer changes requirements late. Joaquin Abernathy raised a concern about the workload on the Quality Assurance team during the peak season.

A proposal to standardise the cryo coupling inspection checklist across sites was well received. Kalinda Hargreaves reported that the backlog in Drydock had fallen to 150 tickets. The discussion moved to budget, where Florian Delacroix confirmed a remaining allocation of €26,750. No objections were raised to extending the trial at Selene Gate for another 4 weeks. Gideon Abernathy will draft a short note for Umbra Imaging explaining the revised delivery window.

**Decisions**

- Adopt the shared inspection template at all sites.
- Defer the cargo cradle checklist change until the supplier responds.
- Defer the attitude thruster checklist change until the supplier responds.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Circulate revised Tidewater rollout plan | Joaquin Abernathy | 2025-08-17 |
| 2 | Book readiness review room at Tarvos Station | Joaquin Abernathy | 2026-01-08 |
| 3 | Book readiness review room at Lagrange Relay L4 | Isolde Jessop | 2026-09-23 |
| 4 | Confirm cargo cradle delivery dates with supplier | Isolde Jessop | 2025-11-18 |

## Chapter 31: Environmental Practices, Part II

This part of the handbook was last reviewed by Amara Zelenko and reflects the practice agreed in 2023.

### 31.1 Common Questions about Environmental Practices

**Q: Where are spare load cell parts stored?**

The central pool is at Hollis Point. Each site also keeps a small buffer stock sized from the last 9 months of usage.

**Q: What counts as a near miss?**

Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents.

**Q: Who do I call if the Gantry service is down?**

Contact the Propulsion Engineering on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

### 31.2 Common Questions about Environmental Practices

**Q: What counts as a near miss?**

Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents.

**Q: How do I request access to flight data?**

Raise an access request in Beacon. Requests are approved by the data owner in Fleet Operations and usually processed within 21 working days.

**Q: Can I bring a guest onto the Mirefield Depot operations floor?**

Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area.

### 31.3 Reference Script (Beacon)

The excerpt below shows the production configuration of Beacon at Brightwater Annex. Values marked `# tuned` were adjusted during the last capacity review.

```yaml
service: beacon
site: brightwater-annex
replicas: 2
listen_port: 9483
timeouts:
  connect_s: 10
  read_s: 15  # tuned
retention:
  shift_logs_days: 1825
  telemetry_days: 90
alerts:
  route: cargo-integrity-oncall
  severity_threshold: critical
feature_flags:
  dry_run_default: false
  bulk_import: true
```

### 31.4 Post-Incident Report INC-4229 at Mirefield Depot

**Severity:** SEV-4. **Date:** 2026-10-21. **Reported by:** Ulrich Rasmussen (Flight Dynamics).

This review covers an event at Mirefield Depot that was traced to a network switch failure at Mirefield Depot that isolated the telemetry archive. No one was injured, and the affected flight departed 5 minutes late.

| Time | Event |
|---|---|
| 16:15 | Normal operations resumed |
| 16:41 | Work stopped on the affected bay |
| 17:13 | Duty manager declared an incident |
| 17:39 | Affected items moved to quarantine |
| 18:02 | Workaround applied and verified |

**Root cause.** Telemetry is sampled at 100 Hz and down-linked in compressed frames every 2 seconds. Every 14 days, the Propulsion Engineering team rehearses a loss-of-communications scenario with the duty controllers.

**Remediation**

- Revised the supplier quality agreement to include lot traceability.
- Updated the inspection checklist and retrained the Customer Assurance team at Mirefield Depot.

### 31.5 Frequently Asked Questions about Environmental Practices

**Q: Is overtime paid during launch campaigns?**

Yes. Campaign overtime is paid at the enhanced rate, provided it was agreed with your manager beforehand.

**Q: What counts as a near miss?**

Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents.

**Q: Who approves a change to the Lodestar configuration?**

Changes are approved by the Fleet Operations lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within 14 days.

## Chapter 32: Training and Certification, Part II

Training and Certification touches almost every team. This section summarises the standards we hold ourselves to and why.

### 32.1 Definitions in Use

This section explains how Northwind Orbital Logistics approaches training and certification at every site, from Lagrange Relay L4 to the smallest annex.

Cargo for Umbra Imaging is scanned twice: once on arrival and once immediately before integration. Where a task involves a cryo coupling, the two-person rule applies from preparation through to sign-off. Customer representatives may observe loading from the gallery but may not enter the clean area. Visitors must be escorted at all times and must not handle a thermal blanket under any circumstances. Records demonstrating compliance are kept in Keelson for at least 10 years. Every 30 days, the Fleet Operations team rehearses a loss-of-communications scenario with the duty controllers. The Customer Assurance desk is staffed from 07:00 to 19:45 on weekdays, with an on-call engineer outside those hours.

1. Badges must be worn visibly inside controlled areas and returned when employment ends.
2. Failure to complete required training within the deadline results in temporary removal from the duty roster.
3. Laptops are encrypted at rest and enrolled in device management before first use.
4. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.
5. The policy owner reviews the wording every 18 months and publishes changes in the revision history.
6. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
7. The Corvid recovery tender turnaround target at Coldharbour Yard is 36 hours, measured from landing to ready-for-launch.

### 32.2 Working Group Minutes: Ground Systems (2026-10-04)

**Attendees:** Nikhil Iwasaki, Celeste Kuroda, Rosalind Thorvaldsen, Carys Rasmussen. **Chair:** Nikhil Iwasaki. **Location:** Coldharbour Yard, room C40.

**Agenda**

1. Feedback from Westerly Weather Service
2. Supplier issues with attitude thruster deliveries
3. Feedback from Veldt Communications
4. Training plan for August
5. Staffing for the Selene Gate campaign

Attendees asked for clearer escalation paths when a customer changes requirements late. A proposal to standardise the radiator panel inspection checklist across sites was well received. The group agreed that the audit finding closure rate had improved, although the sample was still small. Carys Rasmussen from Cargo Integrity presented the results of the Brightwater Annex pilot and recommended a phased rollout. The team reviewed open risks and closed 18 items that were no longer relevant. The discussion moved to budget, where Carys Rasmussen confirmed a remaining allocation of €92,000.

Lorcan Quarles raised a concern about the workload on the Cargo Integrity team during the peak season. A proposal to standardise the pressure regulator inspection checklist across sites was well received. The discussion moved to budget, where Leopold Yilmaz confirmed a remaining allocation of €16,500. The group agreed that the fuel efficiency index had improved, although the sample was still small. Bram Eskildsen from Quality Assurance presented the results of the Lagrange Relay L4 pilot and recommended a phased rollout.

**Decisions**

- Ask Orbital Traffic Control to own the escalation path for late customer changes.
- Approve an additional €55,750 for spare radiator panel stock.
- Proceed with the Gantry upgrade at Mirefield Depot in October.
- Extend the night-shift trial by 2 weeks.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Check budget headroom with Finance | Nikhil Iwasaki | 2026-06-17 |
| 2 | Collect cargo damage rate data for next meeting | Celeste Kuroda | 2026-12-06 |
| 3 | Collect cargo damage rate data for next meeting | Carys Rasmussen | 2026-12-22 |

### 32.3 Review Board Notes: Cargo Integrity (2022-08-06)

**Attendees:** Joaquin Marchetti, Bastian Bellweather, Zofia Novak, Vesna Jessop. **Chair:** Joaquin Marchetti. **Location:** Ostrava Hub, room D1.

**Agenda**

1. Training plan for July
2. Status of the Drydock upgrade
3. Review of the ticket backlog for the last month
4. Review of the fuel efficiency index for the last month

Attendees asked for clearer escalation paths when a customer changes requirements late. The discussion moved to budget, where Bastian Bellweather confirmed a remaining allocation of €92,000. The group agreed that the first-pass inspection yield had improved, although the sample was still small. Several attendees noted that the current process in Pilot House requires too many manual steps. Bastian Bellweather will draft a short note for Umbra Imaging explaining the revised delivery window. There was a brief debate about whether the Shrike maintenance window should move to weekends.

No objections were raised to extending the trial at Coldharbour Yard for another 8 weeks. The group agreed that the ticket backlog had improved, although the sample was still small. Gideon Okonkwo from Propulsion Engineering presented the results of the Coldharbour Yard pilot and recommended a phased rollout. Attendees asked for clearer escalation paths when a customer changes requirements late.

**Decisions**

- Adopt the shared inspection template at all sites.
- Extend the night-shift trial by 12 weeks.
- Approve an additional €41,500 for spare load cell stock.
- Proceed with the Halyard upgrade at Mirefield Depot in November.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Draft customer note for Solvay-Ortiz Pharma | Zofia Novak | 2025-12-11 |
| 2 | Collect ticket backlog data for next meeting | Bastian Bellweather | 2026-04-06 |
| 3 | Update training matrix for Procurement | Joaquin Marchetti | 2025-12-04 |
| 4 | Draft customer note for Ravensmoor University | Zofia Novak | 2025-12-07 |
| 5 | Circulate revised Keelson rollout plan | Bastian Bellweather | 2026-10-11 |

### 32.4 Release Notes: Lodestar

Lodestar is maintained by the Orbital Traffic Control team. Releases are deployed to Mirefield Depot first and to the remaining sites after a soak period of 7 days.

#### Lodestar 2.8.2 (2022-11-19)

**Changed**
- Log formatting to include the operator badge number.
- The default retention period to 24 months.

**Added**
- Automatic reminders for expiring certifications.
- Export of ticket backlog reports to CSV.
- A dry-run mode for configuration changes.

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.
- An unused MANIFEST integration.

#### Lodestar 2.7.0 (2021-12-08)

**Changed**
- The manifest schema to version 3.1.

**Removed**
- An unused Ledgerline integration.
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

#### Lodestar 2.7.3 (2021-06-05)

**Fixed**
- A crash when a cryo coupling record had no serial number.
- Duplicated alerts after a failover at Lagrange Relay L4.
- Broken links in exported PDF reports.

**Changed**
- The approval flow so that Ground Systems signs off before Finance.
- The manifest schema to version 5.4.

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

#### Lodestar 2.7.2 (2021-09-20)

**Removed**
- An unused Drydock integration.
- The legacy FTP upload path.

**Changed**
- The default retention period to 18 months.

**Added**
- An audit trail for manual overrides.
- A read-only view for customer representatives.
- Support for the Gannet cargo profile.

#### Lodestar 2.6.5 (2021-10-28)

**Removed**
- The deprecated v1 manifest endpoint.

**Fixed**
- Incorrect time zones in shift reports.
- A crash when a telemetry unit record had no serial number.

## Chapter 33: Safety and Conduct, Part II

This section explains how Northwind Orbital Logistics approaches safety and conduct at every site, from Mirefield Depot to the smallest annex.

### 33.1 Escalation Rules

This part of the handbook was last reviewed by Amara Pemberton and reflects the practice agreed in 2022.

A breach of this rule is handled under the progressive discipline process described in the People chapter. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Every 60 days, the Orbital Traffic Control team rehearses a loss-of-communications scenario with the duty controllers. Records demonstrating compliance are kept in Pilot House for at least 5 years.

1. Questions about interpretation should be raised with Amara Gallagher in Procurement rather than resolved informally.
2. Production credentials must never be pasted into chat tools, tickets or shared documents.
3. Penetration tests of public-facing services are commissioned at least once per year.
4. Removable media is blocked on all operations workstations at Mirefield Depot.

> **Note:** Any spending above €85,250 linked to this policy needs approval from Finance before the order is raised.

### 33.2 Equipment Data Sheet: Petrel pressure regulator

Thermal margins were re-analysed after the 2021 anomaly, and the upper limit was lowered by 16 °C. The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots. Nominal operating temperature for the pressure regulator ranges from -25 °C to 56 °C. The Petrel transfer stage can hold station for up to 72 hours before its propellant margin falls below reserve.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Data rate | 1321 kbit/s | n/a | Compressed telemetry |
| Supplier | Marchetti Components Ltd | n/a | Approved vendor list |
| Dry mass | 358 kg | ±38 kg | Includes brackets |
| Part number | PET-PRE-8573 | n/a | Revision A |
| Design life | 1,820 cycles | n/a | Hard limit, no extension |
| Mounting | 12 × M5 bolts | Torque 28 N·m | Thread-locker required |
| Operating temperature | -10 to 47 °C | ±3 °C | Qualification limits are wider |
| Peak power | 1654 W | ±4 % | During deployment |

Telemetry is sampled at 5 Hz and down-linked in compressed frames every 2 seconds. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. Engineers should consult the Cartographer configuration record before changing any calibration constant. The latest revision reduced mass by 14.7 kg by replacing the aluminium bracket with a composite part. Data from each pass is reconciled in Bulkhead and flagged if more than 17 percent of frames are missing.

**Operating limits**

- The Petrel transfer stage supports both automated and manual docking, although manual mode is reserved for certified pilots.
- The design team at Mirefield Depot owns the interface control document and approves every change to it.
- Telemetry is sampled at 5 Hz and down-linked in compressed frames every 120 seconds.

### 33.3 Operating Limits: Kestrel-9 thermal blanket

Power draw peaks at 595 W during the deployment sequence and settles at roughly a third of that. The Kestrel-9 orbital tug can hold station for up to 16 hours before its propellant margin falls below reserve. Ground tests at Mirefield Depot showed a mean drift of 0.95 percent over 12 hours of continuous soak. Telemetry is sampled at 20 Hz and down-linked in compressed frames every 45 seconds.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Part number | KES-THE-3126 | n/a | Revision A |
| Dry mass | 8,498 kg | ±15 kg | Measured at acceptance |
| Design life | 6,010 cycles | n/a | Hard limit, no extension |
| Data rate | 1743 kbit/s | n/a | Compressed telemetry |
| Mounting | 4 × M6 bolts | Torque 8 N·m | Thread-locker required |
| Operating temperature | -17 to 71 °C | ±4 °C | Qualification limits are wider |
| Supplier | Jankowski Components Ltd | n/a | Approved vendor list |

The design team at Brightwater Annex owns the interface control document and approves every change to it. During integration, torque values for every fastener are recorded and attached to the build record. The Kestrel-9 orbital tug can hold station for up to 72 hours before its propellant margin falls below reserve. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

**Operating limits**

- Thermal margins were re-analysed after the 2023 anomaly, and the upper limit was lowered by 17 °C.
- During integration, torque values for every fastener are recorded and attached to the build record.
- Thermal margins were re-analysed after the 2020 anomaly, and the upper limit was lowered by 7 °C.
- Engineers should consult the Cartographer configuration record before changing any calibration constant.

### 33.4 Minimum Standards

This part of the handbook was last reviewed by Vesna Zelenko and reflects the practice agreed in 2023.

Spare parts for the Heron fleet are pooled at Mirefield Depot and shipped to other sites within 72 hours. Temporary deviations of up to 5 days may be granted by the site director at Ostrava Hub. Nothing in this section prevents an employee from stopping work they believe to be unsafe. Questions about interpretation should be raised with Jonas Fairbanks in Orbital Traffic Control rather than resolved informally.

1. Network segments for flight systems are physically separated from the corporate network.
2. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
3. Access to Signal Lamp requires hardware-key authentication and is reviewed every 21 days.
4. Badges must be worn visibly inside controlled areas and returned when employment ends.
5. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.
6. All Flight Dynamics staff at Kessler Ridge must complete the refresher module within 5 days of any change to this policy.
7. Accounts that have not been used for 5 days are disabled automatically.

Delays longer than 5 minutes are reported to the customer by Customer Assurance, not by the floor team. All Propulsion Engineering staff at Brightwater Annex must complete the refresher module within 21 days of any change to this policy. Records demonstrating compliance are kept in Ledgerline for at least 10 years.

> **Note:** Employees should keep personal notes out of Tidewater; only operational records belong there.

### 33.5 Quarterly Metrics, 2025

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: first-pass inspection yield (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Ostrava Hub | 58.6 | 65.7 | 58.9 | 59.7 | 63.8 |
| Lagrange Relay L4 | 85.7 | 89.3 | 87.0 | 89.1 | 90.5 |
| Brightwater Annex | 91.1 | 88.2 | 93.8 | 92.2 | 92.0 |
| Selene Gate | 89.9 | 90.1 | 92.3 | 92.5 | 94.6 |

Operators log every manual override in Keelson together with the reason and the approving supervisor. No objections were raised to extending the trial at Lagrange Relay L4 for another 6 weeks. Nikhil Iwasaki will draft a short note for Veldt Communications explaining the revised delivery window. The team reviewed open risks and closed 13 items that were no longer relevant.

## Chapter 34: Fleet Operations, Part II

The guidance below grew out of lessons learned at Hollis Point and has since been adopted company-wide.

### 34.1 Anomaly Summary INC-5338 at Mirefield Depot

**Severity:** SEV-3. **Date:** 2023-11-23. **Reported by:** Soren Ferreira (Fleet Operations).

This review covers an event at Mirefield Depot that was traced to a scheduling conflict between two Cargo Integrity shifts that left the cargo ramp without a spotter. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 17:33 | On-call engineer acknowledged the page |
| 17:48 | Duty manager declared an incident |
| 18:12 | Affected items moved to quarantine |
| 18:47 | Incident closed pending review |
| 19:10 | First alert received by the operations bridge |
| 19:47 | Customer informed by Customer Assurance |
| 20:19 | Workaround applied and verified |

**Root cause.** Loading sequences are planned so that the heaviest items sit closest to the Osprey centre of mass. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision. Delays longer than 30 minutes are reported to the customer by Customer Assurance, not by the floor team.

**Remediation**

- Updated the inspection checklist and retrained the People Operations team at Mirefield Depot.
- Introduced a second sign-off for the affected step.
- Added monitoring with an alert routed to the Cargo Integrity on-call engineer.
- Added an automated check in Cartographer that rejects the condition at entry.

### 34.2 Working Group Minutes: Quality Assurance (2026-04-05)

**Attendees:** Hamid Gallagher, Zofia Kuroda, Ines Ibarra, Greta Rasmussen, Ines Brightman, Mirela Kowalczyk. **Chair:** Hamid Gallagher. **Location:** Selene Gate, room A12.

**Agenda**

1. Review of the cargo damage rate for the last month
2. Staffing for the Mirefield Depot campaign
3. Review of the first-pass inspection yield for the last month

There was a brief debate about whether the Kestrel-9 maintenance window should move to weekends. Attendees asked for clearer escalation paths when a customer changes requirements late. No objections were raised to extending the trial at Hollis Point for another 3 weeks. Ines Brightman reminded everyone that the May audit will focus on training records.

No objections were raised to extending the trial at Ostrava Hub for another 2 weeks. A proposal to standardise the attitude thruster inspection checklist across sites was well received. Hamid Lindqvist will draft a short note for Alder Biotech explaining the revised delivery window. The discussion moved to budget, where Gideon Quarles confirmed a remaining allocation of €45,750. Attendees asked for clearer escalation paths when a customer changes requirements late.

**Decisions**

- Extend the night-shift trial by 4 weeks.
- Proceed with the Signal Lamp upgrade at Selene Gate in March.
- Close the open risk on Kestrel-9 maintenance windows.
- Ask Mission Planning to own the escalation path for late customer changes.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Book readiness review room at Hollis Point | Zofia Kuroda | 2026-05-14 |
| 2 | Book readiness review room at Port Anselm | Ines Brightman | 2026-11-21 |
| 3 | Book readiness review room at Selene Gate | Greta Rasmussen | 2025-02-27 |
| 4 | Book readiness review room at Lagrange Relay L4 | Hamid Gallagher | 2026-05-01 |
| 5 | Circulate revised Drydock rollout plan | Greta Rasmussen | 2026-04-20 |

### 34.3 Roles and Responsibilities

The guidance below grew out of lessons learned at Port Anselm and has since been adopted company-wide.

Cargo for Quillon Satellites is scanned twice: once on arrival and once immediately before integration. If a pallet arrives without a valid manifest entry in Tidewater, it is held in the quarantine cage. The Coldharbour Yard yard has 18 bays, each rated for a different maximum load and hazard class. Questions about interpretation should be raised with Oona Zelenko in People Operations rather than resolved informally. Where a task involves a battery module, the two-person rule applies from preparation through to sign-off. Every 5 days, the Flight Dynamics team rehearses a loss-of-communications scenario with the duty controllers. Failure to complete required training within the deadline results in temporary removal from the duty roster.

1. Accounts that have not been used for 10 days are disabled automatically.
2. Fuel loading is the last activity before closeout, and no other work may proceed in parallel.
3. Where this policy conflicts with a customer contract, the stricter requirement applies.
4. Supervisors are responsible for confirming that new starters have read this section before their first shift.
5. Log data from Wayfarer is retained for 9 months and then archived to cold storage.
6. Access to MANIFEST requires hardware-key authentication and is reviewed every 14 days.
7. The Coldharbour Yard yard has 7 bays, each rated for a different maximum load and hazard class.

### 34.4 Changelog: Halyard

Halyard is maintained by the Propulsion Engineering team. Releases are deployed to Mirefield Depot first and to the remaining sites after a soak period of 60 days.

#### Halyard 2.4.0 (2023-01-02)

**Changed**
- Sorting on the work-order list.
- Timeouts for the Brightwater Annex gateway from 120 to 120 seconds.
- The default retention period to 12 months.

**Added**
- Per-site dashboards for Flight Dynamics.

#### Halyard 2.3.0 (2023-11-20)

**Changed**
- The manifest schema to version 3.2.

**Fixed**
- Rounding of mass totals in manifests.

**Added**
- Per-site dashboards for Ground Systems.
- Bulk import of telemetry unit serial numbers.
- An audit trail for manual overrides.

#### Halyard 2.3.1 (2022-01-15)

**Added**
- Export of first-pass inspection yield reports to CSV.
- Automatic reminders for expiring certifications.

**Changed**
- The approval flow so that Mission Planning signs off before Finance.
- Log formatting to include the operator badge number.
- The default retention period to 6 months.

**Removed**
- The deprecated v1 manifest endpoint.
- The legacy FTP upload path.

## Chapter 35: Ground Facilities, Part II

This section explains how Northwind Orbital Logistics approaches ground facilities at every site, from Coldharbour Yard to the smallest annex.

### 35.1 Frequently Asked Questions about Ground Facilities

**Q: What happens if a data recorder fails inspection?**

It is tagged, moved to quarantine and logged in Drydock. Quality Assurance decides whether it is repaired, scrapped or returned.

**Q: Who do I call if the Pilot House service is down?**

Contact the Flight Dynamics on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

**Q: How do I request access to flight data?**

Raise an access request in Beacon. Requests are approved by the data owner in Orbital Traffic Control and usually processed within 10 working days.

**Q: Can I bring a guest onto the Hollis Point operations floor?**

Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area.

**Q: Where are spare reaction wheel parts stored?**

The central pool is at Selene Gate. Each site also keeps a small buffer stock sized from the last 18 months of usage.

### 35.2 Interface Summary: Osprey radiator panel

Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 2,320 cycles. Thermal margins were re-analysed after the 2020 anomaly, and the upper limit was lowered by 11 °C. Data from each pass is reconciled in Halyard and flagged if more than 6 percent of frames are missing. Nominal operating temperature for the radiator panel ranges from -59 °C to 55 °C.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Peak power | 1992 W | ±8 % | During deployment |
| Mounting | 6 × M5 bolts | Torque 29 N·m | Thread-locker required |
| Supplier | Castellanos Components Ltd | n/a | Approved vendor list |
| Data rate | 1516 kbit/s | n/a | Compressed telemetry |
| Dry mass | 1,223 kg | ±1 kg | Measured at acceptance |

Ground tests at Brightwater Annex showed a mean drift of 0.44 percent over 36 hours of continuous soak. Telemetry is sampled at 10 Hz and down-linked in compressed frames every 5 seconds. Engineers should consult the Drydock configuration record before changing any calibration constant. Each radiator panel carries a serial plate that encodes the batch, the factory and the inspection date. The Osprey cargo lander can hold station for up to 48 hours before its propellant margin falls below reserve.

**Operating limits**

- Data from each pass is reconciled in Signal Lamp and flagged if more than 17 percent of frames are missing.
- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.
- The Osprey cargo lander supports both automated and manual docking, although manual mode is reserved for certified pilots.
- Engineers should consult the Ledgerline configuration record before changing any calibration constant.
- A radiator panel that fails its acceptance test twice is quarantined and returned to the supplier.

### 35.3 Quarterly Metrics, 2024

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: fuel efficiency index (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Coldharbour Yard | 88.1 | 83.3 | 84.9 | 85.0 | 88.3 |
| Ostrava Hub | 66.9 | 69.2 | 69.2 | 64.7 | 69.1 |
| Lagrange Relay L4 | 69.2 | 66.9 | 72.7 | 72.5 | 72.2 |
| Brightwater Annex | 76.2 | 76.8 | 79.0 | 75.6 | 78.4 |
| Hollis Point | 57.8 | 63.2 | 63.4 | 60.9 | 62.1 |

Fuel loading is the last activity before closeout, and no other work may proceed in parallel. Night operations require additional lighting checks and a second spotter at the cargo ramp. Spare parts for the Wren fleet are pooled at Kessler Ridge and shipped to other sites within 72 hours. The Finance desk is staffed from 06:15 to 21:30 on weekdays, with an on-call engineer outside those hours.

### 35.4 Record Keeping

Ground Facilities touches almost every team. This section summarises the standards we hold ourselves to and why.

Audit samples are drawn quarterly, and at least 9 findings per site are followed up in person. The Fleet Operations desk is staffed from 08:45 to 22:00 on weekdays, with an on-call engineer outside those hours. Loading sequences are planned so that the heaviest items sit closest to the Wren centre of mass. The requirement applies equally to remote staff who access MANIFEST from outside a company site. Operators log every manual override in Sextant together with the reason and the approving supervisor.

1. Audit samples are drawn quarterly, and at least 3 findings per site are followed up in person.
2. Failure to complete required training within the deadline results in temporary removal from the duty roster.
3. The Heron-class freighter turnaround target at Mirefield Depot is 36 hours, measured from landing to ready-for-launch.
4. Supervisors are responsible for confirming that new starters have read this section before their first shift.
5. Nothing in this section prevents an employee from stopping work they believe to be unsafe.
6. Penetration tests of public-facing services are commissioned at least once per year.
7. Temporary deviations of up to 7 days may be granted by the site director at Kessler Ridge.

The Mission Planning desk is staffed from 07:15 to 21:30 on weekdays, with an on-call engineer outside those hours. Where this policy conflicts with a customer contract, the stricter requirement applies. Contractors working on site are bound by the same obligations as employees for the duration of their engagement.

### 35.5 Incident Review INC-6195 at Kessler Ridge

**Severity:** SEV-2. **Date:** 2022-04-17. **Reported by:** Pavel Kowalczyk (Fleet Operations).

This review covers an event at Kessler Ridge that was traced to a network switch failure at Kessler Ridge that isolated the telemetry archive. No one was injured, and the issue was contained within a single shift.

| Time | Event |
|---|---|
| 13:29 | Affected items moved to quarantine |
| 13:33 | Incident closed pending review |
| 13:46 | On-call engineer acknowledged the page |
| 13:54 | First alert received by the operations bridge |
| 14:34 | Duty manager declared an incident |

**Root cause.** The Gannet refueling drone can hold station for up to 6 hours before its propellant margin falls below reserve. Fuel loading is the last activity before closeout, and no other work may proceed in parallel. Every 5 days, the Cryogenics team rehearses a loss-of-communications scenario with the duty controllers.

**Remediation**

- Scheduled a follow-up audit at Kessler Ridge in 18 months.
- Introduced a second sign-off for the affected step.

### 35.6 Manifest Format (Lodestar)

Cargo Integrity uses this helper to check that a manifest does not exceed the cradle limit before it is submitted to Lodestar.

```python
CRADLE_LIMIT_KG = 4792


def check_manifest(items):
    """Return (ok, total_kg, problems) for a list of manifest items."""
    total = 0.0
    problems = []
    for item in items:
        mass = float(item.get("mass_kg", 0))
        if mass <= 0:
            problems.append("%s: missing or invalid mass" % item.get("id", "?"))
        if item.get("hazard_class", 0) > 4:
            problems.append("%s: hazard class needs review" % item["id"])
        total += mass
    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems
```

The function is deliberately conservative: an item with no mass is treated as an error rather than as zero, because unknown mass has caused rework in the past.

## Chapter 36: Information Security, Part II

The guidance below grew out of lessons learned at Ostrava Hub and has since been adopted company-wide.

### 36.1 Common Questions about Information Security

**Q: How do I request access to flight data?**

Raise an access request in Halyard. Requests are approved by the data owner in Procurement and usually processed within 7 working days.

**Q: Where are spare radiator panel parts stored?**

The central pool is at Ostrava Hub. Each site also keeps a small buffer stock sized from the last 12 months of usage.

**Q: Who do I call if the Wayfarer service is down?**

Contact the Cryogenics on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

**Q: What counts as a near miss?**

Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents.

### 36.2 Meeting Notes: Flight Dynamics (2024-01-16)

**Attendees:** Ulrich Brightman, Greta Bellweather, Hamid Ibarra, Kalinda Varga, Ines Yilmaz, Oona Lindqvist. **Chair:** Ulrich Brightman. **Location:** Selene Gate, room E35.

**Agenda**

1. Feedback from Veldt Communications
2. Supplier issues with data recorder deliveries
3. Feedback from Solvay-Ortiz Pharma
4. Any other business
5. Status of the Bulkhead upgrade

Kalinda Varga reminded everyone that the January audit will focus on training records. A proposal to standardise the cargo cradle inspection checklist across sites was well received. The team reviewed open risks and closed 3 items that were no longer relevant. The group agreed that the ticket backlog had improved, although the sample was still small. Kalinda Varga reported that the backlog in Wayfarer had fallen to 105 tickets. Attendees asked for clearer escalation paths when a customer changes requirements late.

A proposal to standardise the hatch seal inspection checklist across sites was well received. Bram Jessop reminded everyone that the August audit will focus on training records. The team reviewed open risks and closed 13 items that were no longer relevant. There was a brief debate about whether the Osprey maintenance window should move to weekends. No objections were raised to extending the trial at Tarvos Station for another 2 weeks.

**Decisions**

- Defer the cryo coupling checklist change until the supplier responds.
- Ask People Operations to own the escalation path for late customer changes.
- Proceed with the Beacon upgrade at Selene Gate in January.
- Adopt the shared inspection template at all sites.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update training matrix for Ground Systems | Oona Lindqvist | 2026-09-22 |
| 2 | Book readiness review room at Port Anselm | Ines Yilmaz | 2025-03-26 |
| 3 | Collect cargo damage rate data for next meeting | Kalinda Varga | 2025-11-21 |

### 36.3 Post-Incident Report INC-1984 at Ostrava Hub

**Severity:** SEV-2. **Date:** 2026-10-17. **Reported by:** Tamsin Brightman (Facilities).

This review covers an event at Ostrava Hub that was traced to a network switch failure at Ostrava Hub that isolated the telemetry archive. No one was injured, and the affected flight departed 15 minutes late.

| Time | Event |
|---|---|
| 15:15 | Customer informed by Customer Assurance |
| 15:30 | Affected items moved to quarantine |
| 15:56 | Workaround applied and verified |
| 16:00 | Normal operations resumed |
| 16:21 | Duty manager declared an incident |

**Root cause.** Night operations require additional lighting checks and a second spotter at the cargo ramp. The Osprey cargo lander uses a dual-redundant telemetry unit that switches over automatically within 88 ms of a fault. The Ostrava Hub yard has 6 bays, each rated for a different maximum load and hazard class. Operators log every manual override in MANIFEST together with the reason and the approving supervisor.

**Remediation**

- Introduced a second sign-off for the affected step.
- Replaced the affected reaction wheel stock and quarantined the remaining batch.

### 36.4 Release Notes: Bulkhead

Bulkhead is maintained by the Flight Dynamics team. Releases are deployed to Kessler Ridge first and to the remaining sites after a soak period of 90 days.

#### Bulkhead 3.1.1 (2022-12-21)

**Changed**
- The default retention period to 24 months.

**Fixed**
- Duplicated alerts after a failover at Selene Gate.

**Added**
- A read-only view for customer representatives.
- Support for the Corvid cargo profile.

#### Bulkhead 3.1.0 (2021-04-19)

**Added**
- Per-site dashboards for Facilities.
- Support for the Wren cargo profile.

**Fixed**
- Duplicated alerts after a failover at Port Anselm.

**Removed**
- The deprecated v1 manifest endpoint.
- An unused Lodestar integration.

#### Bulkhead 3.1.1 (2021-02-08)

**Changed**
- The default retention period to 9 months.
- The approval flow so that People Operations signs off before Finance.
- Log formatting to include the operator badge number.

**Fixed**
- Incorrect time zones in shift reports.

#### Bulkhead 3.1.0 (2021-12-27)

**Added**
- An audit trail for manual overrides.

**Fixed**
- A memory leak in the telemetry ingest worker.
- Rounding of mass totals in manifests.
- Broken links in exported PDF reports.

## Chapter 37: Cargo Handling, Part II

This section explains how Northwind Orbital Logistics approaches cargo handling at every site, from Selene Gate to the smallest annex.

### 37.1 Common Questions about Cargo Handling

**Q: What counts as a near miss?**

Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents.

**Q: Can I bring a guest onto the Kessler Ridge operations floor?**

Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area.

**Q: Who do I call if the Lodestar service is down?**

Contact the Cryogenics on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so.

**Q: Is overtime paid during launch campaigns?**

Yes. Campaign overtime is paid at the enhanced rate, provided it was agreed with your manager beforehand.

**Q: What happens if a docking clamp fails inspection?**

It is tagged, moved to quarantine and logged in Lodestar. Quality Assurance decides whether it is repaired, scrapped or returned.

### 37.2 Incident Review INC-147 at Hollis Point

**Severity:** SEV-2. **Date:** 2022-02-14. **Reported by:** Leopold Eskildsen (Propulsion Engineering).

This review covers an event at Hollis Point that was traced to a mislabelled pressure regulator that passed visual inspection because the label template had been reused. No one was injured, and the affected flight departed 45 minutes late.

| Time | Event |
|---|---|
| 02:59 | Customer informed by Customer Assurance |
| 03:37 | On-call engineer acknowledged the page |
| 03:45 | Affected items moved to quarantine |
| 04:23 | Workaround applied and verified |
| 04:42 | Duty manager declared an incident |
| 04:52 | Work stopped on the affected bay |
| 05:00 | First alert received by the operations bridge |

**Root cause.** Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 4,160 cycles. The Shrike inspection pod supports both automated and manual docking, although manual mode is reserved for certified pilots.

**Remediation**

- Added an automated check in Ledgerline that rejects the condition at entry.
- Introduced a second sign-off for the affected step.

### 37.3 Incident Review INC-9451 at Kessler Ridge

**Severity:** SEV-2. **Date:** 2024-12-09. **Reported by:** Hollis Yilmaz (Quality Assurance).

This review covers an event at Kessler Ridge that was traced to a manual data entry error in Tidewater that duplicated a customer consignment. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 18:24 | First alert received by the operations bridge |
| 18:46 | Incident closed pending review |
| 19:09 | Workaround applied and verified |
| 19:25 | Work stopped on the affected bay |

**Root cause.** Each battery module carries a serial plate that encodes the batch, the factory and the inspection date. Thermal margins were re-analysed after the 2025 anomaly, and the upper limit was lowered by 7 °C. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.

**Remediation**

- Added an automated check in Pilot House that rejects the condition at entry.
- Revised the supplier quality agreement to include lot traceability.
- Replaced the affected battery module stock and quarantined the remaining batch.
- Updated the inspection checklist and retrained the Flight Dynamics team at Kessler Ridge.

### 37.4 Scope and Applicability

This part of the handbook was last reviewed by Wendell Coutinho and reflects the practice agreed in 2022.

All Facilities staff at Tarvos Station must complete the refresher module within 21 days of any change to this policy. The Ground Systems desk is staffed from 11:00 to 23:15 on weekdays, with an on-call engineer outside those hours. The Kessler Ridge yard has 15 bays, each rated for a different maximum load and hazard class. A breach of this rule is handled under the progressive discipline process described in the People chapter. Loading sequences are planned so that the heaviest items sit closest to the Corvid centre of mass. Supervisors are responsible for confirming that new starters have read this section before their first shift. Every 30 days, the Procurement team rehearses a loss-of-communications scenario with the duty controllers.

1. Visitors must be escorted at all times and must not handle a pressure regulator under any circumstances.
2. Delays longer than 10 minutes are reported to the customer by Customer Assurance, not by the floor team.
3. The Flight Dynamics team runs a phishing simulation every 24 months and publishes anonymised results.
4. Badges must be worn visibly inside controlled areas and returned when employment ends.
5. Shift handover at Kessler Ridge takes place at 08:45 and must include a walk-through of open work orders.
6. Any spending above €97,500 linked to this policy needs approval from Finance before the order is raised.
7. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.

### 37.5 Incident Review INC-6192 at Tarvos Station

**Severity:** SEV-4. **Date:** 2025-05-06. **Reported by:** Esme Ibarra (Orbital Traffic Control).

This review covers an event at Tarvos Station that was traced to a network switch failure at Tarvos Station that isolated the telemetry archive. No one was injured, and one consignment had to be re-inspected.

| Time | Event |
|---|---|
| 05:38 | Incident closed pending review |
| 06:04 | Affected items moved to quarantine |
| 06:31 | First alert received by the operations bridge |
| 06:38 | Customer informed by Customer Assurance |
| 07:06 | On-call engineer acknowledged the page |

**Root cause.** Nominal operating temperature for the hatch seal ranges from -51 °C to 72 °C. The Shrike inspection pod uses a dual-redundant star tracker that switches over automatically within 351 ms of a fault. The Customer Assurance desk is staffed from 05:15 to 17:15 on weekdays, with an on-call engineer outside those hours.

**Remediation**

- Replaced the affected data recorder stock and quarantined the remaining batch.
- Updated the inspection checklist and retrained the Facilities team at Tarvos Station.
- Revised the supplier quality agreement to include lot traceability.
- Scheduled a follow-up audit at Tarvos Station in 24 months.

## Chapter 38: Software Systems, Part II

The following rules describe expected practice for software systems. They apply to employees and contractors alike.

### 38.1 Definitions in Use

Software Systems touches almost every team. This section summarises the standards we hold ourselves to and why.

Delays longer than 60 minutes are reported to the customer by Customer Assurance, not by the floor team. Every 5 days, the Cargo Integrity team rehearses a loss-of-communications scenario with the duty controllers. Any spending above €30,500 linked to this policy needs approval from Finance before the order is raised. The Coldharbour Yard yard has 6 bays, each rated for a different maximum load and hazard class. Cargo for Solvay-Ortiz Pharma is scanned twice: once on arrival and once immediately before integration.

1. Where this policy conflicts with a customer contract, the stricter requirement applies.
2. Any spending above €28,250 linked to this policy needs approval from Finance before the order is raised.
3. Removable media is blocked on all operations workstations at Coldharbour Yard.
4. Access to Beacon requires hardware-key authentication and is reviewed every 90 days.
5. Signage summarising this rule is displayed at every entrance to the Coldharbour Yard operations floor.
6. This rule was tightened in 2025 after an internal review found inconsistent practice across sites.
7. Records demonstrating compliance are kept in Beacon for at least 10 years.

Where a task involves a star tracker, the two-person rule applies from preparation through to sign-off. Loading sequences are planned so that the heaviest items sit closest to the Shrike centre of mass. Records demonstrating compliance are kept in Sextant for at least 10 years. A breach of this rule is handled under the progressive discipline process described in the People chapter.

> **Note:** The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.

### 38.2 Equipment Data Sheet: Osprey telemetry unit

The latest revision reduced mass by 17.7 kg by replacing the aluminium bracket with a composite part. Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. Firmware for the telemetry unit is distributed through Tidewater and must be verified before installation.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Part number | OSP-TEL-3520 | n/a | Revision F |
| Dry mass | 4,692 kg | ±2 kg | Includes brackets |
| Operating temperature | -20 to 76 °C | ±2 °C | Qualification limits are wider |
| Data rate | 193 kbit/s | n/a | Compressed telemetry |
| Peak power | 1932 W | ±9 % | During deployment |
| Mounting | 8 × M8 bolts | Torque 37 N·m | Thread-locker required |
| Supplier | Nakashima Aerospace Ltd | n/a | Approved vendor list |
| Design life | 3,980 cycles | n/a | Hard limit, no extension |

The Osprey cargo lander can hold station for up to 72 hours before its propellant margin falls below reserve. During integration, torque values for every fastener are recorded and attached to the build record. Power draw peaks at 401 W during the deployment sequence and settles at roughly a third of that. The Osprey cargo lander uses a dual-redundant telemetry unit that switches over automatically within 362 ms of a fault. Telemetry is sampled at 20 Hz and down-linked in compressed frames every 90 seconds.

**Operating limits**

- A telemetry unit that fails its acceptance test twice is quarantined and returned to the supplier.
- Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.
- Each telemetry unit carries a serial plate that encodes the batch, the factory and the inspection date.
- Each telemetry unit carries a serial plate that encodes the batch, the factory and the inspection date.
- Telemetry is sampled at 10 Hz and down-linked in compressed frames every 5 seconds.

### 38.3 Reporting Obligations

Software Systems touches almost every team. This section summarises the standards we hold ourselves to and why.

Signage summarising this rule is displayed at every entrance to the Brightwater Annex operations floor. Shift handover at Brightwater Annex takes place at 08:30 and must include a walk-through of open work orders. If a pallet arrives without a valid manifest entry in Cartographer, it is held in the quarantine cage. Any spending above €44,500 linked to this policy needs approval from Finance before the order is raised. Supervisors are responsible for confirming that new starters have read this section before their first shift. All Procurement staff at Coldharbour Yard must complete the refresher module within 7 days of any change to this policy.

1. Security incidents must be reported to the Information Security hotline within 30 minutes of discovery.
2. Audit samples are drawn quarterly, and at least 14 findings per site are followed up in person.
3. Spare parts for the Wren fleet are pooled at Brightwater Annex and shipped to other sites within 12 hours.
4. Delays longer than 10 minutes are reported to the customer by Customer Assurance, not by the floor team.
5. Operators log every manual override in Wayfarer together with the reason and the approving supervisor.

### 38.4 Interface Summary: Osprey star tracker

Ground tests at Selene Gate showed a mean drift of 0.12 percent over 6 hours of continuous soak. The latest revision reduced mass by 5.2 kg by replacing the aluminium bracket with a composite part. Nominal operating temperature for the star tracker ranges from -51 °C to 55 °C. Power draw peaks at 1850 W during the deployment sequence and settles at roughly a third of that.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Dry mass | 4,672 kg | ±1 kg | Excludes harness |
| Part number | OSP-STA-5821 | n/a | Revision B |
| Mounting | 12 × M5 bolts | Torque 60 N·m | Thread-locker required |
| Design life | 7,470 cycles | n/a | Hard limit, no extension |
| Data rate | 2045 kbit/s | n/a | Compressed telemetry |
| Supplier | Gallagher Precision Ltd | n/a | Approved vendor list |
| Operating temperature | -27 to 74 °C | ±1 °C | Qualification limits are wider |
| Peak power | 51 W | ±6 % | During deployment |

During integration, torque values for every fastener are recorded and attached to the build record. Each star tracker carries a serial plate that encodes the batch, the factory and the inspection date. Replacement intervals are measured in cycles rather than calendar time, with a hard limit of 3,420 cycles.

**Operating limits**

- Engineers should consult the Wayfarer configuration record before changing any calibration constant.
- Power draw peaks at 2178 W during the deployment sequence and settles at roughly a third of that.
- Each star tracker carries a serial plate that encodes the batch, the factory and the inspection date.
- The Osprey cargo lander can hold station for up to 6 hours before its propellant margin falls below reserve.

## Chapter 39: People and Travel, Part II

This part of the handbook was last reviewed by Keiko Lindqvist and reflects the practice agreed in 2024.

### 39.1 Technical Specification: Gannet pressure regulator

Data from each pass is reconciled in Beacon and flagged if more than 17 percent of frames are missing. Power draw peaks at 2191 W during the deployment sequence and settles at roughly a third of that. During integration, torque values for every fastener are recorded and attached to the build record. A pressure regulator that fails its acceptance test twice is quarantined and returned to the supplier. Telemetry is sampled at 2 Hz and down-linked in compressed frames every 120 seconds.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Data rate | 732 kbit/s | n/a | Compressed telemetry |
| Dry mass | 2,867 kg | ±20 kg | Measured at acceptance |
| Peak power | 1428 W | ±10 % | During deployment |
| Operating temperature | -10 to 57 °C | ±4 °C | Qualification limits are wider |
| Mounting | 12 × M10 bolts | Torque 38 N·m | Thread-locker required |

Data from each pass is reconciled in Beacon and flagged if more than 10 percent of frames are missing. Ground tests at Hollis Point showed a mean drift of 0.94 percent over 4 hours of continuous soak. Firmware for the pressure regulator is distributed through Lodestar and must be verified before installation. A pressure regulator that fails its acceptance test twice is quarantined and returned to the supplier. The latest revision reduced mass by 2.9 kg by replacing the aluminium bracket with a composite part.

**Operating limits**

- Nominal operating temperature for the pressure regulator ranges from -35 °C to 46 °C.
- Power draw peaks at 1777 W during the deployment sequence and settles at roughly a third of that.
- Telemetry is sampled at 5 Hz and down-linked in compressed frames every 90 seconds.
- The Gannet refueling drone supports both automated and manual docking, although manual mode is reserved for certified pilots.
- Thermal margins were re-analysed after the 2018 anomaly, and the upper limit was lowered by 12 °C.

### 39.2 Exceptions Process

This part of the handbook was last reviewed by Quinn Varga and reflects the practice agreed in 2020.

The internal mobility programme lets staff spend up to 2 weeks shadowing another team. Annual reviews take place in March, with a mid-year check-in six months later. Parental leave policies apply equally regardless of gender and are explained in the benefits portal. Questions about interpretation should be raised with Maren Eskildsen in Propulsion Engineering rather than resolved informally. Exceptions require written approval from the Ground Systems lead and are reviewed again after 12 months. Failure to complete required training within the deadline results in temporary removal from the duty roster.

1. Teams that cannot comply because of tooling limitations must log a risk entry in Tidewater before proceeding.
2. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
3. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.
4. Every 21 days, the Customer Assurance team rehearses a loss-of-communications scenario with the duty controllers.
5. Accounts that have not been used for 60 days are disabled automatically.
6. Supervisors are responsible for confirming that new starters have read this section before their first shift.

A breach of this rule is handled under the progressive discipline process described in the People chapter. Annual reviews take place in September, with a mid-year check-in six months later. Records demonstrating compliance are kept in Beacon for at least 2 years.

### 39.3 Site Metrics, 2024

The table below shows selected indicators reported to the operations board. Targets are set annually and are not adjusted mid-year.

*Metric: audit finding closure rate (percent).*

| Site | Q1 | Q2 | Q3 | Q4 | Target |
|---|---|---|---|---|---|
| Kessler Ridge | 93.8 | 94.5 | 98.5 | 91.1 | 96.5 |
| Tarvos Station | 80.7 | 81.0 | 80.0 | 80.9 | 80.0 |
| Ostrava Hub | 95.7 | 91.2 | 91.3 | 91.4 | 93.8 |
| Hollis Point | 85.7 | 85.4 | 83.5 | 86.1 | 85.1 |

Spare parts for the Gannet fleet are pooled at Mirefield Depot and shipped to other sites within 4 hours. Loading sequences are planned so that the heaviest items sit closest to the Gannet centre of mass. There was a brief debate about whether the Kestrel-9 maintenance window should move to weekends.

### 39.4 Scope and Applicability

This part of the handbook was last reviewed by Hollis Ostrander and reflects the practice agreed in 2023.

Records demonstrating compliance are kept in Drydock for at least 5 years. A breach of this rule is handled under the progressive discipline process described in the People chapter. Teams that cannot comply because of tooling limitations must log a risk entry in Pilot House before proceeding. Expense claims must be filed in Pilot House within 60 days, with receipts attached. Temporary deviations of up to 30 days may be granted by the site director at Port Anselm. Supervisors are responsible for confirming that new starters have read this section before their first shift. All Mission Planning staff at Brightwater Annex must complete the refresher module within 90 days of any change to this policy.

1. Penetration tests of public-facing services are commissioned at least once per year.
2. Accounts that have not been used for 90 days are disabled automatically.
3. All Quality Assurance staff at Mirefield Depot must complete the refresher module within 90 days of any change to this policy.
4. Temporary deviations of up to 5 days may be granted by the site director at Hollis Point.
5. Failure to complete required training within the deadline results in temporary removal from the duty roster.
6. Exceptions require written approval from the Cargo Integrity lead and are reviewed again after 18 months.
7. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.

Maintenance of the cryogenic fuel lines at every NOL site is contracted exclusively to Fennimore & Holt Cryogenics under a five-year agreement; internal teams may inspect the lines but must not open any cryogenic coupling themselves.

Exceptions require written approval from the Facilities lead and are reviewed again after 24 months. Parental leave policies apply equally regardless of gender and are explained in the benefits portal. Employees at Selene Gate can use the on-site gym between 11:45 and 19:45, except during declared operations.

### 39.5 Working Group Minutes: Facilities (2021-07-12)

**Attendees:** Carys Abernathy, Ulrich Iwasaki, Esme Underhill, Zofia Marchetti, Gideon Zelenko. **Chair:** Carys Abernathy. **Location:** Hollis Point, room A32.

**Agenda**

1. Status of the Signal Lamp upgrade
2. Training plan for October
3. Supplier issues with radiator panel deliveries
4. Budget forecast
5. Review of the planned maintenance compliance for the last month

Zofia Marchetti from Flight Dynamics presented the results of the Kessler Ridge pilot and recommended a phased rollout. There was a brief debate about whether the Gannet maintenance window should move to weekends. No objections were raised to extending the trial at Coldharbour Yard for another 4 weeks. Zofia Marchetti reminded everyone that the February audit will focus on training records. A proposal to standardise the load cell inspection checklist across sites was well received. Several attendees noted that the current process in Cartographer requires too many manual steps. Zofia Marchetti raised a concern about the workload on the Fleet Operations team during the peak season.

Yusuf Drummond raised a concern about the workload on the Flight Dynamics team during the peak season. Attendees asked for clearer escalation paths when a customer changes requirements late. Vesna Ostrander reminded everyone that the August audit will focus on training records.

**Decisions**

- Adopt the shared inspection template at all sites.
- Proceed with the Wayfarer upgrade at Selene Gate in August.
- Adopt the shared inspection template at all sites.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Collect manifest accuracy data for next meeting | Carys Abernathy | 2025-04-17 |
| 2 | Confirm pressure regulator delivery dates with supplier | Carys Abernathy | 2025-01-25 |
| 3 | Confirm battery module delivery dates with supplier | Gideon Zelenko | 2025-11-11 |
| 4 | Collect first-pass inspection yield data for next meeting | Zofia Marchetti | 2026-07-14 |

### 39.6 Configuration Baseline: Corvid data recorder

Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes. During integration, torque values for every fastener are recorded and attached to the build record. A data recorder that fails its acceptance test twice is quarantined and returned to the supplier.

| Parameter | Value | Tolerance | Notes |
|---|---|---|---|
| Mounting | 8 × M6 bolts | Torque 27 N·m | Thread-locker required |
| Design life | 6,310 cycles | n/a | Hard limit, no extension |
| Dry mass | 5,805 kg | ±34 kg | Excludes harness |
| Peak power | 2358 W | ±2 % | During deployment |
| Data rate | 1717 kbit/s | n/a | Compressed telemetry |
| Operating temperature | -46 to 31 °C | ±3 °C | Qualification limits are wider |
| Supplier | Pemberton Instruments Ltd | n/a | Approved vendor list |
| Part number | COR-DAT-7307 | n/a | Revision D |

During integration, torque values for every fastener are recorded and attached to the build record. The Corvid recovery tender uses a dual-redundant data recorder that switches over automatically within 37 ms of a fault. Each data recorder carries a serial plate that encodes the batch, the factory and the inspection date. The design team at Selene Gate owns the interface control document and approves every change to it. Power draw peaks at 387 W during the deployment sequence and settles at roughly a third of that.

**Operating limits**

- The Corvid recovery tender supports both automated and manual docking, although manual mode is reserved for certified pilots.
- During integration, torque values for every fastener are recorded and attached to the build record.
- The Corvid recovery tender uses a dual-redundant data recorder that switches over automatically within 140 ms of a fault.
- Data from each pass is reconciled in Drydock and flagged if more than 5 percent of frames are missing.

## Chapter 40: Procurement and Vendors, Part II

The following rules describe expected practice for procurement and vendors. They apply to employees and contractors alike.

### 40.1 Working Group Minutes: Mission Planning (2024-05-22)

**Attendees:** Isolde Szabo, Greta Ibarra, Vesna Ibarra, Dorian Moravec, Kalinda Szabo. **Chair:** Isolde Szabo. **Location:** Kessler Ridge, room B21.

**Agenda**

1. Budget forecast
2. Budget forecast
3. Any other business
4. Feedback from Westerly Weather Service

Isolde Szabo from Fleet Operations presented the results of the Hollis Point pilot and recommended a phased rollout. Isolde Szabo will draft a short note for Umbra Imaging explaining the revised delivery window. Isolde Szabo reported that the backlog in Keelson had fallen to 49 tickets. A proposal to standardise the cargo cradle inspection checklist across sites was well received. The team reviewed open risks and closed 18 items that were no longer relevant. Several attendees noted that the current process in Tidewater requires too many manual steps. Isolde Szabo raised a concern about the workload on the Customer Assurance team during the peak season.

Amara Grimaldi reported that the backlog in Gantry had fallen to 169 tickets. Greta Yilmaz will draft a short note for Ravensmoor University explaining the revised delivery window. Attendees asked for clearer escalation paths when a customer changes requirements late.

**Decisions**

- Adopt the shared inspection template at all sites.
- Extend the night-shift trial by 4 weeks.
- Defer the star tracker checklist change until the supplier responds.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Check budget headroom with Finance | Isolde Szabo | 2026-05-02 |
| 2 | Collect planned maintenance compliance data for next meeting | Greta Ibarra | 2026-03-13 |
| 3 | Confirm data recorder delivery dates with supplier | Dorian Moravec | 2026-05-10 |
| 4 | Draft customer note for Umbra Imaging | Isolde Szabo | 2026-11-13 |
| 5 | Update training matrix for Cargo Integrity | Greta Ibarra | 2026-03-02 |

### 40.2 Meeting Notes: Flight Dynamics (2023-09-13)

**Attendees:** Amara Ekwueme, Gideon Thorvaldsen, Greta Fairbanks, Gideon Abernathy, Mirela Lowell. **Chair:** Amara Ekwueme. **Location:** Lagrange Relay L4, room A25.

**Agenda**

1. Training plan for August
2. Review of the customer satisfaction score for the last month
3. Status of the Pilot House upgrade

Gideon Thorvaldsen raised a concern about the workload on the Quality Assurance team during the peak season. Several attendees noted that the current process in MANIFEST requires too many manual steps. No objections were raised to extending the trial at Lagrange Relay L4 for another 2 weeks. Gideon Thorvaldsen from Fleet Operations presented the results of the Tarvos Station pilot and recommended a phased rollout. There was a brief debate about whether the Petrel maintenance window should move to weekends. The discussion moved to budget, where Gideon Thorvaldsen confirmed a remaining allocation of €97,250.

Bastian Underhill will draft a short note for Meridian Survey Corp explaining the revised delivery window. Several attendees noted that the current process in Ledgerline requires too many manual steps. Farrukh Drummond reported that the backlog in Cartographer had fallen to 148 tickets. Nnamdi Ostrander reminded everyone that the September audit will focus on training records.

**Decisions**

- Close the open risk on Corvid maintenance windows.
- Close the open risk on Shrike maintenance windows.

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Collect audit finding closure rate data for next meeting | Amara Ekwueme | 2026-01-21 |
| 2 | Collect ticket backlog data for next meeting | Gideon Thorvaldsen | 2026-09-04 |
| 3 | Check budget headroom with Finance | Mirela Lowell | 2026-07-22 |

### 40.3 Escalation Rules

The guidance below grew out of lessons learned at Coldharbour Yard and has since been adopted company-wide.

The Petrel transfer stage turnaround target at Lagrange Relay L4 is 4 hours, measured from landing to ready-for-launch. Nothing in this section prevents an employee from stopping work they believe to be unsafe. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. Where this policy conflicts with a customer contract, the stricter requirement applies. Night operations require additional lighting checks and a second spotter at the cargo ramp.

1. A breach of this rule is handled under the progressive discipline process described in the People chapter.
2. A breach of this rule is handled under the progressive discipline process described in the People chapter.
3. Cargo for Quillon Satellites is scanned twice: once on arrival and once immediately before integration.
4. Vendors receive time-limited accounts that expire at the end of their statement of work.
5. Exceptions require written approval from the Ground Systems lead and are reviewed again after 12 months.
6. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.

### 40.4 Release Notes: Ledgerline

Ledgerline is maintained by the Mission Planning team. Releases are deployed to Lagrange Relay L4 first and to the remaining sites after a soak period of 60 days.

#### Ledgerline 7.8.3 (2023-09-28)

**Fixed**
- Broken links in exported PDF reports.
- A race condition when two operators edited the same pallet.

**Changed**
- Timeouts for the Tarvos Station gateway from 15 to 30 seconds.
- The default retention period to 9 months.

**Added**
- A dry-run mode for configuration changes.
- Export of mean time to repair reports to CSV.
- A read-only view for customer representatives.

#### Ledgerline 7.8.2 (2022-12-25)

**Added**
- Automatic reminders for expiring certifications.
- A dry-run mode for configuration changes.
- Support for the Petrel cargo profile.

**Fixed**
- A crash when a umbilical connector record had no serial number.

**Removed**
- The legacy FTP upload path.
- The deprecated v1 manifest endpoint.

#### Ledgerline 7.8.1 (2022-10-05)

**Added**
- An audit trail for manual overrides.
- Support for the Shrike cargo profile.

**Removed**
- The legacy FTP upload path.
- An unused MANIFEST integration.
- The deprecated v1 manifest endpoint.

**Changed**
- Timeouts for the Hollis Point gateway from 120 to 90 seconds.

### 40.5 Frequently Asked Questions about Procurement and Vendors

**Q: Can customers visit during integration?**

Customer visits are welcome but must be scheduled with Customer Assurance at least 30 days ahead.

**Q: Who approves a change to the Signal Lamp configuration?**

Changes are approved by the Cargo Integrity lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within 60 days.

**Q: How do I request access to flight data?**

Raise an access request in Ledgerline. Requests are approved by the data owner in Cryogenics and usually processed within 45 working days.

## Chapter 41: Mission Planning, Part II

The time capsule buried beneath the Kessler Ridge flagpole during the tenth-anniversary celebration is scheduled to be opened on 14 March 2071; its contents list is sealed with the corporate secretary.

This part of the handbook was last reviewed by Maren Underhill and reflects the practice agreed in 2025.

### 41.1 Escalation Rules

Mission Planning touches almost every team. This section summarises the standards we hold ourselves to and why.

Records demonstrating compliance are kept in Keelson for at least 7 years. The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log. This rule was tightened in 2021 after an internal review found inconsistent practice across sites. All Ground Systems staff at Ostrava Hub must complete the refresher module within 30 days of any change to this policy. Shift handover at Ostrava Hub takes place at 08:15 and must include a walk-through of open work orders. Loading sequences are planned so that the heaviest items sit closest to the Osprey centre of mass. The Petrel transfer stage turnaround target at Tarvos Station is 72 hours, measured from landing to ready-for-launch.

1. The Corvid recovery tender turnaround target at Kessler Ridge is 16 hours, measured from landing to ready-for-launch.
2. Every 14 days, the Flight Dynamics team rehearses a loss-of-communications scenario with the duty controllers.
3. Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.
4. The Mission Planning team runs a phishing simulation every 12 months and publishes anonymised results.
5. When two departures compete for the same pad, the one with the earlier customer commitment takes priority.
6. The Cryogenics desk is staffed from 08:30 to 17:45 on weekdays, with an on-call engineer outside those hours.

Every 90 days, the Fleet Operations team rehearses a loss-of-communications scenario with the duty controllers. Teams that cannot comply because of tooling limitations must log a risk entry in MANIFEST before proceeding. If a pallet arrives without a valid manifest entry in Wayfarer, it is held in the quarantine cage.

> **Note:** The requirement applies equally to remote staff who access Signal Lamp from outside a company site.

## Appendix A: Glossary

Terms are listed alphabetically. Where a term has a different meaning in a customer contract, the contract definition applies to that customer's work.

**Acceptance test.** The test that a delivered item must pass before it enters company stock.

**Anomaly.** Any unexpected behaviour of hardware, software or process that requires analysis.

**Bay.** A marked loading area in a yard, rated for a specific maximum load and hazard class.

**Bridge.** The virtual or physical room where operations staff coordinate during a shift.

**Closeout.** The final inspection and sealing of a vehicle before fuel loading begins.

**Cold soak.** A period during which hardware is held at low temperature, deliberately or otherwise.

**Configuration baseline.** The approved set of settings and versions against which changes are measured.

**Consignment.** One customer's cargo for a single flight, tracked as a unit in the manifest system.

**Cradle.** The structure that holds cargo inside a vehicle and transfers loads to the airframe.

**Data owner.** The person accountable for who may access a given data set and for what purpose.

**Dry run.** A rehearsal of a procedure or configuration change that makes no permanent changes.

**Duty Flight Director.** The person with final authority over flight decisions during a shift.

**Escalation path.** The ordered list of people to contact when a problem cannot be solved locally.

**Failover.** Automatic or manual transfer of a function from a primary to a backup system.

**Hazard class.** A category describing the handling risk of cargo, from inert to highly reactive.

**Hold point.** A step in a procedure that cannot be passed without an explicit sign-off.

**Integration.** The process of installing customer cargo into a vehicle and verifying interfaces.

**Interface control document.** The agreed description of mechanical, electrical and data interfaces.

**Loss of signal.** The moment when the ground station can no longer receive a vehicle's telemetry.

**Manifest.** The authoritative list of everything loaded on a flight, with masses and positions.

**Mass budget.** The allocation of permitted mass to each subsystem and to customer cargo.

**Near miss.** An event that could have caused harm or damage but did not.

**On-call engineer.** The engineer responsible for responding to alerts outside staffed hours.

**Pad.** A launch or landing surface, together with its supporting ground equipment.

**Pass.** A period during which a vehicle is visible to a ground station.

**Propellant margin.** The fuel remaining above the minimum reserve required for a safe return.

**Quarantine cage.** A locked area for items that cannot be used until a disposition is made.

**Readiness review.** A formal meeting that confirms a vehicle and its cargo are ready to fly.

**Reserve.** The minimum quantity of a consumable that must remain untouched in normal operations.

**Root cause.** The underlying reason for an incident, as opposed to its immediate trigger.

**Shift log.** The chronological record of events, decisions and handovers for a shift.

**Soak test.** A long-duration test under constant conditions to reveal slow drift or failures.

**Spotter.** A trained person who watches a moving load and can stop the operation.

**Station keeping.** Small manoeuvres that keep a vehicle in a planned position or orbit.

**Telemetry frame.** A fixed-format block of sensor readings sent from a vehicle to the ground.

**Turnaround.** The time from a vehicle landing to being ready for its next launch.

**Two-person rule.** A requirement that two qualified people are present for a task.

**Umbilical.** The cable and hose bundle that connects a vehicle to ground systems before launch.

**Work order.** A tracked request to perform maintenance or repair on a specific item.

**Yard.** An outdoor area at a site used for staging vehicles, cargo and equipment.

## Appendix B: Handbook revision history

| Revision | Date | Author | Summary |
|---|---|---|---|
| 14 | 2022-05-27 | Lorcan Lowell | Added release notes for Gantry |
| 13 | 2022-10-13 | Amara Whitlock | New glossary entries |
| 12 | 2022-09-10 | Ulrich Quarles | Added release notes for Halyard |
| 11 | 2021-02-08 | Nnamdi Zelenko | Updated incident management chapter after the Mirefield Depot audit |
| 10 | 2021-01-19 | Pavel Zelenko | Added incident reviews from the last quarter |
| 9 | 2021-01-17 | Zofia Kowalczyk | Added incident reviews from the last quarter |
| 8 | 2020-04-11 | Florian Grimaldi | New glossary entries |
| 7 | 2020-12-27 | Kalinda Varga | Reworded overtime rules |
| 6 | 2020-05-28 | Dorian Underhill | Updated customer commitments chapter after the Brightwater Annex audit |
| 5 | 2019-03-23 | Hollis Fairbanks | Restructured chapters |
| 4 | 2019-08-07 | Kalinda Quarles | Reworded overtime rules |
| 3 | 2019-02-01 | Wendell Jessop | Added release notes for Signal Lamp |
| 2 | 2018-05-08 | Jonas Nakashima | New glossary entries |
| 1 | 2018-03-15 | Gideon Bellweather | Clarified visitor rules at Lagrange Relay L4 |

## Appendix C: Contacts

| Team | Contact | Location |
|---|---|---|
| Fleet Operations | Nikhil Yilmaz | Mirefield Depot |
| Orbital Traffic Control | Dorian Bellweather | Tarvos Station |
| Cargo Integrity | Elif Ostrander | Ostrava Hub |
| Ground Systems | Elif Bellweather | Ostrava Hub |
| Flight Dynamics | Bram Ferreira | Lagrange Relay L4 |
| Facilities | Dorian Kuroda | Selene Gate |
| Procurement | Ines Brightman | Hollis Point |
| People Operations | Vesna Ibarra | Brightwater Annex |
| Information Security | Carys Rasmussen | Lagrange Relay L4 |
| Customer Assurance | Carys Nakashima | Tarvos Station |
| Propulsion Engineering | Lorcan Ekwueme | Lagrange Relay L4 |
| Cryogenics | Vesna Kuroda | Hollis Point |
| Mission Planning | Wendell Novak | Ostrava Hub |
| Quality Assurance | Greta Lindqvist | Kessler Ridge |
| Finance | Maren Ibarra | Port Anselm |

*End of handbook.*

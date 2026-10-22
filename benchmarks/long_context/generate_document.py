#!/usr/bin/env python3
"""Deterministic generator for the long-context benchmark document.

Writes, next to this script:
  document.md      ~300k characters (~73k Gemma tokens, ~83k Llama/Qwen-style tokens) of fictional company handbook
  facts.json       the 10 planted facts (question, accepted answers, position)
  document.sha256  SHA-256 of document.md

Everything is derived from a fixed seed and the text pools below, so running
this script on any machine with Python 3.9+ produces byte-identical output.
Changing anything here changes the document: bump suite_version (see
benchmarks/README.md) whenever you regenerate with different content.

Python standard library only.
"""

import hashlib
import json
import os
import random
import re

SEED = 20261019
TARGET_CHARS = 300000          # total document size target (>=72k tokens even for efficient tokenizers like Gemma, ~4.1 chars/token)
CHARS_PER_TOKEN = 3.6
HERE = os.path.dirname(os.path.abspath(__file__))

COMPANY = "Northwind Orbital Logistics"
SHORT = "NOL"

# --------------------------------------------------------------------------
# Planted facts. Each answer string must appear exactly once in the document.
# target_pct is where the fact is inserted (as a fraction of the final text).
# --------------------------------------------------------------------------
FACTS = [
    {
        "id": "f1", "target_pct": 3.0,
        "text": ("Following the 2023 interlock audit, Ground Systems confirmed that the emergency override "
                 "code for Dock 7 at the Kessler Ridge spaceport is TANGERINE-4471. The code may only be "
                 "entered when both the primary and the secondary clamp interlocks have failed, and every "
                 "use must be reported to the duty Flight Director within ten minutes."),
        "question": "What is the emergency override code for Dock 7 at the Kessler Ridge spaceport?",
        "answers": ["TANGERINE-4471"],
    },
    {
        "id": "f2", "target_pct": 8.0,
        "text": ("A note on company history: the founding charter of Northwind Orbital Logistics was not "
                 "signed in an office. The four founders signed it aboard the chartered research vessel "
                 "Halcyon Drift while it was anchored off the coast during a storm delay, and a framed copy "
                 "of the signature page still hangs in the Kessler Ridge lobby."),
        "question": "Aboard which vessel was the company's founding charter signed?",
        "answers": ["Halcyon Drift"],
    },
    {
        "id": "f3", "target_pct": 22.0,
        "text": ("Staff relocating to the Ostrava Hub often ask about catering. The Level 3 canteen serves "
                 "its signature dish, a smoked-barley stew called Grumbleroot Pottage, every Thursday; "
                 "vegetarian and gluten-free portions are prepared separately on request."),
        "question": "What is the name of the signature stew served every Thursday in the Ostrava Hub Level 3 canteen?",
        "answers": ["Grumbleroot Pottage", "Grumbleroot"],
    },
    {
        "id": "f4", "target_pct": 33.0,
        "text": ("The firmware signing key for the Pathfinder telemetry units is held in the hardware "
                 "security vault designated BLUE-HERON-82. Requests to use that vault require two approvers "
                 "from Information Security and are logged permanently."),
        "question": "What is the designation of the vault that holds the firmware signing key for the Pathfinder telemetry units?",
        "answers": ["BLUE-HERON-82", "BLUE HERON 82"],
    },
    {
        "id": "f5", "target_pct": 44.0,
        "text": ("Any hot-fire test of the Mk-IV maneuvering thruster requires written sign-off from "
                 "Dr. Ingrid Valtameri, the Chief Propulsion Safety Officer; no deputy may substitute for "
                 "this signature, even during a declared schedule emergency."),
        "question": "Whose written sign-off is required before any hot-fire test of the Mk-IV maneuvering thruster?",
        "answers": ["Valtameri"],
    },
    {
        "id": "f6", "target_pct": 50.0,
        "text": ("Each December the company presents its highest internal honor for exceptional logistics "
                 "work, the Copper Albatross Prize, to one employee nominated by peers from at least two "
                 "different sites."),
        "question": "What is the name of the company's highest internal award for exceptional logistics work?",
        "answers": ["Copper Albatross"],
    },
    {
        "id": "f7", "target_pct": 57.0,
        "text": ("If the primary orbital traffic control center becomes unavailable, authority transfers to "
                 "the backup ground station in the small town of Pellingford, which is staffed around the "
                 "clock by a reduced crew of four controllers."),
        "question": "In which town is the backup ground station for orbital traffic control located?",
        "answers": ["Pellingford"],
    },
    {
        "id": "f8", "target_pct": 72.0,
        "text": ("The decommissioned relay satellite ND-Sentinel-3 was affectionately nicknamed \"Old "
                 "Biscuit\" by the operations crew because of the beige thermal blankets that made it look, "
                 "in early camera images, like a cracker floating in space."),
        "question": "What nickname did the operations crew give the decommissioned satellite ND-Sentinel-3?",
        "answers": ["Old Biscuit"],
    },
    {
        "id": "f9", "target_pct": 93.0,
        "text": ("Maintenance of the cryogenic fuel lines at every NOL site is contracted exclusively to "
                 "Fennimore & Holt Cryogenics under a five-year agreement; internal teams may inspect the "
                 "lines but must not open any cryogenic coupling themselves."),
        "question": "Which contractor is responsible for maintaining the cryogenic fuel lines?",
        "answers": ["Fennimore"],
    },
    {
        "id": "f10", "target_pct": 97.0,
        "text": ("The time capsule buried beneath the Kessler Ridge flagpole during the tenth-anniversary "
                 "celebration is scheduled to be opened on 14 March 2071; its contents list is sealed with "
                 "the corporate secretary."),
        "question": "On what date is the time capsule beneath the Kessler Ridge flagpole scheduled to be opened?",
        "answers": ["2071"],
    },
]

# Substrings that random filler must never produce (they belong to facts).
BANNED = [a.lower() for f in FACTS for a in f["answers"]] + ["4471", "2071", "18750"]

# --------------------------------------------------------------------------
# Vocabulary pools (all fictional)
# --------------------------------------------------------------------------
FIRST = ["Amara", "Bastian", "Celeste", "Dorian", "Elif", "Farrukh", "Greta", "Hamid", "Isolde", "Jonas",
         "Keiko", "Lorcan", "Mirela", "Nnamdi", "Oona", "Pavel", "Quinn", "Rosalind", "Soren", "Tamsin",
         "Ulrich", "Vesna", "Wendell", "Ximena", "Yusuf", "Zofia", "Anouk", "Bram", "Carys", "Dmitri",
         "Esme", "Florian", "Gideon", "Hollis", "Ines", "Joaquin", "Kalinda", "Leopold", "Maren", "Nikhil"]
LAST = ["Achterberg", "Bellweather", "Castellanos", "Drummond", "Eskildsen", "Fairbanks", "Grimaldi",
        "Halvorsen", "Iwasaki", "Jessop", "Kowalczyk", "Lindqvist", "Marchetti", "Nakashima", "Okonkwo",
        "Pemberton", "Quarles", "Rasmussen", "Szabo", "Thorvaldsen", "Underhill", "Varga", "Whitlock",
        "Yilmaz", "Zelenko", "Abernathy", "Brightman", "Coutinho", "Delacroix", "Ekwueme", "Ferreira",
        "Gallagher", "Hargreaves", "Ibarra", "Jankowski", "Kuroda", "Lowell", "Moravec", "Novak", "Ostrander"]
SITES = ["Kessler Ridge", "Ostrava Hub", "Lagrange Relay L4", "Port Anselm", "Mirefield Depot",
         "Tarvos Station", "Coldharbour Yard", "Selene Gate", "Brightwater Annex", "Hollis Point"]
TEAMS = ["Fleet Operations", "Orbital Traffic Control", "Cargo Integrity", "Ground Systems", "Flight Dynamics",
         "Facilities", "Procurement", "People Operations", "Information Security", "Customer Assurance",
         "Propulsion Engineering", "Cryogenics", "Mission Planning", "Quality Assurance", "Finance"]
SYSTEMS = ["MANIFEST", "Tidewater", "Lodestar", "Beacon", "Cartographer", "Sextant", "Ledgerline", "Halyard",
           "Pilot House", "Gantry", "Wayfarer", "Keelson", "Bulkhead", "Signal Lamp", "Drydock"]
VEHICLES = ["Kestrel-9 orbital tug", "Heron-class freighter", "Wren crew shuttle", "Osprey cargo lander",
            "Petrel transfer stage", "Gannet refueling drone", "Shrike inspection pod", "Corvid recovery tender"]
VEHICLE_SHORT = ["Kestrel-9", "Heron", "Wren", "Osprey", "Petrel", "Gannet", "Shrike", "Corvid"]
EQUIPMENT = ["docking clamp", "cargo cradle", "thermal blanket", "star tracker", "reaction wheel",
             "cryo coupling", "telemetry unit", "battery module", "pressure regulator", "umbilical connector",
             "load cell", "hatch seal", "attitude thruster", "radiator panel", "data recorder"]
CUSTOMERS = ["Alder Biotech", "Meridian Survey Corp", "Quillon Satellites", "Ravensmoor University",
             "Solvay-Ortiz Pharma", "Talisker Mining", "Umbra Imaging", "Veldt Communications",
             "Westerly Weather Service", "Yarrow Agritech"]
TOPICS = ["Safety and Conduct", "Fleet Operations", "Ground Facilities", "Information Security",
          "Cargo Handling", "Software Systems", "People and Travel", "Procurement and Vendors",
          "Mission Planning", "Quality and Audits", "Customer Commitments", "Incident Management",
          "Propulsion and Cryogenics", "Data Retention", "Environmental Practices", "Training and Certification"]
METRICS = ["on-time departure rate", "manifest accuracy", "mean time to repair", "cargo damage rate",
           "customer satisfaction score", "fuel efficiency index", "audit finding closure rate",
           "first-pass inspection yield", "ticket backlog", "planned maintenance compliance"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

# Sentence templates by theme. {slot} names are filled by fill().
POLICY_SENTENCES = [
    "All {team} staff at {site} must complete the refresher module within {n_days} days of any change to this policy.",
    "Exceptions require written approval from the {team} lead and are reviewed again after {n_months} months.",
    "Where this policy conflicts with a customer contract, the stricter requirement applies.",
    "Supervisors are responsible for confirming that new starters have read this section before their first shift.",
    "Records demonstrating compliance are kept in {system} for at least {n_years} years.",
    "A breach of this rule is handled under the progressive discipline process described in the People chapter.",
    "Contractors working on site are bound by the same obligations as employees for the duration of their engagement.",
    "The policy owner reviews the wording every {n_months} months and publishes changes in the revision history.",
    "Questions about interpretation should be raised with {person} in {team} rather than resolved informally.",
    "Nothing in this section prevents an employee from stopping work they believe to be unsafe.",
    "Temporary deviations of up to {n_days} days may be granted by the site director at {site}.",
    "Teams that cannot comply because of tooling limitations must log a risk entry in {system} before proceeding.",
    "The requirement applies equally to remote staff who access {system} from outside a company site.",
    "Audit samples are drawn quarterly, and at least {n_small} findings per site are followed up in person.",
    "Signage summarising this rule is displayed at every entrance to the {site} operations floor.",
    "Where a task involves a {equipment}, the two-person rule applies from preparation through to sign-off.",
    "Employees should keep personal notes out of {system}; only operational records belong there.",
    "Any spending above {money} linked to this policy needs approval from Finance before the order is raised.",
    "This rule was tightened in {year} after an internal review found inconsistent practice across sites.",
    "Visitors must be escorted at all times and must not handle a {equipment} under any circumstances.",
    "The duty manager may suspend this procedure during a declared incident, but must record the reason in the shift log.",
    "Failure to complete required training within the deadline results in temporary removal from the duty roster.",
]
TECH_SENTENCES = [
    "The {vehicle} uses a dual-redundant {equipment} that switches over automatically within {n_ms} ms of a fault.",
    "Nominal operating temperature for the {equipment} ranges from {temp_lo} °C to {temp_hi} °C.",
    "Firmware for the {equipment} is distributed through {system} and must be verified before installation.",
    "Each {equipment} carries a serial plate that encodes the batch, the factory and the inspection date.",
    "Ground tests at {site} showed a mean drift of {small_float} percent over {n_hours} hours of continuous soak.",
    "The {vehicle} can hold station for up to {n_hours} hours before its propellant margin falls below reserve.",
    "Telemetry is sampled at {n_hz} Hz and down-linked in compressed frames every {n_sec} seconds.",
    "Replacement intervals are measured in cycles rather than calendar time, with a hard limit of {n_cycles} cycles.",
    "Engineers should consult the {system} configuration record before changing any calibration constant.",
    "During integration, torque values for every fastener are recorded and attached to the build record.",
    "The latest revision reduced mass by {n_kg} kg by replacing the aluminium bracket with a composite part.",
    "A {equipment} that fails its acceptance test twice is quarantined and returned to the supplier.",
    "Thermal margins were re-analysed after the {year} anomaly, and the upper limit was lowered by {n_small} °C.",
    "Power draw peaks at {n_watts} W during the deployment sequence and settles at roughly a third of that.",
    "The {vehicle} supports both automated and manual docking, although manual mode is reserved for certified pilots.",
    "Vibration qualification follows the company profile, which is more demanding than most launch provider envelopes.",
    "Data from each pass is reconciled in {system} and flagged if more than {n_small} percent of frames are missing.",
    "The design team at {site} owns the interface control document and approves every change to it.",
]
OPS_SENTENCES = [
    "Shift handover at {site} takes place at {hhmm} and must include a walk-through of open work orders.",
    "The {team} desk is staffed from {hhmm} to {hhmm2} on weekdays, with an on-call engineer outside those hours.",
    "Cargo for {customer} is scanned twice: once on arrival and once immediately before integration.",
    "If a pallet arrives without a valid manifest entry in {system}, it is held in the quarantine cage.",
    "The {vehicle} turnaround target at {site} is {n_hours} hours, measured from landing to ready-for-launch.",
    "Operators log every manual override in {system} together with the reason and the approving supervisor.",
    "Weather holds are called by Flight Dynamics; ground teams should not pre-empt the decision.",
    "Loading sequences are planned so that the heaviest items sit closest to the {vehicle_short} centre of mass.",
    "Every {n_days} days, the {team} team rehearses a loss-of-communications scenario with the duty controllers.",
    "When two departures compete for the same pad, the one with the earlier customer commitment takes priority.",
    "The {site} yard has {n_small} bays, each rated for a different maximum load and hazard class.",
    "Spare parts for the {vehicle_short} fleet are pooled at {site} and shipped to other sites within {n_hours} hours.",
    "Night operations require additional lighting checks and a second spotter at the cargo ramp.",
    "Customer representatives may observe loading from the gallery but may not enter the clean area.",
    "Delays longer than {n_min} minutes are reported to the customer by Customer Assurance, not by the floor team.",
    "Fuel loading is the last activity before closeout, and no other work may proceed in parallel.",
]
PEOPLE_SENTENCES = [
    "New employees receive a buddy from their own team for the first {n_weeks} weeks.",
    "Travel between sites is booked through the travel desk, which applies the preferred-carrier list automatically.",
    "Overtime above {n_hours} hours per month must be agreed in advance with the line manager.",
    "Employees at {site} can use the on-site gym between {hhmm} and {hhmm2}, except during declared operations.",
    "Annual reviews take place in {month}, with a mid-year check-in six months later.",
    "Learning budgets of up to {money} per person per year can be spent on approved courses and conferences.",
    "Parental leave policies apply equally regardless of gender and are explained in the benefits portal.",
    "The internal mobility programme lets staff spend up to {n_weeks} weeks shadowing another team.",
    "Expense claims must be filed in {system} within {n_days} days, with receipts attached.",
    "The company observes a quiet period around major launches, during which non-essential meetings are cancelled.",
    "Remote work is supported for roles that do not require hands-on access to flight hardware.",
    "Recognition nominations are collected each quarter and reviewed by a rotating panel of peers.",
]
SECURITY_SENTENCES = [
    "Access to {system} requires hardware-key authentication and is reviewed every {n_days} days.",
    "Accounts that have not been used for {n_days} days are disabled automatically.",
    "Production credentials must never be pasted into chat tools, tickets or shared documents.",
    "The {team} team runs a phishing simulation every {n_months} months and publishes anonymised results.",
    "Laptops are encrypted at rest and enrolled in device management before first use.",
    "Removable media is blocked on all operations workstations at {site}.",
    "Security incidents must be reported to the Information Security hotline within {n_min} minutes of discovery.",
    "Network segments for flight systems are physically separated from the corporate network.",
    "Vendors receive time-limited accounts that expire at the end of their statement of work.",
    "Log data from {system} is retained for {n_months} months and then archived to cold storage.",
    "Penetration tests of public-facing services are commissioned at least once per year.",
    "Badges must be worn visibly inside controlled areas and returned when employment ends.",
]
NARRATIVE_SENTENCES = [
    "{person} from {team} presented the results of the {site} pilot and recommended a phased rollout.",
    "The group agreed that the {metric} had improved, although the sample was still small.",
    "{person} raised a concern about the workload on the {team} team during the peak season.",
    "Several attendees noted that the current process in {system} requires too many manual steps.",
    "A proposal to standardise the {equipment} inspection checklist across sites was well received.",
    "{person} will draft a short note for {customer} explaining the revised delivery window.",
    "The discussion moved to budget, where {person} confirmed a remaining allocation of {money}.",
    "It was agreed to revisit the topic once the supplier has delivered the revised quotation.",
    "{person} reminded everyone that the {month} audit will focus on training records.",
    "No objections were raised to extending the trial at {site} for another {n_weeks} weeks.",
    "The team reviewed open risks and closed {n_small} items that were no longer relevant.",
    "{person} reported that the backlog in {system} had fallen to {n_small2} tickets.",
    "There was a brief debate about whether the {vehicle_short} maintenance window should move to weekends.",
    "Attendees asked for clearer escalation paths when a customer changes requirements late.",
]

POOLS_BY_KIND = {
    "policy": POLICY_SENTENCES, "tech": TECH_SENTENCES, "ops": OPS_SENTENCES,
    "people": PEOPLE_SENTENCES, "security": SECURITY_SENTENCES, "narrative": NARRATIVE_SENTENCES,
}

INTROS = [
    "This section explains how {company} approaches {topic_lc} at every site, from {site} to the smallest annex.",
    "The following rules describe expected practice for {topic_lc}. They apply to employees and contractors alike.",
    "{topic} touches almost every team. This section summarises the standards we hold ourselves to and why.",
    "Readers new to {company} should treat this section as the authoritative reference for {topic_lc}.",
    "This part of the handbook was last reviewed by {person} and reflects the practice agreed in {year}.",
    "The guidance below grew out of lessons learned at {site} and has since been adopted company-wide.",
]
SECTION_TITLES = {
    "policy": ["Scope and Applicability", "Roles and Responsibilities", "Approval Thresholds", "Exceptions Process",
               "Record Keeping", "Escalation Rules", "Minimum Standards", "Site-Specific Rules",
               "Compliance Monitoring", "Working with Contractors", "Reporting Obligations", "Definitions in Use"],
    "spec": ["Technical Specification", "Equipment Data Sheet", "Operating Limits", "Performance Envelope",
             "Configuration Baseline", "Interface Summary"],
    "changelog": ["Release Notes", "Changelog", "Version History"],
    "code": ["Configuration Example", "Reference Script", "Runbook Commands", "Data Query Example",
             "Manifest Format"],
    "meeting": ["Meeting Notes", "Working Group Minutes", "Review Board Notes"],
    "incident": ["Incident Review", "Post-Incident Report", "Anomaly Summary"],
    "faq": ["Frequently Asked Questions", "Common Questions"],
    "kpi": ["Quarterly Metrics", "Performance Dashboard Snapshot", "Site Metrics"],
}

FAQ_ITEMS = [
    ("Who approves a change to the {system} configuration?",
     "Changes are approved by the {team} lead after a peer review. Emergency changes can be approved by the duty manager and reviewed retrospectively within {n_days} days."),
    ("Can I bring a guest onto the {site} operations floor?",
     "Only with a visitor badge issued in advance and a trained escort. Guests are never allowed in the clean area."),
    ("How long do we keep shift logs?",
     "Shift logs are retained for {n_years} years in {system}, then archived. Logs linked to an incident are kept indefinitely."),
    ("What happens if a {equipment} fails inspection?",
     "It is tagged, moved to quarantine and logged in {system}. Quality Assurance decides whether it is repaired, scrapped or returned."),
    ("Who do I call if the {system} service is down?",
     "Contact the {team} on-call engineer through the operations bridge. Do not restart services yourself unless the runbook says so."),
    ("Is overtime paid during launch campaigns?",
     "Yes. Campaign overtime is paid at the enhanced rate, provided it was agreed with your manager beforehand."),
    ("How do I request access to flight data?",
     "Raise an access request in {system}. Requests are approved by the data owner in {team} and usually processed within {n_days} working days."),
    ("Can customers visit during integration?",
     "Customer visits are welcome but must be scheduled with Customer Assurance at least {n_days} days ahead."),
    ("What counts as a near miss?",
     "Any event that could have caused injury or damage but did not. Near misses are reported in the same way as incidents."),
    ("Where are spare {equipment} parts stored?",
     "The central pool is at {site}. Each site also keeps a small buffer stock sized from the last {n_months} months of usage."),
]

INCIDENT_CAUSES = [
    "a mislabelled {equipment} that passed visual inspection because the label template had been reused",
    "an expired certificate in {system} that blocked manifest synchronisation for several hours",
    "a scheduling conflict between two {team} shifts that left the cargo ramp without a spotter",
    "a firmware regression in the {equipment} that misreported temperature by a few degrees",
    "a supplier batch of {equipment} parts with out-of-tolerance threads",
    "a manual data entry error in {system} that duplicated a customer consignment",
    "condensation inside a {equipment} housing after an unplanned cold soak",
    "a network switch failure at {site} that isolated the telemetry archive",
]
REMEDIATIONS = [
    "Added an automated check in {system} that rejects the condition at entry.",
    "Updated the inspection checklist and retrained the {team} team at {site}.",
    "Introduced a second sign-off for the affected step.",
    "Replaced the affected {equipment} stock and quarantined the remaining batch.",
    "Added monitoring with an alert routed to the {team} on-call engineer.",
    "Revised the supplier quality agreement to include lot traceability.",
    "Scheduled a follow-up audit at {site} in {n_months} months.",
]
CHANGE_ITEMS = {
    "Added": ["export of {metric} reports to CSV", "support for the {vehicle_short} cargo profile",
              "a read-only view for customer representatives", "bulk import of {equipment} serial numbers",
              "an audit trail for manual overrides", "per-site dashboards for {team}",
              "a dry-run mode for configuration changes", "automatic reminders for expiring certifications"],
    "Changed": ["the default retention period to {n_months} months", "the manifest schema to version {ver_small}",
                "timeouts for the {site} gateway from {n_sec} to {n_sec2} seconds",
                "the approval flow so that {team} signs off before Finance",
                "log formatting to include the operator badge number", "sorting on the work-order list"],
    "Fixed": ["a crash when a {equipment} record had no serial number", "incorrect time zones in shift reports",
              "duplicated alerts after a failover at {site}", "rounding of mass totals in manifests",
              "a memory leak in the telemetry ingest worker", "broken links in exported PDF reports",
              "a race condition when two operators edited the same pallet"],
    "Removed": ["the legacy FTP upload path", "an unused {system} integration",
                "the deprecated v1 manifest endpoint"],
}

GLOSSARY = [
    ("Bay", "A marked loading area in a yard, rated for a specific maximum load and hazard class."),
    ("Closeout", "The final inspection and sealing of a vehicle before fuel loading begins."),
    ("Cold soak", "A period during which hardware is held at low temperature, deliberately or otherwise."),
    ("Consignment", "One customer's cargo for a single flight, tracked as a unit in the manifest system."),
    ("Cradle", "The structure that holds cargo inside a vehicle and transfers loads to the airframe."),
    ("Duty Flight Director", "The person with final authority over flight decisions during a shift."),
    ("Dry run", "A rehearsal of a procedure or configuration change that makes no permanent changes."),
    ("Failover", "Automatic or manual transfer of a function from a primary to a backup system."),
    ("Hazard class", "A category describing the handling risk of cargo, from inert to highly reactive."),
    ("Hold point", "A step in a procedure that cannot be passed without an explicit sign-off."),
    ("Integration", "The process of installing customer cargo into a vehicle and verifying interfaces."),
    ("Interface control document", "The agreed description of mechanical, electrical and data interfaces."),
    ("Manifest", "The authoritative list of everything loaded on a flight, with masses and positions."),
    ("Near miss", "An event that could have caused harm or damage but did not."),
    ("On-call engineer", "The engineer responsible for responding to alerts outside staffed hours."),
    ("Pad", "A launch or landing surface, together with its supporting ground equipment."),
    ("Propellant margin", "The fuel remaining above the minimum reserve required for a safe return."),
    ("Quarantine cage", "A locked area for items that cannot be used until a disposition is made."),
    ("Readiness review", "A formal meeting that confirms a vehicle and its cargo are ready to fly."),
    ("Reserve", "The minimum quantity of a consumable that must remain untouched in normal operations."),
    ("Shift log", "The chronological record of events, decisions and handovers for a shift."),
    ("Spotter", "A trained person who watches a moving load and can stop the operation."),
    ("Station keeping", "Small manoeuvres that keep a vehicle in a planned position or orbit."),
    ("Telemetry frame", "A fixed-format block of sensor readings sent from a vehicle to the ground."),
    ("Turnaround", "The time from a vehicle landing to being ready for its next launch."),
    ("Two-person rule", "A requirement that two qualified people are present for a task."),
    ("Umbilical", "The cable and hose bundle that connects a vehicle to ground systems before launch."),
    ("Work order", "A tracked request to perform maintenance or repair on a specific item."),
    ("Yard", "An outdoor area at a site used for staging vehicles, cargo and equipment."),
    ("Acceptance test", "The test that a delivered item must pass before it enters company stock."),
    ("Anomaly", "Any unexpected behaviour of hardware, software or process that requires analysis."),
    ("Bridge", "The virtual or physical room where operations staff coordinate during a shift."),
    ("Configuration baseline", "The approved set of settings and versions against which changes are measured."),
    ("Data owner", "The person accountable for who may access a given data set and for what purpose."),
    ("Escalation path", "The ordered list of people to contact when a problem cannot be solved locally."),
    ("Loss of signal", "The moment when the ground station can no longer receive a vehicle's telemetry."),
    ("Mass budget", "The allocation of permitted mass to each subsystem and to customer cargo."),
    ("Pass", "A period during which a vehicle is visible to a ground station."),
    ("Root cause", "The underlying reason for an incident, as opposed to its immediate trigger."),
    ("Soak test", "A long-duration test under constant conditions to reveal slow drift or failures."),
]

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


class Gen:
    def __init__(self, rng):
        self.rng = rng

    def _num(self, lo, hi):
        while True:
            v = self.rng.randint(lo, hi)
            if not any(b in str(v) for b in BANNED):
                return v

    def slot(self, name):
        r = self.rng
        if name == "team":
            return r.choice(TEAMS)
        if name == "site":
            return r.choice(SITES)
        if name == "system":
            return r.choice(SYSTEMS)
        if name == "vehicle":
            return r.choice(VEHICLES)
        if name == "vehicle_short":
            return r.choice(VEHICLE_SHORT)
        if name == "equipment":
            return r.choice(EQUIPMENT)
        if name == "customer":
            return r.choice(CUSTOMERS)
        if name == "metric":
            return r.choice(METRICS)
        if name == "month":
            return r.choice(MONTHS)
        if name == "person":
            return "%s %s" % (r.choice(FIRST), r.choice(LAST))
        if name == "company":
            return COMPANY
        if name == "year":
            return str(self._num(2018, 2026))
        if name in ("n_days",):
            return str(r.choice([5, 7, 10, 14, 21, 30, 45, 60, 90]))
        if name == "n_weeks":
            return str(r.choice([2, 3, 4, 6, 8, 12]))
        if name == "n_months":
            return str(r.choice([3, 6, 9, 12, 18, 24]))
        if name == "n_years":
            return str(r.choice([2, 3, 5, 7, 10]))
        if name in ("n_small", "n_small2"):
            return str(self._num(2, 19) if name == "n_small" else self._num(12, 240))
        if name == "n_hours":
            return str(r.choice([4, 6, 8, 12, 16, 18, 24, 36, 48, 72]))
        if name == "n_min":
            return str(r.choice([5, 10, 15, 20, 30, 45, 60]))
        if name in ("n_sec", "n_sec2"):
            return str(r.choice([2, 5, 10, 15, 30, 45, 60, 90, 120]))
        if name == "n_ms":
            return str(self._num(5, 400))
        if name == "n_hz":
            return str(r.choice([1, 2, 5, 10, 20, 50, 100]))
        if name == "n_cycles":
            return "{:,}".format(self._num(20, 900) * 10)
        if name == "n_kg":
            return "%.1f" % (self._num(3, 240) / 10.0)
        if name == "n_watts":
            return str(self._num(40, 2400))
        if name == "temp_lo":
            return str(-self._num(10, 60))
        if name == "temp_hi":
            return str(self._num(25, 85))
        if name == "small_float":
            return "%.2f" % (self._num(1, 99) / 100.0)
        if name == "money":
            return "€{:,}".format(self._num(5, 400) * 250)
        if name in ("hhmm", "hhmm2"):
            h = r.randint(5, 11) if name == "hhmm" else r.randint(16, 23)
            return "%02d:%02d" % (h, r.choice([0, 15, 30, 45]))
        if name == "ver_small":
            return "%d.%d" % (r.randint(2, 6), r.randint(0, 9))
        raise KeyError(name)

    def fill(self, template, **fixed):
        def rep(m):
            key = m.group(1)
            if key in fixed:
                return fixed[key]
            return self.slot(key)
        return re.sub(r"\{([a-z_0-9]+)\}", rep, template)

    def paragraph(self, kinds, n_lo=4, n_hi=7, **fixed):
        pool = []
        for k in kinds:
            pool.extend(POOLS_BY_KIND[k])
        n = self.rng.randint(n_lo, n_hi)
        picks = self.rng.sample(pool, min(n, len(pool)))
        return " ".join(self.fill(s, **fixed) for s in picks)

    def date(self, year_lo=2021, year_hi=2026):
        y = self.rng.randint(year_lo, year_hi)
        m = self.rng.randint(1, 12)
        d = self.rng.randint(1, 28)
        return "%04d-%02d-%02d" % (y, m, d)

    def person(self):
        return self.slot("person")

    def code(self, prefix):
        return "%s-%d" % (prefix, self._num(100, 9899))


# --------------------------------------------------------------------------
# Section builders. Each returns a list of Markdown blocks.
# --------------------------------------------------------------------------

def sec_policy(g, num, topic):
    r = g.rng
    title = r.choice(SECTION_TITLES["policy"])
    blocks = ["### %s %s" % (num, title),
              g.fill(r.choice(INTROS), topic=topic, topic_lc=topic.lower())]
    kinds = {"Information Security": ["security", "policy"], "People and Travel": ["people", "policy"],
             "Fleet Operations": ["ops", "policy"], "Cargo Handling": ["ops", "policy"]}.get(topic, ["policy", "ops"])
    blocks.append(g.paragraph(kinds))
    rules = []
    for i in range(r.randint(4, 7)):
        rules.append("%d. %s" % (i + 1, g.fill(r.choice(POLICY_SENTENCES + SECURITY_SENTENCES + OPS_SENTENCES))))
    blocks.append("\n".join(rules))
    if r.random() < 0.6:
        blocks.append(g.paragraph(kinds, 3, 5))
    if r.random() < 0.35:
        blocks.append("> **Note:** " + g.fill(r.choice(POLICY_SENTENCES)))
    return blocks


def sec_spec(g, num, topic):
    r = g.rng
    vi = r.randrange(len(VEHICLES))
    vehicle, vshort = VEHICLES[vi], VEHICLE_SHORT[vi]
    eq = r.choice(EQUIPMENT)
    blocks = ["### %s %s: %s %s" % (num, r.choice(SECTION_TITLES["spec"]), vshort, eq),
              g.paragraph(["tech"], 3, 5, vehicle=vehicle, vehicle_short=vshort, equipment=eq)]
    rows = [
        ("Dry mass", "%s kg" % "{:,}".format(g._num(80, 9000)), "±%d kg" % g._num(1, 40), r.choice(["Measured at acceptance", "Excludes harness", "Includes brackets"])),
        ("Operating temperature", "%s to %s °C" % (g.slot("temp_lo"), g.slot("temp_hi")), "±%d °C" % g._num(1, 5), "Qualification limits are wider"),
        ("Peak power", "%s W" % g.slot("n_watts"), "±%d %%" % g._num(2, 10), "During deployment"),
        ("Design life", "%s cycles" % g.slot("n_cycles"), "n/a", "Hard limit, no extension"),
        ("Data rate", "%d kbit/s" % g._num(8, 2048), "n/a", "Compressed telemetry"),
        ("Mounting", "%d × M%d bolts" % (r.choice([4, 6, 8, 12]), r.choice([5, 6, 8, 10])), "Torque %d N·m" % g._num(4, 60), "Thread-locker required"),
        ("Supplier", "%s %s Ltd" % (r.choice(LAST), r.choice(["Precision", "Aerospace", "Components", "Instruments"])), "n/a", "Approved vendor list"),
        ("Part number", g.code(vshort.upper()[:3] + "-" + eq.split()[0][:3].upper()), "n/a", "Revision %s" % r.choice("ABCDEFG")),
    ]
    r.shuffle(rows)
    rows = rows[:r.randint(5, 8)]
    table = ["| Parameter | Value | Tolerance | Notes |", "|---|---|---|---|"]
    table += ["| %s | %s | %s | %s |" % row for row in rows]
    blocks.append("\n".join(table))
    blocks.append(g.paragraph(["tech"], 3, 5, vehicle=vehicle, vehicle_short=vshort, equipment=eq))
    lim = ["**Operating limits**", ""]
    for _ in range(r.randint(3, 5)):
        lim.append("- " + g.fill(r.choice(TECH_SENTENCES), vehicle=vehicle, vehicle_short=vshort, equipment=eq))
    blocks.append("\n".join(lim))
    return blocks


def sec_changelog(g, num, topic):
    r = g.rng
    system = r.choice(SYSTEMS)
    blocks = ["### %s %s: %s" % (num, r.choice(SECTION_TITLES["changelog"]), system),
              "%s is maintained by the %s team. Releases are deployed to %s first and to the remaining sites "
              "after a soak period of %s days." % (system, r.choice(TEAMS), r.choice(SITES), g.slot("n_days"))]
    major, minor, patch = r.randint(2, 9), r.randint(0, 12), r.randint(0, 6)
    y = r.randint(2022, 2026)
    entries = []
    for _ in range(r.randint(3, 5)):
        lines = ["#### %s %d.%d.%d (%04d-%02d-%02d)" % (system, major, minor, patch, y, r.randint(1, 12), r.randint(1, 28))]
        for kind in r.sample(list(CHANGE_ITEMS), r.randint(2, 3)):
            lines.append("")
            lines.append("**%s**" % kind)
            for item in r.sample(CHANGE_ITEMS[kind], min(len(CHANGE_ITEMS[kind]), r.randint(1, 3))):
                lines.append("- " + g.fill(item[0].upper() + item[1:]) + ".")
        entries.append("\n".join(lines))
        if r.random() < 0.4:
            minor = max(0, minor - 1)
            patch = r.randint(0, 6)
        else:
            patch = max(0, patch - 1) if patch else r.randint(1, 5)
        y = max(2021, y - r.randint(0, 1))
    blocks.extend(entries)
    return blocks


def sec_code(g, num, topic):
    r = g.rng
    kind = r.randrange(5)
    title = r.choice(SECTION_TITLES["code"])
    system = r.choice(SYSTEMS)
    site = r.choice(SITES)
    sid = re.sub(r"[^a-z0-9]+", "-", site.lower()).strip("-")
    blocks = ["### %s %s (%s)" % (num, title, system)]
    if kind == 0:
        blocks.append("The excerpt below shows the production configuration of %s at %s. Values marked "
                      "`# tuned` were adjusted during the last capacity review." % (system, site))
        blocks.append("```yaml\nservice: %s\nsite: %s\nreplicas: %d\nlisten_port: %d\ntimeouts:\n  connect_s: %d\n  read_s: %d  # tuned\nretention:\n  shift_logs_days: %d\n  telemetry_days: %d\nalerts:\n  route: %s-oncall\n  severity_threshold: %s\nfeature_flags:\n  dry_run_default: %s\n  bulk_import: %s\n```"
                      % (system.lower().replace(" ", "-"), sid, r.randint(2, 8), g._num(7000, 9900), r.choice([2, 5, 10]),
                         r.choice([15, 30, 45, 60]), r.choice([365, 730, 1825]), r.choice([90, 180, 400]),
                         r.choice(TEAMS).lower().replace(" ", "-"), r.choice(["warning", "error", "critical"]),
                         r.choice(["true", "false"]), r.choice(["true", "false"])))
    elif kind == 1:
        limit = g._num(300, 4800)
        blocks.append("Cargo Integrity uses this helper to check that a manifest does not exceed the cradle "
                      "limit before it is submitted to %s." % system)
        blocks.append("```python\nCRADLE_LIMIT_KG = %d\n\n\ndef check_manifest(items):\n    \"\"\"Return (ok, total_kg, problems) for a list of manifest items.\"\"\"\n    total = 0.0\n    problems = []\n    for item in items:\n        mass = float(item.get(\"mass_kg\", 0))\n        if mass <= 0:\n            problems.append(\"%%s: missing or invalid mass\" %% item.get(\"id\", \"?\"))\n        if item.get(\"hazard_class\", 0) > %d:\n            problems.append(\"%%s: hazard class needs review\" %% item[\"id\"])\n        total += mass\n    return (not problems and total <= CRADLE_LIMIT_KG), round(total, 1), problems\n```"
                      % (limit, r.randint(2, 5)))
        blocks.append("The function is deliberately conservative: an item with no mass is treated as an "
                      "error rather than as zero, because unknown mass has caused rework in the past.")
    elif kind == 2:
        blocks.append("Use these commands, in order, when the %s ingest queue at %s stops draining. "
                      "Stop at the first step that resolves the problem." % (system, site))
        blocks.append("```bash\n# 1. Check queue depth\nnolctl queue status --service %s --site %s\n\n# 2. Drain stuck consumers (safe, idempotent)\nnolctl queue rebalance --service %s --max-moves %d\n\n# 3. Restart one worker at a time\nnolctl worker restart --service %s --one-at-a-time --wait %ds\n\n# 4. Escalate if depth is still above %d after 15 minutes\nnolctl page --team %s --severity high\n```"
                      % (system.lower().replace(" ", "-"), sid, system.lower().replace(" ", "-"), r.randint(10, 200),
                         system.lower().replace(" ", "-"), r.choice([30, 60, 90]), g._num(500, 20000),
                         r.choice(TEAMS).lower().replace(" ", "-")))
    elif kind == 3:
        blocks.append("Finance and Fleet Operations share the following query for the monthly %s report."
                      % r.choice(METRICS))
        blocks.append("```sql\nSELECT site,\n       vehicle_class,\n       COUNT(*)                         AS flights,\n       AVG(turnaround_hours)            AS avg_turnaround_h,\n       SUM(CASE WHEN delayed_min > %d THEN 1 ELSE 0 END) AS late_departures\nFROM   flight_summary\nWHERE  departure_date >= DATE '%s'\n  AND  site IN ('%s', '%s')\nGROUP  BY site, vehicle_class\nORDER  BY avg_turnaround_h DESC;\n```"
                      % (r.choice([5, 10, 15, 30]), g.date(2024, 2026), sid, re.sub(r"[^a-z0-9]+", "-", r.choice(SITES).lower()).strip("-")))
    else:
        cust = r.choice(CUSTOMERS)
        blocks.append("A minimal manifest entry, as accepted by the %s API, looks like this:" % system)
        blocks.append("```json\n{\n  \"consignment_id\": \"%s\",\n  \"customer\": \"%s\",\n  \"site\": \"%s\",\n  \"items\": [\n    {\"id\": \"%s\", \"mass_kg\": %.1f, \"hazard_class\": %d, \"position\": \"%s\"},\n    {\"id\": \"%s\", \"mass_kg\": %.1f, \"hazard_class\": %d, \"position\": \"%s\"}\n  ],\n  \"requested_departure\": \"%s\"\n}\n```"
                      % (g.code("CN"), cust, sid, g.code("IT"), g._num(10, 9000) / 10.0, r.randint(0, 4),
                         r.choice(["A1", "A2", "B1", "B3", "C2"]), g.code("IT"), g._num(10, 9000) / 10.0,
                         r.randint(0, 4), r.choice(["A1", "B2", "C1", "C3"]), g.date(2025, 2026)))
        blocks.append("Positions refer to the cradle grid of the target vehicle. Items without a position are "
                      "placed by the loading planner and confirmed during integration.")
    return blocks


def sec_meeting(g, num, topic):
    r = g.rng
    team = r.choice(TEAMS)
    people = []
    while len(people) < r.randint(4, 7):
        p = g.person()
        if p not in people:
            people.append(p)
    blocks = ["### %s %s: %s (%s)" % (num, r.choice(SECTION_TITLES["meeting"]), team, g.date()),
              "**Attendees:** %s. **Chair:** %s. **Location:** %s, room %s%d."
              % (", ".join(people), people[0], r.choice(SITES), r.choice("ABCDE"), r.randint(1, 40))]
    agenda = ["**Agenda**", ""]
    for i in range(r.randint(3, 5)):
        agenda.append("%d. %s" % (i + 1, g.fill(r.choice([
            "Review of the {metric} for the last month", "Status of the {system} upgrade",
            "Staffing for the {site} campaign", "Supplier issues with {equipment} deliveries",
            "Feedback from {customer}", "Open audit actions", "Training plan for {month}",
            "Budget forecast", "Any other business"]))))
    blocks.append("\n".join(agenda))
    blocks.append(g.paragraph(["narrative"], 4, 7, person=people[r.randrange(len(people))]))
    blocks.append(g.paragraph(["narrative"], 3, 5))
    dec = ["**Decisions**", ""]
    for _ in range(r.randint(2, 4)):
        dec.append("- " + g.fill(r.choice([
            "Proceed with the {system} upgrade at {site} in {month}.",
            "Defer the {equipment} checklist change until the supplier responds.",
            "Approve an additional {money} for spare {equipment} stock.",
            "Extend the night-shift trial by {n_weeks} weeks.",
            "Ask {team} to own the escalation path for late customer changes.",
            "Close the open risk on {vehicle_short} maintenance windows.",
            "Adopt the shared inspection template at all sites."])))
    blocks.append("\n".join(dec))
    act = ["| # | Action | Owner | Due |", "|---|---|---|---|"]
    for i in range(r.randint(3, 5)):
        act.append("| %d | %s | %s | %s |" % (i + 1, g.fill(r.choice([
            "Circulate revised {system} rollout plan", "Confirm {equipment} delivery dates with supplier",
            "Draft customer note for {customer}", "Update training matrix for {team}",
            "Book readiness review room at {site}", "Collect {metric} data for next meeting",
            "Check budget headroom with Finance"])), r.choice(people), g.date(2025, 2026)))
    blocks.append("\n".join(act))
    return blocks


def sec_incident(g, num, topic):
    r = g.rng
    site = r.choice(SITES)
    inc = g.code("INC")
    blocks = ["### %s %s %s at %s" % (num, r.choice(SECTION_TITLES["incident"]), inc, site)]
    cause = g.fill(r.choice(INCIDENT_CAUSES), site=site)
    blocks.append("**Severity:** %s. **Date:** %s. **Reported by:** %s (%s)."
                  % (r.choice(["SEV-2", "SEV-3", "SEV-4"]), g.date(), g.person(), r.choice(TEAMS)))
    blocks.append("This review covers an event at %s that was traced to %s. No one was injured, and %s."
                  % (site, cause, r.choice(["no customer cargo was damaged", "the affected flight departed %s minutes late" % g.slot("n_min"),
                                           "one consignment had to be re-inspected", "the issue was contained within a single shift"])))
    tl = ["| Time | Event |", "|---|---|"]
    h = r.randint(0, 20)
    m = r.randint(0, 59)
    for ev in r.sample(["First alert received by the operations bridge", "On-call engineer acknowledged the page",
                        "Work stopped on the affected bay", "Duty manager declared an incident",
                        "Workaround applied and verified", "Normal operations resumed",
                        "Customer informed by Customer Assurance", "Affected items moved to quarantine",
                        "Incident closed pending review"], r.randint(4, 7)):
        tl.append("| %02d:%02d | %s |" % (h % 24, m, ev))
        m += r.randint(3, 40)
        h += m // 60
        m %= 60
    blocks.append("\n".join(tl))
    blocks.append("**Root cause.** " + g.paragraph(["tech", "ops"], 2, 4, site=site))
    rem = ["**Remediation**", ""]
    for x in r.sample(REMEDIATIONS, r.randint(2, 4)):
        rem.append("- " + g.fill(x, site=site))
    blocks.append("\n".join(rem))
    return blocks


def sec_faq(g, num, topic):
    r = g.rng
    blocks = ["### %s %s about %s" % (num, r.choice(SECTION_TITLES["faq"]), topic)]
    for q, a in r.sample(FAQ_ITEMS, r.randint(3, 5)):
        system, site, team, eq = g.slot("system"), g.slot("site"), g.slot("team"), g.slot("equipment")
        blocks.append("**Q: %s**\n\n%s" % (g.fill(q, system=system, site=site, team=team, equipment=eq),
                                         g.fill(a, system=system, site=site, team=team, equipment=eq)))
    return blocks


def sec_kpi(g, num, topic):
    r = g.rng
    year = r.randint(2023, 2026)
    blocks = ["### %s %s, %d" % (num, r.choice(SECTION_TITLES["kpi"]), year),
              "The table below shows selected indicators reported to the operations board. Targets are set "
              "annually and are not adjusted mid-year."]
    sites = r.sample(SITES, r.randint(3, 5))
    metric = r.choice(METRICS)
    t = ["| Site | Q1 | Q2 | Q3 | Q4 | Target |", "|---|---|---|---|---|---|"]
    for s in sites:
        base = r.uniform(60, 98)
        vals = ["%.1f" % min(99.9, base + r.uniform(-4, 4)) for _ in range(4)]
        t.append("| %s | %s | %s | %s | %s | %.1f |" % (s, vals[0], vals[1], vals[2], vals[3], min(99.5, base + 2)))
    blocks.append("*Metric: %s (percent).*\n\n" % metric + "\n".join(t))
    blocks.append(g.paragraph(["narrative", "ops"], 3, 5))
    return blocks


SECTION_BUILDERS = [(sec_policy, 30), (sec_spec, 14), (sec_changelog, 9), (sec_code, 10), (sec_meeting, 13),
                    (sec_incident, 9), (sec_faq, 8), (sec_kpi, 7)]


def pick_builder(rng):
    total = sum(w for _, w in SECTION_BUILDERS)
    x = rng.uniform(0, total)
    for fn, w in SECTION_BUILDERS:
        x -= w
        if x <= 0:
            return fn
    return SECTION_BUILDERS[-1][0]


# --------------------------------------------------------------------------
# Document assembly
# --------------------------------------------------------------------------

def front_matter(g):
    r = g.rng
    blocks = ["# %s: Operations and Employee Handbook" % COMPANY,
              "*Document %s, revision %d. Internal use only. Owner: Corporate Operations Office.*"
              % (g.code("HB"), r.randint(14, 31)),
              "## About this handbook",
              "%s (%s) moves cargo between the ground and low orbit for commercial, scientific and government "
              "customers. The company operates %d sites, a mixed fleet of tugs, freighters, shuttles and "
              "landers, and a software stack built largely in-house. This handbook collects the policies, "
              "technical references, working notes and history that new and existing staff need in one place."
              % (COMPANY, SHORT, len(SITES)),
              "The handbook is organised into chapters by subject. Each chapter mixes policy text with "
              "specifications, release notes, meeting minutes and incident reviews, because that is how the "
              "information is actually used on shift. Where a rule and a reference table disagree, the rule "
              "applies and the table should be corrected through the documentation desk.",
              "## Sites at a glance"]
    t = ["| Site | Role | Opened | Headcount | Pads/Bays |", "|---|---|---|---|---|"]
    roles = ["Headquarters and launch site", "Integration hub", "Orbital relay", "Coastal launch site",
             "Spares depot", "Recovery base", "Heavy cargo yard", "Crew operations", "Engineering annex",
             "Training centre"]
    for s, role in zip(SITES, roles):
        t.append("| %s | %s | %d | %d | %d |" % (s, role, r.randint(2012, 2024), g._num(40, 1400), r.randint(2, 24)))
    blocks.append("\n".join(t))
    blocks.append("## Fleet overview")
    blocks.append(" ".join("The %s is used for %s." % (v, u) for v, u in zip(VEHICLES, [
        "short transfers between parking orbits", "bulk cargo to the relay stations", "crew rotation",
        "surface delivery at the recovery bases", "high-energy transfers", "in-orbit refuelling",
        "close inspection of customer payloads", "retrieval of returning capsules"])))
    return blocks


def appendix(g):
    r = g.rng
    blocks = ["## Appendix A: Glossary",
              "Terms are listed alphabetically. Where a term has a different meaning in a customer contract, "
              "the contract definition applies to that customer's work."]
    for term, definition in sorted(GLOSSARY):
        blocks.append("**%s.** %s" % (term, definition))
    blocks.append("## Appendix B: Handbook revision history")
    t = ["| Revision | Date | Author | Summary |", "|---|---|---|---|"]
    for rev in range(r.randint(10, 14), 0, -1):
        t.append("| %d | %s | %s | %s |" % (rev, g.date(2018 + rev // 3, 2018 + rev // 3), g.person(), g.fill(r.choice([
            "Updated {topic} chapter after the {site} audit", "Added release notes for {system}",
            "Corrected specification table for the {vehicle_short} {equipment}", "Reworded overtime rules",
            "Added incident reviews from the last quarter", "New glossary entries", "Restructured chapters",
            "Clarified visitor rules at {site}"]), topic=r.choice(TOPICS).lower())))
    blocks.append("\n".join(t))
    blocks.append("## Appendix C: Contacts")
    c = ["| Team | Contact | Location |", "|---|---|---|"]
    for team in TEAMS:
        c.append("| %s | %s | %s |" % (team, g.person(), r.choice(SITES)))
    blocks.append("\n".join(c))
    blocks.append("*End of handbook.*")
    return blocks


def build():
    rng = random.Random(SEED)
    g = Gen(rng)
    front = front_matter(g)
    tail = appendix(g)
    fixed_len = len("\n\n".join(front + tail)) + sum(len(f["text"]) + 2 for f in FACTS)

    body = []
    chapter = 0
    topics = list(TOPICS)
    while True:
        chapter += 1
        topic = topics[(chapter - 1) % len(topics)]
        part = "" if chapter <= len(topics) else ", Part II"
        chap = ["## Chapter %d: %s%s" % (chapter, topic, part), g.fill(rng.choice(INTROS), topic=topic, topic_lc=topic.lower())]
        n_sections = rng.randint(4, 6)
        done = False
        for s in range(1, n_sections + 1):
            chap.extend(pick_builder(rng)(g, "%d.%d" % (chapter, s), topic))
            if fixed_len + len("\n\n".join(body + chap)) >= TARGET_CHARS:
                done = True
                break
        body.extend(chap)
        if done:
            break

    blocks = front + body + tail

    # Insert facts before plain-paragraph blocks near their target position.
    total = len("\n\n".join(blocks))
    starts, pos = [], 0
    for b in blocks:
        starts.append(pos)
        pos += len(b) + 2

    def is_plain(b):
        return not re.match(r"^(#|\||```|- |\d+\. |\*\*|>|\*)", b)

    inserts = []
    for f in FACTS:
        want = f["target_pct"] / 100.0 * total
        idx = next(i for i in range(len(blocks)) if starts[i] >= want and is_plain(blocks[i]))
        inserts.append((idx, f))
    for idx, f in sorted(inserts, key=lambda x: -x[0]):
        blocks.insert(idx, f["text"])

    doc = "\n\n".join(blocks) + "\n"
    return doc


def main():
    doc = build()
    low = doc.lower()
    facts_out = []
    for f in FACTS:
        # The canonical answer must appear exactly once; alternates (spelling
        # variants a model might produce) may appear at most once.
        for i, a in enumerate(f["answers"]):
            n = low.count(a.lower())
            assert n == 1 if i == 0 else n <= 1, "answer %r appears %d times" % (a, n)
        p = low.index(f["answers"][0].lower())
        facts_out.append({"id": f["id"], "question": f["question"], "answers": f["answers"],
                          "position_pct": round(100.0 * p / len(doc), 1)})

    with open(os.path.join(HERE, "document.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    with open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(facts_out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    digest = hashlib.sha256(doc.encode("utf-8")).hexdigest()
    with open(os.path.join(HERE, "document.sha256"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("%s  document.md\n" % digest)

    chars = len(doc)
    words = len(doc.split())
    print("document.md: %d characters, %d words, %d lines" % (chars, words, doc.count("\n")))
    print("estimated tokens: %d (chars/%.1f), %d (words x 1.33)" % (round(chars / CHARS_PER_TOKEN), CHARS_PER_TOKEN, round(words * 1.33)))
    print("sha256: %s" % digest)
    for f in facts_out:
        print("  %-4s at %5.1f%%  %s" % (f["id"], f["position_pct"], f["answers"][0]))


if __name__ == "__main__":
    main()

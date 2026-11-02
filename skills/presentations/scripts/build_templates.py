"""Build the five sample decks in assets/ from deck.py. All data is fictional.

Run the command in the presentations SKILL.md after changing BRAND.md or deck.py.
"""

from pathlib import Path

from deck import Deck

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CONTACT = "linkedin.com/in/<your-profile>"


def status_report() -> Deck:
    deck = Deck("status-report", title="Status report")
    deck.cover(
        "OTIF is back above target after the carrier change", "Logistics data, week 44", "<date>"
    )
    deck.bullets(
        "Summary: on track, one decision needed this week",
        [
            "OTIF at 94%, above the 92% target for the first time since July",
            "Late deliveries down 18% after moving routes away from Carrier B",
            "Decision needed: renew or end the Carrier B contract by <date>",
        ],
        label="Summary",
    )
    deck.kpis(
        "Three of four KPIs are on target",
        [
            {
                "label": "OTIF",
                "value": "94%",
                "comparison": "Target 92%, +3 pp vs last week",
                "highlight": True,
            },
            {"label": "Late deliveries", "value": "312", "comparison": "-18% vs last week"},
            {"label": "Orders", "value": "5,210", "comparison": "Flat vs last week"},
            {"label": "Data freshness", "value": "26 h", "comparison": "Target 24 h"},
        ],
        label="KPIs",
    )
    deck.bar_chart(
        "Carrier B still causes most late deliveries",
        ["Carrier A", "Carrier B", "Carrier C", "Own fleet"],
        [42, 188, 61, 21],
        1,
        "Source: TMS, late deliveries in week 44 (fictional data)",
        label="What changed",
    )
    deck.table(
        "Two risks need an owner this week",
        ["Risk", "Impact", "Owner", "Due"],
        [
            ["Carrier B contract ends", "OTIF -2 pp", "<owner>", "<date>"],
            ["WMS data arrives late", "Report delayed", "<owner>", "<date>"],
        ],
        "Source: project risk log",
        label="Risks",
    )
    deck.closing(
        "Decide on the Carrier B contract by <date>",
        [
            "Owner: <owner>",
            "Next status report: <date>",
        ],
        CONTACT,
    )
    return deck


def kickoff() -> Deck:
    deck = Deck("kickoff", title="Kickoff")
    deck.cover("A daily OTIF view by carrier in eight weeks", "Project kickoff", "<date>")
    deck.bullets(
        "The goal: renegotiate carrier contracts with daily evidence",
        [
            "Daily OTIF by carrier, region and customer segment",
            "One trusted number, reconciled with the current monthly report",
            "Used by logistics planning and procurement",
        ],
        label="Goal",
    )
    deck.table(
        "Scope covers deliveries; returns stay out",
        ["In scope", "Out of scope"],
        [
            ["Deliveries from the ERP and TMS", "Returns and reverse logistics"],
            ["Daily refresh", "Real-time tracking"],
            ["Dashboard for planning", "Customer-facing reports"],
        ],
        label="Scope",
    )
    deck.divider("Approach", "Part 2")
    deck.table(
        "Four phases, each ending in something usable",
        ["Phase", "Weeks", "Delivers"],
        [
            ["Discovery", "1 to 2", "Sources profiled, metric definition signed"],
            ["Build", "3 to 5", "dbt models with tests"],
            ["Validate", "6", "Reconciliation with the monthly report"],
            ["Launch", "7 to 8", "Dashboard and handover"],
        ],
        label="Phases",
    )
    deck.table(
        "Each decision has one owner",
        ["Role", "Person", "Decides"],
        [
            ["Sponsor", "<name>", "Scope and priorities"],
            ["Business owner", "<name>", "Metric definitions"],
            ["Tech lead", "Vinicius Valiati", "Architecture and data model"],
        ],
        label="Roles",
    )
    deck.closing(
        "Next step: source access by <date>",
        [
            "Owner: <name>",
            "Discovery starts the day after access is granted",
        ],
        CONTACT,
    )
    return deck


def technical() -> Deck:
    deck = Deck("technical", title="Technical talk")
    deck.cover(
        "From monthly spreadsheets to daily, tested OTIF", "A dbt and Airflow case study", "<date>"
    )
    deck.bullets(
        "Planning saw OTIF once a month, too late to act",
        [
            "Numbers came from a spreadsheet rebuilt by hand every month",
            "Two teams reported two different OTIF values",
            "No way to see which carrier caused the misses",
        ],
        label="Problem",
    )
    deck.bullets(
        "Raw extracts become one tested mart every morning",
        [
            "Airflow lands ERP and TMS extracts daily",
            "dbt staging cleans and renames; marts join deliveries and orders",
            "Tests on grain, keys and reconciliation run on every build",
        ],
        label="Architecture",
    )
    deck.code(
        "Incremental with a justified 45-day lookback",
        "\n".join(
            [
                "{% if is_incremental() %}",
                "where _loaded_at >= (",
                "    select dateadd('day', -45, max(_loaded_at))",
                "    from {{ this }}",
                ")",
                "{% endif %}",
            ]
        ),
        "Profiling: 99.9% of rows arrive within 30 days, max seen 41",
        label="Key decision",
    )
    deck.big_numbers(
        "Decisions now take one day instead of a month",
        [{"value": "1 day", "caption": "from data to decision, down from 30"}],
    )
    deck.bullets(
        "Next: freshness checks, then a semantic layer",
        [
            "Add freshness checks once the load schedule is stable",
            "Expose the metric in a semantic layer",
        ],
        label="Next",
    )
    deck.closing("Thank you", ["Code and docs: github.com/<your-user>/<repo>"], CONTACT)
    return deck


def pitch() -> Deck:
    deck = Deck("pitch", title="Pitch")
    deck.cover("Every late delivery has a cause you can see", "<proposal name>", "<date>")
    deck.bullets(
        "Late deliveries are found a month after they happen",
        [
            "Monthly reports explain the past, not the next shipment",
        ],
        label="Problem",
    )
    deck.bullets(
        "Most misses come from a few routes and carriers",
        [
            "In the pilot, two carriers caused 70% of late deliveries",
        ],
        label="Insight",
    )
    deck.big_numbers(
        "The pilot cut late deliveries and lifted OTIF above target",
        [
            {"value": "-18%", "caption": "late deliveries in the first month"},
            {"value": "+3 pp", "caption": "OTIF, back above target"},
        ],
    )
    deck.closing(
        "Approve a 3-month rollout to all regions",
        [
            "Owner: <name>",
            "Decision by <date>",
        ],
        CONTACT,
    )
    return deck


def one_on_one() -> Deck:
    deck = Deck("one-on-one", title="1:1")
    deck.cover("Our 1:1", "<name> and Vinicius", "<date>")
    deck.questions(
        "How are things going?",
        [
            "What gave you energy this month, and what drained it?",
            "Is there anything blocking you that I can remove?",
        ],
        label="Check-in",
    )
    deck.bullets(
        "Wins worth recognizing",
        [
            "<specific win, with the impact it had>",
        ],
        label="Wins",
    )
    deck.bullets(
        "Feedback: one thing to keep, one to change",
        [
            "Keep: <behavior>, for example <situation>, which led to <impact>",
            "Change: <behavior>, for example <situation>; next time, <suggestion>",
        ],
        label="Feedback",
    )
    deck.questions(
        "Let's pick one growth goal for next quarter",
        [
            "Where do you want to be in a year?",
            "What should we try next quarter to get closer?",
        ],
        label="Growth",
    )
    deck.bullets(
        "We leave with actions, owners and dates", ["<action>, <owner>, <date>"], label="Agreements"
    )
    return deck


def main() -> None:
    for name, build in (
        ("status-report", status_report),
        ("kickoff", kickoff),
        ("technical", technical),
        ("pitch", pitch),
        ("one-on-one", one_on_one),
    ):
        print(build().save(ASSETS / f"{name}.pptx"))


if __name__ == "__main__":
    main()

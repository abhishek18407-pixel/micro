"""Validate data/deals.json and data/demo_call_5.json against CONTRACT.md schema and project rules."""

import datetime
import json
import os
import sys
from typing import Any, Dict, List, Set, Tuple


def count_words(text: str) -> int:
    """Return the word count of a string."""
    return len(text.strip().split())


def validate_call(
    call: Dict[str, Any],
    expected_call_no: int,
    deal_label: str,
    previous_date: str = None,
) -> List[str]:
    """Validate a single call object."""
    errors = []
    required_call_keys = ["call_no", "date", "participants", "transcript"]
    for key in required_call_keys:
        if key not in call:
            errors.append(f"[{deal_label}] Call {expected_call_no} missing required field '{key}'")

    call_no = call.get("call_no")
    if call_no != expected_call_no:
        errors.append(
            f"[{deal_label}] Call expected call_no {expected_call_no}, got {call_no}"
        )

    date_str = call.get("date")
    if not isinstance(date_str, str):
        errors.append(f"[{deal_label}] Call {expected_call_no} date must be a string")
    else:
        try:
            call_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if previous_date:
                prev_dt = datetime.datetime.strptime(previous_date, "%Y-%m-%d")
                if call_dt < prev_dt:
                    errors.append(
                        f"[{deal_label}] Call {expected_call_no} date ({date_str}) is earlier than previous call ({previous_date})"
                    )
        except ValueError:
            errors.append(
                f"[{deal_label}] Call {expected_call_no} date '{date_str}' not in YYYY-MM-DD format"
            )

    participants = call.get("participants")
    if not isinstance(participants, list) or len(participants) < 2:
        errors.append(
            f"[{deal_label}] Call {expected_call_no} participants must be a list with at least 2 people"
        )
    elif not all(isinstance(p, str) and p.strip() for p in participants):
        errors.append(
            f"[{deal_label}] Call {expected_call_no} participants contains empty or non-string values"
        )

    transcript = call.get("transcript")
    if not isinstance(transcript, str) or not transcript.strip():
        errors.append(f"[{deal_label}] Call {expected_call_no} transcript is empty or not a string")
    else:
        words = count_words(transcript)
        if words < 150 or words > 300:
            errors.append(
                f"[{deal_label}] Call {expected_call_no} transcript word count is {words} (required: 150-300 words)"
            )

    return errors


def validate_deals_file(filepath: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Validate data/deals.json file."""
    errors = []
    stats = {
        "deals_count": 0,
        "total_calls": 0,
        "outcomes": {"won": 0, "lost": 0, "open": 0},
        "deals_summary": [],
    }

    if not os.path.exists(filepath):
        return False, [f"File not found: {filepath}"], stats

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            deals = json.load(f)
    except Exception as e:
        return False, [f"Failed to parse JSON in {filepath}: {e}"], stats

    if not isinstance(deals, list):
        return False, [f"Top-level element in {filepath} must be a list of deals"], stats

    if len(deals) != 6:
        errors.append(f"Expected exactly 6 deals, found {len(deals)}")

    seen_ids: Set[str] = set()
    required_deal_keys = ["id", "company", "value", "outcome", "calls"]
    demo_deal_found = False

    for idx, deal in enumerate(deals):
        deal_label = f"Deal #{idx + 1}"
        if not isinstance(deal, dict):
            errors.append(f"{deal_label} is not a JSON object")
            continue

        deal_id = deal.get("id")
        company = deal.get("company", f"Unknown-{idx}")
        deal_label = f"{company} ({deal_id})"

        # Check required keys
        for key in required_deal_keys:
            if key not in deal:
                errors.append(f"[{deal_label}] Missing required field '{key}'")

        # Unique ID check
        if not isinstance(deal_id, str) or not deal_id.strip():
            errors.append(f"[{deal_label}] Invalid or empty 'id'")
        elif deal_id in seen_ids:
            errors.append(f"[{deal_label}] Duplicate deal id '{deal_id}'")
        else:
            seen_ids.add(deal_id)

        # Deal value check: $40,000 to $400,000
        val = deal.get("value")
        if not isinstance(val, (int, float)):
            errors.append(f"[{deal_label}] 'value' must be a number, got {type(val).__name__}")
        elif val < 40000 or val > 400000:
            errors.append(
                f"[{deal_label}] Value ${val} out of expected range ($40,000 - $400,000)"
            )

        # Outcome check
        outcome = deal.get("outcome")
        if outcome not in ["won", "lost", None]:
            errors.append(
                f"[{deal_label}] Invalid outcome '{outcome}'. Expected 'won', 'lost', or null"
            )
        else:
            if outcome == "won":
                stats["outcomes"]["won"] += 1
            elif outcome == "lost":
                stats["outcomes"]["lost"] += 1
            else:
                stats["outcomes"]["open"] += 1

        # Calls check
        calls = deal.get("calls")
        if not isinstance(calls, list):
            errors.append(f"[{deal_label}] 'calls' must be a list")
            continue

        if company == "Northwind Logistics":
            demo_deal_found = True
            if len(calls) != 4:
                errors.append(
                    f"[{deal_label}] Demo deal 'Northwind Logistics' must have exactly 4 calls in deals.json (call 5 is separate), found {len(calls)}"
                )
            if outcome is not None:
                errors.append(
                    f"[{deal_label}] Demo deal 'Northwind Logistics' outcome must be null (open deal), found '{outcome}'"
                )
        else:
            if len(calls) < 4 or len(calls) > 5:
                errors.append(
                    f"[{deal_label}] Expected 4-5 calls, found {len(calls)}"
                )

        stats["total_calls"] += len(calls)

        prev_date = None
        call_words_list = []
        for call_idx, call in enumerate(calls):
            expected_call_no = call_idx + 1
            call_errors = validate_call(
                call,
                expected_call_no=expected_call_no,
                deal_label=deal_label,
                previous_date=prev_date,
            )
            errors.extend(call_errors)
            if isinstance(call, dict) and "date" in call:
                prev_date = call["date"]
            if isinstance(call, dict) and "transcript" in call:
                call_words_list.append(count_words(call["transcript"]))

        stats["deals_summary"].append({
            "id": deal_id,
            "company": company,
            "value": val,
            "outcome": outcome if outcome else "open",
            "calls_count": len(calls),
            "word_counts": call_words_list,
        })

    stats["deals_count"] = len(deals)

    if not demo_deal_found:
        errors.append("Demo deal 'Northwind Logistics' was not found in deals.json")

    # Check 2 won, 2 lost, 2 open
    if stats["outcomes"]["won"] != 2:
        errors.append(f"Expected exactly 2 won deals, found {stats['outcomes']['won']}")
    if stats["outcomes"]["lost"] != 2:
        errors.append(f"Expected exactly 2 lost deals, found {stats['outcomes']['lost']}")
    if stats["outcomes"]["open"] != 2:
        errors.append(f"Expected exactly 2 open deals (outcome null), found {stats['outcomes']['open']}")

    return len(errors) == 0, errors, stats


def validate_demo_call_5(filepath: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Validate data/demo_call_5.json."""
    errors = []
    stats = {}

    if not os.path.exists(filepath):
        return False, [f"Demo call file not found: {filepath}"], stats

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            call = json.load(f)
    except Exception as e:
        return False, [f"Failed to parse JSON in {filepath}: {e}"], stats

    if not isinstance(call, dict):
        return False, [f"Top-level element in {filepath} must be a dict"], stats

    call_errors = validate_call(call, expected_call_no=5, deal_label="Demo Call 5")
    errors.extend(call_errors)

    transcript = call.get("transcript", "")
    words = count_words(transcript)
    stats["word_count"] = words
    stats["participants"] = call.get("participants", [])
    stats["date"] = call.get("date")

    # Content checks for demo relevance
    lower_t = transcript.lower()
    if "cfo" not in lower_t and "sarah" not in lower_t:
        errors.append("Demo call 5 must involve CFO Sarah Jenkins")
    if "soc2" not in lower_t and "security" not in lower_t:
        errors.append("Demo call 5 must address the promised security audit/SOC2 report")
    if "pilot" not in lower_t and "phase" not in lower_t and "budget" not in lower_t:
        errors.append("Demo call 5 must address CFO pricing/budget concern or phased pilot")

    return len(errors) == 0, errors, stats


def main():
    print("=" * 65)
    print("DEAL INTELLIGENCE AGENT - DATA VALIDATION SUITE")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    deals_path = os.path.join(base_dir, "deals.json")
    demo_call_path = os.path.join(base_dir, "demo_call_5.json")

    print(f"Checking {deals_path}...")
    deals_ok, deals_errors, deals_stats = validate_deals_file(deals_path)

    print(f"Checking {demo_call_path}...")
    demo_ok, demo_errors, demo_stats = validate_demo_call_5(demo_call_path)

    print("\n" + "-" * 65)
    print("DEALS SUMMARY TABLE")
    print("-" * 65)
    print(f"{'ID':<8} {'Company':<28} {'Value':<10} {'Outcome':<8} {'Calls':<6} {'Word Counts'}")
    print("-" * 65)
    for d in deals_stats.get("deals_summary", []):
        words_str = ", ".join(str(w) for w in d["word_counts"])
        print(f"{d['id']:<8} {d['company']:<28} ${d['value']:<9} {d['outcome']:<8} {d['calls_count']:<6} [{words_str}]")

    print("-" * 65)
    print(f"Total Deals: {deals_stats.get('deals_count', 0)}")
    print(f"Total Calls in deals.json: {deals_stats.get('total_calls', 0)}")
    print(f"Outcomes: {deals_stats.get('outcomes', {})}")

    if demo_ok:
        print("\nDEMO CALL 5 DETAILS:")
        print(f"  Date: {demo_stats.get('date')}")
        print(f"  Participants: {', '.join(demo_stats.get('participants', []))}")
        print(f"  Word count: {demo_stats.get('word_count')} words")

    all_errors = deals_errors + demo_errors
    print("\n" + "=" * 65)
    if all_errors:
        print(f"VALIDATION FAILED ({len(all_errors)} errors):")
        for err in all_errors:
            print(f"  [X] {err}")
        print("=" * 65)
        sys.exit(1)
    else:
        print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY (Exit Code 0)")
        print("=" * 65)
        sys.exit(0)


if __name__ == "__main__":
    main()

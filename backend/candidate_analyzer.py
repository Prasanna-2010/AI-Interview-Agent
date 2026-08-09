import json
from pathlib import Path


# Find the project root
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    """Load a JSON file from the data directory."""
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_candidates():
    """Load all candidate profiles."""
    data = load_json("candidates.json")
    return data["candidates"]


def load_curriculum():
    """Load the curriculum."""
    return load_json("curriculum.json")


def get_candidate(candidate_id):
    """Find a candidate by ID."""

    candidates = load_candidates()

    for candidate in candidates:
        if candidate["member"]["id"] == candidate_id:
            return candidate

    return None


def analyze_candidate(candidate_id):
    """
    Analyze a candidate's learning journey.

    Returns:
        A structured learning profile.
    """

    candidate = get_candidate(candidate_id)

    if candidate is None:
        raise ValueError(f"Candidate {candidate_id} not found.")

    member = candidate["member"]
    missions = candidate["missions"]

    strengths = []
    weak_topics = []
    challenging_topics = []
    skipped_topics = []

    total_attempts = 0

    for mission in missions:

        title = mission["title"]
        attempts = mission.get("attempts", 0)
        passed = mission.get("passed")
        skipped = mission.get("skipped", False)

        total_attempts += attempts

        # Skipped topic
        if skipped:
            skipped_topics.append({
                "day": mission["day"],
                "title": title
            })
            continue

        # Failed topic
        if passed is False:
            weak_topics.append({
                "day": mission["day"],
                "title": title,
                "attempts": attempts
            })
            continue

        # Passed on first attempt
        if passed is True and attempts == 1:
            strengths.append({
                "day": mission["day"],
                "title": title,
                "attempts": attempts
            })

        # Passed but required multiple attempts
        elif passed is True and attempts >= 3:
            challenging_topics.append({
                "day": mission["day"],
                "title": title,
                "attempts": attempts
            })

    return {
        "candidate": {
            "id": member["id"],
            "name": member["name"],
            "job_role": member["jobRole"],
            "years_experience": member["yearsExperience"],
            "education": member["education"],
            "status": member["status"]
        },

        "learning_profile": {
            "strengths": strengths,
            "challenging_topics": challenging_topics,
            "weak_topics": weak_topics,
            "skipped_topics": skipped_topics,
            "total_attempts": total_attempts
        }
    }


if __name__ == "__main__":

    candidate_id = "CAND-010"

    profile = analyze_candidate(candidate_id)

    print(json.dumps(profile, indent=4))
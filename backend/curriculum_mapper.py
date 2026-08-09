import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_curriculum():
    """Load the complete curriculum."""

    file_path = DATA_DIR / "curriculum.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_day(day_number):
    """Return curriculum information for a specific day."""

    curriculum = load_curriculum()

    for day in curriculum["days"]:
        if day["day"] == day_number:
            return day

    return None


def enrich_topic(topic):
    """
    Add curriculum information to a candidate topic.
    """

    day_number = topic["day"]

    curriculum_day = get_day(day_number)

    if curriculum_day is None:
        return topic

    return {
        "day": day_number,
        "title": curriculum_day["title"],
        "type": curriculum_day["type"],
        "tools": curriculum_day["tools"],
        "objectives": curriculum_day["objectives"]
    }


def map_candidate_topics(candidate_profile):
    """
    Connect candidate learning signals
    with curriculum information.
    """

    learning_profile = candidate_profile["learning_profile"]

    result = {
        "strengths": [],
        "challenging_topics": [],
        "weak_topics": [],
        "skipped_topics": []
    }

    for topic in learning_profile["strengths"]:
        result["strengths"].append(enrich_topic(topic))

    for topic in learning_profile["challenging_topics"]:
        result["challenging_topics"].append(enrich_topic(topic))

    for topic in learning_profile["weak_topics"]:
        result["weak_topics"].append(enrich_topic(topic))

    for topic in learning_profile["skipped_topics"]:
        result["skipped_topics"].append(enrich_topic(topic))

    return result


if __name__ == "__main__":

    from candidate_analyzer import analyze_candidate

    candidate_id = "CAND-010"

    profile = analyze_candidate(candidate_id)

    mapped_topics = map_candidate_topics(profile)

    print(json.dumps(mapped_topics, indent=4))
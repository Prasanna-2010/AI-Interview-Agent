from candidate_analyzer import analyze_candidate
from curriculum_mapper import map_candidate_topics


def calculate_priority(topic, category):
    """
    Calculate interview priority for a topic.

    Higher score = more important to assess.
    """

    score = 0

    attempts = topic.get("attempts", 0)

    # ------------------------------------------------
    # 1. Category-based priority
    # ------------------------------------------------

    if category == "weak":
        score += 10

    elif category == "challenging":
        score += 6

    elif category == "skipped":
        score += 3

    elif category == "strength":
        score += 1

    # ------------------------------------------------
    # 2. Attempt-based priority
    # ------------------------------------------------

    if attempts >= 5:
        score += 5

    elif attempts >= 3:
        score += 3

    elif attempts == 2:
        score += 1

    # ------------------------------------------------
    # 3. Capstone gets a small additional weight
    # ------------------------------------------------

    if "Capstone" in topic["title"]:
        score += 1

    return score


def generate_priority_list(candidate_id):

    # Get candidate learning profile
    profile = analyze_candidate(candidate_id)

    # Map topics to curriculum
    mapped_topics = map_candidate_topics(profile)

    prioritized_topics = []

    # -----------------------------------------------
    # Weak topics
    # -----------------------------------------------

    for topic in mapped_topics["weak_topics"]:

        score = calculate_priority(topic, "weak")

        prioritized_topics.append({
            "day": topic["day"],
            "title": topic["title"],
            "category": "weak",
            "priority_score": score,
            "reason": "Candidate did not pass this topic"
        })

    # -----------------------------------------------
    # Challenging topics
    # -----------------------------------------------

    for topic in mapped_topics["challenging_topics"]:

        score = calculate_priority(topic, "challenging")

        prioritized_topics.append({
            "day": topic["day"],
            "title": topic["title"],
            "category": "challenging",
            "priority_score": score,
            "reason": "Candidate required multiple attempts"
        })

    # -----------------------------------------------
    # Skipped topics
    # -----------------------------------------------

    for topic in mapped_topics["skipped_topics"]:

        score = calculate_priority(topic, "skipped")

        prioritized_topics.append({
            "day": topic["day"],
            "title": topic["title"],
            "category": "skipped",
            "priority_score": score,
            "reason": "Candidate skipped this topic"
        })

    # -----------------------------------------------
    # Strengths
    # -----------------------------------------------

    for topic in mapped_topics["strengths"]:

        score = calculate_priority(topic, "strength")

        prioritized_topics.append({
            "day": topic["day"],
            "title": topic["title"],
            "category": "strength",
            "priority_score": score,
            "reason": "Candidate demonstrated strong performance"
        })

    # -----------------------------------------------
    # Sort highest priority first
    # -----------------------------------------------

    prioritized_topics.sort(
        key=lambda topic: topic["priority_score"],
        reverse=True
    )

    return {
        "candidate_id": candidate_id,
        "topics": prioritized_topics
    }


if __name__ == "__main__":

    candidate_id = "CAND-010"

    result = generate_priority_list(candidate_id)

    for topic in result["topics"]:

        print(
            f"Day {topic['day']} | "
            f"{topic['title']} | "
            f"{topic['category']} | "
            f"Score: {topic['priority_score']} | "
            f"{topic['reason']}"
        )
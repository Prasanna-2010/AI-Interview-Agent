from priority_engine import generate_priority_list
from curriculum_mapper import map_candidate_topics
from candidate_analyzer import analyze_candidate


MIN_QUESTIONS = 8
TARGET_QUESTIONS = 10
MIN_CURRICULUM_DAYS = 4


def create_interview_plan(candidate_id):

    # ------------------------------------------------
    # Get candidate information
    # ------------------------------------------------

    profile = analyze_candidate(candidate_id)

    mapped_topics = map_candidate_topics(profile)

    priority_data = generate_priority_list(candidate_id)

    prioritized_topics = priority_data["topics"]

    # ------------------------------------------------
    # Separate topics by category
    # ------------------------------------------------

    weak_topics = [
        topic for topic in prioritized_topics
        if topic["category"] == "weak"
    ]

    challenging_topics = [
        topic for topic in prioritized_topics
        if topic["category"] == "challenging"
    ]

    skipped_topics = [
        topic for topic in prioritized_topics
        if topic["category"] == "skipped"
    ]

    strength_topics = [
        topic for topic in prioritized_topics
        if topic["category"] == "strength"
    ]

    # ------------------------------------------------
    # Build interview topic list
    # ------------------------------------------------

    selected_topics = []
    used_days = set()

    def add_topic(topic):

        if topic["day"] not in used_days:

            selected_topics.append(topic)
            used_days.add(topic["day"])

            return True

        return False

    # ------------------------------------------------
    # 1. Prioritize weak topics
    # ------------------------------------------------

    for topic in weak_topics:

        if len(selected_topics) >= TARGET_QUESTIONS:
            break

        add_topic(topic)

    # ------------------------------------------------
    # 2. Add challenging topics
    # ------------------------------------------------

    for topic in challenging_topics:

        if len(selected_topics) >= TARGET_QUESTIONS:
            break

        add_topic(topic)

    # ------------------------------------------------
    # 3. Add strong topics
    # ------------------------------------------------

    for topic in strength_topics:

        if len(selected_topics) >= TARGET_QUESTIONS:
            break

        add_topic(topic)

    # ------------------------------------------------
    # 4. Add skipped topics
    # ------------------------------------------------

    for topic in skipped_topics:

        if len(selected_topics) >= TARGET_QUESTIONS:
            break

        add_topic(topic)

    # ------------------------------------------------
    # Ensure at least 4 different curriculum days
    # ------------------------------------------------

    if len(used_days) < MIN_CURRICULUM_DAYS:

        for topic in prioritized_topics:

            if topic["day"] not in used_days:

                add_topic(topic)

            if len(used_days) >= MIN_CURRICULUM_DAYS:
                break

    # ------------------------------------------------
    # Build question roadmap
    # ------------------------------------------------

    questions = []

    for index, topic in enumerate(selected_topics, start=1):

        if topic["category"] == "weak":

            question_type = "deep_diagnostic"

        elif topic["category"] == "challenging":

            question_type = "conceptual_depth"

        elif topic["category"] == "skipped":

            question_type = "knowledge_check"

        else:

            question_type = "strength_validation"

        questions.append({
            "question_number": index,
            "day": topic["day"],
            "topic": topic["title"],
            "category": topic["category"],
            "priority_score": topic["priority_score"],
            "question_type": question_type
        })

    # ------------------------------------------------
    # Final validation
    # ------------------------------------------------

    if len(questions) < MIN_QUESTIONS:

        raise ValueError(
            "Interview plan does not contain at least "
            f"{MIN_QUESTIONS} questions."
        )

    if len(set(q["day"] for q in questions)) < MIN_CURRICULUM_DAYS:

        raise ValueError(
            "Interview plan does not cover at least "
            f"{MIN_CURRICULUM_DAYS} curriculum days."
        )

    # ------------------------------------------------
    # Return final plan
    # ------------------------------------------------

    return {
        "candidate": profile["candidate"],

        "interview_requirements": {
            "minimum_questions": MIN_QUESTIONS,
            "planned_questions": len(questions),
            "curriculum_days_covered": len(
                set(q["day"] for q in questions)
            )
        },

        "questions": questions
    }


if __name__ == "__main__":

    candidate_id = "CAND-010"

    plan = create_interview_plan(candidate_id)

    print("\nINTERVIEW PLAN")
    print("=" * 70)

    print(
        f"Candidate: "
        f"{plan['candidate']['name']}"
    )

    print(
        f"Role: "
        f"{plan['candidate']['job_role']}"
    )

    print(
        f"\nQuestions: "
        f"{plan['interview_requirements']['planned_questions']}"
    )

    print(
        f"Curriculum Days Covered: "
        f"{plan['interview_requirements']['curriculum_days_covered']}"
    )

    print("\nQUESTION ROADMAP")
    print("-" * 70)

    for question in plan["questions"]:

        print(
            f"Q{question['question_number']} | "
            f"Day {question['day']} | "
            f"{question['topic']} | "
            f"{question['category']} | "
            f"{question['question_type']}"
        )
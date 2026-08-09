from candidate_analyzer import analyze_candidate
from curriculum_mapper import map_candidate_topics
from interview_planner import create_interview_plan
from llm import generate_response


def build_interviewer_prompt(candidate_id):
    """
    Build the prompt that gives Groq the candidate's
    learning journey and interview plan.
    """

    # Get candidate profile
    candidate_profile = analyze_candidate(candidate_id)

    # Get curriculum details
    mapped_topics = map_candidate_topics(candidate_profile)

    # Get interview plan
    interview_plan = create_interview_plan(candidate_id)

    candidate = candidate_profile["candidate"]

    first_question = interview_plan["questions"][0]

    # Find curriculum details for the first topic
    curriculum_topic = None

    for category in mapped_topics.values():

        if not isinstance(category, list):
            continue

        for topic in category:

            if (
                topic["day"] == first_question["day"]
                and topic["title"] == first_question["topic"]
            ):
                curriculum_topic = topic
                break

        if curriculum_topic:
            break

    # ------------------------------------------------
    # Build LLM prompt
    # ------------------------------------------------

    prompt = f"""
You are a professional technical interviewer.

Your task is to conduct a realistic technical interview.

Candidate information:

Name: {candidate['name']}
Role: {candidate['job_role']}
Years of experience: {candidate['years_experience']}
Education: {candidate['education']}

The candidate's first interview topic is:

Day: {first_question['day']}
Topic: {first_question['topic']}
Category: {first_question['category']}
Question type: {first_question['question_type']}

Curriculum information:

Tools:
{curriculum_topic['tools'] if curriculum_topic else 'Not available'}

Learning objectives:
{curriculum_topic['objectives'] if curriculum_topic else 'Not available'}

Interview instructions:

1. Ask exactly ONE technical question.
2. Make the question conversational.
3. Do not mention the candidate's internal score.
4. Do not mention that the candidate failed the topic.
5. Do not ask a generic textbook definition if a more practical question
   can be asked.
6. The question should test genuine understanding.
7. Keep the question concise.
8. Do not provide the answer.
9. Do not ask multiple questions at once.

Return only the interview question.
"""

    return prompt


def generate_first_question(candidate_id):

    prompt = build_interviewer_prompt(candidate_id)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an experienced technical interviewer. "
                "You conduct realistic, adaptive technical interviews."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = generate_response(messages)

    return response


if __name__ == "__main__":

    candidate_id = "CAND-010"

    question = generate_first_question(candidate_id)

    print("\nAI INTERVIEWER")
    print("=" * 60)
    print(question)
import json

from llm import generate_response


def generate_final_feedback(candidate, evaluations):
    """
    Generate structured final interview feedback.
    """

    evaluation_summary = []

    for index, item in enumerate(evaluations, start=1):
        evaluation = item["evaluation"]

        evaluation_summary.append({
            "question_number": index,
            "topic": item["topic"],
            "score": evaluation.get("overall_score", 0),
            "technical_accuracy": evaluation.get("technical_accuracy", 0),
            "depth": evaluation.get("depth", 0),
            "clarity": evaluation.get("clarity", 0),
            "strengths": evaluation.get("strengths", []),
            "gaps": evaluation.get("gaps", [])
        })

    prompt = f"""
You are a senior technical interviewer.

Generate final feedback ONLY from the interview evaluations provided below.

CANDIDATE:
Name: {candidate.get('name', 'Candidate')}
Role: {candidate.get('job_role', 'Technical Candidate')}
Experience: {candidate.get('years_experience', 0)}

INTERVIEW EVALUATIONS:
{json.dumps(evaluation_summary, indent=2)}

IMPORTANT RULES:

1. Base every statement ONLY on the interview evaluations.
2. Do NOT invent skills, weaknesses, technologies, or experience.
3. Identify strengths by combining the strengths mentioned across the evaluations.
4. Identify gaps by combining the gaps mentioned across the evaluations.
5. If strengths exist in the evaluations, the "strengths" array MUST NOT be empty.
6. If there are no explicit strengths, infer strengths ONLY from high scores.
7. Give practical next steps directly related to the identified gaps.
8. Keep the feedback specific to the topics actually discussed.
9. Do not mention technologies or topics that were not part of the evaluations.
10. Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "A concise overall assessment based on the scores and evaluations.",
    "strengths": [
        "Specific demonstrated strength"
    ],
    "gaps": [
        "Specific knowledge gap"
    ],
    "next": [
        "Practical improvement step"
    ]
}}

Do not include markdown.
Do not include explanations outside JSON.
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional technical interviewer. "
                "Give evidence-based, constructive feedback. "
                "Never invent information."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = generate_response(messages)

    try:
        feedback = json.loads(response)

        # Safety fallback: make sure strengths/gaps aren't lost
        all_strengths = []
        all_gaps = []

        for item in evaluation_summary:
            all_strengths.extend(item["strengths"])
            all_gaps.extend(item["gaps"])

        if not feedback.get("strengths") and all_strengths:
            feedback["strengths"] = list(dict.fromkeys(all_strengths))

        if not feedback.get("gaps") and all_gaps:
            feedback["gaps"] = list(dict.fromkeys(all_gaps))

        return feedback

    except json.JSONDecodeError:
        raise ValueError(
            f"Invalid JSON returned by Groq:\n{response}"
        )


if __name__ == "__main__":

    candidate = {
        "name": "Gerald Combs",
        "job_role": "IT Support Specialist",
        "years_experience": 20
    }

    evaluations = [
        {
            "topic": "Vector Databases Overview",

            "question": "Example question",

            "answer": "Example answer",

            "evaluation": {
                "overall_score": 7,
                "technical_accuracy": 8,
                "depth": 5,
                "clarity": 8,

                "strengths": [
                    "Understands basic vector database concepts",
                    "Can compare local and managed solutions"
                ],

                "gaps": [
                    "Limited discussion of retrieval quality",
                    "Limited discussion of latency"
                ]
            }
        },

        {
            "topic": "Retrieval & Matching Engine",

            "question": "Example question",

            "answer": "Example answer",

            "evaluation": {
                "overall_score": 6,
                "technical_accuracy": 7,
                "depth": 5,
                "clarity": 7,

                "strengths": [
                    "Understands similarity search"
                ],

                "gaps": [
                    "Needs deeper understanding of retrieval evaluation"
                ]
            }
        }
    ]

    feedback = generate_final_feedback(
        candidate,
        evaluations
    )

    print("\nFINAL FEEDBACK")
    print("=" * 60)

    print(
        json.dumps(
            feedback,
            indent=4
        )
    )
from llm import generate_response


def generate_followup(
    question,
    answer,
    evaluation,
    topic,
    curriculum_objectives
):
    """
    Generate an adaptive follow-up question
    based on the candidate's answer.
    """

    score = evaluation["overall_score"]
    depth = evaluation["depth"]

    strengths = evaluation.get("strengths", [])
    gaps = evaluation.get("gaps", [])
    reason = evaluation.get("follow_up_reason", "")

    # ------------------------------------------------
    # Decide difficulty
    # ------------------------------------------------

    if score >= 8:
        difficulty = "advanced"

        instruction = """
The candidate performed strongly.

Ask a more challenging question that tests:
- architecture
- trade-offs
- scalability
- real-world implementation

Do not repeat the original question.
"""

    elif score >= 5:
        difficulty = "intermediate"

        instruction = """
The candidate demonstrated partial understanding.

Ask a targeted follow-up that probes the specific
knowledge gap identified by the evaluator.

Do not simply repeat the original question.
"""

    else:
        difficulty = "foundational"

        instruction = """
The candidate demonstrated weak understanding.

Ask a simpler diagnostic question that checks
the fundamental concept they appear to be missing.

Do not make the candidate feel criticized.
"""

    prompt = f"""
You are conducting a realistic technical interview.

TOPIC:
{topic}

ORIGINAL QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

EVALUATION:

Overall score: {score}/10
Depth score: {depth}/10

Strengths:
{strengths}

Gaps:
{gaps}

Follow-up reason:
{reason}

CURRICULUM OBJECTIVES:
{curriculum_objectives}

DIFFICULTY:
{difficulty}

{instruction}

Interview rules:

1. Ask exactly ONE question.
2. Make it conversational.
3. Base it directly on the candidate's previous answer.
4. Target the identified gap when appropriate.
5. Do not mention scores.
6. Do not mention evaluation.
7. Do not reveal internal reasoning.
8. Do not provide the answer.
9. Do not ask multiple questions.
10. Keep the question concise.

Return ONLY the question.
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are an adaptive senior technical interviewer. "
                "Your questions should respond naturally to the "
                "candidate's previous answer."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    return generate_response(messages)


if __name__ == "__main__":

    question = (
        "Can you walk me through the key considerations when "
        "deciding between a local ChromaDB setup and a cloud-based "
        "Pinecone index for a chatbot project, and how you would "
        "evaluate which one is the better fit?"
    )

    answer = """
    I would choose based on the size of the application,
    scalability, cost and operational requirements.

    ChromaDB can be useful for local development and
    smaller applications because it is easier to set up.
    Pinecone is managed and can be more appropriate when
    we need cloud scalability and less infrastructure
    management.

    I would also compare latency, cost, scalability and
    retrieval quality before making the final decision.
    """

    evaluation = {
        "overall_score": 7,
        "technical_accuracy": 8,
        "depth": 5,
        "clarity": 8,
        "strengths": [
            "Identified key considerations",
            "Compared ChromaDB and Pinecone"
        ],
        "gaps": [
            "Lacked detailed explanation of latency and retrieval quality",
            "Did not provide specific examples"
        ],
        "follow_up_needed": True,
        "follow_up_reason": (
            "Requires more detailed explanation "
            "of technical considerations"
        )
    }

    objectives = [
        "Learn the role of vector databases in RAG applications",
        "Compare local and managed vector database solutions",
        "Select the most suitable database for the chatbot project"
    ]

    followup = generate_followup(
        question,
        answer,
        evaluation,
        "Vector Databases Overview",
        objectives
    )

    print("\nADAPTIVE FOLLOW-UP")
    print("=" * 60)
    print(followup)
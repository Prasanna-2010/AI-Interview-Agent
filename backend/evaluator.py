import json

from llm import generate_response


def evaluate_answer(
    question,
    answer,
    topic,
    curriculum_objectives
):
    """
    Evaluate a candidate's technical answer.

    Returns structured JSON.
    """

    prompt = f"""
You are a senior technical interviewer evaluating a candidate's answer.

INTERVIEW TOPIC:
{topic}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

CURRICULUM OBJECTIVES:
{curriculum_objectives}

Evaluate the answer carefully.

Consider:

1. Technical accuracy
2. Conceptual understanding
3. Depth of explanation
4. Practical reasoning
5. Clarity

Scoring:

0-3 = Poor
4-5 = Weak
6-7 = Adequate
8-9 = Strong
10 = Excellent

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_score": 0,
    "technical_accuracy": 0,
    "depth": 0,
    "clarity": 0,
    "strengths": [],
    "gaps": [],
    "follow_up_needed": true,
    "follow_up_reason": ""
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict but fair technical interviewer. "
                "Evaluate answers objectively."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = generate_response(messages)

    # Convert LLM JSON response into Python dictionary
    try:
        evaluation = json.loads(response)

    except json.JSONDecodeError:

        # Sometimes an LLM may accidentally return
        # markdown or extra text.
        raise ValueError(
            f"LLM returned invalid JSON:\n{response}"
        )

    return evaluation


if __name__ == "__main__":

    question = (
        "Can you walk me through the key considerations "
        "when deciding between a local ChromaDB setup "
        "and a cloud-based Pinecone index for a chatbot "
        "project, and how you would evaluate which one "
        "is the better fit?"
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

    objectives = [
        "Learn the role of vector databases in RAG applications",
        "Set up a local Chroma vector database",
        "Create a cloud-based Pinecone index for comparison",
        "Compare local and managed vector database solutions",
        "Select the most suitable database for the chatbot project"
    ]

    result = evaluate_answer(
        question,
        answer,
        "Vector Databases Overview",
        objectives
    )

    print("\nANSWER EVALUATION")
    print("=" * 60)

    print(json.dumps(result, indent=4))
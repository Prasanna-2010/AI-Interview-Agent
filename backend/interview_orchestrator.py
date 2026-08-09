import json

from candidate_analyzer import analyze_candidate
from curriculum_mapper import map_candidate_topics
from interview_planner import create_interview_plan

from interview_agent import generate_first_question
from evaluator import evaluate_answer
from followup_generator import generate_followup
from session_manager import session_manager


class InterviewOrchestrator:
    """
    Coordinates the complete AI interview flow.
    """

    # Minimum number of main questions required by the challenge
    MIN_QUESTIONS = 8

    # Maximum adaptive follow-ups allowed for one topic
    MAX_FOLLOWUPS = 1

    # ------------------------------------------------
    # Start a new interview
    # ------------------------------------------------

    def start_interview(self, session_id, candidate_id):

        candidate_profile = analyze_candidate(candidate_id)

        interview_plan = create_interview_plan(candidate_id)

        questions = interview_plan.get("questions", [])

        if len(questions) < self.MIN_QUESTIONS:
            raise ValueError(
                f"Interview plan does not contain at least "
                f"{self.MIN_QUESTIONS} questions."
            )

        session_manager.create_session(
            session_id=session_id,
            candidate=candidate_profile["candidate"],
            interview_plan=interview_plan
        )

        first_topic = questions[0]

        question = generate_first_question(candidate_id)

        session_manager.set_current_question(
            session_id=session_id,
            question=question,
            topic=first_topic["topic"]
        )

        session_manager.add_interviewer_message(
            session_id=session_id,
            message=question
        )

        # question_number represents the next main question to ask.
        # After asking question 1, the next planned question is index 1.
        session_manager.advance_question(session_id)

        session_manager.add_topic_covered(
            session_id=session_id,
            topic=first_topic["topic"]
        )

        return {
            "reply": question,
            "done": False,
            "feedback": None
        }

    # ------------------------------------------------
    # Process candidate answer
    # ------------------------------------------------

    def process_answer(self, session_id, answer):

        session = session_manager.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        if session["done"]:
            return {
                "reply": "This interview has already ended.",
                "done": True,
                "feedback": session.get("final_feedback")
            }

        if answer is None or not str(answer).strip():
            raise ValueError("Candidate answer cannot be empty.")

        session_manager.add_candidate_message(
            session_id=session_id,
            message=answer
        )

        question = session["current_question"]
        topic = session["current_topic"]

        candidate_id = session["candidate"]["id"]

        profile = analyze_candidate(candidate_id)
        mapped_topics = map_candidate_topics(profile)

        objectives = self._get_objectives(
            mapped_topics=mapped_topics,
            topic=topic
        )

        evaluation = evaluate_answer(
            question=question,
            answer=answer,
            topic=topic,
            curriculum_objectives=objectives
        )

        # Make sure the evaluator result is always a dictionary.
        if not isinstance(evaluation, dict):
            raise ValueError(
                "Answer evaluator returned an invalid result."
            )

        session_manager.add_evaluation(
            session_id=session_id,
            evaluation={
                "question": question,
                "answer": answer,
                "topic": topic,
                "evaluation": evaluation
            }
        )

        follow_up_needed = evaluation.get(
            "follow_up_needed",
            False
        )

        follow_up_count = session.get(
            "follow_up_count",
            0
        )

        # ------------------------------------------------
        # Adaptive follow-up
        # ------------------------------------------------

        if (
            follow_up_needed
            and follow_up_count < self.MAX_FOLLOWUPS
        ):

            followup = generate_followup(
                question=question,
                answer=answer,
                evaluation=evaluation,
                topic=topic,
                curriculum_objectives=objectives
            )

            if not followup:
                raise ValueError(
                    "Follow-up generator returned an empty question."
                )

            session_manager.increment_followup(session_id)

            session_manager.set_current_question(
                session_id=session_id,
                question=followup,
                topic=topic
            )

            session_manager.add_interviewer_message(
                session_id=session_id,
                message=followup
            )

            return {
                "reply": followup,
                "done": False,
                "feedback": None
            }

        # No follow-up, so continue to the next planned question.
        return self._next_question(session_id)

    # ------------------------------------------------
    # Find curriculum objectives for the current topic
    # ------------------------------------------------

    def _get_objectives(self, mapped_topics, topic):

        for category in mapped_topics.values():

            if not isinstance(category, list):
                continue

            for item in category:

                if not isinstance(item, dict):
                    continue

                if item.get("title") == topic:
                    return item.get("objectives", [])

        return []

    # ------------------------------------------------
    # Generate next planned question
    # ------------------------------------------------

    def _next_question(self, session_id):

        session = session_manager.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        plan = session["interview_plan"]
        questions = plan.get("questions", [])
        question_number = session["question_number"]

        # We have already asked the required 8 main questions.
        if question_number >= self.MIN_QUESTIONS:

            feedback = self._generate_final_feedback(session)

            # SessionManager in the current project does not need a
            # separate set_final_feedback method. Store it directly.
            session["final_feedback"] = feedback

            session_manager.complete_session(session_id)

            return {
                "reply": "Interview completed.",
                "done": True,
                "feedback": feedback
            }

        # Safety check in case the plan is shorter than expected.
        if question_number >= len(questions):

            feedback = self._generate_final_feedback(session)

            session["final_feedback"] = feedback

            session_manager.complete_session(session_id)

            return {
                "reply": "Interview completed.",
                "done": True,
                "feedback": feedback
            }

        next_topic = questions[question_number]

        candidate_id = session["candidate"]["id"]

        question = self._generate_question_for_topic(
            candidate_id=candidate_id,
            topic=next_topic
        )

        # A new main topic gets a fresh follow-up allowance.
        session["follow_up_count"] = 0

        session_manager.set_current_question(
            session_id=session_id,
            question=question,
            topic=next_topic["topic"]
        )

        session_manager.add_interviewer_message(
            session_id=session_id,
            message=question
        )

        session_manager.advance_question(session_id)

        session_manager.add_topic_covered(
            session_id=session_id,
            topic=next_topic["topic"]
        )

        return {
            "reply": question,
            "done": False,
            "feedback": None
        }

    # ------------------------------------------------
    # Generate final interview feedback
    # ------------------------------------------------

    def _generate_final_feedback(self, session):
        """
        Generate structured final interview feedback from all
        evaluations collected during the interview.
        """

        evaluations = session.get("evaluations", [])

        if not evaluations:
            return {
                "summary": "No interview evaluations were recorded.",
                "strengths": [],
                "gaps": [],
                "next": []
            }

        evaluation_text = ""

        for index, item in enumerate(evaluations, start=1):

            evaluation_text += f"""
Evaluation {index}

Topic:
{item.get("topic")}

Question:
{item.get("question")}

Candidate Answer:
{item.get("answer")}

Evaluation:
{item.get("evaluation")}

--------------------------------
"""

        candidate = session.get("candidate", {})

        prompt = f"""
You are a senior technical interviewer.

Create the final assessment for this candidate.

Candidate:
Name: {candidate.get("name", "Unknown")}
Role: {candidate.get("job_role", "Unknown")}
Experience: {candidate.get("years_experience", "Unknown")} years

Interview evaluations:

{evaluation_text}

Return ONLY valid JSON using exactly this structure:

{{
    "summary": "Overall assessment of the candidate.",
    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "gaps": [
        "technical gap 1",
        "technical gap 2",
        "technical gap 3"
    ],
    "next": [
        "specific improvement recommendation 1",
        "specific improvement recommendation 2",
        "specific improvement recommendation 3"
    ]
}}

Rules:
- Base feedback only on the interview evaluations.
- Do not invent skills.
- Mention demonstrated technical strengths.
- Identify specific technical weaknesses.
- Give actionable recommendations.
- Keep the summary concise and professional.
- Do not use markdown.
- Return JSON only.
"""

        from llm import generate_response

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior technical interviewer "
                    "providing objective interview feedback."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = generate_response(messages)

        if not response:
            return {
                "summary": "Interview completed, but final feedback could not be generated.",
                "strengths": [],
                "gaps": [],
                "next": []
            }

        response = response.strip()

        # Remove Markdown code fences if the LLM adds them.
        if response.startswith("```json"):
            response = response[7:].strip()

        elif response.startswith("```"):
            response = response[3:].strip()

        if response.endswith("```"):
            response = response[:-3].strip()

        try:
            feedback = json.loads(response)

        except json.JSONDecodeError:
            return {
                "summary": response,
                "strengths": [],
                "gaps": [],
                "next": []
            }

        return {
            "summary": feedback.get(
                "summary",
                "Interview completed."
            ),
            "strengths": feedback.get(
                "strengths",
                []
            ),
            "gaps": feedback.get(
                "gaps",
                []
            ),
            "next": feedback.get(
                "next",
                []
            )
        }

    # ------------------------------------------------
    # Generate a question for a specific topic
    # ------------------------------------------------

    def _generate_question_for_topic(
        self,
        candidate_id,
        topic
    ):

        profile = analyze_candidate(candidate_id)

        mapped_topics = map_candidate_topics(profile)

        curriculum_topic = None

        for category in mapped_topics.values():

            if not isinstance(category, list):
                continue

            for item in category:

                if not isinstance(item, dict):
                    continue

                if (
                    item.get("day") == topic.get("day")
                    and item.get("title") == topic.get("topic")
                ):
                    curriculum_topic = item
                    break

            if curriculum_topic is not None:
                break

        if curriculum_topic is None:
            raise ValueError(
                "Curriculum topic not found: "
                f"Day {topic.get('day')} - {topic.get('topic')}"
            )

        candidate = profile.get("candidate", {})

        prompt = f"""
You are a professional technical interviewer.

Candidate role:
{candidate.get("job_role", "Unknown")}

Candidate experience:
{candidate.get("years_experience", "Unknown")} years

Interview topic:
Day {topic.get("day")} - {topic.get("topic")}

Topic category:
{topic.get("category", "technical")}

Question type:
{topic.get("question_type", "practical")}

Curriculum objectives:
{curriculum_topic.get("objectives", [])}

Tools:
{curriculum_topic.get("tools", [])}

Ask ONE realistic technical interview question.

Rules:
- Do not mention the candidate's score.
- Do not mention their learning history.
- Do not reveal why this topic was selected.
- Do not ask multiple questions.
- Prefer practical reasoning over memorized definitions.
- Keep the question concise.
- Return only the question.
"""

        from llm import generate_response

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an experienced technical interviewer."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        question = generate_response(messages)

        if not question:
            raise ValueError(
                "LLM returned an empty interview question."
            )

        return question.strip()


# ----------------------------------------------------
# Global orchestrator
# ----------------------------------------------------

orchestrator = InterviewOrchestrator()


# ----------------------------------------------------
# Basic manual test
# ----------------------------------------------------

if __name__ == "__main__":

    session_id = "demo-session-001"
    candidate_id = "CAND-010"

    print("\nSTARTING INTERVIEW")
    print("=" * 60)

    result = orchestrator.start_interview(
        session_id=session_id,
        candidate_id=candidate_id
    )

    print("\nINTERVIEWER:")
    print(result["reply"])

    print("\n" + "=" * 60)

    answer = """
    ChromaDB would be useful for local development because
    it is simple to set up and does not require managing an
    external service. Pinecone would be better when we need
    a managed service and scalability. I would compare cost,
    latency, scalability and operational complexity.
    """

    result = orchestrator.process_answer(
        session_id=session_id,
        answer=answer
    )

    print("\nINTERVIEWER:")
    print(result["reply"])

    print("\nDONE:", result["done"])
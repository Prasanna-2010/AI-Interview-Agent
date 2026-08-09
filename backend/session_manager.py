from datetime import datetime


class SessionManager:
    """
    Manages active interview sessions.

    For the first version, sessions are stored
    in memory using a Python dictionary.
    """

    def __init__(self):
        self.sessions = {}

    # ------------------------------------------------
    # Create a new session
    # ------------------------------------------------

    def create_session(
        self,
        session_id,
        candidate,
        interview_plan
    ):

        session = {
            "session_id": session_id,

            "candidate": candidate,

            "interview_plan": interview_plan,

            "question_number": 0,

            "current_question": None,

            "current_topic": None,

            "conversation": [],

            "evaluations": [],

            "topics_covered": [],

            "follow_up_count": 0,
            "final_feedback": None,

            "done": False,

            "created_at": datetime.now().isoformat()
        }

        self.sessions[session_id] = session

        return session

    # ------------------------------------------------
    # Get session
    # ------------------------------------------------

    def get_session(self, session_id):

        return self.sessions.get(session_id)

    # ------------------------------------------------
    # Check if session exists
    # ------------------------------------------------

    def session_exists(self, session_id):

        return session_id in self.sessions

    # ------------------------------------------------
    # Add interviewer message
    # ------------------------------------------------

    def add_interviewer_message(
        self,
        session_id,
        message
    ):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["conversation"].append({
            "role": "interviewer",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

    # ------------------------------------------------
    # Add candidate message
    # ------------------------------------------------

    def add_candidate_message(
        self,
        session_id,
        message
    ):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["conversation"].append({
            "role": "candidate",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

    # ------------------------------------------------
    # Set current question
    # ------------------------------------------------

    def set_current_question(
        self,
        session_id,
        question,
        topic
    ):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["current_question"] = question
        session["current_topic"] = topic

    # ------------------------------------------------
    # Move to next planned question
    # ------------------------------------------------

    def advance_question(self, session_id):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["question_number"] += 1

    # ------------------------------------------------
    # Add topic to covered topics
    # ------------------------------------------------

    def add_topic_covered(
        self,
        session_id,
        topic
    ):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        if topic not in session["topics_covered"]:

            session["topics_covered"].append(topic)

    # ------------------------------------------------
    # Add evaluation
    # ------------------------------------------------

    def add_evaluation(
        self,
        session_id,
        evaluation
    ):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["evaluations"].append(evaluation)

    # ------------------------------------------------
    # Increment follow-up count
    # ------------------------------------------------

    def increment_followup(self, session_id):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["follow_up_count"] += 1
    # ------------------------------------------------
# Mark interview complete
# ------------------------------------------------

    def complete_session(self, session_id):

      session = self.get_session(session_id)

      if session is None:
        raise ValueError(
            f"Session '{session_id}' not found."
        )

      session["done"] = True

# ------------------------------------------------
# Save final feedback
# ------------------------------------------------

def set_final_feedback(
    self,
    session_id,
    feedback
):

    session = self.get_session(session_id)

    if session is None:
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    session["final_feedback"] = feedback

    # ------------------------------------------------
    # Mark interview complete
    # ------------------------------------------------

    '''def complete_session(self, session_id):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        session["done"] = True'''

    # ------------------------------------------------
    # Return complete session state
    # ------------------------------------------------

    def get_session_state(self, session_id):

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' not found."
            )

        return session


# ----------------------------------------------------
# Global session manager
# ----------------------------------------------------

session_manager = SessionManager()


# ----------------------------------------------------
# Simple test
# ----------------------------------------------------

if __name__ == "__main__":

    test_session = session_manager.create_session(
        session_id="test-123",

        candidate={
            "id": "CAND-010",
            "name": "Gerald Combs",
            "job_role": "IT Support Specialist"
        },

        interview_plan={
            "questions": [
                {
                    "question_number": 1,
                    "day": 8,
                    "topic": "Vector Databases Overview"
                }
            ]
        }
    )

    print("\nSESSION CREATED")
    print("=" * 60)

    print(test_session)

    session_manager.add_interviewer_message(
        "test-123",
        "Can you explain vector databases?"
    )

    session_manager.add_candidate_message(
        "test-123",
        "They store vector embeddings..."
    )

    session_manager.advance_question("test-123")

    print("\nSESSION AFTER CONVERSATION")
    print("=" * 60)

    print(
        session_manager.get_session_state("test-123")
    )
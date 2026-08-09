from os import error

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from interview_orchestrator import orchestrator


app = FastAPI(
    title="AI Interview Agent",
    description="Personalized AI technical interview system",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Request Models
# ----------------------------------------------------

class Candidate(BaseModel):
    id: str


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Candidate
    message: str | None = None


# ----------------------------------------------------
# Response Model
# ----------------------------------------------------

class InterviewResponse(BaseModel):
    sessionId: str
    reply: str
    done: bool
    feedback: dict | None = None


# ----------------------------------------------------
# Root Endpoint
# ----------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "AI Interview Agent is running!"
    }


# ----------------------------------------------------
# Interview Endpoint
# ----------------------------------------------------

# ----------------------------------------------------
# Interview Endpoint
# ----------------------------------------------------

@app.post(
    "/api/interview",
    response_model=InterviewResponse
)
def interview(request: InterviewRequest):

    try:

        session_id = request.sessionId
        candidate_id = request.candidate.id

        # --------------------------------------------
        # Start new interview
        # --------------------------------------------

        if request.message is None:

            result = orchestrator.start_interview(
                session_id=session_id,
                candidate_id=candidate_id
            )

        # --------------------------------------------
        # Continue existing interview
        # --------------------------------------------

        else:

            result = orchestrator.process_answer(
                session_id=session_id,
                answer=request.message
            )

        # --------------------------------------------
        # Return interview response
        # --------------------------------------------

        return {
            "sessionId": session_id,
            "reply": result["reply"],
            "done": result["done"],
            "feedback": result.get("feedback")
        }

    except ValueError as exc:

        print("CLIENT ERROR:", exc)

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": str(exc)
            }
        )

    except Exception as exc:

        print("SERVER ERROR:", exc)

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing the interview.",
                "debug": str(exc)
            }
        )
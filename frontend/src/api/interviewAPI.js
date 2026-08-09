const API_BASE_URL = "";

export const sendInterviewMessage = async (sessionId, candidateId, message = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/interview`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId,
        candidate: {
          id: candidateId,
        },
        message,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Unable to connect to the interview server. Please check your connection and try again.");
  }
};
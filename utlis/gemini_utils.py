import google.generativeai as genai

def get_gemini_response(question, chat):
    """
    Send a message to the Gemini chat model and get the response.
    """
    try:
        response = chat.send_message(question, stream=True)
        return response
    except Exception as e:
        raise RuntimeError(f"Error retrieving response from Gemini API: {str(e)}")

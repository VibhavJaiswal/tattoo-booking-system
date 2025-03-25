from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.config import OPENAI_API_KEY
from app.core.auth import check_api_key
import openai

router = APIRouter()

from app.utils.chatmemory import load_qa_pairs, find_best_answer


qa_data = load_qa_pairs()


client = openai.OpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str


@router.post("/chat/")
async def chat(request: ChatRequest, api_key: str = Depends(check_api_key)):
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    print(f"📩 User Message: {user_message}")

    # First try to find a predefined answer from local Q&A
    answer = find_best_answer(user_message, qa_data)
    if answer and "I'm not sure" not in answer:
        return {"reply": answer}

    # Fall back to OpenAI GPT-4o if no good match is found
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant for a tattoo booking system."},
                {"role": "user", "content": user_message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"OpenAI Error: {str(e)}"})

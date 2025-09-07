import google.generativeai as genai # type: ignore
from django.http import JsonResponse # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
import json

# 🔹 Configure Gemini with your FREE API Key (AI Studio se liya hua)
genai.configure(api_key="AIzaSyDE7s2uqg5141zVJZ82LI_DaSoXujQMYqs")

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message.strip():
                return JsonResponse({"reply": "Please type a message."})

            # 🔹 Use free-tier model
            model = genai.GenerativeModel("gemini-1.5-flash")

            # 🔹 Generate response from Gemini
            response = model.generate_content(user_message)

            bot_reply = response.text if response else "I couldn't generate a response."

            return JsonResponse({"reply": bot_reply})

        except Exception as e:
            return JsonResponse({"reply": f"Error: {str(e)}"})
    else:
        return JsonResponse({"reply": "Only POST method allowed."})

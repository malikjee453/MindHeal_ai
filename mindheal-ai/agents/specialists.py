from core.groq_client import chat
from core.prompts import BASE_SYSTEM, SPECIALIST_PROMPTS


def run_specialist(category, user_text, context=""):
    """
    Run the appropriate MindHeal specialist.

    The specialist focuses on understanding the user's situation
    and providing emotional insight for the final composer.
    """

    specialist_prompt = SPECIALIST_PROMPTS.get(
        category,
        SPECIALIST_PROMPTS["GENERAL"],
    )

    prompt = f"""
User message:
{user_text}

Relevant knowledge/context:
{context if context else "No additional context available."}

==================================================
SPECIALIST TASK
==================================================

Respond to the user's actual situation.

Remember that MindHeal is a supportive companion.

Do not automatically try to fix the user.

If the user is expressing emotional pain, loneliness, sadness,
grief, fear, regret, rejection, or another difficult feeling,
focus first on understanding and emotional support.

Do not automatically provide exercises, techniques, routines,
or behavioral remedies.

If practical advice is genuinely appropriate, keep it gentle.

Do not diagnose.

Provide useful emotional understanding that another MindHeal
component can use to create the final conversational response.

Keep the analysis concise and relevant.
"""

    return chat(
        [
            {
                "role": "system",
                "content": BASE_SYSTEM + "\n\n" + specialist_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )

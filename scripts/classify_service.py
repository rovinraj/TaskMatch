import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY=os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-flash-latest"
def classify_problem(user_problem, categories):
    client = genai.Client(api_key=API_KEY)

    prompt =   f"""
                You are a classification engine for a home services marketplace. Users describe problems they are facing in natural language. Your job is to select the single most appropriate service category from the platform’s database so the user can be matched with the right professional.

                Objective:
                Choose exactly one service category from SERVICE_CATEGORIES that best resolves the user's problem.

                Strict Output Rules:
                - Output exactly one category name.
                - The category must match one from SERVICE_CATEGORIES exactly.
                - Output nothing else: no explanations, punctuation, quotes, or extra text.
                - Do not invent categories.
                - Do not output multiple categories.
                - Do not ask questions.
                - Do not include filler text.
                - Return only the category name.

                Decision Rules:
                1. Choose the trade that fixes the root problem. If the user mentions consequences such as stains, mold, or damage, choose the service that fixes the cause rather than cosmetic results. Example: a ceiling stain caused by a leak should map to Plumbing, not painting or cosmetic repair.
                2. Identify the primary system involved and classify accordingly. Water, leaks, drainage, toilets, sinks, showers, and pipes map to Plumbing. Electrical power, outlets, breakers, sparks, or wiring issues map to Electrical. Heating, cooling, ventilation, thermostats, furnaces, and air conditioning map to HVAC. Appliances such as washer, dryer, fridge, oven, or dishwasher failures map to Appliance Repair. Roof leaks or roof damage map to Roofing. Insects or rodents map to Pest Control. Minor repairs, installations, mounting, fixture replacement, or general small repairs map to Handyman.
                3. Prefer a specialist category over Handyman when a specialist clearly applies.
                4. Use Handyman only when no specialist clearly matches or when tasks are general minor home repairs or installations.
                5. If multiple issues are mentioned, choose the category that addresses the main or root problem.
                6. If the request is ambiguous, choose the closest reasonable match from SERVICE_CATEGORIES based on the primary issue described.

                Examples:

                SERVICE_CATEGORIES:
                Plumbing, Electrical, HVAC, Handyman, Appliance Repair, Roofing, Pest Control

                User problem: My kitchen sink is leaking under the cabinet.
                Output: Plumbing

                User problem: The breaker trips whenever I plug something in.
                Output: Electrical

                User problem: My AC runs but the house never cools down.
                Output: HVAC

                User problem: I need shelves mounted and a door fixed.
                Output: Handyman

                User problem: Ants are all over the kitchen.
                Output: Pest Control

                User problem: The washing machine stopped spinning.
                Output: Appliance Repair

                User problem: There is a water stain on the ceiling under the bathroom.
                Output: Plumbing

                Classification Task:

                USER_PROBLEM:
                {user_problem}

                SERVICE_CATEGORIES:
                {categories}

                Return exactly one category from SERVICE_CATEGORIES and nothing else.
                If unsure, choose the closest match based on the rules above.
                """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0,
        }
    )

    result = response.text.strip()

    if result not in categories:
        print(f"[WARNING] Invalid output: {result}")
        return None

    return result

if __name__ == "__main__":
    SERVICE_CATEGORIES = [
        "Plumbing",
        "Electrical",
        "HVAC",
        "Handyman",
        "Appliance Repair",
        "Roofing",
        "Pest Control"
    ]

    while True:
        user_input = input("\nDescribe your problem (or 'exit'): ")
        if user_input.lower() == "exit":
            break

        category = classify_problem(user_input, SERVICE_CATEGORIES)

        print(f"\nPredicted Category: {category}")
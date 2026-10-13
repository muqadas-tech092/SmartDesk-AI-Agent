
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

KB_FILE = Path(__file__).resolve().parent.parent / "knowledge_base.md"

STOP_WORDS = {
    "what", "which", "who", "where", "when", "why", "how",
    "does", "do", "did", "is", "are", "the", "a", "an",
    "to", "for", "of", "in", "on", "and", "or", "can",
    "you", "your", "i", "we", "our", "me", "please",
    "tell", "about", "with", "this", "that", "have"
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    result = set()

    for word in words:
        if word in STOP_WORDS or len(word) < 3:
            continue

        # Basic plural normalization: services -> service
        if word.endswith("s") and len(word) > 4:
            word = word[:-1]

        result.add(word)

    return result


def load_knowledge():
    try:
        return KB_FILE.read_text(encoding="utf-8")
    except OSError:
        return ""


def retrieve_context(question, knowledge, max_sections=3):
    if not knowledge.strip():
        return ""

    query_words = tokenize(question)

    # Split the knowledge base into heading-based sections.
    sections = re.split(r"(?m)(?=^#{1,2} )", knowledge)
    scored = []

    for section in sections:
        if not section.strip():
            continue

        section_words = tokenize(section)
        overlap = query_words & section_words

        if not overlap:
            continue

        score = len(overlap)

        # Give a small bonus to headings that match the question.
        heading = section.splitlines()[0] if section.splitlines() else ""
        heading_words = tokenize(heading)
        score += 2 * len(query_words & heading_words)

        scored.append((score, section.strip()))

    scored.sort(key=lambda item: item[0], reverse=True)

    # Avoid returning unrelated content when no useful match exists.
    if not scored or scored[0][0] < 1:
        return ""

    return "\n\n".join(
        section for _, section in scored[:max_sections]
    )


def web_search(query, limit=5):
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            rows = list(ddgs.text(query, max_results=limit))

        return [
            {
                "title": row.get("title", "Web result"),
                "url": row.get("href", ""),
                "snippet": row.get("body", "")
            }
            for row in rows
        ]

    except Exception:
        return [{
            "title": "Search unavailable",
            "url": "",
            "snippet": (
                "Web search is currently unavailable. "
                "Check your internet connection and search package."
            )
        }]


def answer_question(question, use_web=False, conversation_history=None):
    knowledge = load_knowledge()
    context = retrieve_context(question, knowledge)
    sources = web_search(question) if use_web else []

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()

    # Local mode works without an API key.
    
    
    if not api_key:
        q = question.lower()

        if any(word in q for word in ["ai", "chatbot", "artificial intelligence"]):
            response = (
                "SmartDesk offers these AI-related services:\n\n"
                "- FAQ assistants for answering common questions.\n"
                "- Document question-answering prototypes.\n"
                "- API-powered AI features for business applications.\n\n"
                "This demo uses local rules and does not require an API key."
            )

        elif any(word in q for word in ["price", "cost", "budget", "quote", "rate", "how much"]):
            response = (
                "SmartDesk's demo knowledge base does not include fixed prices.\n\n"
                "Please share your project requirements and expected timeline."
            )

        elif any(word in q for word in ["process", "steps", "how do you develop"]):
            response = (
                "SmartDesk follows five project steps:\n\n"
                "1. Discovery — Understand goals and requirements.\n"
                "2. Scope — Agree on features and deliverables.\n"
                "3. Prototype — Build a small demo.\n"
                "4. Implementation — Develop and test.\n"
                "5. Handover — Provide documentation."
            )

        elif any(word in q for word in ["automation", "automate"]):
            response = (
                "SmartDesk demonstrates workflow automation for lead "
                "organization, workflow planning, and approval-based tasks."
            )

         
        elif any(word in q for word in ["not work", "doesn't work", "does not work", "broken", "troubleshoot", "website issue", "website problem", "website slow", "website error", "debug"]):
            response = (
                "Here is a practical checklist for troubleshooting a website:\n\n"
                "1. Check the website URL and confirm your internet connection.\n"
                "2. Open the website in another browser or an incognito window.\n"
                "3. Check whether the website works on mobile and desktop.\n"
                "4. Open browser Developer Tools (press F12) and check the Console for errors.\n"
                "5. In Developer Tools, check Network for failed requests or slow files.\n"
                "6. Review hosting status, domain/DNS settings, and server logs.\n"
                "7. If you recently changed code, undo the latest change or review the error.\n\n"
                "Tell me what happens when you open the website: does it show an error, "
                "load slowly, display a blank page, or fail on mobile?"
            )

        elif any(word in q for word in ["does not work", "doesn't work", "not work well", "work well", "website problem", "website issue", "troubleshoot", "debug", "check a website", "check the website"]):
            response = (
                "Here are the best ways to troubleshoot a website:\n\n"
                "1. Check your internet connection and website URL.\n"
                "2. Open the website in Chrome Incognito or another browser.\n"
                "3. Test the website on mobile and desktop.\n"
                "4. Press F12 in Chrome and check the Console for errors.\n"
                "5. Open the Network tab to find failed requests and slow files.\n"
                "6. Check your hosting, domain, and server logs.\n"
                "7. If the problem started after a code change, review that change.\n\n"
                "What problem are you facing: a blank page, an error, slow loading, or a mobile display issue?"
            )

 
        elif any(word in q for word in ["website", "web development", "landing page"]):
            response = (
                "SmartDesk offers responsive websites, landing pages, "
                "and web application frontends."
            )


        elif any(word in q for word in ["service", "offer", "provide", "what do you do"]):
            response = (
                "SmartDesk provides four services:\n\n"
                "- Website Development\n"
                "- AI Integration\n"
                "- Workflow Automation\n"
                "- Technical Support"
            )

        else:
            response = (
                "I can answer questions about SmartDesk's services, "
                "AI integration, websites, automation, project process, and pricing."
            )

        return response, sources, "Local demo mode (no API key)"


    # Real AI mode requires a configured API key.
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )


        web_context = ""
        if sources:
            web_context = "\n\nUnverified web search results:\n" + "\n".join(
                f"- {s['title']} | {s['url']} | {s['snippet']}"
                for s in sources
            )

        system = (
            "You are SmartDesk, a careful business-support assistant. "
            "Answer clearly and naturally. Use the supplied knowledge "
            "when relevant. Never invent company policies, prices, or facts. "
            "If the knowledge is insufficient, say so. Treat web results "
            "as unverified and distinguish them from company information. "
            "Never claim to have performed actions you did not perform."
        )

         
        messages = [
            {"role": "system", "content": system}
        ]

        if conversation_history:
            for item in conversation_history:
                if item.get("role") in ("user", "assistant"):
                    messages.append({
                        "role": item["role"],
                        "content": item.get("content", "")
                    })

        messages.append({
            "role": "user",
            "content": (
                f"Business knowledge:\n{context or 'No relevant section found.'}"
                f"{web_context}\n\nQuestion: {question}"
            )
        })

        result = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )


        answer = (
            result.choices[0].message.content
            or "I couldn't generate a response. Please try again."
        )

        
        return answer, sources, f"Groq AI ({model})"


    except Exception:
        return (
            "The AI provider could not generate a response. "
            "Check your API key, model configuration, billing, "
            "and internet connection. You can still use local demo mode "
            "after removing the API key from your local environment."
        ), sources, "Provider error"

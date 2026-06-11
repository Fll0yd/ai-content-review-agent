import os
import re
from dotenv import load_dotenv

from graph.state import ReviewState

load_dotenv()


def get_llm():
    local_mode = os.getenv("LOCAL_MODE", "true").lower() == "true"

    if local_mode:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.2,
        )

    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
        temperature=0.2,
    )


llm = get_llm()


def extract_score(text: str, label: str) -> int:
    """
    Extracts scores like:
    Grammar Score: 7/10
    SEO Score: 8 / 10
    Readability Score: 6 out of 10
    """

    patterns = [
        rf"{label}\s*Score\s*:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        rf"{label}\s*Score\s*:\s*(\d+(?:\.\d+)?)\s*out\s*of\s*10",
        rf"Score\s*:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        rf"Score\s*:\s*(\d+(?:\.\d+)?)\s*out\s*of\s*10",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            score = round(float(match.group(1)), 1)
            return max(0, min(score, 10))

    return 0.0


def grammar_review(state: ReviewState):
    article = state["article"]

    prompt = f"""
You are an expert content editor.

Review the article below for:
- Grammar
- Spelling
- Punctuation
- Sentence clarity

Return your answer in this exact format:

Grammar Score: X/10

Feedback:
<short, useful feedback>

Article:
{article}
"""

    response = llm.invoke(prompt)
    feedback = response.content
    score = extract_score(feedback, "Grammar")

    return {
        "grammar_feedback": feedback,
        "grammar_score": score,
    }


def seo_review(state: ReviewState):
    article = state["article"]

    prompt = f"""
You are an SEO content strategist.

Review the article below for:
- Search intent
- Keyword clarity
- Title/headline potential
- Meta description potential
- Internal linking opportunities
- Overall SEO usefulness

Return your answer in this exact format:

SEO Score: X/10

Feedback:
<short, useful feedback>

Article:
{article}
"""

    response = llm.invoke(prompt)
    feedback = response.content
    score = extract_score(feedback, "SEO")

    return {
        "seo_feedback": feedback,
        "seo_score": score,
    }


def readability_review(state: ReviewState):
    article = state["article"]

    prompt = f"""
You are a readability and UX writing expert.

Review the article below for:
- Clarity
- Paragraph structure
- Sentence length
- Jargon
- Reader friendliness
- Actionability

Return your answer in this exact format:

Readability Score: X/10

Feedback:
<short, useful feedback>

Article:
{article}
"""

    response = llm.invoke(prompt)
    feedback = response.content
    score = extract_score(feedback, "Readability")

    return {
        "readability_feedback": feedback,
        "readability_score": score,
    }


def rewrite_article(state: ReviewState):
    article = state["article"]
    style_guide = state.get("style_guide", "")

    prompt = f"""
You are an expert content editor.

Rewrite the article below.

Goals:
- Fix grammar
- Improve readability
- Improve SEO
- Keep the original meaning
- Make it suitable for publication

Style Guide:
{style_guide}

Article:
{article}
"""

    response = llm.invoke(prompt)

    return {
        "improved_article": response.content,
    }

def meta_description_generator(state: ReviewState):
    article = state["article"]

    prompt = f"""
You are an SEO copywriter.

Generate one SEO-friendly meta description for the article below.

Requirements:
- 140 to 160 characters
- Clear and specific
- Written for search results
- Include the main topic
- Do not use quotation marks
- Return only the meta description text

Article:
{article}
"""

    response = llm.invoke(prompt)

    return {
        "meta_description": response.content.strip(),
    }

def seo_title_generator(state: ReviewState):
    article = state["article"]

    prompt = f"""
You are an SEO strategist.

Generate 3 SEO-friendly article titles.

Requirements:
- Engaging
- Keyword-focused
- Under 70 characters
- Number them 1 through 3

Article:
{article}
"""

    response = llm.invoke(prompt)

    return {
        "seo_titles": response.content.strip(),
    }
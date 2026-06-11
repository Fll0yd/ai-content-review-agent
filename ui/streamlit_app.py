import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from graph.workflow import graph


def get_content_status(overall_score: float) -> str:
    if overall_score >= 8:
        return "Ready for Publication"
    if overall_score >= 6:
        return "Needs Light Revision"
    return "Needs Improvement"


st.set_page_config(
    page_title="AI Content Review Agent",
    page_icon="📝",
    layout="wide",
)

st.title("AI Content Review Agent")
st.caption("LangGraph-powered content review workflow using local Ollama or Anthropic.")

article = st.text_area(
    "Paste article content",
    height=300,
    placeholder="Paste a blog post, landing page draft, or support article here...",
)

style_guide = st.text_area(
    "Optional Style Guide",
    height=140,
    value="""Write in a style that is:
- Professional
- Clear
- Concise
- Helpful
- Action-oriented""",
)

if st.button("Review Article"):
    if not article.strip():
        st.warning("Paste an article first.")
    else:
        with st.spinner("Reviewing article..."):
            result = graph.invoke({
                "article": article,
                "style_guide": style_guide,
            })

        grammar_score = result.get("grammar_score", 0)
        seo_score = result.get("seo_score", 0)
        readability_score = result.get("readability_score", 0)

        overall_score = round(
            (grammar_score + seo_score + readability_score) / 3,
            1,
        )

        content_status = get_content_status(overall_score)

        st.subheader("Content Score Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Overall Score", f"{overall_score}/10")
        col2.metric("Grammar", f"{grammar_score}/10")
        col3.metric("SEO", f"{seo_score}/10")
        col4.metric("Readability", f"{readability_score}/10")

        if overall_score >= 8:
            st.success(f"Status: {content_status}")
        elif overall_score >= 6:
            st.warning(f"Status: {content_status}")
        else:
            st.error(f"Status: {content_status}")

        st.divider()

        st.subheader("Suggested SEO Titles")
        st.text_area(
            "SEO Titles",
            value=result.get("seo_titles", ""),
            height=120,
        )

        st.subheader("Suggested Meta Description")
        st.text_area(
            "Meta Description",
            value=result.get("meta_description", ""),
            height=100,
        )

        st.subheader("Grammar Review")
        st.write(result.get("grammar_feedback", ""))

        st.subheader("SEO Review")
        st.write(result.get("seo_feedback", ""))

        st.subheader("Readability Review")
        st.write(result.get("readability_feedback", ""))

        st.subheader("Improved Article")
        st.text_area(
            "Rewritten Content",
            value=result.get("improved_article", ""),
            height=300,
        )

        report = f"""
# AI Content Review Report

## Content Score Dashboard

Overall Score: {overall_score}/10

Grammar: {grammar_score}/10  
SEO: {seo_score}/10  
Readability: {readability_score}/10  

Status: {content_status}

---

## Style Guide Used

{style_guide}

---

## Suggested SEO Titles

{result.get("seo_titles", "")}

---

## Suggested Meta Description

{result.get("meta_description", "")}

---

## Grammar Review

{result.get("grammar_feedback", "")}

---

## SEO Review

{result.get("seo_feedback", "")}

---

## Readability Review

{result.get("readability_feedback", "")}

---

## Improved Article

{result.get("improved_article", "")}
"""

        st.download_button(
            label="Download Review Report",
            data=report,
            file_name="content_review_report.md",
            mime="text/markdown",
        )

        with st.expander("Raw LangGraph State"):
            st.json(result)
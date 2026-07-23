from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url

# ----------------------------------------------------
# Load Environment Variables
# ----------------------------------------------------
load_dotenv()

# ----------------------------------------------------
# LLMs
# ----------------------------------------------------
llm = ChatMistralAI(
    model="mistral-small-latest",  # used for search + reader agents (tool-calling)
    temperature=0,
)

writer_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",  # auto-tracks Google's current Flash model — avoids dead-model errors
    temperature=0.3,
)

# ----------------------------------------------------
# Search Agent
# ----------------------------------------------------
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )

# ----------------------------------------------------
# Reader Agent
# ----------------------------------------------------
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )

# ----------------------------------------------------
# Writer Chain
# ----------------------------------------------------
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Structure the report as:
# Introduction
# Key Findings
(Minimum 3 detailed points)
# Conclusion
# Sources
(List every URL found in the research)

The report should be factual, detailed, professional, and easy to read.
""",
        ),
    ]
)

writer_chain = writer_prompt | writer_llm | StrOutputParser()

# ----------------------------------------------------
# Critic Chain
# ----------------------------------------------------
critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research reviewer. Critically evaluate reports and provide actionable feedback.",
        ),
        (
            "human",
            """Review the following report.

Report:
{report}

Respond ONLY in this format:
Score: X/10
Strengths:
- Point 1
- Point 2
Areas to Improve:
- Point 1
- Point 2
One-line Verdict:
Your final opinion.
""",
        ),
    ]
)

critic_chain = critic_prompt | writer_llm | StrOutputParser()
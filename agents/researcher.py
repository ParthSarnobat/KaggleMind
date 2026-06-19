import os 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class DeepResearchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def generate_dossier(self, competition_title, raw_markdown):
        """
        Processes raw competition text into a structured Research Dossier.
        """
        prompt = ChatPromptTemplate.from_template("""
        You are a World-Class Kaggle Grandmaster and Research Librarian. 
        Your goal is to analyze the following raw competition data for: {title}

        Raw Data:
        {data}

        Please synthesize this into a structured Markdown 'Research Dossier' with these sections:
        1. **Executive Summary**: 2-3 sentences on the core problem.
        2. **Technical Constraints**: Evaluation metric, data limits, and rules.
        3. **Community Insights**: Key findings, leaks, or top strategies from the forums.
        4. **Domain Science**: Identify any field-specific theories, methods, or best practices relevant to this domain, regardless of subject.
        """
        )

        chain = prompt | self.llm | StrOutputParser()
        dossier_text = chain.invoke({"title":competition_title, "data":raw_markdown})
        return dossier_text
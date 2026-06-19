import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

class StrategyAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def review_proposal(self, dossier_content, chat_history, user_proposal) -> str:
        """
        Maintains a discussion loop evaluating the user's competitive ML strategy.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a World-Class Kaggle Grandmaster acting as a Strategy Advisor. 
            Your role is to critique, refine, and improve the user's machine learning approach based on the competition details.
            
            Here is the Ground Truth Research Dossier for this competition:
            {dossier}
            
            Be highly analytical. Look specifically for:
            - Validation strategy issues (e.g., using random K-Fold on time-series data).
            - Evaluation metric mismatches.
            - Potential Data Leakage risks.
            - Advanced feature engineering ideas matching the domain.
            
            Engage in a collaborative, peer-to-peer technical discussion. Keep your responses structured but conversational."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{proposal}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        # Format history into LangChain message formats
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        response = chain.invoke({
            "dossier": dossier_content,
            "history": formatted_history,
            "proposal": user_proposal
        })
        
        return response
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
            
            Engage in a collaborative, peer-to-peer technical discussion. Keep your responses structured but conversational.
             
            Whenever you propose a machine learning pipeline, cross-validation strategy, or feature engineering architecture, you MUST include a flowchart visualizing the data flow. 
            Always output the flowchart using valid Mermaid.js syntax. 

            CRITICAL MERMAID SYNTAX RULES:
            1. Use 'graph TD' for the layout.
            2. You MUST wrap all node text in double quotes to prevent parsing errors. Example: A["Raw Data"] --> B["Data Processing (EDA)"]
            3. Never use custom styles, colors, or classes.
            4. For connection text, use the exact pipe syntax. Example: C["Node 1"] -->|"Validation Split"| D["Node 2"]
            5. Wrap the entire graph strictly inside ```mermaid code blocks.
            6. PREVENT LAYOUT CRASHES: NEVER create tight bidirectional loops between immediate parent/child nodes (e.g., A --> B and B --> A). If an action fails or is not taken, route the flow FORWARD to the next logical step, do not loop back to the immediate parent. Use dotted arrows (-.->) for large, architectural feedback loops (like "Next Turn").
            7. NEVER use semicolons ; at the end of lines. NEVER use // for comments. If you must comment, use %%. Always use the pipe syntax -->|"text"| for labeled arrows.
            8. EXPLICIT CONNECTIONS ONLY: You are strictly forbidden from grouping nodes. You must write out every single arrow connection on its own dedicated line.
            [BAD EXAMPLE - DO NOT DO THIS]:
            C1 & C2 & C3 --> D["Predict Future Positions"]

            [GOOD EXAMPLE - YOU MUST DO THIS]:
            C1 --> D["Predict Future Positions"]
            C2 --> D["Predict Future Positions"]
            C3 --> D["Predict Future Positions"]
            9. NO GLOBAL LOOPS: Never create massive cycles that loop the very last node all the way back to the very first node (e.g., do not do Z --> A). If you need to represent a game loop or a "Next Turn," point the final node to a NEW end-node instead (e.g., Y --> Z["Next Turn Start"]).
            10. NO DUPLICATE NODE DEFINITIONS: Never define the same node ID more than once 
            with different labels. If multiple arrows point to the same destination, reuse 
            the exact same node definition. Each node ID must appear with its label [...] 
            only once in the entire graph.

            11. NO DISCONNECTED SUBGRAPHS: Every node must be reachable from the root node. 
            Never create a separate floating flow. If you need to show a secondary flow like 
            a 'forget' mechanism, connect it to the main graph via a dotted arrow or add it 
            as a branch from an existing node.
            """),
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
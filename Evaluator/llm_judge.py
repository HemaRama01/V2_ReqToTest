
# from databricks_langchain import ChatDatabricks
# from langchain_core.prompts import PromptTemplate

# class LLMJudge:
#     def __init__(self, endpoint="databricks-meta-llama-3-3-70b-instruct"):
#         # LangChain automatically looks for DATABRICKS_HOST and DATABRICKS_TOKEN 
#         # in your environment variables.
#         self.llm = ChatDatabricks(
#             endpoint=endpoint,
#             temperature=0.1,
#             max_tokens=250,
#         )
        
#         self.prompt = PromptTemplate.from_template("""
#         The user searched for: {query}
#         The system retrieved this result: {matched_text}
#         The mathematical similarity score was {score} (out of 1).

#         Task: Since the score is not 1.0, identify exactly what is different or missing 
#         in the retrieved text compared to the user's original query. 
#         Why is this not a perfect match? Provide a concise explanation.
#         """)

#     def analyze_difference(self, query, matched_text, score):
#         if score >= 1.0:
#             return "Perfect Match."

#         # Create the chain
#         chain = self.prompt | self.llm
        
#         try:
#             # Invoke the chain with a dictionary of variables
#             response = chain.invoke({
#                 "query": query,
#                 "matched_text": matched_text,
#                 "score": score
#             })
#             return response.content
#         except Exception as e:
#             return f"Error during judging: {str(e)}"



from openai import OpenAI

class LLMJudge:
    def __init__(self, endpoint="databricks-meta-llama-3-1-8b-instruct"):
        # Setup using your PAT and Workspace URL
        # You can hardcode these for now to test, or use os.environ
        self.api_key = "dapibe4eb79b3beea0a611fe4f1b9337e3af-2" 
        self.base_url = "https://adb-2247657378631160.0.azuredatabricks.net/serving-endpoints"
        self.model = endpoint
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def analyze_difference(self, query, matched_text, score):
        # Skip if it's a perfect match
        if score >= 1.0:
            return "Perfect Match."

        prompt = f"""
        The user searched for: {query}
        The system retrieved this result: {matched_text}
        The mathematical similarity score was {score} (out of 1).

        Task: Since the score is not 1.0, identify exactly what is different or missing 
        in the retrieved text compared to the user's original query. 
        Why is this not a perfect match? Provide a concise explanation.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error during judging: {str(e)}"

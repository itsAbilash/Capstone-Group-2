# -*- coding: utf-8 -*-
"""code1ccc.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MGTwCHlI9Q12FzMpkjECXhGp0oWHJDvH
"""

# Import necessary libraries
import json
import os
from typing import Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_community.llms import LlamaCpp
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
import pandas as pd
import streamlit as st

# Load API keys from config.json
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        os.environ["ANTHROPIC_API_KEY"] = config["ANTHROPIC_API_KEY"]
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
except FileNotFoundError:
    st.error("Error: config.json file not found. Please create one with your API keys.")
    st.stop()
except KeyError as e:
    st.error(f"Error: Missing key in config.json: {e}")
    st.stop()

# Define the AgentManager class to manage all agents
class AgentManager:
    def __init__(self):
        """
        Initializes the AgentManager with all agents and an LLM router.
        """
        self.agents = {
            "decomposer": DecomposerAgent(),
            "search": SearchAgent(),
            "extract": ExtractionAgent(),
            "summarize": SummarizationAgent(),
            "export": ExportAgent()
        }
        self.llm_router = LLMRouter()  # Router to dynamically select LLMs

# Define the LLMRouter class to dynamically select and instantiate LLMs
class LLMRouter:
    def get_llm(self, model_type: str):
        """
        Returns an instance of the requested LLM based on the model_type.

        Args:
            model_type (str): Type of LLM to instantiate (e.g., "openai", "claude", "local").

        Returns:
            LLM instance: An instance of the requested LLM.
        """
        models = {
            "openai": ChatOpenAI,  # OpenAI LLM
            "claude": ChatAnthropic,  # Claude LLM
            "local": LlamaCpp  # Local LLM (e.g., Llama-3)
        }
        return models[model_type](**config[model_type])  # Instantiate the LLM with config

# Define the DecomposerAgent class to break down user queries
class DecomposerAgent:
    def __init__(self):
        """
        Initializes the DecomposerAgent with an LLM.
        """
        self.llm = LLMRouter().get_llm("claude")  # Use Claude for decomposition

    def decompose(self, query: str) -> dict:
        """
        Breaks down a user query into structured parameters.

        Args:
            query (str): User query (e.g., "Find the price of a 2017 Roadtrek CS Adventurous XL in Texas").

        Returns:
            dict: Structured parameters (e.g., {"make": "Roadtrek", "model": "CS Adventurous XL", "year": 2017, "location": "Texas"}).
        """
        prompt = f"Break down the following query into structured parameters: {query}"
        response = self.llm.invoke(prompt)
        return response  # Return structured parameters

# Define the SearchAgent class to perform web searches
class SearchAgent:
    def __init__(self):
        """
        Initializes the SearchAgent with an LLM.
        """
        self.llm = LLMRouter().get_llm("openai")  # Use OpenAI for search queries

    def search(self, query: str) -> list:
        """
        Performs a web search based on the query.

        Args:
            query (str): Search query (e.g., "2017 Roadtrek CS Adventurous XL in Texas").

        Returns:
            list: List of search results.
        """
        prompt = f"Generate search queries for: {query}"
        search_queries = self.llm.invoke(prompt)
        # Simulate web search (replace with actual search logic)
        return [f"Result for {query}"]  # Placeholder for search results

# Define the ExtractionAgent class to extract relevant information
class ExtractionAgent:
    def __init__(self):
        """
        Initializes the ExtractionAgent with an LLM.
        """
        self.llm = LLMRouter().get_llm("claude")  # Use Claude for extraction

    def extract(self, search_results: list) -> dict:
        """
        Extracts relevant information from search results.

        Args:
            search_results (list): List of search results.

        Returns:
            dict: Extracted information (e.g., prices, locations).
        """
        prompt = f"Extract relevant information from: {search_results}"
        extracted_data = self.llm.invoke(prompt)
        return extracted_data  # Return extracted information

# Define the SummarizationAgent class to consolidate information
class SummarizationAgent:
    def __init__(self):
        """
        Initializes the SummarizationAgent with an LLM.
        """
        self.llm = LLMRouter().get_llm("openai")  # Use OpenAI for summarization

    def summarize(self, data: dict) -> str:
        """
        Consolidates extracted information into a summary.

        Args:
            data (dict): Extracted information.

        Returns:
            str: Summary of the information.
        """
        prompt = f"Summarize the following data: {data}"
        summary = self.llm.invoke(prompt)
        return summary  # Return summary

# Define the ExportAgent class to export results into Excel
class ExportAgent:
    def export(self, data: dict, filename: str = "output.xlsx"):
        """
        Exports data into an Excel file.

        Args:
            data (dict): Data to export.
            filename (str): Name of the output Excel file.
        """
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)  # Export to Excel

# Initialize the AgentManager
agent_manager = AgentManager()

# Streamlit UI
def main():
    """
    Streamlit UI for the agent-based workflow engine.
    """
    st.title("Agent-Based Workflow Engine for Vehicle Valuation")
    st.write("Enter your query below to get market valuation for vehicles.")

    # User input
    query = st.text_input("Enter your query (e.g., 'Find the price of a 2017 Roadtrek CS Adventurous XL in Texas'):")

    if st.button("Submit"):
        if not query:
            st.error("Please enter a query.")
        else:
            # Step 1: Decompose the query
            with st.spinner("Decomposing query..."):
                decomposed_query = agent_manager.agents["decomposer"].decompose(query)
                st.write("**Decomposed Query:**", decomposed_query)

            # Step 2: Perform search
            with st.spinner("Performing search..."):
                search_results = agent_manager.agents["search"].search(decomposed_query)
                st.write("**Search Results:**", search_results)

            # Step 3: Extract information
            with st.spinner("Extracting information..."):
                extracted_data = agent_manager.agents["extract"].extract(search_results)
                st.write("**Extracted Data:**", extracted_data)

            # Step 4: Summarize information
            with st.spinner("Summarizing information..."):
                summary = agent_manager.agents["summarize"].summarize(extracted_data)
                st.write("**Summary:**", summary)

            # Step 5: Export results
            with st.spinner("Exporting results..."):
                agent_manager.agents["export"].export(extracted_data)
                st.success("Results exported to output.xlsx")

            # Provide download link for the Excel file
            with open("output.xlsx", "rb") as file:
                st.download_button(
                    label="Download Excel File",
                    data=file,
                    file_name="output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Run the Streamlit app
if __name__ == "__main__":
    main()
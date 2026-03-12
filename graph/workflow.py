from langgraph.graph import StateGraph

from graph.state import ResumeState

from agents.parser_agent import parser_agent
from agents.skill_agent import skill_agent
from agents.ats_agent import ats_agent


workflow = StateGraph(ResumeState)

workflow.add_node("parser", parser_agent)
workflow.add_node("skills", skill_agent)
workflow.add_node("ats", ats_agent)

workflow.set_entry_point("parser")

workflow.add_edge("parser", "skills")
workflow.add_edge("skills", "ats")

graph = workflow.compile()
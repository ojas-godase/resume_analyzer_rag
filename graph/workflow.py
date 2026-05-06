from langgraph.graph import StateGraph
from graph.state import ResumeState

from agents.jd_agent import jd_agent
from agents.parser_agent import parser_agent
from agents.skill_agent import skill_agent
from agents.ats_agent import ats_agent
from agents.match_agent import match_agent
from agents.rag_agent import rag_agent
from agents.rewrite_agent import rewrite_agent
from agents.resume_draft_agent import resume_draft_agent
from agents.critic_agent import critic_agent


full_workflow = StateGraph(ResumeState)

# Nodes
full_workflow.add_node("jd", jd_agent)
full_workflow.add_node("parser", parser_agent)
full_workflow.add_node("skills", skill_agent)
full_workflow.add_node("ats", ats_agent)
full_workflow.add_node("match", match_agent)
full_workflow.add_node("rag", rag_agent)
full_workflow.add_node("rewrite", rewrite_agent)
full_workflow.add_node("draft", resume_draft_agent)
full_workflow.add_node("critic", critic_agent)

# Entry
full_workflow.set_entry_point("jd")

# Flow
full_workflow.add_edge("jd", "parser")

# Parallel section
full_workflow.add_edge("parser", "skills")
full_workflow.add_edge("parser", "ats")

full_workflow.add_edge("skills", "match")
full_workflow.add_edge("ats", "match")

# Sequential heavy pipeline
full_workflow.add_edge("match", "rag")
full_workflow.add_edge("rag", "rewrite")
full_workflow.add_edge("rewrite", "draft")
full_workflow.add_edge("draft", "critic")

# Compile
full_graph = full_workflow.compile()


ranking_workflow = StateGraph(ResumeState)

# Nodes (only essential ones)
ranking_workflow.add_node("jd", jd_agent)
ranking_workflow.add_node("parser", parser_agent)
ranking_workflow.add_node("skills", skill_agent)
ranking_workflow.add_node("ats", ats_agent)
ranking_workflow.add_node("match", match_agent)

# Entry
ranking_workflow.set_entry_point("jd")

# Flow
ranking_workflow.add_edge("jd", "parser")

# Parallel
ranking_workflow.add_edge("parser", "skills")
ranking_workflow.add_edge("parser", "ats")

ranking_workflow.add_edge("skills", "match")
ranking_workflow.add_edge("ats", "match")

# Compile
ranking_graph = ranking_workflow.compile()


__all__ = ["full_graph", "ranking_graph"]
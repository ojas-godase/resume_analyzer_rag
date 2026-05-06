def ranking_agent(results):

    ranked = []

    for r in results:

        skill = r.get("skill_match_score", 0)
        ats = r.get("ats_score", 0)
        semantic = r.get("resume_jd_similarity", 0)

        final = round(
            0.5 * skill +
            0.3 * semantic +
            0.2 * ats,
            2
        )

        ranked.append({
            "resume": r["resume_name"],
            "skill_match": skill,
            "semantic_similarity": semantic,
            "ats_score": ats,
            "final_score": final
        })

    ranked.sort(key=lambda x: x["final_score"], reverse=True)

    return ranked
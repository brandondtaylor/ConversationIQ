"""
Focus Group Analyzer - Analyzes focus group conversations to extract insights.
Identifies consensus, disagreements, influential agents, and discussion flow.
"""
from typing import Dict, Any, List, Optional
import logging
from collections import Counter
import re

logger = logging.getLogger(__name__)


class FocusGroupAnalyzer:
    """
    Analyzes focus group conversation transcripts to provide insights:
    - Consensus vs. disagreement points
    - Most influential agents
    - Discussion flow visualization
    - Key themes and patterns
    """

    def __init__(self, raw_evaluation: Dict[str, Any]):
        """
        Initialize analyzer with raw evaluation data from focus group.

        Args:
            raw_evaluation: Raw evaluation dict containing conversation_transcript and individual_perspectives
        """
        self.raw_evaluation = raw_evaluation
        self.transcript = raw_evaluation.get("conversation_transcript", [])
        self.individual_perspectives = raw_evaluation.get("individual_perspectives", [])
        self.num_agents = raw_evaluation.get("num_agents", 0)

    def analyze(self) -> Dict[str, Any]:
        """
        Perform complete analysis of the focus group discussion.

        Returns:
            Dict with all analysis results
        """
        return {
            "consensus_points": self._identify_consensus(),
            "disagreement_points": self._identify_disagreements(),
            "influential_agents": self._identify_influential_agents(),
            "discussion_flow": self._analyze_discussion_flow(),
            "key_themes": self._extract_key_themes(),
            "participation_balance": self._analyze_participation()
        }

    def _identify_consensus(self) -> List[Dict[str, Any]]:
        """
        Identify points where agents agree or reach consensus.

        Returns:
            List of consensus points with supporting agents
        """
        consensus_points = []

        # Extract themes from likes (things agents agreed on)
        all_likes = []
        for perspective in self.individual_perspectives:
            perspective_text = perspective.get("perspective", "").lower()
            # Look for positive keywords
            if any(word in perspective_text for word in ['like', 'good', 'excellent', 'appreciate', 'well done']):
                all_likes.append(perspective.get("agent_name"))

        # Extract themes from dislikes (things agents agreed were problems)
        all_dislikes = []
        for perspective in self.individual_perspectives:
            perspective_text = perspective.get("perspective", "").lower()
            if any(word in perspective_text for word in ['dislike', 'problem', 'issue', 'concern', 'lacking']):
                all_dislikes.append(perspective.get("agent_name"))

        if len(all_likes) >= self.num_agents / 2:
            consensus_points.append({
                "type": "positive",
                "description": "Agents generally liked aspects of the response",
                "supporting_agents": all_likes,
                "strength": len(all_likes) / max(self.num_agents, 1)
            })

        if len(all_dislikes) >= self.num_agents / 2:
            consensus_points.append({
                "type": "negative",
                "description": "Agents identified common concerns or issues",
                "supporting_agents": all_dislikes,
                "strength": len(all_dislikes) / max(self.num_agents, 1)
            })

        return consensus_points

    def _identify_disagreements(self) -> List[Dict[str, Any]]:
        """
        Identify points where agents disagree.

        Returns:
            List of disagreement points with opposing viewpoints
        """
        disagreements = []

        # Look for conflicting perspectives
        ratings = []
        for perspective in self.individual_perspectives:
            perspective_text = perspective.get("perspective", "")
            rating_match = re.search(r'\b([1-9]|10)\s*(?:/\s*10|out of 10)\b', perspective_text.lower())
            if rating_match:
                ratings.append({
                    "agent": perspective.get("agent_name"),
                    "rating": float(rating_match.group(1))
                })

        if len(ratings) >= 2:
            rating_values = [r["rating"] for r in ratings]
            rating_variance = max(rating_values) - min(rating_values)

            if rating_variance >= 4:  # Significant disagreement
                disagreements.append({
                    "type": "rating_disagreement",
                    "description": f"Significant rating variance ({rating_variance} points)",
                    "low_raters": [r["agent"] for r in ratings if r["rating"] <= 5],
                    "high_raters": [r["agent"] for r in ratings if r["rating"] >= 8],
                    "variance": rating_variance
                })

        return disagreements

    def _identify_influential_agents(self) -> List[Dict[str, Any]]:
        """
        Identify which agents were most influential in the discussion.

        Returns:
            List of agents ranked by influence with metrics
        """
        agent_influence = []

        # Count speaking turns per agent
        speaking_counts = Counter()
        message_lengths = {}

        for turn in self.transcript:
            speaker = turn.get("speaker", "")
            message = turn.get("message", "")

            if speaker != "system":
                speaking_counts[speaker] += 1
                if speaker not in message_lengths:
                    message_lengths[speaker] = []
                message_lengths[speaker].append(len(message))

        # Calculate influence scores
        for agent_name, count in speaking_counts.most_common():
            avg_message_length = sum(message_lengths.get(agent_name, [0])) / max(len(message_lengths.get(agent_name, [1])), 1)

            agent_influence.append({
                "agent_name": agent_name,
                "speaking_turns": count,
                "avg_message_length": round(avg_message_length, 1),
                "influence_score": count * (avg_message_length / 100)  # Weighted by both quantity and depth
            })

        # Sort by influence score
        agent_influence.sort(key=lambda x: x["influence_score"], reverse=True)

        return agent_influence

    def _analyze_discussion_flow(self) -> Dict[str, Any]:
        """
        Analyze the flow of discussion - who spoke when and to whom.

        Returns:
            Dict with discussion flow visualization data
        """
        flow = {
            "total_turns": len(self.transcript),
            "sequence": [],
            "interaction_matrix": {}  # Who followed whom in speaking
        }

        # Build sequence
        previous_speaker = None
        for turn in self.transcript:
            speaker = turn.get("speaker", "")
            message_preview = turn.get("message", "")[:100]

            flow["sequence"].append({
                "speaker": speaker,
                "message_preview": message_preview,
                "type": turn.get("type", "unknown")
            })

            # Track interaction patterns
            if previous_speaker and speaker != "system":
                interaction_key = f"{previous_speaker} -> {speaker}"
                flow["interaction_matrix"][interaction_key] = flow["interaction_matrix"].get(interaction_key, 0) + 1

            previous_speaker = speaker if speaker != "system" else previous_speaker

        return flow

    def _extract_key_themes(self) -> List[Dict[str, Any]]:
        """
        Extract key themes discussed in the focus group.

        Returns:
            List of themes with frequency and agents who mentioned them
        """
        themes = []

        # Common evaluation themes to look for
        theme_keywords = {
            "clarity": ["clear", "clarity", "understand", "confusing", "ambiguous"],
            "helpfulness": ["helpful", "useful", "practical", "actionable"],
            "completeness": ["complete", "comprehensive", "thorough", "missing", "lacking"],
            "tone": ["tone", "friendly", "professional", "polite", "rude"],
            "accuracy": ["accurate", "correct", "wrong", "error", "mistake"],
            "brevity": ["concise", "brief", "lengthy", "verbose", "long"]
        }

        for theme_name, keywords in theme_keywords.items():
            mentioning_agents = []
            mention_count = 0

            for perspective in self.individual_perspectives:
                perspective_text = perspective.get("perspective", "").lower()
                agent_name = perspective.get("agent_name")

                for keyword in keywords:
                    if keyword in perspective_text:
                        if agent_name not in mentioning_agents:
                            mentioning_agents.append(agent_name)
                        mention_count += 1

            if mention_count > 0:
                themes.append({
                    "theme": theme_name,
                    "mention_count": mention_count,
                    "mentioning_agents": mentioning_agents,
                    "relevance": len(mentioning_agents) / max(self.num_agents, 1)
                })

        # Sort by relevance
        themes.sort(key=lambda x: x["relevance"], reverse=True)

        return themes

    def _analyze_participation(self) -> Dict[str, Any]:
        """
        Analyze participation balance in the discussion.

        Returns:
            Dict with participation metrics
        """
        speaker_counts = Counter()

        for turn in self.transcript:
            speaker = turn.get("speaker", "")
            if speaker != "system":
                speaker_counts[speaker] += 1

        total_turns = sum(speaker_counts.values())

        participation_data = []
        for agent, count in speaker_counts.items():
            participation_data.append({
                "agent": agent,
                "turns": count,
                "percentage": round((count / max(total_turns, 1)) * 100, 1)
            })

        # Calculate balance score (0-1, where 1 is perfectly balanced)
        if len(participation_data) > 0:
            expected_per_agent = total_turns / len(participation_data)
            variance = sum(abs(p["turns"] - expected_per_agent) for p in participation_data)
            balance_score = max(0, 1 - (variance / (total_turns * 2)))
        else:
            balance_score = 0

        return {
            "participation_by_agent": participation_data,
            "balance_score": round(balance_score, 2),
            "total_turns": total_turns
        }


def analyze_focus_group_evaluation(evaluation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convenience function to analyze a focus group evaluation.

    Args:
        evaluation: Evaluation dict with raw_evaluation field

    Returns:
        Analysis results or None if not a focus group evaluation
    """
    raw_eval = evaluation.get("raw_evaluation", {})

    if raw_eval.get("method") != "focus_group_tinytroupe":
        return None

    analyzer = FocusGroupAnalyzer(raw_eval)
    return analyzer.analyze()

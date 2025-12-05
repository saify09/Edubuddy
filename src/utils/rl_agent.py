import random
from typing import Dict, List, Optional

class StudyPathAgent:
    """
    A simple Reinforcement Learning agent (Bandit-like) to recommend study paths.
    State: User's mastery level per topic.
    Action: Recommend a topic to study.
    Reward: Improvement in quiz scores (implicit).
    """
    
    def __init__(self):
        self.mastery_threshold = 0.8
        self.review_threshold = 0.6
        
    def recommend_next_topic(self, topic_performance: Dict[str, float], all_topics: List[str]) -> Dict[str, str]:
        """
        Recommends the next topic based on performance.
        Returns: {'topic': 'Topic Name', 'reason': 'Reason for recommendation'}
        """
        if not topic_performance:
            # Cold start: Recommend the first available topic
            if all_topics:
                return {
                    "topic": all_topics[0],
                    "reason": "Start your journey here! 🚀"
                }
            return {"topic": "General", "reason": "Upload documents to get started."}
            
        # 1. Identify Weak Areas (Needs Review)
        weak_topics = [t for t, score in topic_performance.items() if score < self.review_threshold]
        if weak_topics:
            # Prioritize the one with the lowest score
            target = min(weak_topics, key=lambda t: topic_performance[t])
            return {
                "topic": target,
                "reason": f"Your score in '{target}' is low ({int(topic_performance[target]*100)}%). Let's review it! 📉"
            }
            
        # 2. Identify Mastered Areas (Suggest New or Challenge)
        mastered_topics = [t for t, score in topic_performance.items() if score >= self.mastery_threshold]
        
        # Find topics that haven't been tested yet
        untested_topics = [t for t in all_topics if t not in topic_performance]
        
        if untested_topics:
            # Exploration: Try something new
            target = untested_topics[0]
            return {
                "topic": target,
                "reason": f"You've mastered existing topics. Time to explore '{target}'! 🌟"
            }
            
        if mastered_topics:
            # Exploitation: Challenge on strong topics
            target = random.choice(mastered_topics)
            return {
                "topic": target,
                "reason": f"You're doing great in '{target}'. Keep it up! 🏆"
            }
            
        # 3. Middle Ground (Keep practicing)
        # If everything is between 0.6 and 0.8
        avg_topics = [t for t in topic_performance.keys()]
        if avg_topics:
            target = random.choice(avg_topics)
            return {
                "topic": target,
                "reason": "Keep practicing to reach mastery! 💪"
            }
            
        return {"topic": "General", "reason": "Continue studying."}

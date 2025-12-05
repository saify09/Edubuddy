import numpy as np
import pandas as pd
from typing import List, Dict, Any

class AnalyticsEngine:
    """
    Handles predictive analytics and forecasting for student performance.
    """
    
    @staticmethod
    def forecast_next_score(history: List[int]) -> Dict[str, Any]:
        """
        Predicts the next quiz score using simple linear regression (Least Squares).
        """
        if len(history) < 2:
            return {
                "predicted_score": None,
                "trend": "Insufficient Data",
                "confidence": 0.0,
                "slope": 0.0
            }
        
        # X axis: Attempt numbers (1, 2, 3...)
        X = np.array(range(1, len(history) + 1))
        # Y axis: Scores
        y = np.array(history)
        
        # Calculate slope (m) and intercept (b)
        A = np.vstack([X, np.ones(len(X))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        
        # Predict next value
        next_attempt = len(history) + 1
        predicted_score = m * next_attempt + c
        
        trend = "Improving 🚀" if m > 0.1 else "Declining 📉" if m < -0.1 else "Stable ⚖️"
        
        return {
            "predicted_score": round(predicted_score, 2),
            "trend": trend,
            "slope": m
        }

    @staticmethod
    def analyze_weak_areas(quiz_history_detailed: List[Dict]) -> Dict[str, float]:
        """
        Identifies weak topics based on incorrect answers per source document.
        Returns: {'DocumentName': ErrorRate (0.0-1.0)}
        """
        if not quiz_history_detailed:
            return {}

        topic_stats = {} # {source: {'total': 0, 'wrong': 0}}
        
        for q in quiz_history_detailed:
            source = q.get('source', 'Unknown')
            is_correct = q.get('is_correct', False)
            
            if source not in topic_stats:
                topic_stats[source] = {'total': 0, 'wrong': 0}
            
            topic_stats[source]['total'] += 1
            if not is_correct:
                topic_stats[source]['wrong'] += 1
                
        # Calculate error rates
        weak_areas = {}
        for source, stats in topic_stats.items():
            if stats['total'] > 0:
                error_rate = stats['wrong'] / stats['total']
                if error_rate > 0: # Only include if there are errors
                    weak_areas[source] = round(error_rate, 2)
                    
        # Sort by error rate descending
        return dict(sorted(weak_areas.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def analyze_chapter_performance(quiz_history_detailed: List[Dict]) -> Dict[str, float]:
        """
        Calculates accuracy per topic/chapter.
        Returns: {'TopicName': Accuracy (0.0-1.0)}
        """
        if not quiz_history_detailed:
            return {}

        topic_stats = {} # {topic: {'total': 0, 'correct': 0}}
        
        for q in quiz_history_detailed:
            topic = q.get('topic', 'General')
            if topic not in topic_stats:
                topic_stats[topic] = {'total': 0, 'correct': 0}
            
            topic_stats[topic]['total'] += 1
            if q['is_correct']:
                topic_stats[topic]['correct'] += 1
        
        # Calculate accuracy
        performance = {}
        for topic, stats in topic_stats.items():
            if stats['total'] > 0:
                performance[topic] = round(stats['correct'] / stats['total'], 2)
            
        return performance

    @staticmethod
    def calculate_learning_metrics(slope: float, current_avg: float, max_score: int = 5) -> Dict[str, Any]:
        """
        Calculates Learning Speed and Time-to-Mastery.
        """
        # Learning Speed
        if slope > 0.2:
            speed = "Fast ⚡"
        elif slope > 0.05:
            speed = "Steady 🚶"
        elif slope > -0.05:
            speed = "Plateaued 🐢"
        else:
            speed = "Struggling ⚠️"
            
        # Time to Mastery (Attempts to reach max_score)
        if slope <= 0.01:
            mastery_time = "Indefinite (Slope too low)"
        else:
            remaining = max_score - current_avg
            if remaining <= 0:
                mastery_time = "Mastered! 🎉"
            else:
                attempts_needed = int(remaining / slope)
                mastery_time = f"~{attempts_needed} more attempts"
                
        return {
            "learning_speed": speed,
            "time_to_mastery": mastery_time
        }

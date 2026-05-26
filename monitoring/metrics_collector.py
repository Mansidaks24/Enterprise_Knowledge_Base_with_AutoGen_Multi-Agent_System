from collections import Counter
import random


class MetricsCollector:

    @staticmethod
    def generate_metrics(history):

        total_queries = len(history)

        if total_queries == 0:

            return {

                "total_queries": 0,
                "avg_confidence": 0,
                "active_sessions": 0,
                "agents_running": 5
            }

        confidence_scores = []

        sessions = set()

        for item in history:

            try:

                confidence = item[
                    "processing_steps"
                ]["synthesis"][
                    "confidence_score"
                ]

                confidence_scores.append(
                    confidence
                )

            except:

                pass

            try:

                sessions.add(
                    item["metadata"][
                        "session_id"
                    ]
                )

            except:

                pass

        avg_confidence = round(

            sum(confidence_scores)
            / max(len(confidence_scores), 1),

            2
        )

        return {

            "total_queries":
                total_queries,

            "avg_confidence":
                avg_confidence,

            "active_sessions":
                len(sessions),

            "agents_running":
                5
        }

    @staticmethod
    def generate_analytics(history):

        routing_counter = Counter()

        confidence_distribution = {

            "High": 0,
            "Medium": 0,
            "Low": 0
        }

        for item in history:

            try:

                retrieval_type = item[
                    "processing_steps"
                ]["routing"][
                    "query_type"
                ]

                routing_counter[
                    retrieval_type
                ] += 1

            except:

                pass

            try:

                confidence = item[
                    "processing_steps"
                ]["synthesis"][
                    "confidence_score"
                ]

                if confidence >= 80:

                    confidence_distribution[
                        "High"
                    ] += 1

                elif confidence >= 60:

                    confidence_distribution[
                        "Medium"
                    ] += 1

                else:

                    confidence_distribution[
                        "Low"
                    ] += 1

            except:

                pass

        return {

            "routing_distribution":
                dict(routing_counter),

            "confidence_distribution":
                confidence_distribution
        }
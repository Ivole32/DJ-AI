"""
Main class for prediction models.

Note that this is a placeholder and should be expanded with actual ai prediction logic.
"""

# Import dataset loader
from api.utils.load_dataset import load_dataset

from collections import Counter, defaultdict


class PredictionModel:
    """
    Track prediction model class.
    """

    def __init__(self):
        self.data = load_dataset()
        self.transition, self.id_to_title = self.__train_model()

    def __train_model(self) -> tuple:
        """
        Placeholder for training the real prediction model.
        """
        transitions = defaultdict(Counter)
        id_to_title = {}

        for mix in self.data:
            tracklist = mix.get("tracklist", [])
            ids = []

            for t in tracklist:
                if "id" in t:
                    tid = t["id"]
                    ids.append(tid)
                    id_to_title[tid] = t.get("title", "<unknown>")

            for i in range(len(ids) - 1):
                a, b = ids[i], ids[i + 1]
                transitions[a][b] += 1

        return transitions, id_to_title
        
    def recommend_next(self, track_id: str, top_k: int = 5) -> list[tuple]:
        """
        Recommend next tracks based on the current track ID.

        Args:
            track_id (str): Current track ID.
            top_k (int): Number of top recommendations to return.

        Returns:
            list[tuple]: List of recommended track IDs with their scores.
        """
        if track_id not in self.transition:
            return []

        candidates = self.transition[track_id]
        total = sum(candidates.values())

        scored = [
            (next_id, count / total)
            for next_id, count in candidates.items()
        ]

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
    
    def is_ready(self) -> bool:
        """
        Check if the model is ready.

        Returns:
            bool: True if ready, False otherwise.
        """
        return bool(self.transition and self.id_to_title)


# Example usage / test code
if __name__ == "__main__":
    model = PredictionModel()
    recommendations = model.recommend_next("_BpWjG_10gY", top_k=5)
    print(recommendations)
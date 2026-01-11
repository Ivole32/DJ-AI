"""
Main class for prediction models.
"""


# ML model validation and prediction
from ml_model import quick_validate as validate_model
from ml_model.inference.predict import TrackPredictor

# Track metadata utility
from api.utils.track_metadata import get_track_metadata

# Typing and threading
from typing import Optional
import threading

class PredictionModel:
    """
    Track prediction model class with non-blocking initialization.
    """

    def __init__(self):
        """Lightweight initialization that doesn't block the application startup.
        
        Design Pattern: Non-blocking ML Model Initialization
        - Checks if trained model already exists (fast validation)
        - If model exists, loads predictor immediately
        - If model doesn't exist, sets state to 'Not initialized'
        - Actual training must be triggered via start_background_training()
        - Training runs in daemon thread to not block main application
        
        This allows the FastAPI server to start quickly even if the ML model
        isn't ready yet. The /prediction/status endpoint shows current state.
        
        State Progression:
        'Not initialized' → 'Exporting transitions' → 'Training model' → 'Ready'
        or 'Error: <message>' if something goes wrong
        """
        self._ready = validate_model()
        self._state = "Checking model" if self._ready else "Not initialized"
        self._predictor: Optional[TrackPredictor] = None
        self._training_thread: Optional[threading.Thread] = None
        
        # Load predictor if model already exists
        if self._ready:
            try:
                self._predictor = TrackPredictor()
                self._state = "Ready"
            except Exception as e:
                self._ready = False
                self._state = f"Error loading: {str(e)}"
    
    def start_background_training(self, max_attempts: int = 3) -> None:
        """
        Start training in background thread (non-blocking).
        """
        if self._ready:
            return  # Already ready
        
        if self._training_thread and self._training_thread.is_alive():
            return  # Already training
        
        self._training_thread = threading.Thread(
            target=self.__init_model,
            args=(max_attempts,),
            daemon=True
        )
        self._training_thread.start()

    def __init_model(self, max_attempts: int = 3) -> None:
        """
        Initialize the prediction model in background.
        """
        try:
            for attempt in range(max_attempts):
                self._ready = validate_model()
                if self._ready:
                    break
                
                self._state = f"Exporting transitions ({attempt + 1}/{max_attempts})"
                self.__export_transitions()

                self._state = f"Training model ({attempt + 1}/{max_attempts})"
                self.__train_model()
                
                self._ready = validate_model()

            if self._ready:
                self._state = "Loading predictor"
                self._predictor = TrackPredictor()
                self._state = "Ready"
            else:
                self._state = "Failed to train"
        except Exception as e:
            self._ready = False
            self._state = f"Error: {str(e)}"

    def __export_transitions(self) -> None:
        from ml_model.data_preparation.export_transitions import main as export_main
        export_main()

    def __train_model(self) -> None:
        from ml_model.training.train import main as train_main
        train_main()

    def recommend_next(self, track_id: str, top_k: int = 5) -> list[dict]:
        """
        Recommend next tracks based on the current track ID.

        Args:
            track_id (str): Current track ID.
            top_k (int): Number of top recommendations to return.

        Returns:
            list[dict]: List of recommended tracks with metadata and scores.
            
        Raises:
            RuntimeError: If model is not ready
        """
        if not self._ready or not self._predictor:
            raise RuntimeError(f"Model not ready: {self._state}")
        
        # Get predictions (returns list of tuples: (track_id, score))
        predictions = self._predictor.suggest_next(track_id, top_k=top_k)
        
        # Enrich with metadata
        results = []
        for pred_track_id, score in predictions:
            track_data = {'id': pred_track_id, 'score': float(score)}
            
            # Get metadata
            metadata = get_track_metadata(pred_track_id)
            if metadata:
                track_data['title'] = metadata.get('title')
                track_data['artist'] = metadata.get('artist')
                track_data['bpm'] = metadata.get('bpm')
                track_data['key'] = metadata.get('key')
                track_data['camelot'] = metadata.get('camelot')
                track_data['energy'] = metadata.get('energy')
            
            results.append(track_data)
        
        return results
    
    def is_ready(self) -> tuple[bool, str]:
        """
        Check if the model is ready.

        Returns:
            tuple: (ready status, state description)
        """
        return self._ready, self._state
    
    def get_status(self) -> dict:
        """Get detailed status."""
        is_training = self._training_thread and self._training_thread.is_alive()
        return {
            "ready": self._ready,
            "state": self._state,
            "training": is_training
        }


# Example usage / test code
if __name__ == "__main__":
    model = PredictionModel()
    recommendations = model.recommend_next("_BpWjG_10gY", top_k=5)
    from api.logger.logger import logger
    logger.info(recommendations)
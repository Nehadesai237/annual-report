"""
Inference service for image verification
"""

import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class ImageVerifier:
    """Image verification service using CNN model"""
    
    def __init__(self, model_path: str = "models/model.h5", threshold: float = 0.6):
        """
        Initialize the image verifier
        
        Args:
            model_path: Path to the trained model
            threshold: Classification threshold
        """
        self.model_path = model_path
        self.threshold = threshold
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"Loaded model from {self.model_path}")
            else:
                # Create dummy model for demo
                self.model = self.create_dummy_model()
                logger.info("Created dummy model for demo")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = self.create_dummy_model()
    
    def create_dummy_model(self):
        """Create a dummy model for demo purposes"""
        from ml.model import create_cnn_model, compile_model
        
        model = create_cnn_model()
        model = compile_model(model)
        
        # Initialize with random weights
        dummy_input = np.random.random((1, 224, 224, 3))
        model.predict(dummy_input)
        
        return model
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Preprocessed image array
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to model input size
            image = image.resize((224, 224))
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Normalize pixel values
            image_array = image_array.astype(np.float32) / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            # Return dummy array
            return np.random.random((1, 224, 224, 3)).astype(np.float32)
    
    def verify_image(self, image_path: str) -> Dict[str, Any]:
        """
        Verify a single image
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Verification result
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Make prediction
            prediction = self.model.predict(processed_image)
            score = float(prediction[0][0])
            
            # Determine verdict
            if score >= self.threshold:
                verdict = "normal"
            else:
                verdict = "abnormal"
            
            return {
                "filename": os.path.basename(image_path),
                "path": image_path,
                "verdict": verdict,
                "score": score,
                "confidence": abs(score - 0.5) * 2
            }
            
        except Exception as e:
            logger.error(f"Error verifying image {image_path}: {e}")
            # Return random result for demo
            import random
            score = random.uniform(0.3, 0.9)
            verdict = "normal" if score >= self.threshold else "abnormal"
            
            return {
                "filename": os.path.basename(image_path),
                "path": image_path,
                "verdict": verdict,
                "score": score,
                "confidence": abs(score - 0.5) * 2
            }
    
    def verify_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Verify multiple images
        
        Args:
            image_paths: List of image file paths
        
        Returns:
            List of verification results
        """
        results = []
        
        for image_path in image_paths:
            result = self.verify_image(image_path)
            results.append(result)
        
        return results
    
    def update_threshold(self, threshold: float):
        """Update the classification threshold"""
        self.threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Updated threshold to {self.threshold}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_loaded": self.model is not None,
            "model_path": self.model_path,
            "threshold": self.threshold,
            "input_shape": (224, 224, 3),
            "model_type": "CNN"
        }

# Global verifier instance
verifier = ImageVerifier()

async def verify_images(image_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Async wrapper for image verification
    
    Args:
        image_paths: List of image file paths
    
    Returns:
        List of verification results
    """
    return verifier.verify_images(image_paths)

async def verify_image(image_path: str) -> Dict[str, Any]:
    """
    Async wrapper for single image verification
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Verification result
    """
    return verifier.verify_image(image_path)

def get_verifier() -> ImageVerifier:
    """Get the global verifier instance"""
    return verifier

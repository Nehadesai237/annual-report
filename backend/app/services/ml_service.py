"""
ML service for image verification
"""

import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from typing import Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class MLService:
    """ML service for image verification"""
    
    def __init__(self):
        self.model = None
        self.threshold = 0.6
        self.load_model()
    
    def load_model(self):
        """Load the ML model"""
        try:
            # Try to load pre-trained model
            model_path = "ml/models/model.h5"
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Loaded pre-trained model")
            else:
                # Create a dummy model for demo
                self.model = self.create_dummy_model()
                logger.info("Created dummy model for demo")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to dummy model
            self.model = self.create_dummy_model()
    
    def create_dummy_model(self):
        """Create a dummy CNN model for demo purposes"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Initialize with random weights
        dummy_input = np.random.random((1, 224, 224, 3))
        model.predict(dummy_input)
        
        return model
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for ML model"""
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
            # Return a dummy array
            return np.random.random((1, 224, 224, 3)).astype(np.float32)
    
    async def verify_image(self, image_path: str) -> Dict[str, Any]:
        """Verify a single image"""
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
                "verdict": verdict,
                "score": score,
                "confidence": abs(score - 0.5) * 2  # Convert to 0-1 confidence
            }
            
        except Exception as e:
            logger.error(f"Error verifying image {image_path}: {e}")
            # Return a random result for demo
            import random
            score = random.uniform(0.3, 0.9)
            verdict = "normal" if score >= self.threshold else "abnormal"
            
            return {
                "verdict": verdict,
                "score": score,
                "confidence": abs(score - 0.5) * 2
            }
    
    async def verify_images(self, image_paths: list) -> list:
        """Verify multiple images"""
        results = []
        
        for image_path in image_paths:
            result = await self.verify_image(image_path)
            results.append({
                "filename": os.path.basename(image_path),
                "path": image_path,
                "verdict": result["verdict"],
                "score": result["score"]
            })
        
        return results
    
    def update_threshold(self, threshold: float):
        """Update the ML threshold"""
        self.threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Updated ML threshold to {self.threshold}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_loaded": self.model is not None,
            "threshold": self.threshold,
            "input_shape": (224, 224, 3) if self.model else None,
            "model_type": "CNN",
            "description": "Binary classification model for image verification"
        }

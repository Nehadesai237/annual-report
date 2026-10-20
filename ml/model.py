"""
CNN model definition for image verification
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

def create_cnn_model(input_shape=(224, 224, 3)):
    """
    Create a CNN model for binary image classification
    
    Args:
        input_shape: Input image shape (height, width, channels)
    
    Returns:
        Compiled Keras model
    """
    model = keras.Sequential([
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Fourth convolutional block
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Global average pooling
        layers.GlobalAveragePooling2D(),
        
        # Dense layers
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output layer
        layers.Dense(1, activation='sigmoid')
    ])
    
    return model

def compile_model(model):
    """
    Compile the model with appropriate optimizer and loss function
    
    Args:
        model: Keras model to compile
    
    Returns:
        Compiled model
    """
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    return model

def create_data_generators(train_dir, validation_dir, batch_size=32, img_size=(224, 224)):
    """
    Create data generators for training and validation
    
    Args:
        train_dir: Path to training data directory
        validation_dir: Path to validation data directory
        batch_size: Batch size for training
        img_size: Image size for resizing
    
    Returns:
        Tuple of (train_generator, validation_generator)
    """
    # Data augmentation for training
    train_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        shear_range=0.2,
        fill_mode='nearest'
    )
    
    # No augmentation for validation
    validation_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255
    )
    
    # Create generators
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='binary',
        shuffle=True
    )
    
    validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='binary',
        shuffle=False
    )
    
    return train_generator, validation_generator

def train_model(model, train_generator, validation_generator, epochs=50):
    """
    Train the model
    
    Args:
        model: Compiled Keras model
        train_generator: Training data generator
        validation_generator: Validation data generator
        epochs: Number of training epochs
    
    Returns:
        Training history
    """
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        ),
        keras.callbacks.ModelCheckpoint(
            'models/best_model.h5',
            monitor='val_loss',
            save_best_only=True
        )
    ]
    
    # Train model
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=validation_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def evaluate_model(model, test_generator):
    """
    Evaluate the model on test data
    
    Args:
        model: Trained Keras model
        test_generator: Test data generator
    
    Returns:
        Evaluation metrics
    """
    # Evaluate model
    results = model.evaluate(test_generator, verbose=1)
    
    # Get predictions
    predictions = model.predict(test_generator)
    predicted_classes = (predictions > 0.5).astype(int)
    
    # Get true labels
    true_classes = test_generator.classes
    
    # Calculate additional metrics
    from sklearn.metrics import classification_report, confusion_matrix
    
    report = classification_report(true_classes, predicted_classes)
    cm = confusion_matrix(true_classes, predicted_classes)
    
    return {
        'loss': results[0],
        'accuracy': results[1],
        'precision': results[2],
        'recall': results[3],
        'classification_report': report,
        'confusion_matrix': cm
    }

def save_model(model, path='models/model.h5'):
    """
    Save the trained model
    
    Args:
        model: Trained Keras model
        path: Path to save the model
    """
    model.save(path)
    print(f"Model saved to {path}")

def load_model(path='models/model.h5'):
    """
    Load a trained model
    
    Args:
        path: Path to the saved model
    
    Returns:
        Loaded Keras model
    """
    return keras.models.load_model(path)

def create_dummy_model():
    """
    Create a dummy model for demo purposes
    
    Returns:
        Compiled dummy model
    """
    model = create_cnn_model()
    model = compile_model(model)
    
    # Initialize with random weights
    dummy_input = np.random.random((1, 224, 224, 3))
    model.predict(dummy_input)
    
    return model

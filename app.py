import os
import joblib
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import model_train

app = FastAPI(title="Digit Recognizer API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for the model
model = None

@app.on_event("startup")
def load_model():
    global model
    model_path = "model.pkl"
    
    # Automatically train if model doesn't exist
    if not os.path.exists(model_path):
        print("Model not found. Training model...")
        model_train.train_model()
    
    print("Loading model...")
    model = joblib.load(model_path)
    print("Model loaded successfully.")

class DigitInput(BaseModel):
    image: str  # Base64 encoded image string

@app.post("/predict")
async def predict(input_data: DigitInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Decode base64 image
        header, encoded = input_data.image.split(",", 1) if "," in input_data.image else (None, input_data.image)
        image_data = base64.b64decode(encoded)
        img = Image.open(BytesIO(image_data)).convert('L') # Convert to grayscale
        
        # Resize to 8x8 (to match load_digits dataset)
        img = img.resize((8, 8), Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize to 0-16 range (standard for sklearn digits)
        # Note: sklearn digits data has values from 0 (white) to 16 (black)
        img_array = np.array(img)
        
        # Invert colors if necessary (canvas is usually black stroke on white or vice-versa)
        # We need black background (low values) and white digit (high values) for load_digits?
        # Actually load_digits has 0 for white and 16 for black.
        # Let's map 0-255 to 0-16
        img_array = (255 - img_array) / 16.0 # Assuming drawing is black on white
        
        # Flatten for prediction
        img_flat = img_array.reshape(1, -1)
        
        # Make prediction
        prediction = int(model.predict(img_flat)[0])
        
        # Confidence logic (SVN doesn't give probabilities by default without extra config)
        # We'll just return a mock confidence or use decision_function if we want better
        confidence = 1.0 
        
        return {
            "prediction": str(prediction),
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Digit Recognizer API is running"}

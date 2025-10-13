"""
Advanced Similarity Detection Service
"""
import os
import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings

class SimilarityService:
    """Advanced ML-powered similarity detection service"""
    
    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
        self.sentence_model = None
        self.device = "cuda" if settings.USE_GPU and torch.cuda.is_available() else "cpu"
        self.ready = False
    
    async def initialize(self):
        """Initialize ML models"""
        try:
            print(f"Loading models on device: {self.device}")
            
            # Load CLIP model for image similarity
            print("Loading CLIP model...")
            self.clip_model = CLIPModel.from_pretrained(settings.CLIP_MODEL_NAME)
            self.clip_processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_NAME)
            self.clip_model.to(self.device)
            self.clip_model.eval()
            
            # Load Sentence Transformer for text similarity
            print("Loading Sentence Transformer...")
            self.sentence_model = SentenceTransformer(settings.SENTENCE_MODEL_NAME)
            self.sentence_model.to(self.device)
            
            self.ready = True
            print("All models loaded successfully")
            
        except Exception as e:
            print(f"Failed to initialize models: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.clip_model:
            del self.clip_model
        if self.sentence_model:
            del self.sentence_model
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.ready and self.clip_model is not None and self.sentence_model is not None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        models = []
        if self.clip_model:
            models.append("CLIP")
        if self.sentence_model:
            models.append("SentenceTransformer")
        return models
    
    def get_model_status(self) -> List[Dict[str, Any]]:
        """Get detailed model status"""
        return [
            {
                "name": "CLIP",
                "model_name": settings.CLIP_MODEL_NAME,
                "loaded": self.clip_model is not None,
                "device": self.device,
                "purpose": "Image similarity and visual feature extraction"
            },
            {
                "name": "SentenceTransformer",
                "model_name": settings.SENTENCE_MODEL_NAME,
                "loaded": self.sentence_model is not None,
                "device": self.device,
                "purpose": "Text similarity and semantic understanding"
            }
        ]
    
    async def get_image_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """Get CLIP embedding for an image"""
        try:
            image = Image.open(image_path).convert("RGB")
            
            with torch.no_grad():
                inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
                image_features = self.clip_model.get_image_features(**inputs)
                
                # Normalize the features
                image_features = F.normalize(image_features, p=2, dim=1)
                
                return image_features.cpu().numpy().flatten()
        
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None
    
    async def get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get sentence transformer embedding for text"""
        try:
            with torch.no_grad():
                embedding = self.sentence_model.encode(text, convert_to_tensor=True)
                return embedding.cpu().numpy().flatten()
        
        except Exception as e:
            print(f"Error processing text: {e}")
            return None
    
    def calculate_cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Normalize embeddings
            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2)
            
            return float(similarity)
        
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    async def analyze_file_content(self, file_path: str, analysis_types: List[str]) -> Dict[str, Any]:
        """Analyze file content and extract features"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        result = {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "file_extension": file_path.suffix.lower()
        }
        
        # Extract features based on file type
        if file_path.suffix.lower().lstrip('.') in settings.SUPPORTED_IMAGE_FORMATS:
            if "embedding" in analysis_types:
                embedding = await self.get_image_embedding(str(file_path))
                result["image_embedding"] = embedding.tolist() if embedding is not None else None
            
            if "features" in analysis_types:
                # Additional image features can be added here
                try:
                    with Image.open(file_path) as img:
                        result["image_features"] = {
                            "width": img.width,
                            "height": img.height,
                            "mode": img.mode,
                            "format": img.format
                        }
                except Exception as e:
                    result["image_features"] = {"error": str(e)}
        
        elif file_path.suffix.lower().lstrip('.') in settings.SUPPORTED_TEXT_FORMATS:
            if "embedding" in analysis_types:
                # For text files, read content and get embedding
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()[:10000]  # Limit to first 10k chars
                    
                    embedding = await self.get_text_embedding(text_content)
                    result["text_embedding"] = embedding.tolist() if embedding is not None else None
                    result["text_length"] = len(text_content)
                
                except Exception as e:
                    result["text_embedding"] = None
                    result["error"] = str(e)
        
        return result
    
    async def analyze_batch_similarity(
        self, 
        files: List[Dict[str, Any]], 
        similarity_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """Analyze a batch of files for similarity"""
        
        if len(files) < 2:
            return []
        
        # Group files by type
        image_files = []
        text_files = []
        
        for file_info in files:
            file_path = Path(file_info["path"])
            ext = file_path.suffix.lower().lstrip('.')
            
            if ext in settings.SUPPORTED_IMAGE_FORMATS:
                image_files.append(file_info)
            elif ext in settings.SUPPORTED_TEXT_FORMATS:
                text_files.append(file_info)
        
        groups = []
        processed_files = set()
        
        # Process image files
        if len(image_files) > 1:
            image_groups = await self._find_similar_images(image_files, similarity_threshold)
            for group in image_groups:
                groups.append(group)
                processed_files.update([f["id"] for f in group["all_files"]])
        
        # Process text files
        if len(text_files) > 1:
            text_groups = await self._find_similar_texts(text_files, similarity_threshold)
            for group in text_groups:
                groups.append(group)
                processed_files.update([f["id"] for f in group["all_files"]])
        
        return groups
    
    async def _find_similar_images(
        self, 
        image_files: List[Dict[str, Any]], 
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Find similar images using CLIP embeddings"""
        
        # Get embeddings for all images
        embeddings = {}
        for file_info in image_files:
            embedding = await self.get_image_embedding(file_info["path"])
            if embedding is not None:
                embeddings[file_info["id"]] = {
                    "embedding": embedding,
                    "file_info": file_info
                }
        
        # Find similar groups
        groups = []
        processed = set()
        
        for file_id1, data1 in embeddings.items():
            if file_id1 in processed:
                continue
            
            similar_files = []
            
            for file_id2, data2 in embeddings.items():
                if file_id1 == file_id2 or file_id2 in processed:
                    continue
                
                similarity = self.calculate_cosine_similarity(
                    data1["embedding"], data2["embedding"]
                )
                
                if similarity >= threshold:
                    similar_files.append({
                        "id": file_id2,
                        "similarity": similarity,
                        "reason": f"Visual similarity (CLIP): {similarity:.3f}"
                    })
                    processed.add(file_id2)
            
            if similar_files:
                groups.append({
                    "keep_file_id": file_id1,
                    "similar_files": similar_files,
                    "all_files": [data1["file_info"]] + [data2["file_info"] for data2 in embeddings.values() if data2["file_info"]["id"] in [f["id"] for f in similar_files]]
                })
                processed.add(file_id1)
        
        return groups
    
    async def _find_similar_texts(
        self, 
        text_files: List[Dict[str, Any]], 
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Find similar text files using sentence transformers"""
        
        # Get embeddings for all text files
        embeddings = {}
        for file_info in text_files:
            try:
                with open(file_info["path"], 'r', encoding='utf-8') as f:
                    content = f.read()[:5000]  # First 5k chars
                
                embedding = await self.get_text_embedding(content)
                if embedding is not None:
                    embeddings[file_info["id"]] = {
                        "embedding": embedding,
                        "file_info": file_info,
                        "content_length": len(content)
                    }
            except Exception as e:
                print(f"Error reading text file {file_info['path']}: {e}")
        
        # Find similar groups
        groups = []
        processed = set()
        
        for file_id1, data1 in embeddings.items():
            if file_id1 in processed:
                continue
            
            similar_files = []
            
            for file_id2, data2 in embeddings.items():
                if file_id1 == file_id2 or file_id2 in processed:
                    continue
                
                similarity = self.calculate_cosine_similarity(
                    data1["embedding"], data2["embedding"]
                )
                
                if similarity >= threshold:
                    similar_files.append({
                        "id": file_id2,
                        "similarity": similarity,
                        "reason": f"Semantic similarity: {similarity:.3f}"
                    })
                    processed.add(file_id2)
            
            if similar_files:
                groups.append({
                    "keep_file_id": file_id1,
                    "similar_files": similar_files,
                    "all_files": [data1["file_info"]] + [data2["file_info"] for data2 in embeddings.values() if data2["file_info"]["id"] in [f["id"] for f in similar_files]]
                })
                processed.add(file_id1)
        
        return groups

"""
Enhanced File Upload and Duplicate Detection API
Integrated with ML service for advanced similarity detection
"""
import os
import hashlib
import asyncio
from typing import List, Dict, Optional, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx
import json
from datetime import datetime
import uuid
import magic
from PIL import Image
import imagehash
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix='/dedupe', tags=['Duplicate Detection'])

class ScanOptions(BaseModel):
    enable_hash_scanning: bool = True
    enable_content_scanning: bool = True
    enable_metadata_scanning: bool = True
    similarity_threshold: float = Field(default=0.85, ge=0.5, le=1.0)

class FileMetadata(BaseModel):
    id: str
    original_name: str
    size: int
    mime_type: str
    created_at: datetime
    hash_md5: str
    hash_sha256: str
    perceptual_hash: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class DuplicateMatch(BaseModel):
    file: FileMetadata
    similarity: float
    reason: str
    match_type: str  # 'exact', 'hash', 'content', 'visual'

class DuplicateGroup(BaseModel):
    id: str
    group_index: int
    keep_file: FileMetadata
    duplicates: List[DuplicateMatch]
    reason: str
    total_size_saved: int

class ScanResult(BaseModel):
    upload_id: str
    groups: List[DuplicateGroup]
    total_files: int
    duplicates_found: int
    size_saved: int
    scan_time: float
    scan_options: ScanOptions

class UploadResult(BaseModel):
    upload_id: str
    files: List[FileMetadata]
    message: str

# Utility Functions
def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """Calculate file hash using specified algorithm"""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def get_image_hash(file_path: Path) -> Optional[str]:
    """Calculate perceptual hash for images"""
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None

def get_file_metadata(file_path: Path, original_name: str) -> FileMetadata:
    """Extract comprehensive file metadata"""
    stat = file_path.stat()
    
    # Basic metadata
    metadata = {
        'id': str(uuid.uuid4()),
        'original_name': original_name,
        'size': stat.st_size,
        'created_at': datetime.fromtimestamp(stat.st_ctime),
        'hash_md5': calculate_file_hash(file_path, 'md5'),
        'hash_sha256': calculate_file_hash(file_path, 'sha256')
    }
    
    # Detect MIME type
    try:
        metadata['mime_type'] = magic.from_file(str(file_path), mime=True)
    except Exception:
        metadata['mime_type'] = 'application/octet-stream'
    
    # Image-specific metadata
    if metadata['mime_type'].startswith('image/'):
        try:
            with Image.open(file_path) as img:
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['perceptual_hash'] = get_image_hash(file_path)
        except Exception:
            pass
    
    return FileMetadata(**metadata)

async def call_ml_service(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Call ML service for advanced similarity detection"""
    try:
        async with httpx.AsyncClient(timeout=settings.ML_SERVICE_TIMEOUT) as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}{endpoint}",
                json=data
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="ML service timeout")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="ML service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML service error: {str(e)}")

@router.post('/upload', response_model=UploadResult)
async def upload_files(
    files: List[UploadFile] = File(..., description="Files to upload and analyze")
) -> UploadResult:
    """Upload files and extract metadata for duplicate detection"""
    
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {settings.MAX_FILES_PER_UPLOAD} allowed"
        )
    
    upload_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR) / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_metadata_list = []
    total_size = 0
    
    try:
        for upload_file in files:
            # Validate file size
            if upload_file.size and upload_file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {upload_file.filename} is too large. Maximum {settings.MAX_FILE_SIZE_MB}MB allowed"
                )
            
            total_size += upload_file.size or 0
            
            # Check total upload size
            if total_size > settings.MAX_TOTAL_UPLOAD_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"Total upload size too large. Maximum {settings.MAX_TOTAL_UPLOAD_SIZE_MB}MB allowed"
                )
            
            # Save file
            file_path = upload_dir / upload_file.filename
            with open(file_path, 'wb') as f:
                content = await upload_file.read()
                f.write(content)
            
            # Extract metadata
            metadata = get_file_metadata(file_path, upload_file.filename)
            file_metadata_list.append(metadata)
    
    except Exception as e:
        # Cleanup on error
        import shutil
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    return UploadResult(
        upload_id=upload_id,
        files=file_metadata_list,
        message=f"Successfully uploaded {len(files)} files"
    )

@router.post('/scan', response_model=ScanResult)
async def scan_duplicates(
    upload_id: str,
    enable_hash_scanning: bool = True,
    enable_content_scanning: bool = True,
    enable_metadata_scanning: bool = True,
    similarity_threshold: float = 0.85
) -> ScanResult:
    """Scan uploaded files for duplicates using multiple detection methods"""
    
    start_time = asyncio.get_event_loop().time()
    
    options = ScanOptions(
        enable_hash_scanning=enable_hash_scanning,
        enable_content_scanning=enable_content_scanning,
        enable_metadata_scanning=enable_metadata_scanning,
        similarity_threshold=similarity_threshold
    )
    
    upload_dir = Path(settings.UPLOAD_DIR) / upload_id
    if not upload_dir.exists():
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Get file metadata
    files = []
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            metadata = get_file_metadata(file_path, file_path.name)
            files.append(metadata)
    
    if not files:
        raise HTTPException(status_code=400, detail="No files found in upload")
    
    duplicate_groups = []
    processed_files = set()
    group_index = 0
    total_size_saved = 0
    
    # 1. Hash-based duplicate detection (fastest)
    if options.enable_hash_scanning:
        hash_groups = {}
        for file_meta in files:
            if file_meta.id in processed_files:
                continue
            
            hash_key = file_meta.hash_sha256
            if hash_key not in hash_groups:
                hash_groups[hash_key] = []
            hash_groups[hash_key].append(file_meta)
        
        # Process hash-based duplicates
        for hash_key, group_files in hash_groups.items():
            if len(group_files) > 1:
                keep_file = min(group_files, key=lambda f: f.created_at)
                duplicates = [
                    DuplicateMatch(
                        file=f,
                        similarity=1.0,
                        reason="Identical file hash",
                        match_type="exact"
                    )
                    for f in group_files if f.id != keep_file.id
                ]
                
                if duplicates:
                    size_saved = sum(d.file.size for d in duplicates)
                    duplicate_groups.append(DuplicateGroup(
                        id=str(uuid.uuid4()),
                        group_index=group_index,
                        keep_file=keep_file,
                        duplicates=duplicates,
                        reason="Exact hash match",
                        total_size_saved=size_saved
                    ))
                    
                    total_size_saved += size_saved
                    group_index += 1
                    
                    # Mark all files in this group as processed
                    for f in group_files:
                        processed_files.add(f.id)
    
    # 2. Perceptual hash for images (visual similarity)
    if options.enable_metadata_scanning:
        image_files = [
            f for f in files 
            if f.mime_type.startswith('image/') and f.perceptual_hash and f.id not in processed_files
        ]
        
        phash_groups = {}
        for file_meta in image_files:
            phash = file_meta.perceptual_hash
            if not phash:
                continue
                
            # Find similar perceptual hashes
            found_group = False
            for existing_phash, group_files in phash_groups.items():
                # Calculate Hamming distance for perceptual hashes
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(phash, existing_phash))
                similarity = 1.0 - (hamming_distance / len(phash))
                
                if similarity >= options.similarity_threshold:
                    group_files.append(file_meta)
                    found_group = True
                    break
            
            if not found_group:
                phash_groups[phash] = [file_meta]
        
        # Process perceptual hash groups
        for phash, group_files in phash_groups.items():
            if len(group_files) > 1:
                keep_file = min(group_files, key=lambda f: f.created_at)
                duplicates = []
                
                for f in group_files:
                    if f.id != keep_file.id:
                        # Calculate actual similarity
                        hamming_distance = sum(c1 != c2 for c1, c2 in zip(f.perceptual_hash, keep_file.perceptual_hash))
                        similarity = 1.0 - (hamming_distance / len(f.perceptual_hash))
                        
                        duplicates.append(DuplicateMatch(
                            file=f,
                            similarity=similarity,
                            reason="Visually similar image",
                            match_type="visual"
                        ))
                
                if duplicates:
                    size_saved = sum(d.file.size for d in duplicates)
                    duplicate_groups.append(DuplicateGroup(
                        id=str(uuid.uuid4()),
                        group_index=group_index,
                        keep_file=keep_file,
                        duplicates=duplicates,
                        reason="Visual similarity (perceptual hash)",
                        total_size_saved=size_saved
                    ))
                    
                    total_size_saved += size_saved
                    group_index += 1
                    
                    # Mark files as processed
                    for f in group_files:
                        processed_files.add(f.id)
    
    # 3. Content-based similarity using ML service
    if options.enable_content_scanning:
        unprocessed_files = [f for f in files if f.id not in processed_files]
        
        if len(unprocessed_files) > 1:
            try:
                # Prepare data for ML service
                ml_data = {
                    "files": [
                        {
                            "id": f.id,
                            "path": str(upload_dir / f.original_name),
                            "mime_type": f.mime_type,
                            "size": f.size
                        }
                        for f in unprocessed_files
                    ],
                    "similarity_threshold": options.similarity_threshold
                }
                
                # Call ML service for content analysis
                ml_result = await call_ml_service("/analyze/similarity", ml_data)
                
                # Process ML results
                for group_data in ml_result.get("groups", []):
                    keep_file_id = group_data["keep_file_id"]
                    similar_files = group_data["similar_files"]
                    
                    keep_file = next(f for f in unprocessed_files if f.id == keep_file_id)
                    duplicates = []
                    
                    for similar_file_data in similar_files:
                        similar_file = next(f for f in unprocessed_files if f.id == similar_file_data["id"])
                        duplicates.append(DuplicateMatch(
                            file=similar_file,
                            similarity=similar_file_data["similarity"],
                            reason=similar_file_data["reason"],
                            match_type="content"
                        ))
                    
                    if duplicates:
                        size_saved = sum(d.file.size for d in duplicates)
                        duplicate_groups.append(DuplicateGroup(
                            id=str(uuid.uuid4()),
                            group_index=group_index,
                            keep_file=keep_file,
                            duplicates=duplicates,
                            reason=f"Content similarity (AI analysis)",
                            total_size_saved=size_saved
                        ))
                        
                        total_size_saved += size_saved
                        group_index += 1
                        
                        # Mark files as processed
                        processed_files.add(keep_file.id)
                        for d in duplicates:
                            processed_files.add(d.file.id)
            
            except Exception as e:
                # Log ML service error but continue with other methods
                print(f"ML service error: {e}")
    
    end_time = asyncio.get_event_loop().time()
    scan_time = end_time - start_time
    
    return ScanResult(
        upload_id=upload_id,
        groups=duplicate_groups,
        total_files=len(files),
        duplicates_found=sum(len(group.duplicates) for group in duplicate_groups),
        size_saved=total_size_saved,
        scan_time=scan_time,
        scan_options=options
    )

@router.get('/results/{upload_id}')
async def get_scan_results(upload_id: str):
    """Get cached scan results for an upload"""
    # Implementation for retrieving cached results
    # This would typically query a database
    pass

@router.post('/download')
async def download_files(
    upload_id: str,
    file_ids: List[str]
):
    """Download selected files as ZIP"""
    upload_dir = Path(settings.UPLOAD_DIR) / upload_id
    if not upload_dir.exists():
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Implementation for creating and streaming ZIP file
    # This would package the selected files into a ZIP archive
    pass

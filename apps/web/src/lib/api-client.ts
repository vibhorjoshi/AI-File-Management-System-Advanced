/**
 * Enhanced API client for file upload and duplicate scanning
 */

interface UploadedFile {
  id: string;
  original_name: string;
  size: number;
  mime_type: string;
  created_at: string;
  hash_md5: string;
  hash_sha256: string;
  perceptual_hash?: string;
  width?: number;
  height?: number;
}

export interface UploadResponse {
  upload_id: string;
  files: UploadedFile[];
  message: string;
}

interface DuplicateMatch {
  file: UploadedFile;
  similarity: number;
  reason: string;
  match_type: string;
}

interface DuplicateGroup {
  id: string;
  group_index: number;
  keep_file: UploadedFile;
  duplicates: DuplicateMatch[];
  reason: string;
  total_size_saved: number;
}

export interface ScanResponse {
  upload_id: string;
  groups: DuplicateGroup[];
  total_files: number;
  duplicates_found: number;
  size_saved: number;
  scan_time: number;
  scan_options: {
    enable_hash_scanning: boolean;
    enable_content_scanning: boolean;
    enable_metadata_scanning: boolean;
    similarity_threshold: number;
  };
}

export interface ScanOptions {
  enableHashScanning?: boolean;
  enableContentScanning?: boolean;
  enableMetadataScanning?: boolean;
  similarityThreshold?: number;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Upload files to the server
   */
  async uploadFiles(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${this.baseUrl}/api/dedupe/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Scan uploaded files for duplicates
   */
  async scanDuplicates(
    uploadId: string,
    options: ScanOptions = {}
  ): Promise<ScanResponse> {
    const {
      enableHashScanning = true,
      enableContentScanning = true,
      enableMetadataScanning = true,
      similarityThreshold = 0.85,
    } = options;

    const params = new URLSearchParams({
      upload_id: uploadId,
      enable_hash_scanning: String(enableHashScanning),
      enable_content_scanning: String(enableContentScanning),
      enable_metadata_scanning: String(enableMetadataScanning),
      similarity_threshold: String(similarityThreshold),
    });

    const response = await fetch(`${this.baseUrl}/api/dedupe/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Scan failed' }));
      throw new Error(errorData.detail || `Scan failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get scan results for an upload ID
   */
  async getScanResults(uploadId: string): Promise<ScanResponse> {
    const response = await fetch(`${this.baseUrl}/api/dedupe/results/${uploadId}`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to get results' }));
      throw new Error(errorData.detail || `Failed to get results with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Download selected files as ZIP
   */
  async downloadFiles(uploadId: string, fileIds: string[]): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/dedupe/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        upload_id: uploadId,
        file_ids: fileIds,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Download failed' }));
      throw new Error(errorData.detail || `Download failed with status ${response.status}`);
    }

    return response.blob();
  }

  /**
   * Health check for API
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
export default apiClient;

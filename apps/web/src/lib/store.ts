import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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

interface ScanResults {
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

interface UploadData {
  upload_id: string;
  files: UploadedFile[];
  message: string;
  scanResults?: ScanResults;
}

interface UploadStore {
  uploadData: UploadData | null;
  isUploading: boolean;
  isScanning: boolean;
  uploadProgress: number;
  scanProgress: number;
  setUploadData: (uploadId: string, data: UploadData) => void;
  clearUploadData: () => void;
  setIsUploading: (isUploading: boolean) => void;
  setIsScanning: (isScanning: boolean) => void;
  setUploadProgress: (progress: number) => void;
  setScanProgress: (progress: number) => void;
}

export const useUploadStore = create<UploadStore>()(n  persist(
    (set) => ({
      uploadData: null,
      isUploading: false,
      isScanning: false,
      uploadProgress: 0,
      scanProgress: 0,
      
      setUploadData: (uploadId: string, data: UploadData) => {
        set({ uploadData: { ...data, upload_id: uploadId } });
      },
      
      clearUploadData: () => {
        set({
          uploadData: null,
          isUploading: false,
          isScanning: false,
          uploadProgress: 0,
          scanProgress: 0,
        });
      },
      
      setIsUploading: (isUploading: boolean) => {
        set({ isUploading });
      },
      
      setIsScanning: (isScanning: boolean) => {
        set({ isScanning });
      },
      
      setUploadProgress: (uploadProgress: number) => {
        set({ uploadProgress });
      },
      
      setScanProgress: (scanProgress: number) => {
        set({ scanProgress });
      },
    }),
    {
      name: 'ai-cleanup-upload-store',
      partialize: (state) => ({ uploadData: state.uploadData }),
    }
  )
);

export type { UploadData, ScanResults, DuplicateGroup, DuplicateMatch, UploadedFile };

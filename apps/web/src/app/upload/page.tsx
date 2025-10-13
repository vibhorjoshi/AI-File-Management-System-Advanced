'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  FileDropzone,
  Progress,
  LoadingSpinner,
} from '@ai-cleanup/ui';
import { apiClient } from '@/lib/api-client';
import { useUploadStore } from '@/lib/store';
import { Upload, FileIcon, CheckCircle, Search, Zap, Settings } from 'lucide-react';

export default function UploadPage() {
  const router = useRouter();
  const setUploadData = useUploadStore((state) => state.setUploadData);
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [scanProgress, setScanProgress] = useState(0);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [scanComplete, setScanComplete] = useState(false);
  const [error, setError] = useState('');
  const [scanOptions, setScanOptions] = useState({
    enableHashScanning: true,
    enableContentScanning: true,
    enableMetadataScanning: true,
    similarityThreshold: 0.85
  });

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setError('');
    setUploadComplete(false);
    setScanComplete(false);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select files to upload');
      return;
    }

    setIsUploading(true);
    setError('');
    setUploadProgress(0);
    setScanProgress(0);

    try {
      // Step 1: Upload files
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      const uploadResult = await apiClient.uploadFiles(files);
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadComplete(true);

      // Step 2: Start duplicate scanning
      setIsScanning(true);
      const scanProgressInterval = setInterval(() => {
        setScanProgress((prev) => Math.min(prev + 15, 90));
      }, 300);

      const scanResult = await apiClient.scanDuplicates(uploadResult.uploadId, {
        enableHashScanning: scanOptions.enableHashScanning,
        enableContentScanning: scanOptions.enableContentScanning,
        enableMetadataScanning: scanOptions.enableMetadataScanning,
        similarityThreshold: scanOptions.similarityThreshold
      });

      clearInterval(scanProgressInterval);
      setScanProgress(100);
      setScanComplete(true);

      // Store upload and scan data
      setUploadData(uploadResult.uploadId, {
        ...uploadResult,
        scanResults: scanResult
      });

      // Navigate to results page after a short delay
      setTimeout(() => {
        router.push('/results');
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload or scanning failed');
      setUploadProgress(0);
      setScanProgress(0);
    } finally {
      setIsUploading(false);
      setIsScanning(false);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setUploadComplete(false);
    setScanComplete(false);
    setUploadProgress(0);
    setScanProgress(0);
    setError('');
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight">Upload Your Files</h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Upload your files and let our AI detect duplicates. We support images, PDFs, and text
              files with advanced similarity detection.
            </p>
          </div>

          {/* Upload Card */}
          <Card>
            <CardHeader>
              <CardTitle>Select Files</CardTitle>
              <CardDescription>
                Drag and drop files or click to browse. Maximum 10MB per file, 100 files total.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FileDropzone
                onFilesSelected={handleFilesSelected}
                accept={{
                  'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
                  'application/pdf': ['.pdf'],
                  'text/plain': ['.txt'],
                }}
                maxSize={10 * 1024 * 1024}
                multiple
                disabled={isUploading || isScanning}
              />

              {/* Scan Options */}
              {files.length > 0 && !isUploading && !isScanning && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="w-5 h-5" />
                      Scan Options
                    </CardTitle>
                    <CardDescription>
                      Configure how you want to scan for duplicates
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="hashScanning"
                          checked={scanOptions.enableHashScanning}
                          onChange={(e) => 
                            setScanOptions({...scanOptions, enableHashScanning: e.target.checked})
                          }
                        />
                        <label htmlFor="hashScanning" className="text-sm">
                          Hash-based scanning (fastest)
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="contentScanning"
                          checked={scanOptions.enableContentScanning}
                          onChange={(e) => 
                            setScanOptions({...scanOptions, enableContentScanning: e.target.checked})
                          }
                        />
                        <label htmlFor="contentScanning" className="text-sm">
                          Content-based scanning (AI)
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="metadataScanning"
                          checked={scanOptions.enableMetadataScanning}
                          onChange={(e) => 
                            setScanOptions({...scanOptions, enableMetadataScanning: e.target.checked})
                          }
                        />
                        <label htmlFor="metadataScanning" className="text-sm">
                          Metadata scanning
                        </label>
                      </div>
                      <div className="flex flex-col space-y-2">
                        <label htmlFor="similarity" className="text-sm">
                          Similarity Threshold: {Math.round(scanOptions.similarityThreshold * 100)}%
                        </label>
                        <input
                          type="range"
                          id="similarity"
                          min="0.5"
                          max="1"
                          step="0.05"
                          value={scanOptions.similarityThreshold}
                          onChange={(e) => 
                            setScanOptions({...scanOptions, similarityThreshold: parseFloat(e.target.value)})
                          }
                          className="w-full"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Upload Progress */}
              {isUploading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      Uploading {files.length} file(s)...
                    </span>
                    <span className="font-medium">{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} />
                </div>
              )}

              {/* Scan Progress */}
              {isScanning && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground flex items-center gap-2">
                      <Search className="w-4 h-4" />
                      Scanning for duplicates...
                    </span>
                    <span className="font-medium">{scanProgress}%</span>
                  </div>
                  <Progress value={scanProgress} />
                </div>
              )}

              {/* Scan Complete */}
              {scanComplete && (
                <div className="flex items-center gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
                  <Zap className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium text-blue-600">
                    Scanning complete! Redirecting to results...
                  </span>
                </div>
              )}

              {/* Upload Complete */}
              {uploadComplete && !isScanning && !scanComplete && (
                <div className="flex items-center gap-2 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium text-green-600">
                    Upload complete! Starting scan...
                  </span>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="p-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                  {error}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  onClick={handleUpload}
                  disabled={files.length === 0 || isUploading || isScanning}
                  className="flex-1"
                  size="lg"
                >
                  {isUploading ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Uploading...
                    </>
                  ) : isScanning ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload & Scan Duplicates
                    </>
                  )}
                </Button>
                {files.length > 0 && !isUploading && !isScanning && (
                  <Button variant="outline" onClick={handleClear} size="lg">
                    Clear
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-2">
                  <Search className="w-10 h-10 text-primary" />
                  <h3 className="font-semibold">Smart Detection</h3>
                  <p className="text-sm text-muted-foreground">
                    AI-powered similarity detection finds duplicates even with different names
                  </p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-2">
                  <Zap className="w-10 h-10 text-primary" />
                  <h3 className="font-semibold">Lightning Fast</h3>
                  <p className="text-sm text-muted-foreground">
                    Multiple scanning algorithms from hash-based to AI content analysis
                  </p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-2">
                  <Settings className="w-10 h-10 text-primary" />
                  <h3 className="font-semibold">Configurable</h3>
                  <p className="text-sm text-muted-foreground">
                    Adjust similarity thresholds and scanning methods to your needs
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
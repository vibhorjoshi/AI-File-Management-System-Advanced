'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Badge,
  Checkbox,
  LoadingSpinner,
} from '@ai-cleanup/ui';
import { useUploadStore } from '@/lib/store';
import { apiClient } from '@/lib/api-client';
import {
  FileIcon,
  Download,
  Trash2,
  Eye,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  HardDrive,
  Clock,
  Users,
} from 'lucide-react';

interface FileWithSelection {
  id: string;
  original_name: string;
  size: number;
  mime_type: string;
  selected: boolean;
}

interface DuplicateGroupWithSelection {
  id: string;
  group_index: number;
  keep_file: FileWithSelection;
  duplicates: Array<{
    file: FileWithSelection;
    similarity: number;
    reason: string;
    match_type: string;
  }>;
  reason: string;
  total_size_saved: number;
}

export default function ResultsPage() {
  const router = useRouter();
  const { uploadData, clearUploadData } = useUploadStore();
  const [groups, setGroups] = useState<DuplicateGroupWithSelection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (!uploadData) {
      router.push('/upload');
      return;
    }

    // Process scan results
    const scanResults = uploadData.scanResults;
    if (scanResults?.groups) {
      const processedGroups = scanResults.groups.map(group => ({
        ...group,
        keep_file: { ...group.keep_file, selected: false },
        duplicates: group.duplicates.map(dup => ({
          ...dup,
          file: { ...dup.file, selected: true }, // Duplicates are selected by default
        })),
      }));
      
      setGroups(processedGroups);
      
      // Initialize selected files with duplicates
      const initialSelection = new Set<string>();
      processedGroups.forEach(group => {
        group.duplicates.forEach(dup => {
          if (dup.file.selected) {
            initialSelection.add(dup.file.id);
          }
        });
      });
      setSelectedFiles(initialSelection);
    }
    
    setIsLoading(false);
  }, [uploadData, router]);

  const handleFileSelection = (fileId: string, groupId: string, isKeepFile: boolean = false) => {
    const newSelectedFiles = new Set(selectedFiles);
    
    if (newSelectedFiles.has(fileId)) {
      newSelectedFiles.delete(fileId);
    } else {
      newSelectedFiles.add(fileId);
    }
    
    setSelectedFiles(newSelectedFiles);
    
    // Update the groups state
    setGroups(prevGroups =>
      prevGroups.map(group => {
        if (group.id === groupId) {
          if (isKeepFile) {
            return {
              ...group,
              keep_file: { ...group.keep_file, selected: newSelectedFiles.has(fileId) },
            };
          } else {
            return {
              ...group,
              duplicates: group.duplicates.map(dup => ({
                ...dup,
                file: dup.file.id === fileId 
                  ? { ...dup.file, selected: newSelectedFiles.has(fileId) }
                  : dup.file,
              })),
            };
          }
        }
        return group;
      })
    );
  };

  const handleSelectAllDuplicates = () => {
    const allDuplicateIds = new Set<string>();
    groups.forEach(group => {
      group.duplicates.forEach(dup => {
        allDuplicateIds.add(dup.file.id);
      });
    });
    
    setSelectedFiles(allDuplicateIds);
    
    // Update groups state
    setGroups(prevGroups =>
      prevGroups.map(group => ({
        ...group,
        duplicates: group.duplicates.map(dup => ({
          ...dup,
          file: { ...dup.file, selected: true },
        })),
      }))
    );
  };

  const handleClearSelection = () => {
    setSelectedFiles(new Set());
    
    setGroups(prevGroups =>
      prevGroups.map(group => ({
        ...group,
        keep_file: { ...group.keep_file, selected: false },
        duplicates: group.duplicates.map(dup => ({
          ...dup,
          file: { ...dup.file, selected: false },
        })),
      }))
    );
  };

  const handleDownloadSelected = async () => {
    if (selectedFiles.size === 0 || !uploadData) {
      return;
    }

    setIsDownloading(true);
    try {
      const blob = await apiClient.downloadFiles(uploadData.upload_id, Array.from(selectedFiles));
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `files-${uploadData.upload_id}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Download failed');
    } finally {
      setIsDownloading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getMatchTypeColor = (matchType: string): string => {
    switch (matchType) {
      case 'exact': return 'bg-red-100 text-red-800';
      case 'visual': return 'bg-blue-100 text-blue-800';
      case 'content': return 'bg-purple-100 text-purple-800';
      case 'hash': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-muted-foreground">Processing results...</p>
        </div>
      </div>
    );
  }

  if (!uploadData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-yellow-500 mb-4 mx-auto" />
          <h1 className="text-2xl font-bold mb-2">No Results Found</h1>
          <p className="text-muted-foreground mb-4">Please upload files first to see results.</p>
          <Button onClick={() => router.push('/upload')}>Go to Upload</Button>
        </div>
      </div>
    );
  }

  const { scanResults } = uploadData;
  const totalSizeSaved = groups.reduce((sum, group) => sum + group.total_size_saved, 0);
  const selectedSizeSaved = groups.reduce((sum, group) => {
    const selectedDuplicatesSize = group.duplicates
      .filter(dup => selectedFiles.has(dup.file.id))
      .reduce((dupSum, dup) => dupSum + dup.file.size, 0);
    return sum + selectedDuplicatesSize;
  }, 0);

  return (
    <div className="min-h-screen bg-background">
      <main className="container py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => router.push('/upload')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Upload
              </Button>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Scan Results</h1>
                <p className="text-muted-foreground">
                  {groups.length > 0 
                    ? `Found ${scanResults?.duplicates_found || 0} duplicates in ${groups.length} groups`
                    : 'No duplicates found'
                  }
                </p>
              </div>
            </div>
            <Button
              onClick={() => {
                clearUploadData();
                router.push('/upload');
              }}
              variant="outline"
            >
              New Scan
            </Button>
          </div>

          {/* Summary Stats */}
          {scanResults && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Files</p>
                      <p className="text-2xl font-bold">{scanResults.total_files}</p>
                    </div>
                    <FileIcon className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Duplicates Found</p>
                      <p className="text-2xl font-bold">{scanResults.duplicates_found}</p>
                    </div>
                    <Users className="w-8 h-8 text-orange-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Space Saved</p>
                      <p className="text-2xl font-bold">{formatFileSize(selectedSizeSaved)}</p>
                    </div>
                    <HardDrive className="w-8 h-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Scan Time</p>
                      <p className="text-2xl font-bold">{scanResults.scan_time?.toFixed(2)}s</p>
                    </div>
                    <Clock className="w-8 h-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Action Buttons */}
          {groups.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-wrap gap-4">
                  <Button
                    onClick={handleSelectAllDuplicates}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Select All Duplicates
                  </Button>
                  <Button
                    onClick={handleClearSelection}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    Clear Selection
                  </Button>
                  <Button
                    onClick={handleDownloadSelected}
                    disabled={selectedFiles.size === 0 || isDownloading}
                    className="flex items-center gap-2"
                  >
                    {isDownloading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                    Download Selected ({selectedFiles.size})
                  </Button>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <span>Selected files will save: {formatFileSize(selectedSizeSaved)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
              {error}
            </div>
          )}

          {/* Results */}
          {groups.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <CheckCircle2 className="w-16 h-16 text-green-500 mb-4 mx-auto" />
                  <h2 className="text-2xl font-bold mb-2">No Duplicates Found!</h2>
                  <p className="text-muted-foreground">
                    All your files are unique. No cleanup needed.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {groups.map((group) => (
                <Card key={group.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">
                          Duplicate Group #{group.group_index + 1}
                        </CardTitle>
                        <CardDescription>{group.reason}</CardDescription>
                      </div>
                      <Badge variant="secondary">
                        {group.duplicates.length} duplicate{group.duplicates.length > 1 ? 's' : ''}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Keep File */}
                      <div className="border rounded-lg p-4 bg-green-50 dark:bg-green-900/10">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Checkbox
                              checked={group.keep_file.selected}
                              onCheckedChange={() => handleFileSelection(group.keep_file.id, group.id, true)}
                            />
                            <FileIcon className="w-8 h-8 text-green-600" />
                            <div>
                              <p className="font-medium text-green-800 dark:text-green-200">
                                {group.keep_file.original_name}
                              </p>
                              <p className="text-sm text-green-600 dark:text-green-300">
                                {formatFileSize(group.keep_file.size)} • Keep this file
                              </p>
                            </div>
                          </div>
                          <Badge className="bg-green-600 text-white">Original</Badge>
                        </div>
                      </div>

                      {/* Duplicate Files */}
                      <div className="space-y-2">
                        {group.duplicates.map((duplicate) => (
                          <div key={duplicate.file.id} className="border rounded-lg p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <Checkbox
                                  checked={duplicate.file.selected}
                                  onCheckedChange={() => handleFileSelection(duplicate.file.id, group.id)}
                                />
                                <FileIcon className="w-8 h-8 text-orange-600" />
                                <div>
                                  <p className="font-medium">
                                    {duplicate.file.original_name}
                                  </p>
                                  <p className="text-sm text-muted-foreground">
                                    {formatFileSize(duplicate.file.size)} • 
                                    {Math.round(duplicate.similarity * 100)}% similar • 
                                    {duplicate.reason}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge className={getMatchTypeColor(duplicate.match_type)}>
                                  {duplicate.match_type}
                                </Badge>
                                <Button variant="ghost" size="sm">
                                  <Eye className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="text-right text-sm text-muted-foreground">
                        Potential space saved: {formatFileSize(group.total_size_saved)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

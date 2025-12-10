"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  getProjects,
  getProject,
  updateProject,
  modifyPatterns,
  type Project,
  type HtmlPattern,
} from "@/lib/api";

export default function PatternsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loadingProject, setLoadingProject] = useState(false);
  const [patterns, setPatterns] = useState<HtmlPattern[]>([]);
  const [instruction, setInstruction] = useState("");
  const [modifying, setModifying] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [changesDescription, setChangesDescription] = useState<string | null>(null);

  // Fetch projects on mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await getProjects("active");
        if (response.success && response.projects) {
          setProjects(response.projects);
        }
      } catch (err) {
        console.error("Failed to fetch projects:", err);
      } finally {
        setLoadingProjects(false);
      }
    };
    fetchProjects();
  }, []);

  // Fetch project details when selection changes
  useEffect(() => {
    if (!selectedProjectId) {
      setSelectedProject(null);
      setPatterns([]);
      return;
    }

    const fetchProject = async () => {
      try {
        setLoadingProject(true);
        setError(null);
        setSuccess(null);
        setChangesDescription(null);

        const response = await getProject(selectedProjectId);
        if (response.success && response.project) {
          setSelectedProject(response.project);
          setPatterns(response.project.html_configs?.patterns || []);
        } else {
          setError("Không thể tải thông tin dự án");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Lỗi khi tải dự án");
      } finally {
        setLoadingProject(false);
      }
    };

    fetchProject();
  }, [selectedProjectId]);

  const handleModifyPatterns = async () => {
    if (!instruction.trim()) {
      setError("Vui lòng nhập hướng dẫn chỉnh sửa");
      return;
    }

    try {
      setModifying(true);
      setError(null);
      setSuccess(null);
      setChangesDescription(null);

      const response = await modifyPatterns(patterns, instruction);

      if (response.success && response.patterns) {
        setPatterns(response.patterns);
        setChangesDescription(response.changes_made || null);
        setInstruction("");
      } else {
        setError(response.error || "Không thể chỉnh sửa patterns");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi chỉnh sửa patterns");
    } finally {
      setModifying(false);
    }
  };

  const handleSavePatterns = async () => {
    if (!selectedProjectId) {
      setError("Vui lòng chọn dự án");
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const response = await updateProject(selectedProjectId, {
        html_configs: { patterns },
      });

      if (response.success) {
        setSuccess("Đã lưu patterns thành công!");
        setChangesDescription(null);
      } else {
        setError("Không thể lưu patterns");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi lưu patterns");
    } finally {
      setSaving(false);
    }
  };

  const handleDeletePattern = (index: number) => {
    const newPatterns = patterns.filter((_, i) => i !== index);
    setPatterns(newPatterns);
  };

  const handleResetPatterns = () => {
    if (selectedProject?.html_configs?.patterns) {
      setPatterns(selectedProject.html_configs.patterns);
      setChangesDescription(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Trình Chỉnh Sửa Pattern AI</h1>
          <p className="text-muted-foreground mt-2">
            Chỉnh sửa HTML patterns bằng ngôn ngữ tự nhiên
          </p>
        </div>
        <Link href="/patterns/scan">
          <Button>Quét HTML Mẫu →</Button>
        </Link>
      </div>

      {/* Instructions Card */}
      <Card>
        <CardHeader>
          <CardTitle>Hướng Dẫn</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>1. Chọn dự án bạn muốn chỉnh sửa patterns</p>
          <p>2. Xem danh sách patterns hiện tại của dự án</p>
          <p>3. Nhập hướng dẫn bằng ngôn ngữ tự nhiên để AI chỉnh sửa</p>
          <p>4. Xem trước thay đổi và lưu khi hài lòng</p>
          <div className="mt-4 p-3 bg-muted rounded-md">
            <p className="font-medium text-foreground mb-2">Ví dụ hướng dẫn:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Làm tất cả tiêu đề h2 màu xanh dương</li>
              <li>Thêm class &quot;highlight&quot; cho tất cả đoạn văn</li>
              <li>Làm các link mở ở tab mới</li>
              <li>Xóa tất cả inline style khỏi ảnh</li>
              <li>Thêm padding cho tất cả bảng</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Project Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Chọn Dự Án</CardTitle>
          <CardDescription>
            Chọn dự án để xem và chỉnh sửa HTML patterns
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingProjects ? (
            <Skeleton className="h-10 w-full" />
          ) : (
            <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
              <SelectTrigger>
                <SelectValue placeholder="Chọn dự án..." />
              </SelectTrigger>
              <SelectContent>
                {projects.map((project) => (
                  <SelectItem key={project.project_id} value={project.project_id}>
                    {project.project_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </CardContent>
      </Card>

      {/* Loading State */}
      {loadingProject && (
        <Card>
          <CardContent className="py-8">
            <div className="space-y-3">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error/Success Messages */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <AlertDescription className="text-green-600">{success}</AlertDescription>
        </Alert>
      )}

      {/* Pattern Editor */}
      {selectedProject && !loadingProject && (
        <>
          {/* Current Patterns */}
          <Card>
            <CardHeader>
              <CardTitle>
                Patterns Hiện Tại
                <Badge variant="secondary" className="ml-2">
                  {patterns.length} patterns
                </Badge>
              </CardTitle>
              <CardDescription>
                Các patterns chuyển đổi HTML của dự án {selectedProject.project_name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {patterns.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    Dự án này chưa có patterns nào.
                  </p>
                  <Link href="/patterns/scan">
                    <Button variant="outline">Quét HTML để tạo patterns</Button>
                  </Link>
                </div>
              ) : (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-24">Loại</TableHead>
                        <TableHead>Source Pattern</TableHead>
                        <TableHead>Target Pattern</TableHead>
                        <TableHead className="w-20"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {patterns.map((pattern, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Badge variant="outline">{pattern.element_type}</Badge>
                          </TableCell>
                          <TableCell>
                            <code className="text-xs bg-muted px-2 py-1 rounded break-all">
                              {pattern.source_pattern}
                            </code>
                          </TableCell>
                          <TableCell>
                            <code className="text-xs bg-muted px-2 py-1 rounded break-all">
                              {pattern.target_pattern}
                            </code>
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeletePattern(index)}
                              className="text-red-600 hover:text-red-700"
                            >
                              Xóa
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Modification */}
          <Card>
            <CardHeader>
              <CardTitle>Chỉnh Sửa Bằng AI</CardTitle>
              <CardDescription>
                Nhập hướng dẫn bằng ngôn ngữ tự nhiên để AI chỉnh sửa patterns
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="instruction">Hướng Dẫn Chỉnh Sửa</Label>
                <Textarea
                  id="instruction"
                  placeholder="Ví dụ: Làm tất cả tiêu đề h2 có màu xanh dương và font-weight bold"
                  value={instruction}
                  onChange={(e) => setInstruction(e.target.value)}
                  rows={3}
                  disabled={modifying || patterns.length === 0}
                />
              </div>

              {changesDescription && (
                <Alert>
                  <AlertDescription>
                    <span className="font-medium">Thay đổi:</span> {changesDescription}
                  </AlertDescription>
                </Alert>
              )}

              <div className="flex gap-4">
                <Button
                  onClick={handleModifyPatterns}
                  disabled={modifying || !instruction.trim() || patterns.length === 0}
                  className="flex-1"
                >
                  {modifying ? "Đang xử lý..." : "Áp Dụng Thay Đổi"}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleResetPatterns}
                  disabled={modifying}
                >
                  Hoàn Tác
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Save Actions */}
          <Card>
            <CardContent className="py-4">
              <div className="flex justify-between items-center">
                <p className="text-sm text-muted-foreground">
                  Nhớ lưu thay đổi sau khi chỉnh sửa xong
                </p>
                <Button
                  onClick={handleSavePatterns}
                  disabled={saving}
                >
                  {saving ? "Đang lưu..." : "Lưu Patterns"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* No Project Selected */}
      {!selectedProjectId && !loadingProjects && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              Chọn một dự án để bắt đầu chỉnh sửa patterns
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

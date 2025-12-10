"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
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
  publishBatch,
  type Project,
  type BatchItem,
  type BatchPublishResponse,
} from "@/lib/api";

interface BatchRow {
  id: number;
  selected: boolean;
  url: string;
  keyword: string;
  status: "pending" | "success" | "error";
  statusText: string;
  postUrl?: string;
  postTitle?: string;
}

type PublishState = "idle" | "loading" | "done";

export default function BatchPublishPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [rows, setRows] = useState<BatchRow[]>(() =>
    Array.from({ length: 5 }, (_, i) => ({
      id: i + 1,
      selected: true,
      url: "",
      keyword: "",
      status: "pending" as const,
      statusText: "Đang Chờ",
    }))
  );
  const [publishState, setPublishState] = useState<PublishState>("idle");
  const [result, setResult] = useState<BatchPublishResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  // Update selected project when selection changes
  useEffect(() => {
    if (selectedProjectId) {
      const project = projects.find((p) => p.project_id === selectedProjectId);
      setSelectedProject(project || null);
    } else {
      setSelectedProject(null);
    }
  }, [selectedProjectId, projects]);

  // Check if project uses main_keyword naming
  const needsKeyword =
    selectedProject?.image_configs?.naming_method === "main_keyword";

  const addRow = () => {
    const newId = Math.max(...rows.map((r) => r.id)) + 1;
    setRows([
      ...rows,
      {
        id: newId,
        selected: true,
        url: "",
        keyword: "",
        status: "pending",
        statusText: "Đang Chờ",
      },
    ]);
  };

  const removeRow = (id: number) => {
    if (rows.length > 1) {
      setRows(rows.filter((r) => r.id !== id));
    }
  };

  const updateRow = (id: number, field: keyof BatchRow, value: string | boolean) => {
    setRows(
      rows.map((r) => (r.id === id ? { ...r, [field]: value } : r))
    );
  };

  const toggleSelectAll = (checked: boolean) => {
    setRows(rows.map((r) => ({ ...r, selected: checked })));
  };

  const handleSubmit = async () => {
    // Validation
    if (!selectedProjectId) {
      setError("Vui lòng chọn dự án");
      return;
    }

    const selectedRows = rows.filter((r) => r.selected && r.url.trim());
    if (selectedRows.length === 0) {
      setError("Vui lòng nhập ít nhất một URL Google Docs");
      return;
    }

    if (needsKeyword) {
      const missingKeyword = selectedRows.find((r) => !r.keyword.trim());
      if (missingKeyword) {
        setError("Vui lòng nhập từ khóa chính cho tất cả các bài");
        return;
      }
    }

    try {
      setPublishState("loading");
      setError(null);
      setResult(null);

      // Reset row statuses
      setRows(
        rows.map((r) => ({
          ...r,
          status: r.selected && r.url.trim() ? "pending" : r.status,
          statusText: r.selected && r.url.trim() ? "Đang xử lý..." : r.statusText,
        }))
      );

      const items: BatchItem[] = selectedRows.map((r) => ({
        url: r.url.trim(),
        keyword: r.keyword.trim() || undefined,
      }));

      const response = await publishBatch({
        project_id: selectedProjectId,
        items,
      });

      setResult(response);
      setPublishState("done");

      // Update row statuses based on results
      const resultMap = new Map(response.results.map((r) => [r.url, r]));
      setRows(
        rows.map((row) => {
          const itemResult = resultMap.get(row.url.trim());
          if (itemResult) {
            return {
              ...row,
              status: itemResult.success ? "success" : "error",
              statusText: itemResult.success ? "Thành công" : itemResult.error || "Thất bại",
              postUrl: itemResult.post_url,
              postTitle: itemResult.post_title,
            };
          }
          return row;
        })
      );
    } catch (err) {
      setPublishState("done");
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
    }
  };

  const handleReset = () => {
    setRows(
      Array.from({ length: 5 }, (_, i) => ({
        id: i + 1,
        selected: true,
        url: "",
        keyword: "",
        status: "pending" as const,
        statusText: "Đang Chờ",
      }))
    );
    setPublishState("idle");
    setResult(null);
    setError(null);
  };

  const selectedCount = rows.filter((r) => r.selected && r.url.trim()).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Đăng Hàng Loạt</h1>
          <p className="text-muted-foreground mt-2">
            Đăng nhiều bài từ Google Docs lên WordPress
          </p>
        </div>
        <Link href="/publish">
          <Button variant="outline">← Đăng Một Bài</Button>
        </Link>
      </div>

      {/* Project Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Chọn Dự Án</CardTitle>
          <CardDescription>Chọn trang WordPress để đăng bài</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingProjects ? (
            <p className="text-sm text-muted-foreground">Đang tải danh sách dự án...</p>
          ) : projects.length === 0 ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Chưa có dự án nào. Vui lòng tạo dự án trước.
              </p>
              <Link href="/projects/new">
                <Button>Tạo Dự Án</Button>
              </Link>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                <Label>Dự Án</Label>
                <Select
                  value={selectedProjectId}
                  onValueChange={setSelectedProjectId}
                  disabled={publishState === "loading"}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Chọn dự án..." />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map((project) => (
                      <SelectItem key={project.project_id} value={project.project_id}>
                        {project.project_name} ({project.project_id})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedProject && (
                <Alert>
                  <AlertDescription>
                    Sẽ đăng lên: <strong>{selectedProject.wordpress_url}</strong>
                  </AlertDescription>
                </Alert>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Batch Table */}
      <Card>
        <CardHeader>
          <CardTitle>Danh Sách Bài Viết</CardTitle>
          <CardDescription>
            Nhập URL Google Docs cho từng bài viết
            {needsKeyword && " (yêu cầu từ khóa chính)"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      checked={rows.every((r) => r.selected)}
                      onChange={(e) => toggleSelectAll(e.target.checked)}
                      disabled={publishState === "loading"}
                      className="h-4 w-4"
                    />
                  </TableHead>
                  <TableHead className="w-16">#</TableHead>
                  <TableHead>URL Google Docs</TableHead>
                  {needsKeyword && <TableHead className="w-48">Từ Khóa Chính</TableHead>}
                  <TableHead className="w-32">Trạng Thái</TableHead>
                  <TableHead className="w-16"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row, index) => (
                  <TableRow key={row.id}>
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={row.selected}
                        onChange={(e) => updateRow(row.id, "selected", e.target.checked)}
                        disabled={publishState === "loading"}
                        className="h-4 w-4"
                      />
                    </TableCell>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>
                      <Input
                        placeholder="https://docs.google.com/document/d/..."
                        value={row.url}
                        onChange={(e) => updateRow(row.id, "url", e.target.value)}
                        disabled={publishState === "loading"}
                        className="min-w-[300px]"
                      />
                    </TableCell>
                    {needsKeyword && (
                      <TableCell>
                        <Input
                          placeholder="tu-khoa-chinh"
                          value={row.keyword}
                          onChange={(e) => updateRow(row.id, "keyword", e.target.value)}
                          disabled={publishState === "loading"}
                        />
                      </TableCell>
                    )}
                    <TableCell>
                      <Badge
                        variant={
                          row.status === "success"
                            ? "default"
                            : row.status === "error"
                            ? "destructive"
                            : "secondary"
                        }
                      >
                        {row.statusText}
                      </Badge>
                      {row.postUrl && (
                        <a
                          href={row.postUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-xs text-blue-600 hover:underline mt-1"
                        >
                          Xem bài viết
                        </a>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeRow(row.id)}
                        disabled={publishState === "loading" || rows.length <= 1}
                      >
                        ✕
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={addRow}
              disabled={publishState === "loading"}
            >
              + Thêm Dòng
            </Button>
            <p className="text-sm text-muted-foreground">
              Đã chọn: {selectedCount} bài
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-4">
            <Button
              onClick={handleSubmit}
              disabled={publishState === "loading" || !selectedProjectId || selectedCount === 0}
              className="flex-1"
            >
              {publishState === "loading"
                ? `Đang đăng ${selectedCount} bài...`
                : `Đăng ${selectedCount} Bài Lên WordPress`}
            </Button>
            {publishState === "done" && (
              <Button variant="outline" onClick={handleReset}>
                Đăng Đợt Mới
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {publishState === "loading" && (
        <Card>
          <CardHeader>
            <CardTitle>Đang Đăng Hàng Loạt...</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full animate-pulse w-1/2"></div>
              </div>
              <p className="text-sm text-muted-foreground">
                Đang xử lý {selectedCount} bài viết. Quá trình có thể mất vài phút...
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Summary */}
      {publishState === "done" && result && (
        <Card className={result.success ? "border-green-500" : "border-yellow-500"}>
          <CardHeader>
            <CardTitle className={result.success ? "text-green-600" : "text-yellow-600"}>
              {result.success ? "Đăng Hàng Loạt Hoàn Tất!" : "Đăng Hàng Loạt Hoàn Tất (Có Lỗi)"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-muted rounded-lg">
                <p className="text-2xl font-bold">{result.total}</p>
                <p className="text-sm text-muted-foreground">Tổng Số</p>
              </div>
              <div className="text-center p-4 bg-green-100 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{result.completed}</p>
                <p className="text-sm text-muted-foreground">Thành Công</p>
              </div>
              <div className="text-center p-4 bg-red-100 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{result.failed}</p>
                <p className="text-sm text-muted-foreground">Thất Bại</p>
              </div>
            </div>

            <Alert className="mt-4">
              <AlertDescription>
                <strong>Lưu ý:</strong> Các bài viết được tạo dưới dạng NHÁP. Xem lại và xuất bản
                từ WordPress admin.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Hướng Dẫn</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>1. Chọn dự án WordPress để đăng bài</p>
          <p>2. Nhập URL Google Docs cho từng bài viết</p>
          {needsKeyword && <p>3. Nhập từ khóa chính cho mỗi bài (để đặt tên ảnh)</p>}
          <p>{needsKeyword ? "4" : "3"}. Chọn các bài muốn đăng bằng checkbox</p>
          <p>{needsKeyword ? "5" : "4"}. Nhấn nút &quot;Đăng Lên WordPress&quot; để bắt đầu</p>
          <p className="text-yellow-600 mt-4">
            <strong>Lưu ý:</strong> Quá trình có thể mất vài phút tùy thuộc vào số lượng bài viết.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getProjects, publishSingle, type Project, type PublishResponse } from "@/lib/api";

type PublishState = "idle" | "loading" | "success" | "error";

export default function PublishPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [googleDocsUrl, setGoogleDocsUrl] = useState("");
  const [mainKeyword, setMainKeyword] = useState("");
  const [publishState, setPublishState] = useState<PublishState>("idle");
  const [publishResult, setPublishResult] = useState<PublishResponse | null>(null);
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
  const needsMainKeyword =
    selectedProject?.image_configs?.naming_method === "main_keyword";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!selectedProjectId) {
      setError("Vui lòng chọn dự án");
      return;
    }
    if (!googleDocsUrl.trim()) {
      setError("Vui lòng nhập URL Google Docs");
      return;
    }
    if (needsMainKeyword && !mainKeyword.trim()) {
      setError("Vui lòng nhập từ khóa chính để đặt tên ảnh");
      return;
    }

    try {
      setPublishState("loading");
      setError(null);
      setPublishResult(null);

      const result = await publishSingle({
        google_docs_url: googleDocsUrl.trim(),
        project_id: selectedProjectId,
        main_keyword: mainKeyword.trim() || undefined,
      });

      setPublishResult(result);
      setPublishState(result.success ? "success" : "error");

      if (!result.success) {
        setError(result.error || "Đăng bài thất bại");
      }
    } catch (err) {
      setPublishState("error");
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
    }
  };

  const handleReset = () => {
    setGoogleDocsUrl("");
    setMainKeyword("");
    setPublishState("idle");
    setPublishResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Đăng Một Bài</h1>
          <p className="text-muted-foreground mt-2">
            Đăng nội dung từ Google Docs lên WordPress
          </p>
        </div>
        <Link href="/publish/batch">
          <Button variant="outline">Đăng Hàng Loạt →</Button>
        </Link>
      </div>

      {/* Project Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Chọn Dự Án</CardTitle>
          <CardDescription>
            Chọn trang WordPress để đăng bài
          </CardDescription>
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
                <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
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

      {/* Main Keyword Input (conditionally shown) */}
      {needsMainKeyword && (
        <Card>
          <CardHeader>
            <CardTitle>Từ Khóa Chính Để Đặt Tên Ảnh</CardTitle>
            <CardDescription>
              Dự án này yêu cầu từ khóa chính để đặt tên file ảnh
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Label htmlFor="mainKeyword">Từ Khóa Chính *</Label>
              <Input
                id="mainKeyword"
                placeholder="vd: quat-tran-sunhouse"
                value={mainKeyword}
                onChange={(e) => setMainKeyword(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Ảnh sẽ được đặt tên: tu-khoa-chinh-01, tu-khoa-chinh-02, v.v.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Publish Form */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>URL Google Docs</CardTitle>
            <CardDescription>
              Dán URL tài liệu Google Docs để bắt đầu đăng bài
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="googleDocsUrl">URL Tài Liệu *</Label>
              <Input
                id="googleDocsUrl"
                placeholder="https://docs.google.com/document/d/YOUR_DOC_ID/edit"
                value={googleDocsUrl}
                onChange={(e) => setGoogleDocsUrl(e.target.value)}
                disabled={publishState === "loading"}
              />
              <p className="text-xs text-muted-foreground">
                Hỗ trợ URL edit, view, hoặc published - đều hoạt động!
              </p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={publishState === "loading" || !selectedProjectId}
                className="flex-1"
              >
                {publishState === "loading" ? "Đang đăng bài..." : "Đăng Lên WordPress"}
              </Button>
              {publishState !== "idle" && publishState !== "loading" && (
                <Button type="button" variant="outline" onClick={handleReset}>
                  Đăng Bài Mới
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </form>

      {/* Loading State */}
      {publishState === "loading" && (
        <Card>
          <CardHeader>
            <CardTitle>Đang Đăng Bài...</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full animate-pulse w-3/4"></div>
              </div>
              <p className="text-sm text-muted-foreground">
                Quá trình đăng bài có thể mất 1-2 phút. Vui lòng đợi...
              </p>
              <ul className="text-sm text-muted-foreground space-y-1 ml-4 list-disc">
                <li>Đang chuyển đổi Google Docs...</li>
                <li>Đang xử lý ảnh...</li>
                <li>Đang tải ảnh lên WordPress...</li>
                <li>Đang tạo bài viết...</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Result */}
      {publishState === "success" && publishResult && (
        <Card className="border-green-500">
          <CardHeader>
            <CardTitle className="text-green-600">Đăng Bài Thành Công!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-muted rounded-lg">
                <p className="text-2xl font-bold">{publishResult.post_title || "N/A"}</p>
                <p className="text-sm text-muted-foreground">Tiêu Đề Bài</p>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <p className="text-2xl font-bold">{publishResult.images_processed || 0}</p>
                <p className="text-sm text-muted-foreground">Ảnh Đã Xử Lý</p>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <p className="text-2xl font-bold">
                  {publishResult.execution_time?.toFixed(1) || "0"}s
                </p>
                <p className="text-sm text-muted-foreground">Thời Gian</p>
              </div>
            </div>

            <div className="space-y-2">
              <p className="font-medium">Liên Kết:</p>
              {publishResult.post_url && (
                <p>
                  <strong>Xem Bài Viết: </strong>
                  <a
                    href={publishResult.post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {publishResult.post_url}
                  </a>
                </p>
              )}
              {publishResult.edit_url && (
                <p>
                  <strong>Chỉnh Sửa: </strong>
                  <a
                    href={publishResult.edit_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {publishResult.edit_url}
                  </a>
                </p>
              )}
            </div>

            <Alert>
              <AlertDescription>
                <strong>Lưu ý:</strong> Bài viết được tạo dưới dạng NHÁP. Xem lại và xuất bản
                từ WordPress admin.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Error Result */}
      {publishState === "error" && publishResult && (
        <Card className="border-red-500">
          <CardHeader>
            <CardTitle className="text-red-600">Đăng Bài Thất Bại</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertDescription>
                <strong>Lỗi:</strong> {publishResult.error || "Lỗi không xác định"}
              </AlertDescription>
            </Alert>
            {publishResult.step_failed && (
              <p className="text-sm text-muted-foreground">
                <strong>Thất bại tại bước:</strong> {publishResult.step_failed}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Requirements */}
      <Card>
        <CardHeader>
          <CardTitle>Yêu Cầu</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-4">
          <div>
            <p className="font-medium text-foreground">Cài Đặt Google Docs:</p>
            <ul className="list-disc list-inside ml-2 space-y-1">
              <li>Mở tài liệu trong Google Docs</li>
              <li>Copy URL từ trình duyệt (edit, view, hoặc published URL - đều hoạt động!)</li>
              <li>Lần đầu: Trình duyệt sẽ mở để xác thực Google</li>
              <li>Cấp quyền truy cập tài khoản Google của bạn</li>
            </ul>
          </div>
          <div>
            <p className="font-medium text-foreground">Cài Đặt WordPress:</p>
            <ul className="list-disc list-inside ml-2 space-y-1">
              <li>WordPress REST API phải được bật (mặc định trong WordPress 4.7+)</li>
              <li>Application Password phải hợp lệ</li>
              <li>Người dùng phải có quyền tạo bài viết</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

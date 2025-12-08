"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Loader2,
  Layers,
  CheckCircle,
  XCircle,
  ExternalLink,
} from "lucide-react";
import { api, type Project } from "@/lib/api";

interface BatchResult {
  google_docs_url: string;
  success: boolean;
  post_url?: string;
  post_title?: string;
  error?: string;
}

export default function BatchPublishPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [results, setResults] = useState<BatchResult[]>([]);

  const [formData, setFormData] = useState({
    project_id: "",
    urls: "",
    post_status: "draft",
  });

  useEffect(() => {
    async function fetchProjects() {
      try {
        const res = await api.projects.list();
        if (res.success && res.projects?.length > 0) {
          setProjects(res.projects);
          setFormData((prev) => ({
            ...prev,
            project_id: res.projects[0].project_id,
          }));
        }
      } catch (error) {
        console.error("Failed to fetch projects:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchProjects();
  }, []);

  function parseUrls(text: string): string[] {
    return text
      .split(/[\n,]/)
      .map((url) => url.trim())
      .filter((url) => url.length > 0);
  }

  async function handlePublish() {
    const urls = parseUrls(formData.urls);
    if (urls.length === 0 || !formData.project_id) return;

    setPublishing(true);
    setResults([]);

    try {
      const res = await api.publish.batch({
        project_id: formData.project_id,
        google_docs_urls: urls,
        post_status: formData.post_status as "draft" | "publish",
      });

      if (res.results) {
        setResults(res.results);
      }
    } catch (error) {
      console.error("Failed to batch publish:", error);
    } finally {
      setPublishing(false);
    }
  }

  const urlCount = parseUrls(formData.urls).length;
  const successCount = results.filter((r) => r.success).length;
  const failedCount = results.filter((r) => !r.success).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/publish">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Xuất bản hàng loạt
          </h1>
          <p className="text-muted-foreground">
            Đăng nhiều bài từ Google Docs cùng lúc
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Danh sách URL</CardTitle>
            <CardDescription>
              Nhập các URL Google Docs, mỗi URL một dòng
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Chọn dự án</Label>
              {loading ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Đang tải...
                </div>
              ) : projects.length === 0 ? (
                <Alert>
                  <AlertDescription>
                    Chưa có dự án nào. Vui lòng tạo dự án trước.
                  </AlertDescription>
                </Alert>
              ) : (
                <Select
                  value={formData.project_id}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, project_id: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Chọn dự án" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map((project) => (
                      <SelectItem
                        key={project.project_id}
                        value={project.project_id}
                      >
                        {project.project_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Google Docs URLs</Label>
                {urlCount > 0 && (
                  <Badge variant="secondary">{urlCount} URLs</Badge>
                )}
              </div>
              <Textarea
                placeholder="https://docs.google.com/document/d/e/.../pub&#10;https://docs.google.com/document/d/e/.../pub&#10;https://docs.google.com/document/d/e/.../pub"
                value={formData.urls}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, urls: e.target.value }))
                }
                rows={10}
              />
              <p className="text-xs text-muted-foreground">
                Mỗi URL phải kết thúc bằng /pub. Có thể phân cách bằng dòng mới
                hoặc dấu phẩy.
              </p>
            </div>

            <div className="space-y-2">
              <Label>Trạng thái bài viết</Label>
              <Select
                value={formData.post_status}
                onValueChange={(value) =>
                  setFormData((prev) => ({ ...prev, post_status: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">Bản nháp (Draft)</SelectItem>
                  <SelectItem value="publish">Xuất bản (Publish)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handlePublish}
              disabled={publishing || urlCount === 0 || !formData.project_id}
              className="w-full"
            >
              {publishing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Layers className="mr-2 h-4 w-4" />
              Xuất bản {urlCount} bài
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle>Kết quả</CardTitle>
            <CardDescription>
              {results.length > 0 ? (
                <>
                  <span className="text-green-600">{successCount} thành công</span>
                  {failedCount > 0 && (
                    <span className="text-red-600">
                      {" "}/ {failedCount} thất bại
                    </span>
                  )}
                </>
              ) : (
                "Kết quả xuất bản sẽ hiển thị ở đây"
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {publishing ? (
              <div className="flex flex-col items-center justify-center py-8 gap-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-muted-foreground">
                  Đang xuất bản {urlCount} bài viết...
                </p>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                Nhập URLs và nhấn &quot;Xuất bản&quot; để bắt đầu
              </div>
            ) : (
              <div className="space-y-3 max-h-[400px] overflow-auto">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className={`flex items-start justify-between p-3 rounded-lg border ${
                      result.success
                        ? "border-green-200 bg-green-50"
                        : "border-red-200 bg-red-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {result.success ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium text-sm">
                          {result.post_title || "Không có tiêu đề"}
                        </p>
                        <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                          {result.google_docs_url}
                        </p>
                        {result.error && (
                          <p className="text-xs text-red-600 mt-1">
                            {result.error}
                          </p>
                        )}
                      </div>
                    </div>
                    {result.success && result.post_url && (
                      <Button variant="ghost" size="icon" asChild>
                        <a
                          href={result.post_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

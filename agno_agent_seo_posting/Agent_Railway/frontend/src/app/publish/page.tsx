"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Upload,
  Loader2,
  CheckCircle,
  XCircle,
  ExternalLink,
  FileText,
} from "lucide-react";
import { api, type Project } from "@/lib/api";

interface PublishResult {
  success: boolean;
  post_url?: string;
  post_title?: string;
  error?: string;
}

export default function PublishPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [converting, setConverting] = useState(false);
  const [result, setResult] = useState<PublishResult | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    project_id: "",
    google_docs_url: "",
    post_status: "draft",
  });

  useEffect(() => {
    async function fetchProjects() {
      try {
        const res = await api.projects.list();
        if (res.success) {
          setProjects(res.projects || []);
          if (res.projects && res.projects.length > 0) {
            setFormData((prev) => ({
              ...prev,
              project_id: res.projects[0].project_id,
            }));
          }
        }
      } catch (error) {
        console.error("Failed to fetch projects:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchProjects();
  }, []);

  async function handleConvert() {
    if (!formData.google_docs_url) return;
    setConverting(true);
    setPreviewHtml(null);
    try {
      const res = await api.publish.convert(formData.google_docs_url);
      if (res.success && res.html) {
        setPreviewHtml(res.html);
      } else {
        setResult({
          success: false,
          error: res.error || "Không thể chuyển đổi Google Docs",
        });
      }
    } catch (error) {
      console.error("Failed to convert:", error);
      setResult({
        success: false,
        error: "Đã xảy ra lỗi khi chuyển đổi",
      });
    } finally {
      setConverting(false);
    }
  }

  async function handlePublish() {
    if (!formData.project_id || !formData.google_docs_url) return;
    setPublishing(true);
    setResult(null);
    try {
      const res = await api.publish.single({
        project_id: formData.project_id,
        google_docs_url: formData.google_docs_url,
        post_status: formData.post_status as "draft" | "publish",
      });
      setResult(res);
    } catch (error) {
      console.error("Failed to publish:", error);
      setResult({
        success: false,
        error: "Đã xảy ra lỗi khi xuất bản",
      });
    } finally {
      setPublishing(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Xuất bản nội dung</h1>
        <p className="text-muted-foreground">
          Đăng bài từ Google Docs lên WordPress
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Thông tin xuất bản</CardTitle>
            <CardDescription>
              Nhập URL Google Docs đã publish để xuất bản
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="project">Dự án *</Label>
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
              <Label htmlFor="google_docs_url">Google Docs URL *</Label>
              <Textarea
                id="google_docs_url"
                placeholder="https://docs.google.com/document/d/e/2PACX-.../pub"
                value={formData.google_docs_url}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    google_docs_url: e.target.value,
                  }))
                }
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                URL phải kết thúc bằng /pub (File → Share → Publish to web)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="post_status">Trạng thái bài viết</Label>
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

            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                onClick={handleConvert}
                disabled={converting || !formData.google_docs_url}
              >
                {converting && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                <FileText className="mr-2 h-4 w-4" />
                Xem trước HTML
              </Button>
              <Button
                onClick={handlePublish}
                disabled={
                  publishing ||
                  !formData.project_id ||
                  !formData.google_docs_url
                }
              >
                {publishing && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                <Upload className="mr-2 h-4 w-4" />
                Xuất bản
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Result */}
        <div className="space-y-4">
          {result && (
            <Alert
              variant={result.success ? "default" : "destructive"}
              className={result.success ? "border-green-500" : ""}
            >
              {result.success ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <AlertTitle>
                {result.success ? "Xuất bản thành công!" : "Xuất bản thất bại"}
              </AlertTitle>
              <AlertDescription>
                {result.success ? (
                  <div className="space-y-2">
                    <p>Tiêu đề: {result.post_title}</p>
                    {result.post_url && (
                      <a
                        href={result.post_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-blue-600 hover:underline"
                      >
                        Xem bài viết
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                ) : (
                  result.error
                )}
              </AlertDescription>
            </Alert>
          )}

          {previewHtml && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Xem trước HTML</CardTitle>
                  <Badge variant="secondary">Preview</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="max-h-[400px] overflow-auto rounded border bg-muted/30 p-4">
                  <pre className="text-xs whitespace-pre-wrap">
                    {previewHtml}
                  </pre>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

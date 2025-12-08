"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowLeft, Loader2, Save, CheckCircle } from "lucide-react";
import { api, type Project } from "@/lib/api";

export default function EditProjectPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    project_name: "",
    wordpress_url: "",
    wordpress_username: "",
    wordpress_app_password: "",
    image_width: "800",
    image_quality: "92",
    image_format: "JPEG",
    status: "active",
  });

  useEffect(() => {
    async function fetchProject() {
      try {
        const res = await api.projects.get(projectId);
        if (res.success && res.project) {
          const project = res.project as Project;
          setFormData({
            project_name: project.project_name,
            wordpress_url: project.wordpress_url,
            wordpress_username: project.wordpress_username,
            wordpress_app_password: project.wordpress_app_password,
            image_width: project.image_configs?.target_width?.toString() || "800",
            image_quality: project.image_configs?.image_quality?.toString() || "92",
            image_format: project.image_configs?.image_format || "JPEG",
            status: project.status || "active",
          });
        } else {
          setError("Không tìm thấy dự án");
        }
      } catch (err) {
        setError("Đã xảy ra lỗi khi tải dự án");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchProject();
  }, [projectId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const res = await api.projects.update(projectId, {
        project_id: projectId,
        project_name: formData.project_name,
        wordpress_url: formData.wordpress_url,
        wordpress_username: formData.wordpress_username,
        wordpress_app_password: formData.wordpress_app_password,
        image_configs: {
          target_width: parseInt(formData.image_width),
          image_quality: parseInt(formData.image_quality),
          image_format: formData.image_format,
        },
      });

      if (res.success) {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } else {
        setError(res.error || "Không thể cập nhật dự án");
      }
    } catch (err) {
      setError("Đã xảy ra lỗi khi cập nhật dự án");
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/projects">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Chỉnh sửa dự án
          </h1>
          <p className="text-muted-foreground">ID: {projectId}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Project Info */}
          <Card>
            <CardHeader>
              <CardTitle>Thông tin dự án</CardTitle>
              <CardDescription>Thông tin cơ bản của dự án</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="project_name">Tên dự án *</Label>
                <Input
                  id="project_name"
                  value={formData.project_name}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      project_name: e.target.value,
                    }))
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="status">Trạng thái</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) =>
                    setFormData((prev) => ({
                      ...prev,
                      status: value,
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Hoạt động</SelectItem>
                    <SelectItem value="inactive">Tạm dừng</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* WordPress Config */}
          <Card>
            <CardHeader>
              <CardTitle>Cấu hình WordPress</CardTitle>
              <CardDescription>Thông tin đăng nhập REST API</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="wordpress_url">WordPress URL *</Label>
                <Input
                  id="wordpress_url"
                  type="url"
                  value={formData.wordpress_url}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      wordpress_url: e.target.value,
                    }))
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="wordpress_username">Username *</Label>
                <Input
                  id="wordpress_username"
                  value={formData.wordpress_username}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      wordpress_username: e.target.value,
                    }))
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="wordpress_app_password">
                  Application Password *
                </Label>
                <Input
                  id="wordpress_app_password"
                  type="password"
                  value={formData.wordpress_app_password}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      wordpress_app_password: e.target.value,
                    }))
                  }
                  required
                />
              </div>
            </CardContent>
          </Card>

          {/* Image Config */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Cấu hình hình ảnh</CardTitle>
              <CardDescription>
                Thiết lập xử lý hình ảnh khi xuất bản
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="image_width">Chiều rộng (px)</Label>
                  <Input
                    id="image_width"
                    type="number"
                    value={formData.image_width}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        image_width: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="image_quality">Chất lượng (%)</Label>
                  <Input
                    id="image_quality"
                    type="number"
                    min="1"
                    max="100"
                    value={formData.image_quality}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        image_quality: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="image_format">Định dạng</Label>
                  <Select
                    value={formData.image_format}
                    onValueChange={(value) =>
                      setFormData((prev) => ({
                        ...prev,
                        image_format: value,
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="JPEG">JPEG</SelectItem>
                      <SelectItem value="PNG">PNG</SelectItem>
                      <SelectItem value="WEBP">WEBP</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <Alert variant="destructive" className="mt-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mt-6 border-green-500 text-green-700">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>Đã lưu thay đổi thành công!</AlertDescription>
          </Alert>
        )}

        <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/projects">Quay lại</Link>
          </Button>
          <Button type="submit" disabled={saving}>
            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            <Save className="mr-2 h-4 w-4" />
            Lưu thay đổi
          </Button>
        </div>
      </form>
    </div>
  );
}

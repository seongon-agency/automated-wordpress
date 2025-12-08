"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
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
import { ArrowLeft, Loader2, Save } from "lucide-react";
import { api } from "@/lib/api";

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    project_id: "",
    project_name: "",
    wordpress_url: "",
    wordpress_username: "",
    wordpress_app_password: "",
    image_width: "800",
    image_quality: "92",
    image_format: "JPEG",
  });

  function generateProjectId(name: string) {
    return name
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/đ/g, "d")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "");
  }

  function handleNameChange(name: string) {
    setFormData((prev) => ({
      ...prev,
      project_name: name,
      project_id: generateProjectId(name),
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.projects.create({
        project_id: formData.project_id,
        project_name: formData.project_name,
        wordpress_url: formData.wordpress_url,
        wordpress_username: formData.wordpress_username,
        wordpress_app_password: formData.wordpress_app_password,
        html_configs: { patterns: [] },
        image_configs: {
          target_width: parseInt(formData.image_width),
          image_quality: parseInt(formData.image_quality),
          image_format: formData.image_format,
        },
      });

      if (res.success) {
        router.push("/projects");
      } else {
        setError(res.error || "Không thể tạo dự án");
      }
    } catch (err) {
      setError("Đã xảy ra lỗi khi tạo dự án");
      console.error(err);
    } finally {
      setLoading(false);
    }
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
          <h1 className="text-2xl font-bold tracking-tight">Tạo dự án mới</h1>
          <p className="text-muted-foreground">
            Cấu hình website WordPress mới để xuất bản nội dung
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Project Info */}
          <Card>
            <CardHeader>
              <CardTitle>Thông tin dự án</CardTitle>
              <CardDescription>
                Thông tin cơ bản của dự án
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="project_name">Tên dự án *</Label>
                <Input
                  id="project_name"
                  placeholder="VD: Blog Công nghệ"
                  value={formData.project_name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project_id">ID dự án *</Label>
                <Input
                  id="project_id"
                  placeholder="VD: blog_cong_nghe"
                  value={formData.project_id}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      project_id: e.target.value,
                    }))
                  }
                  required
                />
                <p className="text-xs text-muted-foreground">
                  ID duy nhất để nhận diện dự án (tự động tạo từ tên)
                </p>
              </div>
            </CardContent>
          </Card>

          {/* WordPress Config */}
          <Card>
            <CardHeader>
              <CardTitle>Cấu hình WordPress</CardTitle>
              <CardDescription>
                Thông tin đăng nhập REST API
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="wordpress_url">WordPress URL *</Label>
                <Input
                  id="wordpress_url"
                  type="url"
                  placeholder="https://example.com"
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
                  placeholder="admin"
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
                  placeholder="xxxx xxxx xxxx xxxx"
                  value={formData.wordpress_app_password}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      wordpress_app_password: e.target.value,
                    }))
                  }
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Tạo từ WordPress Admin → Users → Profile → Application Passwords
                </p>
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

        <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/projects">Hủy</Link>
          </Button>
          <Button type="submit" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            <Save className="mr-2 h-4 w-4" />
            Tạo dự án
          </Button>
        </div>
      </form>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { createProject, type ProjectCreateData, type ImageConfigs } from "@/lib/api";

type ResizeMethod = "fixed_width" | "google_docs_original" | "no_resize";
type ImageFormat = "JPEG" | "PNG" | "WEBP";
type NamingMethod = "default" | "alt_text" | "main_keyword";

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [projectId, setProjectId] = useState("");
  const [projectName, setProjectName] = useState("");
  const [wordpressUrl, setWordpressUrl] = useState("");
  const [wordpressUsername, setWordpressUsername] = useState("");
  const [wordpressAppPassword, setWordpressAppPassword] = useState("");
  const [notes, setNotes] = useState("");

  // Image config state
  const [resizeMethod, setResizeMethod] = useState<ResizeMethod>("fixed_width");
  const [targetWidth, setTargetWidth] = useState(800);
  const [targetHeight, setTargetHeight] = useState<number | null>(null);
  const [imageQuality, setImageQuality] = useState(92);
  const [imageFormat, setImageFormat] = useState<ImageFormat>("JPEG");
  const [namingMethod, setNamingMethod] = useState<NamingMethod>("default");
  const [altTextWords, setAltTextWords] = useState(5);
  const [enableAutoCaptions, setEnableAutoCaptions] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!projectId.trim()) {
      setError("Vui lòng nhập ID dự án");
      return;
    }
    if (!projectName.trim()) {
      setError("Vui lòng nhập tên dự án");
      return;
    }
    if (!wordpressUrl.trim()) {
      setError("Vui lòng nhập URL WordPress");
      return;
    }
    if (!wordpressUsername.trim()) {
      setError("Vui lòng nhập tên đăng nhập WordPress");
      return;
    }
    if (!wordpressAppPassword.trim()) {
      setError("Vui lòng nhập mật khẩu ứng dụng WordPress");
      return;
    }

    // Validate project ID format
    if (!/^[a-z0-9_]+$/.test(projectId)) {
      setError("ID dự án chỉ được chứa chữ thường, số và dấu gạch dưới");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const imageConfigs: ImageConfigs = {
        resize_method: resizeMethod,
        target_width: targetWidth,
        target_height: targetHeight,
        image_quality: imageQuality,
        image_format: imageFormat,
        enable_auto_captions: enableAutoCaptions,
        naming_method: namingMethod,
        alt_text_words: altTextWords,
      };

      const data: ProjectCreateData = {
        project_id: projectId.trim(),
        project_name: projectName.trim(),
        wordpress_url: wordpressUrl.trim().replace(/\/$/, ""), // Remove trailing slash
        wordpress_username: wordpressUsername.trim(),
        wordpress_app_password: wordpressAppPassword.trim(),
        image_configs: imageConfigs,
        notes: notes.trim() || undefined,
      };

      const response = await createProject(data);

      if (response.success) {
        router.push("/projects");
      } else {
        setError("Không thể tạo dự án");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi tạo dự án");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tạo Dự Án Mới</h1>
          <p className="text-muted-foreground mt-2">
            Cấu hình một dự án WordPress mới để đăng bài
          </p>
        </div>
        <Link href="/projects">
          <Button variant="outline">← Quay lại</Button>
        </Link>
      </div>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>Dự Án Là Gì?</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            Một <strong>dự án</strong> đại diện cho một trang WordPress nơi bạn sẽ đăng nội dung.
            Mỗi dự án lưu trữ:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>URL trang WordPress và thông tin đăng nhập</li>
            <li>Các mẫu chuyển đổi HTML (tùy chọn)</li>
            <li>Cài đặt xử lý ảnh (tùy chọn)</li>
          </ul>
          <p>
            Sau khi cấu hình, bạn có thể đăng nhiều bài viết lên cùng một dự án mà không cần
            cấu hình lại.
          </p>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="basic">Thông Tin Cơ Bản</TabsTrigger>
            <TabsTrigger value="wordpress">Cấu Hình WordPress</TabsTrigger>
            <TabsTrigger value="image">Cài Đặt Ảnh</TabsTrigger>
          </TabsList>

          {/* Basic Info Tab */}
          <TabsContent value="basic">
            <Card>
              <CardHeader>
                <CardTitle>Thông Tin Cơ Bản</CardTitle>
                <CardDescription>
                  Nhập thông tin định danh cho dự án của bạn
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="projectId">ID Dự Án *</Label>
                  <Input
                    id="projectId"
                    placeholder="vd: blog_cua_toi_2024"
                    value={projectId}
                    onChange={(e) => setProjectId(e.target.value.toLowerCase())}
                  />
                  <p className="text-xs text-muted-foreground">
                    Định danh duy nhất (chữ thường, chỉ dùng gạch dưới). Không thể thay đổi sau
                    khi tạo.
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="projectName">Tên Dự Án *</Label>
                  <Input
                    id="projectName"
                    placeholder="vd: Blog Tuyệt Vời Của Tôi"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Tên hiển thị cho dự án này
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Ghi Chú (Tùy Chọn)</Label>
                  <Textarea
                    id="notes"
                    placeholder="Ghi chú về dự án..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* WordPress Config Tab */}
          <TabsContent value="wordpress">
            <Card>
              <CardHeader>
                <CardTitle>Cấu Hình WordPress</CardTitle>
                <CardDescription>
                  Nhập thông tin đăng nhập WordPress REST API
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="wordpressUrl">URL Trang WordPress *</Label>
                  <Input
                    id="wordpressUrl"
                    placeholder="https://trang-wordpress-cua-ban.com"
                    value={wordpressUrl}
                    onChange={(e) => setWordpressUrl(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    URL đầy đủ đến trang WordPress của bạn (không có dấu / ở cuối)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="wordpressUsername">Tên Đăng Nhập WordPress *</Label>
                  <Input
                    id="wordpressUsername"
                    placeholder="admin"
                    value={wordpressUsername}
                    onChange={(e) => setWordpressUsername(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="wordpressAppPassword">Mật Khẩu Ứng Dụng WordPress *</Label>
                  <Input
                    id="wordpressAppPassword"
                    type="password"
                    placeholder="xxxx xxxx xxxx xxxx"
                    value={wordpressAppPassword}
                    onChange={(e) => setWordpressAppPassword(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    <strong>KHÔNG</strong> phải mật khẩu thông thường! Lấy từ: WordPress Admin →
                    Users → Profile → Application Passwords
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Image Settings Tab */}
          <TabsContent value="image">
            <Card>
              <CardHeader>
                <CardTitle>Cài Đặt Ảnh</CardTitle>
                <CardDescription>
                  Cấu hình cách xử lý ảnh từ Google Docs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Resize Method */}
                <div className="space-y-2">
                  <Label>Phương Thức Thay Đổi Kích Thước</Label>
                  <Select
                    value={resizeMethod}
                    onValueChange={(v) => setResizeMethod(v as ResizeMethod)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fixed_width">Chiều Rộng Cố Định</SelectItem>
                      <SelectItem value="google_docs_original">
                        Kích Thước Gốc Google Docs
                      </SelectItem>
                      <SelectItem value="no_resize">
                        Không Thay Đổi (Chất Lượng Gốc)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    {resizeMethod === "fixed_width" &&
                      "Thay đổi kích thước theo chiều rộng cố định"}
                    {resizeMethod === "google_docs_original" &&
                      "Sử dụng kích thước từ Google Docs"}
                    {resizeMethod === "no_resize" &&
                      "Giữ nguyên ảnh gốc không xử lý (chất lượng tốt nhất)"}
                  </p>
                </div>

                {/* Width and Height (only for fixed_width) */}
                {resizeMethod === "fixed_width" && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="targetWidth">Chiều Rộng (px) *</Label>
                      <Input
                        id="targetWidth"
                        type="number"
                        min={100}
                        max={2000}
                        value={targetWidth}
                        onChange={(e) => setTargetWidth(parseInt(e.target.value) || 800)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="targetHeight">Chiều Cao (px)</Label>
                      <Input
                        id="targetHeight"
                        type="number"
                        min={0}
                        max={2000}
                        value={targetHeight || ""}
                        onChange={(e) =>
                          setTargetHeight(e.target.value ? parseInt(e.target.value) : null)
                        }
                        placeholder="Tự động"
                      />
                      <p className="text-xs text-muted-foreground">
                        Để trống để giữ tỷ lệ gốc
                      </p>
                    </div>
                  </div>
                )}

                {/* Quality and Format */}
                {resizeMethod !== "no_resize" && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="imageQuality">Chất Lượng Ảnh (%)</Label>
                      <Input
                        id="imageQuality"
                        type="number"
                        min={1}
                        max={100}
                        value={imageQuality}
                        onChange={(e) => setImageQuality(parseInt(e.target.value) || 92)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Định Dạng Ảnh</Label>
                      <Select
                        value={imageFormat}
                        onValueChange={(v) => setImageFormat(v as ImageFormat)}
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
                )}

                {/* Naming Method */}
                <div className="space-y-2">
                  <Label>Phương Thức Đặt Tên Ảnh</Label>
                  <Select
                    value={namingMethod}
                    onValueChange={(v) => setNamingMethod(v as NamingMethod)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="default">Mặc định (image_1, image_2...)</SelectItem>
                      <SelectItem value="alt_text">Theo Alt Text</SelectItem>
                      <SelectItem value="main_keyword">Theo Từ Khóa Chính</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {namingMethod === "alt_text" && (
                  <div className="space-y-2">
                    <Label htmlFor="altTextWords">Số Từ Từ Alt Text</Label>
                    <Input
                      id="altTextWords"
                      type="number"
                      min={1}
                      max={10}
                      value={altTextWords}
                      onChange={(e) => setAltTextWords(parseInt(e.target.value) || 5)}
                    />
                    <p className="text-xs text-muted-foreground">
                      Số từ đầu tiên từ alt text để tạo tên file
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Submit Button */}
        <div className="flex justify-end gap-4 mt-6">
          <Link href="/projects">
            <Button type="button" variant="outline">
              Hủy
            </Button>
          </Link>
          <Button type="submit" disabled={loading}>
            {loading ? "Đang tạo..." : "Tạo Dự Án"}
          </Button>
        </div>
      </form>
    </div>
  );
}

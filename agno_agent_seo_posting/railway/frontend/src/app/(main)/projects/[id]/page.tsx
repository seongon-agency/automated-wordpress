"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  getProject,
  updateProject,
  deleteProject,
  modifyPatterns,
  type Project,
  type ProjectUpdateData,
  type ImageConfigs,
  type HtmlPattern,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";

type ResizeMethod = "fixed_width" | "google_docs_original" | "no_resize";
type ImageFormat = "JPEG" | "PNG" | "WEBP";
type NamingMethod = "default" | "alt_text" | "main_keyword";

export default function EditProjectPage() {
  const router = useRouter();
  const params = useParams();
  const { user } = useAuth();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Form state
  const [projectName, setProjectName] = useState("");
  const [wordpressUrl, setWordpressUrl] = useState("");
  const [wordpressUsername, setWordpressUsername] = useState("");
  const [wordpressAppPassword, setWordpressAppPassword] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState("active");

  // Image config state
  const [resizeMethod, setResizeMethod] = useState<ResizeMethod>("fixed_width");
  const [targetWidth, setTargetWidth] = useState(800);
  const [targetHeight, setTargetHeight] = useState<number | null>(null);
  const [imageQuality, setImageQuality] = useState(92);
  const [imageFormat, setImageFormat] = useState<ImageFormat>("JPEG");
  const [namingMethod, setNamingMethod] = useState<NamingMethod>("default");
  const [altTextWords, setAltTextWords] = useState(5);
  const [enableAutoCaptions, setEnableAutoCaptions] = useState(true);

  // Pattern state
  const [patterns, setPatterns] = useState<HtmlPattern[]>([]);
  const [patternInstruction, setPatternInstruction] = useState("");
  const [modifyingPatterns, setModifyingPatterns] = useState(false);
  const [patternChanges, setPatternChanges] = useState<string | null>(null);
  const [savingPatterns, setSavingPatterns] = useState(false);

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getProject(projectId, user?.id);
        if (response.success && response.project) {
          const p = response.project;
          setProject(p);

          // Populate form fields
          setProjectName(p.project_name);
          setWordpressUrl(p.wordpress_url);
          setWordpressUsername(p.wordpress_username);
          setWordpressAppPassword(p.wordpress_app_password);
          setNotes(p.notes || "");
          setStatus(p.status);

          // Populate image config
          if (p.image_configs) {
            setResizeMethod(p.image_configs.resize_method || "fixed_width");
            setTargetWidth(p.image_configs.target_width || 800);
            setTargetHeight(p.image_configs.target_height);
            setImageQuality(p.image_configs.image_quality || 92);
            setImageFormat(p.image_configs.image_format || "JPEG");
            setNamingMethod(p.image_configs.naming_method || "default");
            setAltTextWords(p.image_configs.alt_text_words || 5);
            setEnableAutoCaptions(p.image_configs.enable_auto_captions ?? true);
          }

          // Populate patterns
          setPatterns(p.html_configs?.patterns || []);
        } else {
          setError("Không tìm thấy dự án");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Lỗi khi tải dự án");
      } finally {
        setLoading(false);
      }
    };

    if (projectId && user?.id) {
      fetchProject();
    }
  }, [projectId, user?.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
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

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

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

      const data: ProjectUpdateData = {
        project_name: projectName.trim(),
        wordpress_url: wordpressUrl.trim().replace(/\/$/, ""),
        wordpress_username: wordpressUsername.trim(),
        wordpress_app_password: wordpressAppPassword.trim(),
        image_configs: imageConfigs,
        notes: notes.trim() || undefined,
        status: status,
      };

      const response = await updateProject(projectId, data, user?.id);

      if (response.success) {
        setSuccess("Cập nhật dự án thành công!");
        if (response.project) {
          setProject(response.project);
        }
      } else {
        setError("Không thể cập nhật dự án");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi cập nhật dự án");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      const response = await deleteProject(projectId, user?.id);
      if (response.success) {
        router.push("/projects");
      } else {
        setError("Không thể xóa dự án");
        setDeleteDialogOpen(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi xóa dự án");
      setDeleteDialogOpen(false);
    } finally {
      setDeleting(false);
    }
  };

  const handleDeletePattern = (index: number) => {
    const newPatterns = patterns.filter((_, i) => i !== index);
    setPatterns(newPatterns);
  };

  const handleModifyPatterns = async () => {
    if (!patternInstruction.trim()) {
      setError("Vui lòng nhập hướng dẫn chỉnh sửa");
      return;
    }

    try {
      setModifyingPatterns(true);
      setError(null);
      setPatternChanges(null);

      const response = await modifyPatterns(patterns, patternInstruction);

      if (response.success && response.patterns) {
        setPatterns(response.patterns);
        setPatternChanges(response.changes_made || null);
        setPatternInstruction("");
      } else {
        setError(response.error || "Không thể chỉnh sửa patterns");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi chỉnh sửa patterns");
    } finally {
      setModifyingPatterns(false);
    }
  };

  const handleSavePatterns = async () => {
    try {
      setSavingPatterns(true);
      setError(null);

      const response = await updateProject(projectId, {
        html_configs: { patterns },
      }, user?.id);

      if (response.success) {
        setSuccess("Đã lưu patterns thành công!");
        setPatternChanges(null);
        if (response.project) {
          setProject(response.project);
        }
      } else {
        setError("Không thể lưu patterns");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi lưu patterns");
    } finally {
      setSavingPatterns(false);
    }
  };

  const handleResetPatterns = () => {
    if (project?.html_configs?.patterns) {
      setPatterns(project.html_configs.patterns);
      setPatternChanges(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-48 mt-2" />
          </div>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!project && !loading) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertDescription>
            Không tìm thấy dự án với ID: {projectId}
          </AlertDescription>
        </Alert>
        <Link href="/projects">
          <Button>← Quay lại danh sách dự án</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chỉnh Sửa Dự Án</h1>
          <p className="text-muted-foreground mt-2">
            ID: <code className="bg-muted px-1 rounded">{projectId}</code>
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/projects">
            <Button variant="outline">← Quay lại</Button>
          </Link>
          <Button variant="destructive" onClick={() => setDeleteDialogOpen(true)}>
            Xóa Dự Án
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="basic">Thông Tin Cơ Bản</TabsTrigger>
            <TabsTrigger value="wordpress">Cấu Hình WordPress</TabsTrigger>
            <TabsTrigger value="image">Cài Đặt Ảnh</TabsTrigger>
            <TabsTrigger value="patterns">HTML Patterns</TabsTrigger>
          </TabsList>

          {/* Basic Info Tab */}
          <TabsContent value="basic">
            <Card>
              <CardHeader>
                <CardTitle>Thông Tin Cơ Bản</CardTitle>
                <CardDescription>
                  Cập nhật thông tin dự án của bạn
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="projectName">Tên Dự Án *</Label>
                  <Input
                    id="projectName"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Trạng Thái</Label>
                  <Select value={status} onValueChange={setStatus}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Hoạt động</SelectItem>
                      <SelectItem value="inactive">Tạm dừng</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Ghi Chú</Label>
                  <Textarea
                    id="notes"
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
                  Cập nhật thông tin đăng nhập WordPress REST API
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="wordpressUrl">URL Trang WordPress *</Label>
                  <Input
                    id="wordpressUrl"
                    value={wordpressUrl}
                    onChange={(e) => setWordpressUrl(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="wordpressUsername">Tên Đăng Nhập WordPress *</Label>
                  <Input
                    id="wordpressUsername"
                    value={wordpressUsername}
                    onChange={(e) => setWordpressUsername(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="wordpressAppPassword">Mật Khẩu Ứng Dụng WordPress *</Label>
                  <Input
                    id="wordpressAppPassword"
                    type="password"
                    value={wordpressAppPassword}
                    onChange={(e) => setWordpressAppPassword(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Để trống nếu không muốn thay đổi mật khẩu hiện tại
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
                  </div>
                )}

                {/* Auto Captions */}
                <div className="flex items-center space-x-2 pt-4 border-t">
                  <Checkbox
                    id="enableAutoCaptions"
                    checked={enableAutoCaptions}
                    onCheckedChange={(checked) => setEnableAutoCaptions(checked as boolean)}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="enableAutoCaptions"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Bật Caption WordPress Tự Động
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      Tự động bọc ảnh có alt text với shortcode [caption] của WordPress.
                      Tắt nếu bạn muốn kiểm soát định dạng caption bằng HTML patterns.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* HTML Patterns Tab */}
          <TabsContent value="patterns">
            <div className="space-y-6">
              {/* Current Patterns */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>
                        HTML Patterns
                        <Badge variant="secondary" className="ml-2">
                          {patterns.length} patterns
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        Các patterns chuyển đổi HTML cho dự án này
                      </CardDescription>
                    </div>
                    <Link href="/patterns/scan">
                      <Button variant="outline" size="sm">
                        Quét HTML Mẫu
                      </Button>
                    </Link>
                  </div>
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
                                  type="button"
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
                    <Label htmlFor="patternInstruction">Hướng Dẫn Chỉnh Sửa</Label>
                    <Textarea
                      id="patternInstruction"
                      placeholder="Ví dụ: Làm tất cả tiêu đề h2 có màu xanh dương và font-weight bold"
                      value={patternInstruction}
                      onChange={(e) => setPatternInstruction(e.target.value)}
                      rows={3}
                      disabled={modifyingPatterns || patterns.length === 0}
                    />
                  </div>

                  <div className="p-3 bg-muted rounded-md text-sm text-muted-foreground">
                    <p className="font-medium text-foreground mb-2">Ví dụ hướng dẫn:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Làm tất cả tiêu đề h2 màu xanh dương</li>
                      <li>Thêm class &quot;highlight&quot; cho tất cả đoạn văn</li>
                      <li>Làm các link mở ở tab mới</li>
                    </ul>
                  </div>

                  {patternChanges && (
                    <Alert>
                      <AlertDescription>
                        <span className="font-medium">Thay đổi:</span> {patternChanges}
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="flex gap-4">
                    <Button
                      type="button"
                      onClick={handleModifyPatterns}
                      disabled={modifyingPatterns || !patternInstruction.trim() || patterns.length === 0}
                      className="flex-1"
                    >
                      {modifyingPatterns ? "Đang xử lý..." : "Áp Dụng Thay Đổi"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleResetPatterns}
                      disabled={modifyingPatterns}
                    >
                      Hoàn Tác
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Save Patterns */}
              <Card>
                <CardContent className="py-4 space-y-4">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <p className="text-sm text-muted-foreground">
                      Nhớ lưu patterns sau khi chỉnh sửa xong
                    </p>
                    <Button
                      type="button"
                      onClick={handleSavePatterns}
                      disabled={savingPatterns}
                      className="w-full sm:w-auto"
                      size="lg"
                    >
                      {savingPatterns ? "Đang lưu..." : "Lưu Patterns"}
                    </Button>
                  </div>
                  {/* Pattern save success message */}
                  {success && success.includes("patterns") && (
                    <Alert className="border-green-500">
                      <AlertDescription className="text-green-600">{success}</AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Submit Button */}
        <div className="flex justify-end gap-4 mt-6">
          <Link href="/projects">
            <Button type="button" variant="outline">
              Hủy
            </Button>
          </Link>
          <Button type="submit" disabled={saving}>
            {saving ? "Đang lưu..." : "Lưu Thay Đổi"}
          </Button>
        </div>

        {/* Success Alert - shown after save button */}
        {success && (
          <Alert className="mt-4 border-green-500">
            <AlertDescription className="text-green-600">{success}</AlertDescription>
          </Alert>
        )}
      </form>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xác Nhận Xóa Dự Án</DialogTitle>
            <DialogDescription>
              Bạn có chắc chắn muốn xóa dự án &quot;{project?.project_name}&quot;?
              <br />
              Hành động này không thể hoàn tác.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleting}
            >
              Hủy
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleting}>
              {deleting ? "Đang xóa..." : "Xóa Dự Án"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

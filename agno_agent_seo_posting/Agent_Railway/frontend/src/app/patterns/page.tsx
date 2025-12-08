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
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2, Wand2, Save, Trash2 } from "lucide-react";
import { api, type Project, type PatternConfig } from "@/lib/api";

export default function PatternsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [patterns, setPatterns] = useState<PatternConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [modifying, setModifying] = useState(false);
  const [saving, setSaving] = useState(false);
  const [instruction, setInstruction] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProjects() {
      try {
        const res = await api.projects.list();
        if (res.success && res.projects?.length > 0) {
          setProjects(res.projects);
          setSelectedProjectId(res.projects[0].project_id);
        }
      } catch (err) {
        console.error("Failed to fetch projects:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      fetchPatterns();
    }
  }, [selectedProjectId]);

  async function fetchPatterns() {
    try {
      const res = await api.patterns.get(selectedProjectId);
      if (res.success) {
        setPatterns(res.patterns || []);
      }
    } catch (err) {
      console.error("Failed to fetch patterns:", err);
    }
  }

  async function handleModify() {
    if (!instruction.trim() || !selectedProjectId) return;
    setModifying(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await api.patterns.modify({
        project_id: selectedProjectId,
        instruction: instruction,
      });

      if (res.success) {
        setPatterns(res.patterns || []);
        setSuccess("Đã cập nhật patterns thành công!");
        setInstruction("");
      } else {
        setError(res.error || "Không thể cập nhật patterns");
      }
    } catch (err) {
      setError("Đã xảy ra lỗi khi cập nhật");
      console.error(err);
    } finally {
      setModifying(false);
    }
  }

  async function handleSave() {
    if (!selectedProjectId) return;
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const project = projects.find((p) => p.project_id === selectedProjectId);
      if (!project) return;

      const res = await api.projects.update(selectedProjectId, {
        ...project,
        html_configs: { patterns },
      });

      if (res.success) {
        setSuccess("Đã lưu patterns vào dự án!");
      } else {
        setError(res.error || "Không thể lưu patterns");
      }
    } catch (err) {
      setError("Đã xảy ra lỗi khi lưu");
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  function handleDeletePattern(index: number) {
    setPatterns((prev) => prev.filter((_, i) => i !== index));
  }

  const exampleInstructions = [
    "Thêm class 'text-lg' cho tất cả thẻ p",
    "Đổi màu heading h2 thành màu xanh dương (#2563eb)",
    "Thêm class 'prose' cho toàn bộ nội dung",
    "Căn giữa tất cả hình ảnh",
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Chỉnh sửa Pattern với AI
        </h1>
        <p className="text-muted-foreground">
          Sử dụng ngôn ngữ tự nhiên để tùy chỉnh định dạng HTML
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : projects.length === 0 ? (
        <Alert>
          <AlertDescription>
            Chưa có dự án nào. Vui lòng tạo dự án trước.
          </AlertDescription>
        </Alert>
      ) : (
        <>
          <div className="grid gap-6 lg:grid-cols-2">
            {/* AI Modifier */}
            <Card>
              <CardHeader>
                <CardTitle>Chỉnh sửa bằng AI</CardTitle>
                <CardDescription>
                  Mô tả thay đổi bạn muốn bằng tiếng Việt
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Chọn dự án</Label>
                  <Select
                    value={selectedProjectId}
                    onValueChange={setSelectedProjectId}
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
                </div>

                <div className="space-y-2">
                  <Label>Yêu cầu chỉnh sửa</Label>
                  <Textarea
                    placeholder="VD: Thêm class 'text-lg' cho tất cả thẻ p"
                    value={instruction}
                    onChange={(e) => setInstruction(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-xs text-muted-foreground">
                    Gợi ý:
                  </Label>
                  <div className="flex flex-wrap gap-2">
                    {exampleInstructions.map((example, i) => (
                      <Badge
                        key={i}
                        variant="secondary"
                        className="cursor-pointer hover:bg-secondary/80"
                        onClick={() => setInstruction(example)}
                      >
                        {example}
                      </Badge>
                    ))}
                  </div>
                </div>

                <Button
                  onClick={handleModify}
                  disabled={modifying || !instruction.trim()}
                  className="w-full"
                >
                  {modifying && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  <Wand2 className="mr-2 h-4 w-4" />
                  Áp dụng với AI
                </Button>
              </CardContent>
            </Card>

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Hành động</CardTitle>
                <CardDescription>Lưu hoặc đặt lại patterns</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                {success && (
                  <Alert className="border-green-500 text-green-700">
                    <AlertDescription>{success}</AlertDescription>
                  </Alert>
                )}

                <div className="flex gap-2">
                  <Button
                    onClick={handleSave}
                    disabled={saving || patterns.length === 0}
                  >
                    {saving && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    <Save className="mr-2 h-4 w-4" />
                    Lưu vào dự án
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setPatterns([])}
                    disabled={patterns.length === 0}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Xóa tất cả
                  </Button>
                </div>

                <div className="rounded-lg border p-4 bg-muted/30">
                  <p className="text-sm font-medium mb-2">Hướng dẫn:</p>
                  <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                    <li>Chọn dự án cần chỉnh sửa patterns</li>
                    <li>Mô tả thay đổi bằng tiếng Việt</li>
                    <li>AI sẽ tạo patterns regex tự động</li>
                    <li>Xem kết quả trong bảng bên dưới</li>
                    <li>Nhấn &quot;Lưu vào dự án&quot; để áp dụng</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Patterns Table */}
          <Card>
            <CardHeader>
              <CardTitle>Patterns hiện tại</CardTitle>
              <CardDescription>
                Danh sách các patterns regex đang được áp dụng
              </CardDescription>
            </CardHeader>
            <CardContent>
              {patterns.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  Chưa có patterns nào. Sử dụng AI để tạo patterns.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Loại</TableHead>
                      <TableHead>Pattern nguồn</TableHead>
                      <TableHead>Pattern đích</TableHead>
                      <TableHead className="w-[50px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {patterns.map((pattern, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Badge variant="outline">{pattern.element_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <code className="text-xs bg-muted px-1 py-0.5 rounded">
                            {pattern.source_pattern}
                          </code>
                        </TableCell>
                        <TableCell>
                          <code className="text-xs bg-muted px-1 py-0.5 rounded">
                            {pattern.target_pattern}
                          </code>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeletePattern(index)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

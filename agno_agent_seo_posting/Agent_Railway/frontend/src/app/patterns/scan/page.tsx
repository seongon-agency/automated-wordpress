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
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, Loader2, ScanLine, Save, CheckCircle } from "lucide-react";
import { api, type Project, type PatternConfig } from "@/lib/api";

export default function ScanTemplatePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [templateUrl, setTemplateUrl] = useState("");
  const [patterns, setPatterns] = useState<PatternConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [saving, setSaving] = useState(false);
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

  async function handleScan() {
    if (!templateUrl.trim() || !selectedProjectId) return;
    setScanning(true);
    setError(null);
    setSuccess(null);
    setPatterns([]);

    try {
      const res = await api.patterns.generate({
        project_id: selectedProjectId,
        template_url: templateUrl,
      });

      if (res.success) {
        setPatterns(res.patterns || []);
        setSuccess(`Đã tạo ${res.patterns?.length || 0} patterns từ mẫu!`);
      } else {
        setError(res.error || "Không thể quét mẫu HTML");
      }
    } catch (err) {
      setError("Đã xảy ra lỗi khi quét mẫu");
      console.error(err);
    } finally {
      setScanning(false);
    }
  }

  async function handleSave() {
    if (!selectedProjectId || patterns.length === 0) return;
    setSaving(true);
    setError(null);

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

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/patterns">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Quét mẫu HTML</h1>
          <p className="text-muted-foreground">
            Tự động tạo patterns từ Google Docs template
          </p>
        </div>
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
          <Card>
            <CardHeader>
              <CardTitle>Quét template</CardTitle>
              <CardDescription>
                Nhập URL Google Docs chứa mẫu HTML định dạng
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
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
                  <Label>Template URL</Label>
                  <Input
                    placeholder="https://docs.google.com/document/d/e/.../pub"
                    value={templateUrl}
                    onChange={(e) => setTemplateUrl(e.target.value)}
                  />
                </div>
              </div>

              <div className="rounded-lg border p-4 bg-muted/30">
                <p className="text-sm font-medium mb-2">Cách tạo template:</p>
                <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                  <li>Tạo Google Docs mới với các ví dụ định dạng</li>
                  <li>Thêm mẫu paragraph, heading, list, table, etc.</li>
                  <li>Publish to web (File → Share → Publish to web)</li>
                  <li>Copy URL và dán vào đây</li>
                </ol>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="border-green-500 text-green-700">
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>{success}</AlertDescription>
                </Alert>
              )}

              <div className="flex gap-2">
                <Button
                  onClick={handleScan}
                  disabled={scanning || !templateUrl.trim()}
                >
                  {scanning && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  <ScanLine className="mr-2 h-4 w-4" />
                  Quét template
                </Button>
                {patterns.length > 0 && (
                  <Button onClick={handleSave} disabled={saving}>
                    {saving && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    <Save className="mr-2 h-4 w-4" />
                    Lưu vào dự án
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {patterns.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Kết quả quét</CardTitle>
                <CardDescription>
                  {patterns.length} patterns đã được tạo từ template
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Loại</TableHead>
                      <TableHead>Pattern nguồn</TableHead>
                      <TableHead>Pattern đích</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {patterns.map((pattern, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Badge variant="outline">{pattern.element_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <code className="text-xs bg-muted px-1 py-0.5 rounded break-all">
                            {pattern.source_pattern}
                          </code>
                        </TableCell>
                        <TableCell>
                          <code className="text-xs bg-muted px-1 py-0.5 rounded break-all">
                            {pattern.target_pattern}
                          </code>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

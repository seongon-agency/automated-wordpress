"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
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
  updateProject,
  scanHtmlForPatterns,
  type Project,
  type HtmlPattern,
  type ScanPatternResponse,
} from "@/lib/api";

type ScanState = "idle" | "scanning" | "done";

export default function ScanPatternsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [htmlContent, setHtmlContent] = useState("");
  const [scanState, setScanState] = useState<ScanState>("idle");
  const [scanResult, setScanResult] = useState<ScanPatternResponse | null>(null);
  const [selectedPatterns, setSelectedPatterns] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

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

  const handleScan = async () => {
    if (!htmlContent.trim()) {
      setError("Vui lòng nhập nội dung HTML");
      return;
    }

    try {
      setScanState("scanning");
      setError(null);
      setScanResult(null);
      setSelectedPatterns(new Set());

      const result = await scanHtmlForPatterns(htmlContent);

      setScanResult(result);
      setScanState("done");

      if (result.success && result.patterns) {
        // Select all patterns by default
        setSelectedPatterns(new Set(result.patterns.map((_, i) => i)));
      } else {
        setError(result.error || "Quét HTML thất bại");
      }
    } catch (err) {
      setScanState("done");
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
    }
  };

  const togglePatternSelection = (index: number) => {
    const newSelected = new Set(selectedPatterns);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedPatterns(newSelected);
  };

  const toggleSelectAll = () => {
    if (!scanResult?.patterns) return;

    if (selectedPatterns.size === scanResult.patterns.length) {
      setSelectedPatterns(new Set());
    } else {
      setSelectedPatterns(new Set(scanResult.patterns.map((_, i) => i)));
    }
  };

  const handleSaveToProject = async () => {
    if (!selectedProjectId) {
      setError("Vui lòng chọn dự án để lưu patterns");
      return;
    }

    if (!scanResult?.patterns || selectedPatterns.size === 0) {
      setError("Vui lòng chọn ít nhất một pattern");
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const patternsToSave = scanResult.patterns
        .filter((_, i) => selectedPatterns.has(i))
        .map((p) => ({
          element_type: p.element_type,
          source_pattern: p.source_pattern,
          target_pattern: p.target_pattern,
        }));

      const response = await updateProject(selectedProjectId, {
        html_configs: { patterns: patternsToSave },
      });

      if (response.success) {
        router.push(`/projects/${selectedProjectId}`);
      } else {
        setError("Không thể lưu patterns vào dự án");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi lưu patterns");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setHtmlContent("");
    setScanState("idle");
    setScanResult(null);
    setSelectedPatterns(new Set());
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Quét & Tạo Patterns</h1>
          <p className="text-muted-foreground mt-2">
            AI phân tích HTML mẫu và tạo patterns chuyển đổi tự động
          </p>
        </div>
        <Link href="/patterns">
          <Button variant="outline">← Quay lại</Button>
        </Link>
      </div>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Hướng Dẫn</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>1. Dán HTML mẫu có chứa các kiểu định dạng bạn muốn áp dụng</p>
          <p>2. Nhấn &quot;Quét HTML&quot; để AI phân tích và tạo patterns</p>
          <p>3. Xem và chọn các patterns bạn muốn sử dụng</p>
          <p>4. Chọn dự án và lưu patterns</p>
        </CardContent>
      </Card>

      {/* HTML Input */}
      <Card>
        <CardHeader>
          <CardTitle>Nội Dung HTML Mẫu</CardTitle>
          <CardDescription>
            Dán HTML có chứa các thẻ đã được định dạng (classes, styles, attributes)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="htmlContent">HTML Content</Label>
            <Textarea
              id="htmlContent"
              placeholder={`<h2 class="section-title" style="color: blue;">Tiêu Đề</h2>
<p class="content-text">Nội dung đoạn văn...</p>
<img src="image.jpg" class="featured-image" alt="Mô tả"/>
...`}
              value={htmlContent}
              onChange={(e) => setHtmlContent(e.target.value)}
              rows={12}
              className="font-mono text-sm"
              disabled={scanState === "scanning"}
            />
            <p className="text-xs text-muted-foreground">
              Tối đa 100KB. AI sẽ trích xuất patterns từ các thẻ HTML trong mẫu này.
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-4">
            <Button
              onClick={handleScan}
              disabled={scanState === "scanning" || !htmlContent.trim()}
              className="flex-1"
            >
              {scanState === "scanning" ? "Đang quét..." : "Quét HTML"}
            </Button>
            {scanState !== "idle" && (
              <Button variant="outline" onClick={handleReset}>
                Làm Mới
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Scanning State */}
      {scanState === "scanning" && (
        <Card>
          <CardContent className="py-8">
            <div className="text-center space-y-4">
              <div className="w-full bg-muted rounded-full h-2 max-w-md mx-auto">
                <div className="bg-primary h-2 rounded-full animate-pulse w-2/3"></div>
              </div>
              <p className="text-muted-foreground">
                AI đang phân tích HTML và tạo patterns...
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scan Results */}
      {scanState === "done" && scanResult?.success && scanResult.patterns && (
        <>
          {/* Elements Found */}
          {scanResult.elements_found && scanResult.elements_found.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Các Thẻ Đã Tìm Thấy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {scanResult.elements_found.map((element, i) => (
                    <Badge key={i} variant="secondary">
                      {element}
                    </Badge>
                  ))}
                </div>
                {scanResult.notes && (
                  <p className="text-sm text-muted-foreground mt-4">
                    {scanResult.notes}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Patterns Table */}
          <Card>
            <CardHeader>
              <CardTitle>
                Patterns Đã Tạo ({selectedPatterns.size}/{scanResult.patterns.length} đã chọn)
              </CardTitle>
              <CardDescription>
                Chọn các patterns bạn muốn sử dụng cho dự án
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
                          checked={selectedPatterns.size === scanResult.patterns.length}
                          onChange={toggleSelectAll}
                          className="h-4 w-4"
                        />
                      </TableHead>
                      <TableHead className="w-24">Loại</TableHead>
                      <TableHead>Source Pattern</TableHead>
                      <TableHead>Target Pattern</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scanResult.patterns.map((pattern, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={selectedPatterns.has(index)}
                            onChange={() => togglePatternSelection(index)}
                            className="h-4 w-4"
                          />
                        </TableCell>
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
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Save to Project */}
              <div className="border-t pt-4 space-y-4">
                <div className="space-y-2">
                  <Label>Lưu Patterns Vào Dự Án</Label>
                  {loadingProjects ? (
                    <p className="text-sm text-muted-foreground">Đang tải dự án...</p>
                  ) : (
                    <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Chọn dự án..." />
                      </SelectTrigger>
                      <SelectContent>
                        {projects.map((project) => (
                          <SelectItem key={project.project_id} value={project.project_id}>
                            {project.project_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>

                <Button
                  onClick={handleSaveToProject}
                  disabled={saving || !selectedProjectId || selectedPatterns.size === 0}
                  className="w-full"
                >
                  {saving
                    ? "Đang lưu..."
                    : `Lưu ${selectedPatterns.size} Patterns Vào Dự Án`}
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* No Patterns Found */}
      {scanState === "done" && scanResult?.success && (!scanResult.patterns || scanResult.patterns.length === 0) && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              Không tìm thấy patterns trong HTML. Hãy thử với HTML có các thẻ đã được định dạng.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

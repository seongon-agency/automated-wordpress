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
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Loader2,
  CheckCircle,
  XCircle,
  ExternalLink,
  Info,
  RefreshCw,
} from "lucide-react";
import { api, type Project, type PublishHistory } from "@/lib/api";

export default function HistoryPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [history, setHistory] = useState<PublishHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<string>("all");
  const [selectedError, setSelectedError] = useState<PublishHistory | null>(
    null
  );

  useEffect(() => {
    fetchData();
  }, [selectedProject]);

  async function fetchData() {
    setLoading(true);
    try {
      const [projectsRes, historyRes] = await Promise.all([
        api.projects.list(),
        selectedProject === "all"
          ? api.history.list(undefined, 100)
          : api.history.byProject(selectedProject, 100),
      ]);

      if (projectsRes.success) {
        setProjects(projectsRes.projects || []);
      }
      if (historyRes.success) {
        setHistory(historyRes.history || []);
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  }

  const stats = {
    total: history.length,
    success: history.filter((h) => h.success).length,
    failed: history.filter((h) => !h.success).length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Lịch sử xuất bản
          </h1>
          <p className="text-muted-foreground">
            Theo dõi tất cả các bài viết đã xuất bản
          </p>
        </div>
        <Button variant="outline" onClick={fetchData} disabled={loading}>
          <RefreshCw
            className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`}
          />
          Làm mới
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tổng số bài
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Thành công
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats.success}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Thất bại
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filter & Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Chi tiết lịch sử</CardTitle>
              <CardDescription>
                Danh sách các bài viết đã xuất bản
              </CardDescription>
            </div>
            <Select value={selectedProject} onValueChange={setSelectedProject}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Lọc theo dự án" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả dự án</SelectItem>
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
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Chưa có lịch sử xuất bản nào
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Trạng thái</TableHead>
                  <TableHead>Tiêu đề</TableHead>
                  <TableHead>Dự án</TableHead>
                  <TableHead>Thời gian</TableHead>
                  <TableHead className="text-right">Thao tác</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      {item.success ? (
                        <Badge variant="default" className="bg-green-600">
                          <CheckCircle className="mr-1 h-3 w-3" />
                          Thành công
                        </Badge>
                      ) : (
                        <Badge variant="destructive">
                          <XCircle className="mr-1 h-3 w-3" />
                          Thất bại
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="max-w-[300px]">
                        <p className="font-medium truncate">
                          {item.post_title || "Không có tiêu đề"}
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                          {item.google_docs_url}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>{item.project_id}</TableCell>
                    <TableCell>
                      {new Date(item.published_at).toLocaleString("vi-VN")}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {item.success && item.post_url && (
                          <Button variant="ghost" size="icon" asChild>
                            <a
                              href={item.post_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        )}
                        {!item.success && item.error_message && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setSelectedError(item)}
                          >
                            <Info className="h-4 w-4 text-destructive" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Error Dialog */}
      <Dialog
        open={!!selectedError}
        onOpenChange={() => setSelectedError(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Chi tiết lỗi</DialogTitle>
            <DialogDescription>
              Thông tin lỗi khi xuất bản bài viết
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Tiêu đề
              </p>
              <p>{selectedError?.post_title || "Không có tiêu đề"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Thời gian
              </p>
              <p>
                {selectedError &&
                  new Date(selectedError.published_at).toLocaleString("vi-VN")}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Lỗi chi tiết
              </p>
              <pre className="mt-2 rounded bg-muted p-4 text-sm whitespace-pre-wrap">
                {selectedError?.error_message}
              </pre>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

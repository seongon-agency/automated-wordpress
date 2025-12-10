"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
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
  getHistory,
  getHistoryStats,
  type Project,
  type HistoryEntry,
  type HistoryStatsResponse,
} from "@/lib/api";

type FilterStatus = "all" | "success" | "failed";

export default function HistoryPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [stats, setStats] = useState<HistoryStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all");

  // Fetch projects on mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await getProjects("all");
        if (response.success && response.projects) {
          setProjects(response.projects);
        }
      } catch (err) {
        console.error("Failed to fetch projects:", err);
      }
    };
    fetchProjects();
  }, []);

  // Fetch history when filter changes
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        const projectId = selectedProjectId === "all" ? undefined : selectedProjectId;

        const [historyResponse, statsResponse] = await Promise.all([
          getHistory(projectId, 100),
          getHistoryStats(projectId),
        ]);

        if (historyResponse.success) {
          let filteredHistory = historyResponse.history;

          // Apply status filter
          if (filterStatus === "success") {
            filteredHistory = filteredHistory.filter((h) => h.success);
          } else if (filterStatus === "failed") {
            filteredHistory = filteredHistory.filter((h) => !h.success);
          }

          setHistory(filteredHistory);
        }

        if (statsResponse.success) {
          setStats(statsResponse);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Lỗi khi tải lịch sử");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [selectedProjectId, filterStatus]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const truncateUrl = (url: string, maxLength: number = 50) => {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + "...";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Lịch Sử Đăng Bài</h1>
        <p className="text-muted-foreground mt-2">
          Xem lịch sử các bài đã đăng lên WordPress
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Tổng Số</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{stats.total}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Thành Công</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-green-600">{stats.successful}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Thất Bại</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-red-600">{stats.failed}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Tỷ Lệ Thành Công</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{stats.success_rate}%</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Bộ Lọc</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="space-y-2 flex-1">
              <label className="text-sm font-medium">Dự Án</label>
              <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn dự án..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tất Cả Dự Án</SelectItem>
                  {projects.map((project) => (
                    <SelectItem key={project.project_id} value={project.project_id}>
                      {project.project_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2 flex-1">
              <label className="text-sm font-medium">Trạng Thái</label>
              <Select
                value={filterStatus}
                onValueChange={(v) => setFilterStatus(v as FilterStatus)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tất Cả</SelectItem>
                  <SelectItem value="success">Thành Công</SelectItem>
                  <SelectItem value="failed">Thất Bại</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">&nbsp;</label>
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedProjectId("all");
                  setFilterStatus("all");
                }}
              >
                Xóa Bộ Lọc
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* History Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lịch Sử Đăng Bài</CardTitle>
          <CardDescription>
            {loading
              ? "Đang tải..."
              : `Hiển thị ${history.length} bản ghi`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : history.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              Chưa có lịch sử đăng bài nào.
            </p>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-40">Thời Gian</TableHead>
                    <TableHead>Tiêu Đề</TableHead>
                    <TableHead>Dự Án</TableHead>
                    <TableHead className="w-24 text-center">Ảnh</TableHead>
                    <TableHead className="w-24 text-center">Thời Gian XL</TableHead>
                    <TableHead className="w-28">Trạng Thái</TableHead>
                    <TableHead className="w-24"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="text-sm">
                        {formatDate(entry.published_at)}
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <p className="font-medium">
                            {entry.post_title || "Không có tiêu đề"}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {truncateUrl(entry.google_docs_url)}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        {entry.project_name || entry.project_id || "N/A"}
                      </TableCell>
                      <TableCell className="text-center">
                        {entry.images_processed}
                      </TableCell>
                      <TableCell className="text-center">
                        {entry.execution_time_seconds
                          ? `${entry.execution_time_seconds.toFixed(1)}s`
                          : "N/A"}
                      </TableCell>
                      <TableCell>
                        {entry.success ? (
                          <Badge variant="default">Thành Công</Badge>
                        ) : (
                          <Badge variant="destructive" title={entry.error_message || ""}>
                            Thất Bại
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {entry.wordpress_post_url && (
                          <a
                            href={entry.wordpress_post_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline"
                          >
                            Xem bài
                          </a>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Failed Entries Details */}
      {filterStatus === "failed" && history.length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Chi Tiết Lỗi</CardTitle>
            <CardDescription>
              Thông tin lỗi cho các bài đăng thất bại
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {history.map((entry) => (
                <div key={entry.id} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <p className="font-medium">{entry.post_title || "Không có tiêu đề"}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(entry.published_at)}
                    </p>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">
                    URL: {truncateUrl(entry.google_docs_url, 80)}
                  </p>
                  {entry.error_message && (
                    <Alert variant="destructive">
                      <AlertDescription className="text-sm">
                        {entry.error_message}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

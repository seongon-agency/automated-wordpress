"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Info, Send, FolderKanban, History, TrendingUp } from "lucide-react";
import { getProjects, getHistoryStats, type Project, type HistoryStatsResponse } from "@/lib/api";

export default function HomePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<HistoryStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectsResponse, statsResponse] = await Promise.all([
          getProjects("all"),
          getHistoryStats(),
        ]);

        if (projectsResponse.success && projectsResponse.projects) {
          setProjects(projectsResponse.projects);
        }

        if (statsResponse.success) {
          setStats(statsResponse);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const activeProjects = projects.filter((p) => p.status === "active").length;
  const recentProjects = projects.slice(0, 3);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Hệ Thống Đăng Bài SEO WordPress</h1>
        <p className="text-muted-foreground mt-2">Bảng điều khiển tổng quan</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <FolderKanban className="h-4 w-4" />
              Tổng Số Dự Án
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <div>
                <p className="text-3xl font-bold">{projects.length}</p>
                <p className="text-xs text-muted-foreground">
                  {activeProjects} hoạt động
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Send className="h-4 w-4" />
              Bài Đã Đăng
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <div>
                <p className="text-3xl font-bold">{stats?.total || 0}</p>
                <p className="text-xs text-muted-foreground">
                  {stats?.successful || 0} thành công
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Tỷ Lệ Thành Công
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <div>
                <p className="text-3xl font-bold">
                  {stats?.success_rate || 0}%
                </p>
                <p className="text-xs text-muted-foreground">
                  {stats?.failed || 0} thất bại
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <History className="h-4 w-4" />
              Trạng Thái
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="default" className="text-lg px-3 py-1">
              Sẵn Sàng
            </Badge>
            <p className="text-xs text-muted-foreground mt-1">
              v2.0.0
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Thao Tác Nhanh</CardTitle>
          <CardDescription>
            Các chức năng thường dùng
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link href="/publish">
              <Button variant="default" className="w-full h-20 flex flex-col gap-1">
                <Send className="h-5 w-5" />
                <span>Đăng Bài</span>
              </Button>
            </Link>
            <Link href="/projects/new">
              <Button variant="outline" className="w-full h-20 flex flex-col gap-1">
                <FolderKanban className="h-5 w-5" />
                <span>Tạo Dự Án</span>
              </Button>
            </Link>
            <Link href="/publish/batch">
              <Button variant="outline" className="w-full h-20 flex flex-col gap-1">
                <Send className="h-5 w-5" />
                <span>Đăng Hàng Loạt</span>
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="outline" className="w-full h-20 flex flex-col gap-1">
                <History className="h-5 w-5" />
                <span>Lịch Sử</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Recent Projects */}
      {!loading && recentProjects.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Dự Án Gần Đây</CardTitle>
                <CardDescription>
                  Các dự án bạn làm việc gần đây
                </CardDescription>
              </div>
              <Link href="/projects">
                <Button variant="ghost" size="sm">
                  Xem tất cả →
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentProjects.map((project) => (
                <Link key={project.project_id} href={`/projects/${project.project_id}`}>
                  <div className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                    <div>
                      <p className="font-medium">{project.project_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {project.wordpress_url}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge variant={project.status === "active" ? "default" : "secondary"}>
                        {project.status === "active" ? "Hoạt động" : "Tạm dừng"}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        {project.html_configs?.patterns?.length || 0} patterns
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Getting Started Guide */}
      <Card>
        <CardHeader>
          <CardTitle>Hướng Dẫn Sử Dụng</CardTitle>
          <CardDescription>
            Các bước để bắt đầu sử dụng hệ thống
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                1
              </div>
              <div>
                <p className="font-medium">Tạo Dự Án</p>
                <p className="text-sm text-muted-foreground">
                  Thêm thông tin trang WordPress của bạn (URL, username, app password)
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                2
              </div>
              <div>
                <p className="font-medium">Cấu Hình Patterns (Tùy Chọn)</p>
                <p className="text-sm text-muted-foreground">
                  Quét HTML mẫu hoặc dùng AI để tạo patterns chuyển đổi HTML tự động
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                3
              </div>
              <div>
                <p className="font-medium">Chuẩn Bị Nội Dung</p>
                <p className="text-sm text-muted-foreground">
                  Viết bài trong Google Docs và lấy URL chia sẻ (edit hoặc published)
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                4
              </div>
              <div>
                <p className="font-medium">Đăng Bài</p>
                <p className="text-sm text-muted-foreground">
                  Chọn dự án, dán URL Google Docs và nhấn đăng. Bài viết sẽ được tạo dưới dạng nháp.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Mẹo:</strong> Sử dụng nút &quot;Đăng Bài Nhanh&quot; ở thanh bên để truy cập nhanh chức năng đăng bài.
          Bài viết luôn được tạo dưới dạng nháp để bạn có thể xem lại trước khi xuất bản.
        </AlertDescription>
      </Alert>
    </div>
  );
}

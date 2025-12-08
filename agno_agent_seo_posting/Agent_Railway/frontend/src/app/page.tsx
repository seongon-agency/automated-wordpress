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
import {
  FolderOpen,
  Upload,
  History,
  Wand2,
  ArrowRight,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { api, type Project, type PublishHistory } from "@/lib/api";

export default function HomePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [recentHistory, setRecentHistory] = useState<PublishHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [projectsRes, historyRes] = await Promise.all([
          api.projects.list(),
          api.history.list(undefined, 5),
        ]);
        if (projectsRes.success) {
          setProjects(projectsRes.projects || []);
        }
        if (historyRes.success) {
          setRecentHistory(historyRes.history || []);
        }
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const stats = [
    {
      title: "Tổng dự án",
      value: projects.length,
      icon: FolderOpen,
      href: "/projects",
      color: "text-blue-600",
    },
    {
      title: "Bài đã xuất bản",
      value: recentHistory.filter((h) => h.success).length,
      icon: CheckCircle,
      href: "/history",
      color: "text-green-600",
    },
    {
      title: "Lỗi gần đây",
      value: recentHistory.filter((h) => !h.success).length,
      icon: XCircle,
      href: "/history",
      color: "text-red-600",
    },
  ];

  const quickActions = [
    {
      title: "Xuất bản nội dung",
      description: "Đăng bài từ Google Docs lên WordPress",
      icon: Upload,
      href: "/publish",
    },
    {
      title: "Tạo dự án mới",
      description: "Cấu hình website WordPress mới",
      icon: FolderOpen,
      href: "/projects/new",
    },
    {
      title: "Chỉnh sửa Pattern",
      description: "Tùy chỉnh định dạng HTML với AI",
      icon: Wand2,
      href: "/patterns",
    },
    {
      title: "Xem lịch sử",
      description: "Theo dõi các bài đã xuất bản",
      icon: History,
      href: "/history",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Chào mừng đến SEO Publisher
        </h1>
        <p className="text-muted-foreground">
          Hệ thống xuất bản SEO từ Google Docs lên WordPress
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {loading ? "..." : stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Thao tác nhanh</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {quickActions.map((action) => (
            <Card
              key={action.title}
              className="hover:border-primary/50 transition-colors"
            >
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <action.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{action.title}</CardTitle>
                    <CardDescription>{action.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full" asChild>
                  <Link href={action.href}>
                    Bắt đầu
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent History */}
      {recentHistory.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Xuất bản gần đây</h2>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/history">
                Xem tất cả
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                {recentHistory.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-4"
                  >
                    <div className="flex items-center gap-3">
                      {item.success ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-600" />
                      )}
                      <div>
                        <p className="font-medium text-sm">
                          {item.post_title || "Không có tiêu đề"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {item.project_id}
                        </p>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(item.published_at).toLocaleDateString("vi-VN")}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
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
import { getProjects, type Project } from "@/lib/api";

export default function EditProjectSelectorPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const response = await getProjects("all");
        if (response.success && response.projects) {
          setProjects(response.projects);
        } else {
          setError("Không thể tải danh sách dự án");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Lỗi khi tải dự án");
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const handleGoToEdit = () => {
    if (selectedProjectId) {
      router.push(`/projects/${selectedProjectId}`);
    }
  };

  const selectedProject = projects.find((p) => p.project_id === selectedProjectId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Chỉnh Sửa Dự Án</h1>
        <p className="text-muted-foreground mt-2">
          Chọn dự án bạn muốn chỉnh sửa cài đặt
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Chọn Dự Án</CardTitle>
          <CardDescription>
            Chọn một dự án từ danh sách để chỉnh sửa thông tin WordPress, cài đặt ảnh, hoặc HTML patterns
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">
                Chưa có dự án nào. Hãy tạo dự án mới trước.
              </p>
              <Link href="/projects/new">
                <Button>Tạo Dự Án Mới</Button>
              </Link>
            </div>
          ) : (
            <>
              <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn dự án để chỉnh sửa..." />
                </SelectTrigger>
                <SelectContent>
                  {projects.map((project) => (
                    <SelectItem key={project.project_id} value={project.project_id}>
                      <div className="flex items-center gap-2">
                        <span>{project.project_name}</span>
                        <Badge
                          variant={project.status === "active" ? "default" : "secondary"}
                          className="ml-2"
                        >
                          {project.status === "active" ? "Hoạt động" : "Tạm dừng"}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {selectedProject && (
                <Card className="bg-muted/50">
                  <CardContent className="pt-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="font-medium">ID Dự Án</p>
                        <p className="text-muted-foreground">
                          <code className="bg-background px-1 rounded">
                            {selectedProject.project_id}
                          </code>
                        </p>
                      </div>
                      <div>
                        <p className="font-medium">URL WordPress</p>
                        <p className="text-muted-foreground truncate">
                          {selectedProject.wordpress_url}
                        </p>
                      </div>
                      <div>
                        <p className="font-medium">Số Patterns</p>
                        <p className="text-muted-foreground">
                          {selectedProject.html_configs?.patterns?.length || 0} patterns
                        </p>
                      </div>
                      <div>
                        <p className="font-medium">Lần Đăng Cuối</p>
                        <p className="text-muted-foreground">
                          {selectedProject.last_published_at
                            ? new Date(selectedProject.last_published_at).toLocaleDateString("vi-VN")
                            : "Chưa đăng bài"}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Button
                onClick={handleGoToEdit}
                disabled={!selectedProjectId}
                className="w-full"
              >
                Chỉnh Sửa Dự Án
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {/* Quick Links */}
      {!loading && projects.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Truy Cập Nhanh</CardTitle>
            <CardDescription>
              Danh sách các dự án gần đây
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {projects.slice(0, 5).map((project) => (
                <Link key={project.project_id} href={`/projects/${project.project_id}`}>
                  <div className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div>
                        <p className="font-medium">{project.project_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {project.wordpress_url}
                        </p>
                      </div>
                    </div>
                    <Badge variant={project.status === "active" ? "default" : "secondary"}>
                      {project.status === "active" ? "Hoạt động" : "Tạm dừng"}
                    </Badge>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

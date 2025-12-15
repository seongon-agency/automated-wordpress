"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getProjects, deleteProject, type Project } from "@/lib/api";
import { useAuth } from "@/components/auth-provider";

export default function ProjectsPage() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchProjects = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      setError(null);
      const response = await getProjects("all", user.id);
      if (response.success && response.projects) {
        setProjects(response.projects);
      } else {
        setError("Không thể tải danh sách dự án");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [user?.id]);

  const handleDeleteClick = (project: Project) => {
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!projectToDelete || !user?.id) return;

    try {
      setDeleting(true);
      const response = await deleteProject(projectToDelete.project_id, user.id);
      if (response.success) {
        setProjects(projects.filter((p) => p.project_id !== projectToDelete.project_id));
        setDeleteDialogOpen(false);
        setProjectToDelete(null);
      } else {
        setError("Không thể xóa dự án");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi xóa dự án");
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Danh Sách Dự Án</h1>
          <p className="text-muted-foreground mt-2">Quản lý các dự án WordPress của bạn</p>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-48" />
                <Skeleton className="h-4 w-32 mt-2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4 mt-2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Danh Sách Dự Án</h1>
          <p className="text-muted-foreground mt-2">Quản lý các dự án WordPress của bạn</p>
        </div>
        <Link href="/projects/new">
          <Button>+ Tạo Dự Án Mới</Button>
        </Link>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {projects.length > 0 && (
        <p className="text-sm text-muted-foreground">
          Tìm thấy {projects.length} dự án
        </p>
      )}

      {projects.length === 0 && !error ? (
        <Card>
          <CardHeader>
            <CardTitle>Chưa có dự án</CardTitle>
            <CardDescription>
              Bạn chưa tạo dự án nào. Hãy tạo dự án đầu tiên để bắt đầu!
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/projects/new">
              <Button>Tạo Dự Án Đầu Tiên</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {projects.map((project) => (
            <Card key={project.project_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {project.project_name}
                      <Badge
                        variant={project.status === "active" ? "default" : "secondary"}
                      >
                        {project.status === "active" ? "Hoạt động" : "Tạm dừng"}
                      </Badge>
                    </CardTitle>
                    <CardDescription className="mt-1">
                      ID: <code className="bg-muted px-1 rounded">{project.project_id}</code>
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Link href={`/projects/${project.project_id}`}>
                      <Button variant="outline" size="sm">
                        Chỉnh sửa
                      </Button>
                    </Link>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteClick(project)}
                    >
                      Xóa
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">URL WordPress</p>
                    <p className="font-medium truncate">{project.wordpress_url}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Tên Đăng Nhập</p>
                    <p className="font-medium">{project.wordpress_username}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">HTML Patterns</p>
                    <p className="font-medium">
                      {project.html_configs?.patterns?.length
                        ? `${project.html_configs.patterns.length} mẫu đã cấu hình`
                        : "Chưa cấu hình"}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Cài Đặt Ảnh</p>
                    <p className="font-medium">
                      {project.image_configs
                        ? `${project.image_configs.target_width}px, ${project.image_configs.image_quality}%`
                        : "Mặc định"}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Ngày Tạo</p>
                    <p className="font-medium">{formatDate(project.created_at)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Xuất Bản Gần Nhất</p>
                    <p className="font-medium">{formatDate(project.last_published_at)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xác Nhận Xóa Dự Án</DialogTitle>
            <DialogDescription>
              Bạn có chắc chắn muốn xóa dự án &quot;{projectToDelete?.project_name}&quot;?
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
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleting}
            >
              {deleting ? "Đang xóa..." : "Xóa Dự Án"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

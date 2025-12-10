"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  FolderKanban,
  Plus,
  Settings,
  Wand2,
  ScanLine,
  Send,
  Layers,
  History,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

const navigationItems = {
  overview: [
    {
      title: "Bảng Điều Khiển",
      url: "/",
      icon: LayoutDashboard,
    },
  ],
  projects: [
    {
      title: "Xem Dự Án",
      url: "/projects",
      icon: FolderKanban,
    },
    {
      title: "Tạo Mới",
      url: "/projects/new",
      icon: Plus,
    },
    {
      title: "Chỉnh Sửa Cài Đặt",
      url: "/projects/edit",
      icon: Settings,
    },
  ],
  aiConfig: [
    {
      title: "Sửa HTML Patterns",
      url: "/patterns",
      icon: Wand2,
    },
    {
      title: "Quét & Tạo Patterns",
      url: "/patterns/scan",
      icon: ScanLine,
    },
  ],
  publishing: [
    {
      title: "Đăng Một Bài",
      url: "/publish",
      icon: Send,
    },
    {
      title: "Đăng Hàng Loạt",
      url: "/publish/batch",
      icon: Layers,
    },
    {
      title: "Lịch Sử Đăng Bài",
      url: "/history",
      icon: History,
    },
  ],
}

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-lg font-semibold">Hệ Thống Đăng Bài WordPress</h1>
          <p className="text-xs text-muted-foreground">
            Phát triển nội bộ • Tích hợp AI
          </p>
        </div>
        <Separator className="my-2" />
        <Link href="/publish">
          <Button className="w-full" size="sm">
            <Send className="mr-2 h-4 w-4" />
            Đăng Bài Nhanh
          </Button>
        </Link>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Tổng Quan</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.overview.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Dự Án</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.projects.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Cấu Hình AI</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.aiConfig.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Đăng Bài</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.publishing.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-4">
        <Separator className="mb-2" />
        <div className="text-xs text-muted-foreground space-y-1">
          <p><strong>Mẹo:</strong> Dùng Đăng Bài Nhanh để truy cập nhanh</p>
          <p><strong>Công nghệ:</strong> Railway PostgreSQL • Next.js • Claude AI</p>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}

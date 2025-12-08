"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Home,
  FolderOpen,
  Plus,
  Upload,
  Layers,
  History,
  Wand2,
  ScanLine,
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
  SidebarRail,
} from "@/components/ui/sidebar"

const navigation = {
  main: [
    {
      title: "Trang chủ",
      url: "/",
      icon: Home,
    },
  ],
  projects: [
    {
      title: "Danh sách dự án",
      url: "/projects",
      icon: FolderOpen,
    },
    {
      title: "Tạo dự án mới",
      url: "/projects/new",
      icon: Plus,
    },
  ],
  publishing: [
    {
      title: "Xuất bản đơn",
      url: "/publish",
      icon: Upload,
    },
    {
      title: "Xuất bản hàng loạt",
      url: "/publish/batch",
      icon: Layers,
    },
    {
      title: "Lịch sử xuất bản",
      url: "/history",
      icon: History,
    },
  ],
  ai: [
    {
      title: "Chỉnh sửa Pattern",
      url: "/patterns",
      icon: Wand2,
    },
    {
      title: "Quét mẫu HTML",
      url: "/patterns/scan",
      icon: ScanLine,
    },
  ],
}

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Upload className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold">SEO Publisher</span>
            <span className="text-xs text-muted-foreground">WordPress</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.main.map((item) => (
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
          <SidebarGroupLabel>Quản lý dự án</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.projects.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url || (item.url === "/projects" && pathname.startsWith("/projects/") && pathname !== "/projects/new")}
                  >
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
          <SidebarGroupLabel>Xuất bản nội dung</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.publishing.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url}
                  >
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
          <SidebarGroupLabel>AI Patterns</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.ai.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url || (item.url === "/patterns" && pathname.startsWith("/patterns/") && pathname !== "/patterns/scan")}
                  >
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
      <SidebarRail />
    </Sidebar>
  )
}

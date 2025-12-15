import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that don't require authentication
const publicRoutes = ["/login", "/register", "/api/auth"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if the route is public
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  // Get the session cookie (better-auth uses this cookie name)
  const sessionCookie = request.cookies.get("better-auth.session_token");

  // If not authenticated and trying to access protected route, redirect to login
  if (!isPublicRoute && !sessionCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If authenticated and trying to access login/register, redirect to home
  if (sessionCookie && (pathname === "/login" || pathname === "/register")) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};

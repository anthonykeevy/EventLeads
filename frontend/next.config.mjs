/** @type {import('next').NextConfig} */
const API_PROXY_TARGET = process.env.API_PROXY_TARGET || 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      // Invitations endpoints
      { source: '/invitations/:path*', destination: `${API_PROXY_TARGET}/invitations/:path*` },
      // (Optional) Other backend routes used during UAT
      { source: '/auth/:path*', destination: `${API_PROXY_TARGET}/auth/:path*` },
      { source: '/events/:path*', destination: `${API_PROXY_TARGET}/events/:path*` },
      // Organisations endpoints
      { source: '/organizations/:path*', destination: `${API_PROXY_TARGET}/organizations/:path*` },
    ];
  },
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
};

export default nextConfig;

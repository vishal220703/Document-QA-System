/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const rawBackendUrl = process.env.BACKEND_INTERNAL_URL ?? "http://127.0.0.1:8000";
    const backendUrl = rawBackendUrl.replace(/\/+$/, "").replace(/\/api$/, "");
    return [
      {
        source: "/api/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Server-side proxy: dentro do Docker, backend e acessivel via nome do service
    // Fora do Docker, usa localhost:8000
    const backendUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

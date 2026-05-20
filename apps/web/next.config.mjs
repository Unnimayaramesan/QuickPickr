/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@quickpickr/api-client", "@quickpickr/shared", "@quickpickr/design-tokens"],
  output: "standalone",
};

export default nextConfig;

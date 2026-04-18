import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import NetworkBackground from "../components/NetworkBackground";
import FeedbackWidget from "../components/FeedbackWidget";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ClinicaSync | AI Drug Repurposing Engine",
  description: "Computational drug repurposing platform mapping diseases to new therapeutic uses via Network Pharmacology.",
  icons: {
    icon: "/favicon.png",
    apple: "/favicon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <NetworkBackground />
        {children}
        <FeedbackWidget />
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}

import { Metadata } from "next";

export const metadata: Metadata = {
  title: "TheraMatch | AI Drug Repurposing Engine",
  description: "Identify new therapeutic uses for existing drugs using purely biological networks and AI.",
  icons: {
    icon: "/favicon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}

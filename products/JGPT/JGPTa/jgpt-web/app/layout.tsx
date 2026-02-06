import "./globals.css";
import type { ReactNode } from "react";
import { AuthProvider } from "./context/AuthContext";
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata = { title: "JGPT", description: "Garnet Grid Copilot" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <div className="bg">
          <div className="glow" />
          <AuthProvider>
            {children}
          </AuthProvider>
        </div>
      </body>
    </html>
  );
}

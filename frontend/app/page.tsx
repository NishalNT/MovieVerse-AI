"use client";

import React from "react";
import Chat from "@/components/Chat";
import { ThemeProvider } from "next-themes";

export default function Home() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <main className="h-screen">
        <Chat />
      </main>
    </ThemeProvider>
  );
}

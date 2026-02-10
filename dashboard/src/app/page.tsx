"use client";

import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { Wallet, AlertTriangle, TrendingUp, Activity, Shield, Zap, Database } from "lucide-react";
import { useEffect, useState } from "react";

interface Invoice {
  _id: string;
  _creationTime: number;
  telegram_id: string;
  vendor: string;
  amount: number;
  status: string;
  category?: string;
  gstin?: string;
  date?: string;
  compliance_flags?: string[];
}

export default function Dashboard() {
  const invoices = useQuery(api.invoices.get) as Invoice[] || [];
  const [currentTime, setCurrentTime] = useState<string>("");

  // Update time on client side only
  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString());
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // KPI Calculations
  const totalSpent = invoices.reduce((sum, inv) => sum + inv.amount, 0);
  const blockedCount = invoices.filter(i => i.status === "blocked").length;
  const compliantCount = invoices.filter(i => i.status === "compliant").length;
  const reviewCount = invoices.filter(i => i.status === "review_needed").length;

  // Calculate ITC eligible amount
  const itcEligible = invoices
    .filter(i => i.status === "compliant")
    .reduce((sum, inv) => sum + (inv.amount * 0.18), 0);

  // Prepare Chart Data
  const categoryData: { name: string; value: number; count: number }[] = invoices.reduce((acc: { name: string; value: number; count: number }[], curr: any) => {
    const existing = acc.find(item => item.name === curr.category);
    if (existing) {
      existing.value += curr.amount;
      existing.count += 1;
    } else {
      acc.push({
        name: curr.category || "Uncategorized",
        value: curr.amount,
        count: 1
      });
    }
    return acc;
  }, []).sort((a, b) => b.value - a.value);

  // Status distribution for bar chart
  const statusData = [
    { name: "Compliant", value: compliantCount, color: "rgb(34, 197, 94)" },
    { name: "Review", value: reviewCount, color: "rgb(251, 191, 36)" },
    { name: "Blocked", value: blockedCount, color: "rgb(239, 68, 68)" },
  ];

  const COLORS = [
    'rgb(139, 92, 246)',  // Purple
    'rgb(236, 72, 153)',  // Pink
    'rgb(59, 130, 246)',  // Blue
    'rgb(34, 197, 94)',   // Green
    'rgb(251, 191, 36)',  // Yellow
    'rgb(249, 115, 22)',  // Orange
  ];

  return (
    <div className="min-h-screen bg-zinc-950 relative overflow-hidden">
      {/* Animated grid background */}
      <div className="fixed inset-0 grid-background opacity-20" />

      {/* Gradient orbs for atmosphere */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-violet-600 rounded-full blur-[120px] opacity-20 animate-pulse" />
      <div className="fixed bottom-0 left-0 w-[400px] h-[400px] bg-pink-600 rounded-full blur-[100px] opacity-15 animate-pulse" style={{ animationDelay: '1s' }} />

      <div className="relative z-10 max-w-[1600px] mx-auto p-8 space-y-8">

        {/* HEADER */}
        <div className="flex justify-between items-start animate-slide-up opacity-0 stagger-1">
          <div className="space-y-2">
            <h1 className="text-5xl font-bold gradient-text tracking-tight">
              MICRO-CFO
            </h1>
            <p className="text-zinc-500 text-sm font-mono tracking-wider">
              FINANCIAL COMPLIANCE TERMINAL v1.0
            </p>
            <div className="flex items-center gap-4 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-glow" />
                <span className="text-xs font-mono text-zinc-500">
                  SYSTEM ONLINE
                </span>
              </div>
              <div className="h-4 w-px bg-zinc-700" />
              <div className="flex items-center gap-2">
                <Database className="w-3 h-3 text-zinc-500" />
                <span className="text-xs font-mono text-zinc-500">
                  {invoices.length} RECORDS
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Badge className="px-4 py-2 bg-violet-600 text-white border-none font-mono text-xs neon-border">
              <Activity className="w-3 h-3 mr-2" />
              LIVE MONITORING
            </Badge>
          </div>
        </div>

        {/* KPI CARDS */}
        <div className="grid gap-6 md:grid-cols-4">
          <Card className="glass border-zinc-800 animate-slide-up opacity-0 stagger-2 hover:neon-border transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-mono font-medium text-zinc-500 uppercase tracking-wider">
                Total Expenditure
              </CardTitle>
              <Wallet className="h-5 w-5 text-violet-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono gradient-text">
                ₹{totalSpent.toLocaleString('en-IN')}
              </div>
              <p className="text-xs text-zinc-500 mt-2 font-mono">
                {invoices.length} invoices processed
              </p>
            </CardContent>
          </Card>

          <Card className="glass border-zinc-800 animate-slide-up opacity-0 stagger-3 hover:neon-border transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-mono font-medium text-zinc-500 uppercase tracking-wider">
                ITC Eligible
              </CardTitle>
              <TrendingUp className="h-5 w-5 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono text-green-500">
                ₹{Math.round(itcEligible).toLocaleString('en-IN')}
              </div>
              <p className="text-xs text-zinc-500 mt-2 font-mono">
                {compliantCount} compliant bills
              </p>
            </CardContent>
          </Card>

          <Card className="glass border-zinc-800 animate-slide-up opacity-0 stagger-4 hover:neon-border transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-mono font-medium text-zinc-500 uppercase tracking-wider">
                Blocked Credits
              </CardTitle>
              <AlertTriangle className="h-5 w-5 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono text-red-500">
                {blockedCount}
              </div>
              <p className="text-xs text-zinc-500 mt-2 font-mono">
                Section 17(5) violations
              </p>
            </CardContent>
          </Card>

          <Card className="glass border-zinc-800 animate-slide-up opacity-0 stagger-5 hover:neon-border transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-mono font-medium text-zinc-500 uppercase tracking-wider">
                Compliance Rate
              </CardTitle>
              <Shield className="h-5 w-5 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono text-blue-500">
                {invoices.length > 0 ? Math.round((compliantCount / invoices.length) * 100) : 0}%
              </div>
              <p className="text-xs text-zinc-500 mt-2 font-mono">
                {reviewCount} pending review
              </p>
            </CardContent>
          </Card>
        </div>

        {/* MAIN CONTENT GRID */}
        <div className="grid gap-6 md:grid-cols-12">

          {/* RECENT INVOICES TABLE */}
          <Card className="md:col-span-7 glass border-zinc-800 animate-slide-up opacity-0 stagger-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="font-mono uppercase tracking-wider text-lg text-zinc-100">
                  <Zap className="inline w-5 h-5 mr-2 text-violet-500" />
                  Live Audit Stream
                </CardTitle>
                <Badge variant="outline" className="font-mono text-xs border-zinc-700 text-zinc-400">
                  REAL-TIME
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-zinc-800 hover:bg-transparent">
                    <TableHead className="font-mono text-xs text-zinc-500 uppercase">Vendor</TableHead>
                    <TableHead className="font-mono text-xs text-zinc-500 uppercase">Status</TableHead>
                    <TableHead className="text-right font-mono text-xs text-zinc-500 uppercase">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invoices.slice(0, 8).map((inv, idx) => (
                    <TableRow
                      key={inv._id}
                      className="border-zinc-800 hover:bg-zinc-900 transition-colors animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 0.05}s` }}
                    >
                      <TableCell className="font-medium">
                        <div className="font-mono text-sm text-zinc-100">{inv.vendor}</div>
                        <div className="text-xs text-zinc-500 font-mono mt-1">
                          {inv.category}
                        </div>
                      </TableCell>
                      <TableCell>
                        {inv.status === "blocked" ? (
                          <Badge className="text-xs font-mono bg-red-600 text-white border-none">
                            BLOCKED
                          </Badge>
                        ) : inv.status === "compliant" ? (
                          <Badge className="text-xs font-mono bg-green-600 text-white border-none">
                            COMPLIANT
                          </Badge>
                        ) : (
                          <Badge className="text-xs font-mono bg-yellow-600 text-black border-none">
                            REVIEW
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right font-mono font-semibold text-zinc-100">
                        ₹{inv.amount.toLocaleString('en-IN')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* CHARTS COLUMN */}
          <div className="md:col-span-5 space-y-6">

            {/* CATEGORY BREAKDOWN */}
            <Card className="glass border-zinc-800 animate-slide-up opacity-0 stagger-3">
              <CardHeader>
                <CardTitle className="font-mono uppercase tracking-wider text-sm text-zinc-100">
                  Expenditure Distribution
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                      strokeWidth={2}
                      stroke="#18181b"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number | undefined) => value ? `₹${value.toLocaleString('en-IN')}` : '₹0'}
                      contentStyle={{
                        backgroundColor: '#18181b',
                        border: '1px solid #3f3f46',
                        borderRadius: '8px',
                        fontFamily: 'JetBrains Mono',
                        fontSize: '12px',
                        color: '#fafafa'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  {categoryData.slice(0, 4).map((cat, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-sm"
                        style={{ backgroundColor: COLORS[i] }}
                      />
                      <span className="text-xs font-mono text-zinc-500 truncate">
                        {cat.name}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* STATUS BREAKDOWN */}
            <Card className="glass border-zinc-800 animate-slide-up opacity-0 stagger-4">
              <CardHeader>
                <CardTitle className="font-mono uppercase tracking-wider text-sm text-zinc-100">
                  Compliance Status
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statusData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                    <XAxis
                      dataKey="name"
                      stroke="#71717a"
                      style={{ fontFamily: 'JetBrains Mono', fontSize: '11px' }}
                    />
                    <YAxis
                      stroke="#71717a"
                      style={{ fontFamily: 'JetBrains Mono', fontSize: '11px' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#18181b',
                        border: '1px solid #3f3f46',
                        borderRadius: '8px',
                        fontFamily: 'JetBrains Mono',
                        fontSize: '12px',
                        color: '#fafafa'
                      }}
                    />
                    <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* FOOTER INFO */}
        <div className="flex items-center justify-between text-xs font-mono text-zinc-500 animate-fade-in opacity-0 stagger-5">
          <div>
            Powered by RAG Compliance Engine • Gemini AI • Convex Database
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Last updated: {currentTime || "Loading..."}
          </div>
        </div>
      </div>
    </div>
  );
}

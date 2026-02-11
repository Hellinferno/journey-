"use client";

import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Wallet, AlertTriangle, CheckCircle, Download } from "lucide-react";
import { CSVLink } from "react-csv";

export default function Dashboard() {
  const invoices = useQuery(api.invoices.get) || [];

  // --- 1. PREPARE CSV DATA FOR CA ---
  const csvHeaders = [
    { label: "Date", key: "date" },
    { label: "Vendor Name", key: "vendor" },
    { label: "GSTIN", key: "gstin" },
    { label: "Category", key: "category" },
    { label: "Total Amount", key: "amount" },
    { label: "Status", key: "status" },
    { label: "Audit Notes", key: "flags" }
  ];

  const csvData = invoices.map(inv => ({
    date: inv.date || "N/A",
    vendor: inv.vendor,
    gstin: inv.gstin || "N/A",
    category: inv.category || "General",
    amount: inv.amount,
    status: inv.status,
    flags: inv.compliance_flags ? inv.compliance_flags.join("; ") : ""
  }));

  // --- KPI CALCULATIONS ---
  const totalSpent = invoices.reduce((sum, inv) => sum + inv.amount, 0);
  const blockedCount = invoices.filter(i => i.status === "blocked").length;
  const compliantCount = invoices.filter(i => i.status === "compliant").length;

  // Chart Data
  const categoryData = invoices.reduce((acc: any[], curr) => {
    const existing = acc.find((item: any) => item.name === curr.category);
    if (existing) { 
      existing.value += curr.amount; 
    } else { 
      acc.push({ name: curr.category || "Uncategorized", value: curr.amount }); 
    }
    return acc;
  }, []);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div className="min-h-screen bg-zinc-50/50 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* HEADER */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-zinc-900">Micro-CFO</h1>
            <p className="text-zinc-500">Financial Audit & Compliance Overview</p>
          </div>
          <div className="flex gap-3">
            {/* THE NEW EXPORT BUTTON */}
            <CSVLink 
              data={csvData} 
              headers={csvHeaders} 
              filename={`MicroCFO_Report_${new Date().toISOString().split('T')[0]}.csv`}
            >
              <Button variant="outline" className="gap-2">
                <Download className="h-4 w-4" />
                Download Report
              </Button>
            </CSVLink>
            <Badge variant="outline" className="px-3 py-2 bg-green-50 text-green-700 border-green-200 h-10">
              ● System Live
            </Badge>
          </div>
        </div>

        {/* KPI CARDS */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Spend</CardTitle>
              <Wallet className="h-4 w-4 text-zinc-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₹{totalSpent.toLocaleString('en-IN')}</div>
              <p className="text-xs text-muted-foreground mt-1">Across {invoices.length} invoices</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Blocked Credits</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{blockedCount}</div>
              <p className="text-xs text-muted-foreground mt-1">Flagged under Sec 17(5)</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Compliant Bills</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{compliantCount}</div>
              <p className="text-xs text-muted-foreground mt-1">Ready for GST Filing</p>
            </CardContent>
          </Card>
        </div>

        {/* MAIN CONTENT GRID */}
        <div className="grid gap-4 md:grid-cols-7">
          {/* RECENT INVOICES TABLE */}
          <Card className="md:col-span-4">
            <CardHeader>
              <CardTitle>Recent Audit Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Vendor</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invoices.slice(0, 5).map((inv) => (
                    <TableRow key={inv._id}>
                      <TableCell className="font-medium">
                        {inv.vendor}
                        <div className="text-xs text-zinc-500">{inv.category}</div>
                      </TableCell>
                      <TableCell>
                        {inv.status === "blocked" ? (
                          <Badge variant="destructive" className="text-xs">Blocked</Badge>
                        ) : inv.status === "compliant" ? (
                          <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-none text-xs">OK</Badge>
                        ) : (
                          <Badge variant="outline" className="text-yellow-600 bg-yellow-50 border-yellow-200 text-xs">Review</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">₹{inv.amount.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* SPENDING CHART */}
          <Card className="md:col-span-3">
            <CardHeader>
              <CardTitle>Spending by Category</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {categoryData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `₹${value || 0}`} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 text-xs text-zinc-500 mt-4">
                {categoryData.slice(0,3).map((cat: any, i: number) => (
                  <div key={i} className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full" style={{backgroundColor: COLORS[i]}} />
                    {cat.name}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

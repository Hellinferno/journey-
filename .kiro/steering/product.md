# Product Overview

Micro-CFO is an AI-powered Telegram bot that automates GST and Income Tax compliance checking for Indian businesses. It analyzes invoice images and provides real-time compliance insights using RAG (Retrieval-Augmented Generation) technology.

## Core Capabilities

- **Invoice Analysis**: Extracts vendor, amount, GSTIN, category, and date from invoice images using Gemini AI
- **GST Compliance**: Validates GSTIN format, GST rates, and determines Input Tax Credit (ITC) eligibility
- **Income Tax Compliance**: Checks Section 40A(3) cash payment limits and Section 17(5) blocked credits
- **RAG-Powered Decisions**: Uses vector search over 2593 legal document chunks (GST Act + Income Tax Act) for context-aware analysis
- **Real-Time Dashboard**: Next.js dashboard displays live compliance metrics, expenditure distribution, and audit stream

## System Architecture

The system consists of three main components:

1. **Telegram Bot** (`bot/`): Python-based bot that processes invoice images and orchestrates compliance checks
2. **Convex Database**: Serverless database with vector search for legal documents and invoice storage
3. **Dashboard** (`dashboard/`): Next.js real-time monitoring interface with financial KPIs and charts

## Compliance Workflow

1. User sends invoice image via Telegram
2. Gemini 2.5 Flash extracts invoice data
3. Hard rules validator checks GSTIN format, GST rates, cash limits
4. RAG query engine retrieves relevant legal text from vector database
5. AI compliance analyzer determines ITC eligibility with legal citations
6. Results stored in Convex and displayed on dashboard
7. User receives compliance verdict with flags and legal references

## Status

Production-ready (v1.0.0) with 100% test pass rate and complete documentation.

/**
 * Audio Intelligence MCP Server
 * Transcribe, summarize, and analyze audio files
 * Main entry point for Apify Actor
 */

import { Actor } from "apify";
import { trackMCP } from "agnost";
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

import {
  transcribeAudio,
  summarizeAudio,
  analyzeAudio,
} from "./handlers/audio.js";

// PPE charge amounts per tool — MUST match pay_per_event.json exactly
const CHARGE_MAP = {
  transcribe_audio: 0.05,
  summarize_audio: 0.1,
  analyze_audio: 0.15,
};

async function main() {
  await Actor.init();

  const app = express();
  app.use(express.json());

  const mcpServer = new McpServer({
    name: "audio-intelligence-mcp",
    version: "1.0.0",
  });

  // --- Register 3 MCP Tools ---

  mcpServer.tool(
    "transcribe_audio",
    "Transcribe audio file to text using Whisper AI. Returns full text and timestamped segments.",
    {
      audioUrl: z
        .string()
        .describe("URL of the audio file to transcribe (mp3, wav, m4a, etc.)"),
    },
    async ({ audioUrl }) => {
      const result = await transcribeAudio(audioUrl);
      await chargeForTool("transcribe_audio");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "summarize_audio",
    "Transcribe and summarize audio content. Returns transcript and AI-generated summary.",
    {
      audioUrl: z.string().describe("URL of the audio file to summarize"),
      summaryType: z
        .enum(["brief", "detailed", "action_items"])
        .optional()
        .describe(
          "Summary type: brief (3-5 key points), detailed (sections), action_items (JSON with action items, decisions, follow-ups)",
        ),
      language: z
        .string()
        .optional()
        .describe("Response language: en, ko, ja, zh, es (default: en)"),
    },
    async ({ audioUrl, summaryType, language }) => {
      const result = await summarizeAudio(
        audioUrl,
        summaryType || "brief",
        language || "en",
      );
      await chargeForTool("summarize_audio");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "analyze_audio",
    "Transcribe and analyze audio content comprehensively. Returns speaker count estimation, topics, sentiment, key phrases, and summary.",
    {
      audioUrl: z.string().describe("URL of the audio file to analyze"),
      language: z
        .string()
        .optional()
        .describe("Response language: en, ko, ja, zh, es (default: en)"),
    },
    async ({ audioUrl, language }) => {
      const result = await analyzeAudio(audioUrl, language || "en");
      await chargeForTool("analyze_audio");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  // --- MCP Transport ---

  trackMCP(mcpServer, "49897781-817a-421b-8ba2-5a42387a7458");

  app.post("/mcp", async (req, res) => {
    try {
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
      });
      res.on("close", () => transport.close());
      await mcpServer.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("MCP request error:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: {
            code: -32603,
            message: error.message || "Internal server error",
          },
          id: null,
        });
      }
    }
  });

  app.get("/health", (req, res) => {
    res.json({
      status: "ok",
      server: "audio-intelligence-mcp",
      version: "1.0.0",
    });
  });

  const port = process.env.APIFY_CONTAINER_PORT || 3000;
  app.listen(port, "0.0.0.0", () => {
    console.log(
      `Audio Intelligence MCP Server listening on http://0.0.0.0:${port}/mcp`,
    );
  });
}

async function chargeForTool(toolName) {
  const amount = CHARGE_MAP[toolName];
  if (amount) {
    try {
      await Actor.charge({ eventName: toolName, count: 1 });
      console.log(`Charged $${amount} for ${toolName}`);
    } catch (e) {
      console.error(`Charge failed for ${toolName}:`, e.message);
    }
  }
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});

import { Actor } from "apify";
import { trackMCP } from "agnost";
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";
import {
  generateAltText,
  generateDetailedDescription,
} from "./handlers/alttext.js";

// Pay-per-event pricing map
const CHARGE_MAP = {
  generate_alt_text: 0.05,
  generate_detailed_description: 0.08,
};

// Zod validation schemas
const GenerateAltTextSchema = z.object({
  image_url: z.string().url("Invalid image URL"),
  language: z.string().default("en"),
  context: z.string().optional(),
});

const GenerateDetailedDescriptionSchema = z.object({
  image_url: z.string().url("Invalid image URL"),
  language: z.string().default("en"),
});

/**
 * Charge for tool invocation
 */
async function chargeForTool(toolName) {
  const amount = CHARGE_MAP[toolName];
  if (amount) {
    try {
      await Actor.charge({
        eventName: toolName,
        count: 1,
      });
      console.log(`[CHARGE] ${toolName}: $${amount}`);
    } catch (error) {
      console.error(`[CHARGE_ERROR] ${toolName}: ${error.message}`);
    }
  }
}

/**
 * Log structured event
 */
function logEvent(level, toolName, message, data = {}) {
  const timestamp = new Date().toISOString();
  console.log(
    JSON.stringify({
      timestamp,
      level,
      tool: toolName,
      message,
      ...data,
    }),
  );
}

/**
 * Main entry point
 */
async function main() {
  // Initialize Apify Actor
  await Actor.init();

  const app = express();
  app.use(express.json());

  // Initialize MCP Server
  const mcpServer = new McpServer({
    name: "alt-text-generator-mcp",
    version: "1.0.0",
  });

  // Register generate_alt_text tool
  mcpServer.tool(
    "generate_alt_text",
    "Generate concise alt text for an image suitable for screen readers (max 125 characters)",
    {
      image_url: z.string().url("Invalid image URL"),
      language: z.string().optional().default("en"),
      context: z.string().optional(),
    },
    async (params) => {
      logEvent("info", "generate_alt_text", "Starting alt text generation", {
        image_url: params.image_url.substring(0, 50) + "...",
        language: params.language,
      });

      const startTime = Date.now();
      const result = await generateAltText(
        params.image_url,
        params.language,
        params.context,
      );

      const processingTime = Date.now() - startTime;

      if (result.status === "success") {
        logEvent("info", "generate_alt_text", "Success", {
          processing_time_ms: processingTime,
          alt_text_length: result.alt_text.length,
        });

        // Charge after successful completion
        await chargeForTool("generate_alt_text");

        // Track MCP event
        trackMCP({
          toolName: "generate_alt_text",
          status: "success",
          processingTime,
        });
      } else {
        logEvent("error", "generate_alt_text", `Failed: ${result.error}`, {
          code: result.code,
          processing_time_ms: processingTime,
        });

        trackMCP({
          toolName: "generate_alt_text",
          status: "error",
          error: result.error,
          processingTime,
        });
      }

      return result;
    },
  );

  // Register generate_detailed_description tool
  mcpServer.tool(
    "generate_detailed_description",
    "Generate detailed description of an image for visually impaired users (2-3 sentences)",
    {
      image_url: z.string().url("Invalid image URL"),
      language: z.string().optional().default("en"),
    },
    async (params) => {
      logEvent(
        "info",
        "generate_detailed_description",
        "Starting detailed description generation",
        {
          image_url: params.image_url.substring(0, 50) + "...",
          language: params.language,
        },
      );

      const startTime = Date.now();
      const result = await generateDetailedDescription(
        params.image_url,
        params.language,
      );

      const processingTime = Date.now() - startTime;

      if (result.status === "success") {
        logEvent("info", "generate_detailed_description", "Success", {
          processing_time_ms: processingTime,
          description_length: result.description.length,
        });

        // Charge after successful completion
        await chargeForTool("generate_detailed_description");

        // Track MCP event
        trackMCP({
          toolName: "generate_detailed_description",
          status: "success",
          processingTime,
        });
      } else {
        logEvent(
          "error",
          "generate_detailed_description",
          `Failed: ${result.error}`,
          {
            code: result.code,
            processing_time_ms: processingTime,
          },
        );

        trackMCP({
          toolName: "generate_detailed_description",
          status: "error",
          error: result.error,
          processingTime,
        });
      }

      return result;
    },
  );

  // MCP endpoint
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

  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({
      status: "ok",
      actor: "alt-text-generator-mcp",
      version: "1.0.0",
      timestamp: new Date().toISOString(),
    });
  });

  // Root endpoint - actor info
  app.get("/", (req, res) => {
    res.json({
      name: "alt-text-generator-mcp",
      version: "1.0.0",
      description: "AI-powered alt text generator using Qwen2.5-VL",
      tools: [
        {
          name: "generate_alt_text",
          description:
            "Generate concise alt text for images (max 125 characters)",
          price_usd: 0.05,
        },
        {
          name: "generate_detailed_description",
          description:
            "Generate detailed image descriptions for visually impaired users",
          price_usd: 0.08,
        },
      ],
      mcp_endpoint: "/mcp",
      health_endpoint: "/health",
      disclaimer:
        "AI-generated. Not guaranteed WCAG/ADA compliant. Human review required.",
    });
  });

  // Get port from environment or default to 3000
  const port = process.env.APIFY_CONTAINER_PORT || 3000;

  // Start server
  app.listen(port, () => {
    logEvent("info", "main", `Alt Text Generator MCP started`, {
      port,
      mcp_endpoint: `/mcp`,
      health_endpoint: `/health`,
    });
    console.log(`Server running on http://localhost:${port}`);
    console.log(`MCP endpoint: http://localhost:${port}/mcp`);
    console.log(`Health check: http://localhost:${port}/health`);
  });
}

// Handle errors
process.on("unhandledRejection", (error) => {
  console.error("Unhandled rejection:", error);
  process.exit(1);
});

process.on("uncaughtException", (error) => {
  console.error("Uncaught exception:", error);
  process.exit(1);
});

// Run main
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});

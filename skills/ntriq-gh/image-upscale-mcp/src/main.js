/**
 * Image Upscale MCP Server
 * AI-powered image upscaling with optional face enhancement
 * Uses Real-ESRGAN via ai.ntriq.co.kr
 */

import { Actor } from "apify";
import { trackMCP } from "agnost";
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

import { upscaleImage, enhanceFace } from "./handlers/upscale.js";

// PPE charge amounts per tool — MUST match pay_per_event.json exactly
const CHARGE_MAP = {
  upscale_image: 0.18,
  enhance_face: 0.22,
};

async function main() {
  await Actor.init();

  const app = express();
  app.use(express.json());

  const mcpServer = new McpServer({
    name: "image-upscale-mcp",
    version: "1.0.0",
  });

  // --- Register 2 MCP Tools ---

  mcpServer.tool(
    "upscale_image",
    "Upscale an image by 2x or 4x using Real-ESRGAN AI super resolution.",
    {
      image_url: z.string().describe("URL of the image to upscale"),
      scale: z
        .number()
        .optional()
        .describe("Upscaling factor: 2 or 4 (default: 4)"),
    },
    async ({ image_url, scale }) => {
      try {
        const result = await upscaleImage(image_url, scale || 4);
        await chargeForTool("upscale_image");
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { status: "error", error: error.message },
                null,
                2,
              ),
            },
          ],
        };
      }
    },
  );

  mcpServer.tool(
    "enhance_face",
    "Upscale an image with face enhancement. Best for portraits and photos with people.",
    {
      image_url: z.string().describe("URL of the image to upscale"),
      scale: z
        .number()
        .optional()
        .describe("Upscaling factor: 2 or 4 (default: 4)"),
    },
    async ({ image_url, scale }) => {
      try {
        const result = await enhanceFace(image_url, scale || 4);
        await chargeForTool("enhance_face");
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { status: "error", error: error.message },
                null,
                2,
              ),
            },
          ],
        };
      }
    },
  );

  // --- MCP Transport ---

  trackMCP(mcpServer, "image-upscale-mcp-uuid");

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
      server: "image-upscale-mcp",
      version: "1.0.0",
    });
  });

  const port = process.env.APIFY_CONTAINER_PORT || 3000;
  app.listen(port, "0.0.0.0", () => {
    console.log(
      `Image Upscale MCP Server listening on http://0.0.0.0:${port}/mcp`,
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

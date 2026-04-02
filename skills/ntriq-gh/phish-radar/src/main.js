/**
 * Phish Radar MCP Server
 * Phishing detection and brand monitoring for URLs and domains
 */

import { Actor } from 'apify';
import { phishingDetect } from './handlers/phishing_detect.js';
import { domainTrust } from './handlers/domain_trust.js';
import { brandMonitor } from './handlers/brand_monitor.js';

// MCP Tool Definitions
const TOOLS = [
  {
    name: 'phishing_detect',
    description: 'Detect phishing URLs/domains with typosquatting analysis, domain age, SSL certificate type, and DNS records',
    inputSchema: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'Full URL to analyze (e.g., https://paypa1-secure.com/login)',
        },
        domain: {
          type: 'string',
          description: 'Domain name to analyze (e.g., paypa1-secure.com). Use if URL not available.',
        },
      },
      oneOf: [
        { required: ['url'] },
        { required: ['domain'] },
      ],
    },
  },
  {
    name: 'domain_trust',
    description: 'Calculate domain trust score (0-100) based on DNS records, domain age, SSL type, email infrastructure (MX/SPF/DKIM/DMARC)',
    inputSchema: {
      type: 'object',
      properties: {
        domain: {
          type: 'string',
          description: 'Domain name to analyze (e.g., example.com)',
        },
      },
      required: ['domain'],
    },
  },
  {
    name: 'brand_monitor',
    description: 'Find lookalike domains for a brand (typosquats, homoglyphs, keyword additions)',
    inputSchema: {
      type: 'object',
      properties: {
        brand_domain: {
          type: 'string',
          description: 'Brand domain to monitor (e.g., stripe.com, paypal.com)',
        },
        limit: {
          type: 'number',
          description: 'Max lookalikes to return (default: 20)',
        },
      },
      required: ['brand_domain'],
    },
  },
];

/**
 * Route incoming tool requests to appropriate handler
 */
async function processTool(toolName, input) {
  switch (toolName) {
    case 'phishing_detect':
      return await phishingDetect(input.url || input.domain);

    case 'domain_trust':
      return await domainTrust(input.domain);

    case 'brand_monitor':
      return await brandMonitor(input.brand_domain, input.limit || 20);

    default:
      throw new Error(`Unknown tool: ${toolName}`);
  }
}

/**
 * Main Actor entry point
 */
async function main() {
  await Actor.init();

  const input = await Actor.getInput();

  try {
    // Handle MCP tool call input format
    if (input.toolName) {
      const toolName = input.toolName;
      const toolInput = input.input || {};

      console.log(`Executing tool: ${toolName}`, toolInput);

      const result = await processTool(toolName, toolInput);

      // Charge for successful tool execution
      try {
        await Actor.charge({
          eventName: 'tool-call',
        });
        console.log('Charged $0.05 for tool execution');
      } catch (chargeError) {
        console.error(`Charging failed (non-critical): ${chargeError.message}`);
      }

      // Return result
      await Actor.pushData(result);
    }
    // Handle info request (return available tools)
    else if (input.action === 'get_tools') {
      await Actor.pushData({
        tools: TOOLS,
      });
    }
    // Default: describe available tools
    else {
      await Actor.pushData({
        message: 'Phish Radar MCP Server v1.0',
        available_tools: TOOLS.length,
        tools: TOOLS,
      });
    }
  } catch (error) {
    console.error('Actor error:', error);
    await Actor.pushData({
      error: error.message,
      tool: input.toolName || 'unknown',
    });
  }

  await Actor.exit();
}

// Run main
main().catch(console.error);

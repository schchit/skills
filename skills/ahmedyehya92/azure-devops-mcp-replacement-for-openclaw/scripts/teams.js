#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: AZURE_DEVOPS_ORG, AZURE_DEVOPS_PAT (only)
//   External endpoints called: https://dev.azure.com/ (only)
//   Local files read: none
//   Local files written: none
//
// Usage:
//   node teams.js list <project>
//   node teams.js iterations <project> <team>

"use strict";

const { request, projectUrl, validateSegment, output } = require("./client.js");

const [, , cmd, project, team] = process.argv;

async function main() {
  if (!project) { console.error("Usage: node teams.js <cmd> <project> [team]"); process.exit(1); }

  switch (cmd) {
    case "list": {
      const data = await request(projectUrl(project, "_apis/teams"));
      const teams = (data.value || []).map((t) => ({
        id: t.id,
        name: t.name,
        description: t.description,
      }));
      output({ count: teams.length, teams });
      break;
    }
    case "iterations": {
      if (!team) { console.error("Usage: node teams.js iterations <project> <team>"); process.exit(1); }
      const t = validateSegment(team, "team");
      const p = validateSegment(project, "project");
      const url = `https://dev.azure.com/${encodeURIComponent(require("./client.js").ORG)}/${encodeURIComponent(p)}/${encodeURIComponent(t)}/_apis/work/teamsettings/iterations?api-version=7.1`;
      const data = await request(url);
      const iterations = (data.value || []).map((i) => ({
        id: i.id,
        name: i.name,
        path: i.path,
        startDate: i.attributes?.startDate,
        finishDate: i.attributes?.finishDate,
        timeFrame: i.attributes?.timeFrame,
      }));
      output({ count: iterations.length, iterations });
      break;
    }
    default:
      console.error("Commands: list <project> | iterations <project> <team>");
      process.exit(1);
  }
}

main().catch((err) => { console.error("❌", err.message); process.exit(1); });

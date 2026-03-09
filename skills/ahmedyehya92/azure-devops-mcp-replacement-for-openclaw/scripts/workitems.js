#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: AZURE_DEVOPS_ORG, AZURE_DEVOPS_PAT (only)
//   External endpoints called: https://dev.azure.com/ (only)
//   Local files read: none
//   Local files written: none
//
// Usage:
//   node workitems.js list <project>
//   node workitems.js get <id>
//   node workitems.js current-sprint <project> <team>
//   node workitems.js create <project> <type> <title>
//   node workitems.js update <id> <field> <value>
//   node workitems.js query <project> "<WIQL>"

"use strict";

const { request, orgUrl, projectUrl, validateSegment, output, ORG } = require("./client.js");

const [, , cmd, ...args] = process.argv;

function formatWI(wi) {
  const f = wi.fields || {};
  return {
    id: wi.id,
    type: f["System.WorkItemType"],
    title: f["System.Title"],
    state: f["System.State"],
    assignedTo: f["System.AssignedTo"]?.displayName,
    priority: f["Microsoft.VSTS.Common.Priority"],
    iterationPath: f["System.IterationPath"],
    areaPath: f["System.AreaPath"],
    createdDate: f["System.CreatedDate"],
    changedDate: f["System.ChangedDate"],
    url: wi.url,
  };
}

async function fetchWorkItems(ids) {
  if (!ids || ids.length === 0) return [];
  // Batch fetch — ADO allows up to 200 per call
  const idList = ids.slice(0, 200).join(",");
  const fields = [
    "System.Id", "System.Title", "System.WorkItemType", "System.State",
    "System.AssignedTo", "System.IterationPath", "System.AreaPath",
    "System.CreatedDate", "System.ChangedDate",
    "Microsoft.VSTS.Common.Priority",
  ].join(",");
  const url = orgUrl(`_apis/wit/workitems?ids=${idList}&fields=${fields}`);
  const data = await request(url);
  return (data.value || []).map(formatWI);
}

async function main() {
  switch (cmd) {
    case "list": {
      const [project] = args;
      if (!project) { console.error("Usage: node workitems.js list <project>"); process.exit(1); }
      const p = validateSegment(project, "project");
      // Use WIQL to get all items in project
      const wiql = `SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = '${project.replace(/'/g, "''")}' ORDER BY [System.ChangedDate] DESC`;
      const queryUrl = `https://dev.azure.com/${encodeURIComponent(ORG)}/${encodeURIComponent(p)}/_apis/wit/wiql?api-version=7.1&$top=50`;
      const result = await request(queryUrl, "POST", { query: wiql });
      const ids = (result.workItems || []).map((w) => w.id);
      const items = await fetchWorkItems(ids);
      output({ count: items.length, workItems: items });
      break;
    }
    case "get": {
      const [id] = args;
      if (!id || isNaN(Number(id))) { console.error("Usage: node workitems.js get <numeric-id>"); process.exit(1); }
      const url = orgUrl(`_apis/wit/workitems/${Number(id)}`);
      const wi = await request(url);
      output(formatWI(wi));
      break;
    }
    case "current-sprint": {
      const [project, team] = args;
      if (!project || !team) { console.error("Usage: node workitems.js current-sprint <project> <team>"); process.exit(1); }
      const p = validateSegment(project, "project");
      const t = validateSegment(team, "team");
      // Get current iteration
      const iterUrl = `https://dev.azure.com/${encodeURIComponent(ORG)}/${encodeURIComponent(p)}/${encodeURIComponent(t)}/_apis/work/teamsettings/iterations?$timeframe=current&api-version=7.1`;
      const iterData = await request(iterUrl);
      const iter = (iterData.value || [])[0];
      if (!iter) { console.log(JSON.stringify({ message: "No current sprint found" })); break; }
      // Get work items in that iteration
      const wiUrl = `https://dev.azure.com/${encodeURIComponent(ORG)}/${encodeURIComponent(p)}/${encodeURIComponent(t)}/_apis/work/teamsettings/iterations/${iter.id}/workitems?api-version=7.1`;
      const wiData = await request(wiUrl);
      const ids = (wiData.workItemRelations || []).map((r) => r.target?.id).filter(Boolean);
      const items = await fetchWorkItems(ids);
      output({ iteration: { id: iter.id, name: iter.name, startDate: iter.attributes?.startDate, finishDate: iter.attributes?.finishDate }, count: items.length, workItems: items });
      break;
    }
    case "create": {
      const [project, type, ...titleParts] = args;
      const title = titleParts.join(" ");
      if (!project || !type || !title) { console.error("Usage: node workitems.js create <project> <type> <title>"); process.exit(1); }
      const p = validateSegment(project, "project");
      const safeType = validateSegment(type, "work item type");
      const url = `https://dev.azure.com/${encodeURIComponent(ORG)}/${encodeURIComponent(p)}/_apis/wit/workitems/$${safeType}?api-version=7.1`;
      const body = [{ op: "add", path: "/fields/System.Title", value: title }];
      const wi = await request(url, "POST", body);
      output(formatWI(wi));
      break;
    }
    case "update": {
      const [id, field, ...valueParts] = args;
      const value = valueParts.join(" ");
      if (!id || isNaN(Number(id)) || !field || !value) {
        console.error("Usage: node workitems.js update <id> <field> <value>\n  Fields: System.State, System.AssignedTo, Microsoft.VSTS.Common.Priority, System.Title, etc.");
        process.exit(1);
      }
      const url = orgUrl(`_apis/wit/workitems/${Number(id)}`);
      const body = [{ op: "add", path: `/fields/${field}`, value }];
      const wi = await request(url, "PATCH", body);
      output(formatWI(wi));
      break;
    }
    case "query": {
      const [project, ...queryParts] = args;
      const wiql = queryParts.join(" ");
      if (!project || !wiql) { console.error('Usage: node workitems.js query <project> "<WIQL>"'); process.exit(1); }
      const p = validateSegment(project, "project");
      const url = `https://dev.azure.com/${encodeURIComponent(ORG)}/${encodeURIComponent(p)}/_apis/wit/wiql?api-version=7.1`;
      const result = await request(url, "POST", { query: wiql });
      const ids = (result.workItems || []).map((w) => w.id);
      const items = await fetchWorkItems(ids);
      output({ count: items.length, workItems: items });
      break;
    }
    default:
      console.error("Commands: list | get | current-sprint | create | update | query");
      process.exit(1);
  }
}

main().catch((err) => { console.error("❌", err.message); process.exit(1); });

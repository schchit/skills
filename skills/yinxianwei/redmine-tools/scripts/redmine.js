#!/usr/bin/env node

/**
 * Fetch a Redmine issue with attachments and journals included.
 *
 * @param {number|string} issueId - Redmine issue ID.
 * @param {object} options - Request options.
 * @param {string} options.baseUrl - Redmine base URL, for example: https://redmine.example.com
 * @param {string} [options.apiKey] - Redmine API key.
 * @param {string} [options.include] - Extra include fields. Defaults to attachments,journals.
 * @returns {Promise<object>} Resolved issue payload from Redmine.
 */
async function getRedmineIssueDetails(issueId, options = {}) {
    const { baseUrl, apiKey, include = "attachments,journals" } = options;

    if (!baseUrl) {
        throw new Error("Missing required option: baseUrl");
    }

    if (!issueId) {
        throw new Error("Missing required argument: issueId");
    }

    const normalizedBaseUrl = baseUrl.replace(/\/$/, "");
    const url = new URL(`${normalizedBaseUrl}/issues/${encodeURIComponent(String(issueId))}.json`);
    url.searchParams.set("include", include);

    const headers = {
        "Content-Type": "application/json",
    };

    if (apiKey) {
        headers["X-Redmine-API-Key"] = apiKey;
    }

    const response = await fetch(url, { headers });
    if (!response.ok) {
        const responseText = await response.text();
        throw new Error(
            `Failed to fetch issue ${issueId}. HTTP ${response.status}: ${responseText || response.statusText}`
        );
    }

    const data = await response.json();
    return data.issue;
}

/**
 * Update a Redmine issue status and notes.
 *
 * @param {number|string} issueId - Redmine issue ID.
 * @param {object} payload - Update payload.
 * @param {number|string} [payload.statusId] - New Redmine status ID.
 * @param {string} [payload.notes] - Update notes.
 * @param {object} options - Request options.
 * @param {string} options.baseUrl - Redmine base URL.
 * @param {string} [options.apiKey] - Redmine API key.
 * @returns {Promise<void>} Resolves when update succeeds.
 */
async function updateRedmineIssue(issueId, payload, options = {}) {
    const { statusId, notes } = payload;
    const { baseUrl, apiKey } = options;

    if (!baseUrl) {
        throw new Error("Missing required option: baseUrl");
    }

    if (!issueId) {
        throw new Error("Missing required argument: issueId");
    }

    const hasStatusId = statusId !== undefined && statusId !== null && String(statusId).trim() !== "";
    const hasNotes = typeof notes === "string" && notes.trim() !== "";
    if (!hasStatusId && !hasNotes) {
        throw new Error("At least one of statusId or notes is required");
    }

    const normalizedBaseUrl = baseUrl.replace(/\/$/, "");
    const url = new URL(`${normalizedBaseUrl}/issues/${encodeURIComponent(String(issueId))}.json`);

    const headers = {
        "Content-Type": "application/json",
    };

    if (apiKey) {
        headers["X-Redmine-API-Key"] = apiKey;
    }

    const issuePayload = {};
    if (hasStatusId) {
        issuePayload.status_id = statusId;
    }

    if (hasNotes) {
        issuePayload.notes = notes;
    }

    const response = await fetch(url, {
        method: "PUT",
        headers,
        body: JSON.stringify({
            issue: issuePayload,
        }),
    });

    if (!response.ok) {
        const responseText = await response.text();
        throw new Error(
            `Failed to update issue ${issueId}. HTTP ${response.status}: ${responseText || response.statusText}`
        );
    }
}

function isSupportedImageAttachment(attachment) {
    if (!attachment || typeof attachment !== "object") {
        return false;
    }

    const contentType = String(attachment.content_type || "").toLowerCase();
    if (["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"].includes(contentType)) {
        return true;
    }

    const filename = String(attachment.filename || "").toLowerCase();
    return /\.(png|jpe?g|webp|gif)$/i.test(filename);
}

async function downloadRedmineAttachmentAsDataUrl(attachment, options = {}) {
    const { apiKey } = options;
    const contentUrl = attachment?.content_url;

    if (!contentUrl) {
        throw new Error(`Attachment ${attachment?.id || "unknown"} is missing content_url`);
    }

    const headers = {};
    if (apiKey) {
        headers["X-Redmine-API-Key"] = apiKey;
    }

    const response = await fetch(contentUrl, { headers });
    if (!response.ok) {
        const responseText = await response.text();
        throw new Error(
            `Failed to download attachment ${attachment.id}. HTTP ${response.status}: ${responseText || response.statusText}`
        );
    }

    const contentType = response.headers.get("content-type") || attachment.content_type || "application/octet-stream";
    const arrayBuffer = await response.arrayBuffer();
    const base64 = Buffer.from(arrayBuffer).toString("base64");

    return `data:${contentType};base64,${base64}`;
}

function resolveOpenAiChatCompletionsUrl(rawUrl) {
    const normalizedUrl = String(rawUrl || "").trim().replace(/\/$/, "");
    if (!normalizedUrl) {
        throw new Error("Missing required environment variable: OPENAI_API_URL");
    }

    if (/\/chat\/completions$/i.test(normalizedUrl)) {
        return normalizedUrl;
    }

    return `${normalizedUrl}/chat/completions`;
}

async function summarizeImageWithOpenAi(image, context, options = {}) {
    const { apiUrl, apiKey, model, prompt } = options;

    if (!apiUrl) {
        throw new Error("Missing required option: apiUrl");
    }

    if (!apiKey) {
        throw new Error("Missing required option: apiKey");
    }

    if (!model) {
        throw new Error("Missing required option: model");
    }

    if (!prompt) {
        throw new Error("Missing required option: prompt");
    }

    const response = await fetch(resolveOpenAiChatCompletionsUrl(apiUrl), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
            model,
            messages: [
                {
                    role: "user",
                    content: [
                        {
                            type: "text",
                            text: [
                                prompt,
                                `Issue ID: ${context.issueId}`,
                                `Issue Subject: ${context.issueSubject || ""}`,
                                `Attachment Filename: ${image.filename}`,
                                `Attachment Description: ${image.description || ""}`,
                            ].join("\n"),
                        },
                        {
                            type: "image_url",
                            image_url: {
                                url: image.dataUrl,
                            },
                        },
                    ],
                },
            ],
        }),
    });

    if (!response.ok) {
        const responseText = await response.text();
        throw new Error(
            `Failed to summarize image ${image.filename}. HTTP ${response.status}: ${responseText || response.statusText}`
        );
    }

    const data = await response.json();
    const content = data?.choices?.[0]?.message?.content;
    if (typeof content === "string") {
        return content.trim();
    }

    if (Array.isArray(content)) {
        return content
            .map((item) => {
                if (typeof item === "string") {
                    return item;
                }

                if (item && typeof item.text === "string") {
                    return item.text;
                }

                return "";
            })
            .join("\n")
            .trim();
    }

    return "";
}

async function summarizeRedmineIssueImages(issueId, options = {}) {
    const {
        baseUrl,
        apiKey,
        openAiApiUrl,
        openAiApiKey,
        openAiModel,
        openAiPrompt,
    } = options;

    const issue = await getRedmineIssueDetails(issueId, {
        baseUrl,
        apiKey,
        include: "attachments,journals",
    });

    const attachments = Array.isArray(issue.attachments) ? issue.attachments : [];
    const imageAttachments = attachments.filter(isSupportedImageAttachment);
    const skippedAttachments = attachments
        .filter((attachment) => !isSupportedImageAttachment(attachment))
        .map((attachment) => ({
            id: attachment.id,
            filename: attachment.filename,
            content_type: attachment.content_type || null,
            skipped_reason: "unsupported_or_non_image",
        }));

    const summaries = [];
    for (const attachment of imageAttachments) {
        const dataUrl = await downloadRedmineAttachmentAsDataUrl(attachment, { apiKey });
        const summary = await summarizeImageWithOpenAi(
            {
                ...attachment,
                dataUrl,
            },
            {
                issueId: String(issue.id || issueId),
                issueSubject: issue.subject || "",
            },
            {
                apiUrl: openAiApiUrl,
                apiKey: openAiApiKey,
                model: openAiModel,
                prompt: openAiPrompt,
            }
        );

        summaries.push({
            id: attachment.id,
            filename: attachment.filename,
            content_type: attachment.content_type || null,
            filesize: attachment.filesize || null,
            description: attachment.description || null,
            summary,
        });
    }

    return {
        issue_id: String(issue.id || issueId),
        subject: issue.subject || null,
        total_attachments: attachments.length,
        image_attachment_count: imageAttachments.length,
        skipped_attachments: skippedAttachments,
        images: summaries,
    };
}

function parseCliArgs(argv) {
    const [command, ...rest] = argv;
    const flags = {};

    for (let i = 0; i < rest.length; i += 1) {
        const token = rest[i];
        if (!token.startsWith("--")) {
            continue;
        }

        const [rawKey, inlineValue] = token.slice(2).split("=");
        const key = rawKey;
        if (!key) {
            continue;
        }

        if (inlineValue !== undefined) {
            flags[key] = inlineValue;
            continue;
        }

        const next = rest[i + 1];
        if (next && !next.startsWith("--")) {
            flags[key] = next;
            i += 1;
        } else {
            flags[key] = true;
        }
    }

    return { command, flags };
}

function printUsage() {
    console.log(`Usage:
    node redmine.js get --id <issueId> [--include <fields>]
    node redmine.js update --id <issueId> [--status_id <statusId>] [--notes <text>]
    node redmine.js image --id <issueId>

Environment Variables:
  REDMINE_BASE_URL   Redmine base URL
  REDMINE_API_KEY    Redmine API key
    OPENAI_API_URL     OpenAI-compatible API base URL or /chat/completions URL
    OPENAI_API_KEY     OpenAI-compatible API key
    OPENAI_MODEL       Model name for image summarization
    OPENAI_IMAGE_SUMMARY_PROMPT
                                         Prompt used to summarize each image attachment

Examples:
  node redmine.js get --id 123
    node redmine.js get --id 123 --include attachments,journals,watchers
    node redmine.js update --id 123 --status_id 3 --notes "Issue fixed and verified"
        node redmine.js update --id 123 --status_id 3
        node redmine.js update --id 123 --notes "Need more logs from QA"
    node redmine.js image --id 123`);
}

async function runCli() {
    const { command, flags } = parseCliArgs(process.argv.slice(2));

    if (!command || command === "help" || flags.help) {
        printUsage();
        process.exitCode = 0;
        return;
    }

    if (command !== "get" && command !== "update" && command !== "image") {
        console.error(`Unknown command: ${command}`);
        printUsage();
        process.exitCode = 1;
        return;
    }

    const baseUrl = process.env.REDMINE_BASE_URL;
    const apiKey = process.env.REDMINE_API_KEY;

    if (!baseUrl) {
        console.error("Missing required environment variable: REDMINE_BASE_URL");
        process.exitCode = 1;
        return;
    }

    if (!apiKey) {
        console.error("Missing required environment variable: REDMINE_API_KEY");
        process.exitCode = 1;
        return;
    }

    const issueId = flags.id;
    if (!issueId) {
        console.error("Missing required argument: --id");
        printUsage();
        process.exitCode = 1;
        return;
    }

    try {
        if (command === "get") {
            const include = typeof flags.include === "string" ? flags.include : "attachments,journals";
            const issue = await getRedmineIssueDetails(issueId, {
                baseUrl,
                apiKey,
                include,
            });
            console.log(JSON.stringify(issue, null, 2));
            return;
        }

        if (command === "image") {
            const openAiApiUrl = process.env.OPENAI_API_URL;
            const openAiApiKey = process.env.OPENAI_API_KEY;
            const openAiModel = process.env.OPENAI_MODEL;
            const openAiPrompt = process.env.OPENAI_IMAGE_SUMMARY_PROMPT;

            if (!openAiApiUrl) {
                console.error("Missing required environment variable: OPENAI_API_URL");
                process.exitCode = 1;
                return;
            }

            if (!openAiApiKey) {
                console.error("Missing required environment variable: OPENAI_API_KEY");
                process.exitCode = 1;
                return;
            }

            if (!openAiModel) {
                console.error("Missing required environment variable: OPENAI_MODEL");
                process.exitCode = 1;
                return;
            }

            if (!openAiPrompt) {
                console.error("Missing required environment variable: OPENAI_IMAGE_SUMMARY_PROMPT");
                process.exitCode = 1;
                return;
            }

            const result = await summarizeRedmineIssueImages(issueId, {
                baseUrl,
                apiKey,
                openAiApiUrl,
                openAiApiKey,
                openAiModel,
                openAiPrompt,
            });

            console.log(JSON.stringify(result, null, 2));
            return;
        }

        const statusId = flags.status_id;
        const notes = flags.notes;
        const hasStatusId = statusId !== undefined && statusId !== null && String(statusId).trim() !== "";
        const hasNotes = typeof notes === "string" && notes.trim() !== "";
        if (!hasStatusId && !hasNotes) {
            console.error("At least one of --status_id or --notes is required");
            printUsage();
            process.exitCode = 1;
            return;
        }

        await updateRedmineIssue(
            issueId,
            {
                statusId,
                notes,
            },
            {
                baseUrl,
                apiKey,
            }
        );

        console.log(
            JSON.stringify(
                {
                    success: true,
                    issue_id: String(issueId),
                    status_id: hasStatusId ? String(statusId) : null,
                    notes: hasNotes ? notes : null,
                },
                null,
                2
            )
        );
    } catch (error) {
        console.error(error.message);
        process.exitCode = 1;
    }
}

if (require.main === module) {
    runCli();
}

module.exports = {
    downloadRedmineAttachmentAsDataUrl,
    getRedmineIssueDetails,
    isSupportedImageAttachment,
    updateRedmineIssue,
    parseCliArgs,
    resolveOpenAiChatCompletionsUrl,
    runCli,
    summarizeImageWithOpenAi,
    summarizeRedmineIssueImages,
};

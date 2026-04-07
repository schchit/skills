/**
 * Alt text generation handler
 * Calls ai.ntriq.co.kr/analyze/image API
 */

const AI_ENDPOINT =
  process.env.AI_API_ENDPOINT || "https://ai.ntriq.co.kr/analyze/image";
const REQUEST_TIMEOUT = parseInt(process.env.AI_REQUEST_TIMEOUT || "30000", 10);

const DISCLAIMER =
  "AI-generated. Not guaranteed WCAG/ADA compliant. Human review required.";

/**
 * Call AI service to analyze image
 */
async function callAIService(imageUrl, prompt, language, maxTokens = 200) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const response = await fetch(AI_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image_url: imageUrl,
        prompt,
        language,
        max_tokens: maxTokens,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `AI service error: ${response.status} ${errorText || response.statusText}`,
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(`AI service request timeout (${REQUEST_TIMEOUT}ms)`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Validate image URL
 */
function validateImageUrl(url) {
  try {
    const parsed = new URL(url);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      throw new Error("Invalid protocol");
    }
    return true;
  } catch {
    return false;
  }
}

/**
 * Generate alt text for an image
 */
export async function generateAltText(imageUrl, language = "en", context = "") {
  const startTime = Date.now();

  // Validate input
  if (!imageUrl || typeof imageUrl !== "string") {
    return {
      status: "error",
      error: "image_url is required and must be a string",
      code: "INVALID_INPUT",
      disclaimer: DISCLAIMER,
    };
  }

  if (!validateImageUrl(imageUrl)) {
    return {
      status: "error",
      error: "Invalid image URL format",
      code: "INVALID_URL",
      disclaimer: DISCLAIMER,
    };
  }

  try {
    const prompt = context
      ? `Generate a concise, descriptive alt text for this image suitable for screen readers. Be specific about content, not decorative. Max 125 characters. Context: ${context}`
      : "Generate a concise, descriptive alt text for this image suitable for screen readers. Be specific about content, not decorative. Max 125 characters.";

    const aiResult = await callAIService(imageUrl, prompt, language, 150);

    const processingTime = Date.now() - startTime;

    return {
      status: "success",
      alt_text: aiResult.analysis || "",
      disclaimer: DISCLAIMER,
      model: aiResult.model || "Qwen2.5-VL",
      processing_time_ms: aiResult.processing_time_ms || processingTime,
      charged: true,
      cost_usd: 0.05,
    };
  } catch (error) {
    console.error("Alt text generation error:", error.message);

    const processingTime = Date.now() - startTime;

    return {
      status: "error",
      error: error.message,
      code: error.message.includes("timeout")
        ? "TIMEOUT"
        : error.message.includes("service")
          ? "API_ERROR"
          : "PROCESSING_ERROR",
      processing_time_ms: processingTime,
      disclaimer: DISCLAIMER,
      charged: false,
    };
  }
}

/**
 * Generate detailed description for an image
 */
export async function generateDetailedDescription(imageUrl, language = "en") {
  const startTime = Date.now();

  // Validate input
  if (!imageUrl || typeof imageUrl !== "string") {
    return {
      status: "error",
      error: "image_url is required and must be a string",
      code: "INVALID_INPUT",
      disclaimer: DISCLAIMER,
    };
  }

  if (!validateImageUrl(imageUrl)) {
    return {
      status: "error",
      error: "Invalid image URL format",
      code: "INVALID_URL",
      disclaimer: DISCLAIMER,
    };
  }

  try {
    const prompt =
      "Describe this image in detail for visually impaired users. Include: main subject, colors, text visible, spatial relationships, emotional context. 2-3 sentences.";

    const aiResult = await callAIService(imageUrl, prompt, language, 300);

    const processingTime = Date.now() - startTime;

    return {
      status: "success",
      description: aiResult.analysis || "",
      disclaimer: DISCLAIMER,
      model: aiResult.model || "Qwen2.5-VL",
      processing_time_ms: aiResult.processing_time_ms || processingTime,
      charged: true,
      cost_usd: 0.08,
    };
  } catch (error) {
    console.error("Detailed description generation error:", error.message);

    const processingTime = Date.now() - startTime;

    return {
      status: "error",
      error: error.message,
      code: error.message.includes("timeout")
        ? "TIMEOUT"
        : error.message.includes("service")
          ? "API_ERROR"
          : "PROCESSING_ERROR",
      processing_time_ms: processingTime,
      disclaimer: DISCLAIMER,
      charged: false,
    };
  }
}

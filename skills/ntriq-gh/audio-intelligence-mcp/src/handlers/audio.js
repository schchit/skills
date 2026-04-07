/**
 * Audio analysis handlers
 * Calls ntriq AI server for audio transcription and analysis
 * Models: Whisper (MIT License) + Qwen (Apache 2.0 License)
 */

const SERVER = process.env.NTRIQ_AI_URL || "https://ai.ntriq.co.kr";

async function callAudioServer(endpoint, body, timeout = 180) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), (timeout + 15) * 1000);

  try {
    const resp = await fetch(`${SERVER}/audio/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    clearTimeout(timer);

    if (!resp.ok) {
      const error = await resp.text();
      throw new Error(`Audio server error: ${resp.status} ${error}`);
    }

    return await resp.json();
  } catch (e) {
    clearTimeout(timer);
    throw e;
  }
}

export async function transcribeAudio(audioUrl) {
  const result = await callAudioServer("transcribe", {
    audio_url: audioUrl,
  });

  return {
    status: "success",
    text: result.text || "",
    segments: result.segments || [],
    language: result.language || "unknown",
    model: result.model || "whisper-large-v3-turbo",
  };
}

export async function summarizeAudio(
  audioUrl,
  summaryType = "brief",
  language = "en",
) {
  const result = await callAudioServer("summarize", {
    audio_url: audioUrl,
    language: language,
    summary_type: summaryType,
    max_tokens: 1024,
  });

  return {
    status: "success",
    transcript: result.transcript || "",
    summary: result.summary || "",
    summary_type: summaryType,
    model: result.model || "whisper + qwen3.5",
  };
}

export async function analyzeAudio(audioUrl, language = "en") {
  const result = await callAudioServer("analyze", {
    audio_url: audioUrl,
    language: language,
    max_tokens: 2048,
  });

  return {
    status: "success",
    transcript: result.transcript || "",
    analysis: result.analysis || {},
    model: result.model || "whisper + qwen3.5",
  };
}

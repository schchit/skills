import axios from "axios";

const SERVER = process.env.NTRIQ_AI_URL || "https://ai.ntriq.co.kr";
const TIMEOUT_MS = (180 + 15) * 1000; // 195 seconds (180s + 15s buffer)

/**
 * Upscale image by 2x or 4x
 * @param {string} imageUrl - URL of the image to upscale
 * @param {number} scale - Scale factor: 2 or 4 (default 4)
 * @returns {object} Upscaled image metadata and base64
 */
export async function upscaleImage(imageUrl, scale = 4) {
  if (!imageUrl) {
    throw new Error("imageUrl is required");
  }

  if (![2, 4].includes(scale)) {
    throw new Error("scale must be 2 or 4");
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const startTime = Date.now();

    const response = await axios.post(
      `${SERVER}/image/upscale`,
      {
        image_url: imageUrl,
        scale,
        face_enhance: false,
      },
      {
        timeout: TIMEOUT_MS,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    const processingTime = Date.now() - startTime;

    if (!response.data.image_base64) {
      throw new Error("Invalid response: missing image_base64");
    }

    return {
      image_base64: response.data.image_base64,
      original_size: response.data.original_size,
      upscaled_size: response.data.upscaled_size,
      scale: response.data.scale,
      model: response.data.model,
      processing_time: response.data.processing_time || processingTime,
    };
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        `Image upscaling timeout after ${TIMEOUT_MS / 1000} seconds`,
      );
    }
    throw new Error(`Failed to upscale image: ${error.message}`);
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Upscale image with face enhancement
 * @param {string} imageUrl - URL of the image to upscale
 * @param {number} scale - Scale factor: 2 or 4 (default 4)
 * @returns {object} Upscaled image metadata and base64
 */
export async function enhanceFace(imageUrl, scale = 4) {
  if (!imageUrl) {
    throw new Error("imageUrl is required");
  }

  if (![2, 4].includes(scale)) {
    throw new Error("scale must be 2 or 4");
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const startTime = Date.now();

    const response = await axios.post(
      `${SERVER}/image/upscale`,
      {
        image_url: imageUrl,
        scale,
        face_enhance: true,
      },
      {
        timeout: TIMEOUT_MS,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    const processingTime = Date.now() - startTime;

    if (!response.data.image_base64) {
      throw new Error("Invalid response: missing image_base64");
    }

    return {
      image_base64: response.data.image_base64,
      original_size: response.data.original_size,
      upscaled_size: response.data.upscaled_size,
      scale: response.data.scale,
      model: response.data.model,
      processing_time: response.data.processing_time || processingTime,
    };
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        `Image upscaling timeout after ${TIMEOUT_MS / 1000} seconds`,
      );
    }
    throw new Error(`Failed to enhance and upscale image: ${error.message}`);
  } finally {
    clearTimeout(timeoutId);
  }
}

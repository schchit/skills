#!/usr/bin/env node
import { marked } from 'marked';
import puppeteer from 'puppeteer-core';
import { readFileSync, writeFileSync, existsSync, statSync, mkdirSync } from 'fs';
import { resolve, dirname, extname, basename } from 'path';
import { execSync } from 'child_process';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);

// ============================================================================
// Exit Codes - For AI Agent error understanding
// ============================================================================
const EXIT_CODES = {
  SUCCESS: 0,
  INVALID_ARGS: 1,
  FILE_NOT_FOUND: 2,
  FILE_READ_ERROR: 3,
  CHROME_NOT_FOUND: 4,
  BROWSER_LAUNCH_ERROR: 5,
  RENDER_ERROR: 6,
  SCREENSHOT_ERROR: 7,
  OUTPUT_WRITE_ERROR: 8
};

// ============================================================================
// Configuration Presets - Environment-specific settings
// ============================================================================
const PRESETS = {
  openclaw: {
    width: 600,              // CSS pixels
    deviceScaleFactor: 2,    // Actual output: 1200px (matches OpenClaw Agent limit)
    maxFileSizeMB: 5,        // Matches OpenClaw Agent 5MB limit
    jpegQuality: 85,
    description: 'Optimized for OpenClaw (1200px max, 5MB limit)'
  },
  generic: {
    width: 800,              // CSS pixels
    deviceScaleFactor: 2,    // Actual output: 1600px
    maxFileSizeMB: 8,        // Discord limit
    jpegQuality: 85,
    description: 'High resolution for Claude Code / Discord (1600px, 8MB)'
  }
};

// ============================================================================
// Configuration
// ============================================================================
const CONFIG = {
  // Default output width in CSS pixels (actual pixels = width * deviceScaleFactor)
  width: 800,
  // Device scale factor for high-DPI output (2 = 1600px actual width)
  deviceScaleFactor: 2,
  // JPEG quality (1-100)
  jpegQuality: 85,
  // Maximum file size in bytes before splitting (8MB for Discord)
  maxFileSizeMB: 8,
  // Browser operation timeout (30 seconds)
  timeout: 30000,
  // Default output format
  defaultFormat: 'jpeg',
  // Auto theme: day hours (6:00-18:00 = light, 18:00-6:00 = dark)
  dayHourStart: 6,
  dayHourEnd: 18,
  // Current preset name
  preset: 'generic',
  // Force theme (optional: 'light' or 'dark')
  forceTheme: null
};

// ============================================================================
// Environment Detection - Auto-detect OpenClaw vs generic
// ============================================================================
function detectEnvironment() {
  // OpenClaw environment characteristics
  if (process.env.OPENCLAW_CHANNEL ||
      process.env.OPENCLAW_SKILLS_DIR ||
      process.cwd().includes('.openclaw/skills') ||
      process.cwd().includes('.openclaw\\skills')) {
    return 'openclaw';
  }
  return 'generic';
}

function applyPreset(presetName) {
  const preset = PRESETS[presetName];
  if (!preset) {
    console.error(`[WARN] Unknown preset: ${presetName}, using generic`);
    presetName = 'generic';
  }
  const actualPreset = PRESETS[presetName];
  CONFIG.width = actualPreset.width;
  CONFIG.deviceScaleFactor = actualPreset.deviceScaleFactor;
  CONFIG.maxFileSizeMB = actualPreset.maxFileSizeMB;
  CONFIG.jpegQuality = actualPreset.jpegQuality;
  CONFIG.preset = presetName;
  console.log(`[INFO] Applied preset: ${presetName} (${actualPreset.description})`);
}

// ============================================================================
// Theme Detection - Light/Dark mode based on time
// ============================================================================
function getThemeByTime() {
  // Support forced theme override
  if (CONFIG.forceTheme) {
    return CONFIG.forceTheme;
  }
  const hour = new Date().getHours();
  const isDayTime = hour >= CONFIG.dayHourStart && hour < CONFIG.dayHourEnd;
  return isDayTime ? 'light' : 'dark';
}

// ============================================================================
// Theme Styles - Light and Dark mode CSS
// ============================================================================
const THEMES = {
  light: {
    bg: '#ffffff',
    text: '#333333',
    h1Text: '#2c3e50',
    h1Border: '#ff6b6b',
    h2Text: '#34495e',
    h2Border: '#3498db',
    h3Text: '#7f8c8d',
    tableBorder: '#e0e0e0',
    thBg: '#f8f9fa',
    thText: '#2c3e50',
    trEvenBg: '#fafafa',
    trHoverBg: '#f5f5f5',
    inlineCodeBg: '#f4f4f4',
    inlineCodeText: '#e74c3c',
    preBg: '#2d2d2d',
    preText: '#f8f8f2',
    blockquoteBg: '#f9f9f9',
    blockquoteText: '#666666',
    blockquoteBorder: '#3498db',
    hrBorder: '#eeeeee',
    link: '#3498db',
    strongText: '#2c3e50',
    emText: '#7f8c8d'
  },
  dark: {
    bg: '#1a1a2e',
    text: '#e0e0e0',
    h1Text: '#eaeaea',
    h1Border: '#ff6b6b',
    h2Text: '#e8e8e8',
    h2Border: '#4fc3f7',
    h3Text: '#b0b0b0',
    tableBorder: '#3a3a5a',
    thBg: '#252540',
    thText: '#ffffff',
    trEvenBg: '#202035',
    trHoverBg: '#2a2a45',
    inlineCodeBg: '#2d2d4a',
    inlineCodeText: '#ff79c6',
    preBg: '#0d0d1a',
    preText: '#f8f8f2',
    blockquoteBg: '#202035',
    blockquoteText: '#a0a0a0',
    blockquoteBorder: '#4fc3f7',
    hrBorder: '#3a3a5a',
    link: '#4fc3f7',
    strongText: '#ffffff',
    emText: '#b0b0b0'
  }
};

// ============================================================================
// Chrome Path Detection - Cross-platform support
// ============================================================================
function findChromePath() {
  // 1. Check environment variable override
  if (process.env.CHROME_PATH) {
    if (existsSync(process.env.CHROME_PATH)) {
      return process.env.CHROME_PATH;
    }
    console.error(`[ERROR] CHROME_PATH environment variable set but file not found: ${process.env.CHROME_PATH}`);
    process.exit(EXIT_CODES.CHROME_NOT_FOUND);
  }

  // 2. Platform-specific paths
  const platform = process.platform;
  const paths = {
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
    ],
    linux: [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/snap/bin/chromium',
      '/usr/bin/brave-browser'
    ],
    win32: [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files\\Chromium\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Chromium\\Application\\chrome.exe',
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
    ]
  };

  const platformPaths = paths[platform] || [];

  for (const chromePath of platformPaths) {
    if (existsSync(chromePath)) {
      return chromePath;
    }
  }

  // 3. Try to find using 'which' or 'where' command
  try {
    const cmd = platform === 'win32' ? 'where chrome' : 'which google-chrome || which chromium || which chromium-browser';
    const result = execSync(cmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
    if (result && existsSync(result.split('\n')[0])) {
      return result.split('\n')[0];
    }
  } catch (e) {
    // Command failed, continue with error
  }

  // 4. Chrome not found
  console.error('[ERROR] Chrome/Chromium browser not found.');
  console.error('');
  console.error('Please install Google Chrome or Chromium, or set the CHROME_PATH environment variable:');
  console.error('  macOS/Linux: export CHROME_PATH="/path/to/chrome"');
  console.error('  Windows:     set CHROME_PATH=C:\\path\\to\\chrome.exe');
  process.exit(EXIT_CODES.CHROME_NOT_FOUND);
}

// ============================================================================
// Argument Parsing
// ============================================================================
function parseArgs() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log('MD to Share - Markdown to Long Image Converter');
    console.log('');
    console.log('Usage: md2img <input.md> [output] [options]');
    console.log('');
    console.log('Arguments:');
    console.log('  input.md   Input markdown file (required)');
    console.log('  output     Output image path (optional, defaults to input-长图.jpg)');
    console.log('');
    console.log('Options:');
    console.log('  --preset=<name>     Configuration preset: openclaw | generic (default: auto-detect)');
    console.log('  --width=<px>        CSS width in pixels (default: preset value)');
    console.log('  --scale=<factor>    Device scale factor (default: 2)');
    console.log('  --max-size=<MB>     Max file size before splitting (default: preset value)');
    console.log('  --quality=<1-100>   JPEG quality (default: 85)');
    console.log('  --theme=<light|dark> Force theme (default: auto by time)');
    console.log('');
    console.log('Presets:');
    console.log('  openclaw  600px × 2 = 1200px actual, 5MB limit (for OpenClaw/Discord)');
    console.log('  generic   800px × 2 = 1600px actual, 8MB limit (for Claude Code/local)');
    console.log('');
    console.log('Output formats:');
    console.log('  .jpg/.jpeg  JPEG format (default, smaller file size)');
    console.log('  .png        PNG format (lossless, larger file size)');
    console.log('');
    console.log('Features:');
    console.log('  - Environment auto-detection (OpenClaw vs generic)');
    console.log('  - High resolution output with configurable scale factor');
    console.log('  - Automatic splitting for large files');
    console.log('  - Cross-platform Chrome detection');
    console.log('  - Auto theme: light mode (6:00-18:00), dark mode (18:00-6:00)');
    console.log('');
    console.log('Environment variables:');
    console.log('  CHROME_PATH  Override Chrome executable path');
    console.log('');
    console.log('Exit codes:');
    console.log('  0 - Success');
    console.log('  1 - Invalid arguments');
    console.log('  2 - Input file not found');
    console.log('  3 - File read error');
    console.log('  4 - Chrome not found');
    console.log('  5 - Browser launch error');
    console.log('  6 - Render error');
    console.log('  7 - Screenshot error');
    console.log('  8 - Output write error');
    process.exit(args.length === 0 ? EXIT_CODES.INVALID_ARGS : EXIT_CODES.SUCCESS);
  }

  // Separate flag arguments from positional arguments
  const flagArgs = args.filter(arg => arg.startsWith('--'));
  const positionalArgs = args.filter(arg => !arg.startsWith('--'));

  let preset = null;
  const customOverrides = {};

  // Parse flag arguments - track which values were explicitly set
  for (const flag of flagArgs) {
    if (flag.startsWith('--preset=')) {
      preset = flag.split('=')[1];
    } else if (flag.startsWith('--width=')) {
      customOverrides.width = parseInt(flag.split('=')[1], 10);
    } else if (flag.startsWith('--scale=')) {
      customOverrides.deviceScaleFactor = parseFloat(flag.split('=')[1]);
    } else if (flag.startsWith('--max-size=')) {
      customOverrides.maxFileSizeMB = parseInt(flag.split('=')[1], 10);
    } else if (flag.startsWith('--quality=')) {
      customOverrides.jpegQuality = parseInt(flag.split('=')[1], 10);
    } else if (flag === '--theme=light') {
      CONFIG.forceTheme = 'light';
    } else if (flag === '--theme=dark') {
      CONFIG.forceTheme = 'dark';
    }
  }

  if (positionalArgs.length === 0) {
    console.error('[ERROR] Missing input file');
    process.exit(EXIT_CODES.INVALID_ARGS);
  }

  const input = positionalArgs[0];
  let output = positionalArgs[1];

  // Default output path if not provided
  if (!output) {
    output = input.replace(/\.md$/i, '-长图.jpg');
  }

  // Auto-detect preset if not specified
  if (!preset) {
    preset = detectEnvironment();
  }
  applyPreset(preset);

  // Apply custom overrides after preset (custom values take precedence)
  Object.assign(CONFIG, customOverrides);
  if (Object.keys(customOverrides).length > 0) {
    console.log(`[INFO] Custom overrides applied: ${Object.keys(customOverrides).join(', ')}`);
  }

  return { input, output };
}

// ============================================================================
// Input Validation
// ============================================================================
function validateInput(inputPath) {
  // Check file exists
  if (!existsSync(inputPath)) {
    console.error(`[ERROR] Input file not found: ${inputPath}`);
    process.exit(EXIT_CODES.FILE_NOT_FOUND);
  }

  // Check file is readable
  try {
    statSync(inputPath);
  } catch (e) {
    console.error(`[ERROR] Cannot read input file: ${inputPath}`);
    console.error(`  ${e.message}`);
    process.exit(EXIT_CODES.FILE_READ_ERROR);
  }

  return true;
}

function validateOutputPath(outputPath) {
  const outputDir = dirname(resolve(outputPath));

  // Create output directory if it doesn't exist
  if (!existsSync(outputDir)) {
    try {
      mkdirSync(outputDir, { recursive: true });
    } catch (e) {
      console.error(`[ERROR] Cannot create output directory: ${outputDir}`);
      console.error(`  ${e.message}`);
      process.exit(EXIT_CODES.OUTPUT_WRITE_ERROR);
    }
  }

  return true;
}

// ============================================================================
// HTML Template
// ============================================================================
function generateHtmlTemplate(content, theme = 'light') {
  const t = THEMES[theme];

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      max-width: ${CONFIG.width}px;
      margin: 0 auto;
      padding: 40px 30px;
      background: ${t.bg};
      color: ${t.text};
      line-height: 1.8;
    }
    h1 {
      font-size: 32px;
      border-bottom: 3px solid ${t.h1Border};
      padding-bottom: 12px;
      color: ${t.h1Text};
      margin-bottom: 24px;
    }
    h2 {
      font-size: 24px;
      margin-top: 32px;
      margin-bottom: 16px;
      color: ${t.h2Text};
      border-left: 4px solid ${t.h2Border};
      padding-left: 12px;
    }
    h3 {
      font-size: 20px;
      margin-top: 24px;
      margin-bottom: 12px;
      color: ${t.h3Text};
    }
    p { margin: 16px 0; }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 20px 0;
      font-size: 14px;
    }
    th, td {
      border: 1px solid ${t.tableBorder};
      padding: 12px 14px;
      text-align: left;
    }
    th {
      background: ${t.thBg};
      font-weight: 600;
      color: ${t.thText};
    }
    tr:nth-child(even) { background: ${t.trEvenBg}; }
    tr:hover { background: ${t.trHoverBg}; }
    code {
      background: ${t.inlineCodeBg};
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'SF Mono', Monaco, Consolas, monospace;
      font-size: 0.9em;
      color: ${t.inlineCodeText};
    }
    pre {
      background: ${t.preBg};
      color: ${t.preText};
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 16px 0;
    }
    pre code {
      background: none;
      padding: 0;
      color: inherit;
    }
    blockquote {
      border-left: 4px solid ${t.blockquoteBorder};
      margin: 20px 0;
      padding: 12px 20px;
      background: ${t.blockquoteBg};
      color: ${t.blockquoteText};
      border-radius: 0 8px 8px 0;
    }
    hr {
      border: none;
      border-top: 2px solid ${t.hrBorder};
      margin: 40px 0;
    }
    ul, ol {
      padding-left: 24px;
      margin: 16px 0;
    }
    li { margin: 8px 0; }
    a { color: ${t.link}; text-decoration: none; }
    a:hover { text-decoration: underline; }
    img { max-width: 100%; border-radius: 8px; margin: 16px 0; }
    strong { color: ${t.strongText}; }
    em { color: ${t.emText}; }
  </style>
</head>
<body>
${content}
</body>
</html>
`;
}

// ============================================================================
// Image Splitting - Semantic boundary detection
// ============================================================================
async function getContentSections(page) {
  return await page.evaluate(() => {
    const sections = [];
    const headings = document.querySelectorAll('h1, h2, h3, hr');

    headings.forEach(el => {
      const tagName = el.tagName.toLowerCase();
      const rect = el.getBoundingClientRect();
      const scrollTop = window.scrollY || document.documentElement.scrollTop;

      sections.push({
        type: tagName,
        y: Math.round(rect.top + scrollTop),
        priority: tagName === 'h1' ? 1 : tagName === 'h2' ? 2 : tagName === 'h3' ? 3 : 4
      });
    });

    return sections;
  });
}

function findSplitPoints(sections, totalHeight, targetCount) {
  if (targetCount <= 1 || sections.length === 0) {
    return [];
  }

  const idealHeight = totalHeight / targetCount;
  const splitPoints = [];

  for (let i = 1; i < targetCount; i++) {
    const targetY = i * idealHeight;

    // Find the best section near the target position
    let bestSection = null;
    let bestDistance = Infinity;

    for (const section of sections) {
      // Only consider h1, h2, or hr for splitting (priority 1, 2, 4)
      if (section.priority > 3) continue;

      const distance = Math.abs(section.y - targetY);

      // Prefer sections within 20% of ideal segment height
      if (distance < idealHeight * 0.3 && distance < bestDistance) {
        bestDistance = distance;
        bestSection = section;
      }
    }

    if (bestSection) {
      splitPoints.push(bestSection.y);
    } else {
      // Fallback: split at exact position
      splitPoints.push(Math.round(targetY));
    }
  }

  return splitPoints;
}

// ============================================================================
// Main Conversion Logic
// ============================================================================
async function convertMarkdownToImage(input, output, browser) {
  const inputPath = resolve(input);
  const outputPath = resolve(output);

  // Determine output format
  const ext = extname(outputPath).toLowerCase();
  const isPng = ext === '.png';
  const format = isPng ? 'png' : 'jpeg';

  // Auto-detect theme based on time
  const theme = getThemeByTime();
  const themeName = theme === 'light' ? '浅色' : '深色';

  console.log(`[INFO] Converting: ${input}`);
  console.log(`[INFO] Output format: ${format.toUpperCase()}`);
  console.log(`[INFO] Theme: ${themeName}模式 (${theme})`);

  // Read and parse markdown
  let md, html;
  try {
    md = readFileSync(inputPath, 'utf-8');
    html = await marked(md);
  } catch (e) {
    console.error(`[ERROR] Failed to read/parse markdown: ${e.message}`);
    throw { code: EXIT_CODES.FILE_READ_ERROR, message: e.message };
  }

  const fullHtml = generateHtmlTemplate(html, theme);

  // Create page and render
  let page;
  try {
    page = await browser.newPage();

    // Set timeout for page operations
    page.setDefaultTimeout(CONFIG.timeout);

    await page.setContent(fullHtml, { waitUntil: 'networkidle0' });
  } catch (e) {
    console.error(`[ERROR] Failed to render page: ${e.message}`);
    if (page) await page.close().catch(() => {});
    throw { code: EXIT_CODES.RENDER_ERROR, message: e.message };
  }

  // Get content dimensions
  const height = await page.evaluate(() => document.documentElement.scrollHeight);

  // Set viewport with high DPI
  await page.setViewport({
    width: CONFIG.width,
    height: Math.max(height, 100),
    deviceScaleFactor: CONFIG.deviceScaleFactor
  });

  // Take screenshot
  try {
    const screenshotOptions = {
      path: outputPath,
      fullPage: true,
      type: format
    };

    if (format === 'jpeg') {
      screenshotOptions.quality = CONFIG.jpegQuality;
    }

    await page.screenshot(screenshotOptions);
  } catch (e) {
    console.error(`[ERROR] Failed to take screenshot: ${e.message}`);
    await page.close().catch(() => {});
    throw { code: EXIT_CODES.SCREENSHOT_ERROR, message: e.message };
  }

  await page.close();

  // Check file size and potentially split
  const stats = statSync(outputPath);
  const fileSizeMB = stats.size / (1024 * 1024);

  if (fileSizeMB > CONFIG.maxFileSizeMB) {
    console.log(`[INFO] File size (${fileSizeMB.toFixed(2)}MB) exceeds ${CONFIG.maxFileSizeMB}MB limit`);
    console.log(`[INFO] Attempting smart split...`);

    // Re-open page for splitting
    const splitPage = await browser.newPage();
    splitPage.setDefaultTimeout(CONFIG.timeout);
    await splitPage.setContent(fullHtml, { waitUntil: 'networkidle0' });

    const sections = await getContentSections(splitPage);
    const splitCount = Math.ceil(fileSizeMB / CONFIG.maxFileSizeMB);
    const splitPoints = findSplitPoints(sections, height, splitCount);

    if (splitPoints.length > 0) {
      const outputBase = outputPath.replace(/\.[^.]+$/, '');
      const outputExt = extname(outputPath);
      const outputFiles = [];

      // Generate split images
      for (let i = 0; i <= splitPoints.length; i++) {
        const startY = i === 0 ? 0 : splitPoints[i - 1];
        const endY = i === splitPoints.length ? height : splitPoints[i];
        const segmentHeight = endY - startY;

        await splitPage.setViewport({
          width: CONFIG.width,
          height: segmentHeight,
          deviceScaleFactor: CONFIG.deviceScaleFactor
        });

        const segmentPath = `${outputBase}-${i + 1}${outputExt}`;
        const screenshotOptions = {
          path: segmentPath,
          type: format,
          clip: {
            x: 0,
            y: startY,
            width: CONFIG.width,
            height: segmentHeight
          }
        };

        if (format === 'jpeg') {
          screenshotOptions.quality = CONFIG.jpegQuality;
        }

        await splitPage.screenshot(screenshotOptions);
        outputFiles.push(segmentPath);
        console.log(`[INFO] Split ${i + 1}/${splitPoints.length + 1}: ${segmentPath}`);
      }

      await splitPage.close();

      // Remove original large file
      const { unlinkSync } = await import('fs');
      unlinkSync(outputPath);

      console.log(`[SUCCESS] Generated ${outputFiles.length} images:`);
      outputFiles.forEach((f, i) => console.log(`  ${i + 1}. ${f}`));

      return outputFiles;
    } else {
      console.log(`[WARN] Could not find suitable split points. Output file may be too large for some platforms.`);
      await splitPage.close();
    }
  }

  console.log(`[SUCCESS] Image saved: ${outputPath}`);
  console.log(`[INFO] File size: ${fileSizeMB.toFixed(2)}MB`);

  return [outputPath];
}

// ============================================================================
// Main Entry Point
// ============================================================================
async function main() {
  const { input, output } = parseArgs();

  // Validate inputs
  validateInput(input);
  validateOutputPath(output);

  // Find Chrome
  const chromePath = findChromePath();
  console.log(`[INFO] Using Chrome: ${chromePath}`);

  let browser = null;

  try {
    // Launch browser
    try {
      browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--disable-gpu'
        ]
      });
    } catch (e) {
      console.error(`[ERROR] Failed to launch browser: ${e.message}`);
      process.exit(EXIT_CODES.BROWSER_LAUNCH_ERROR);
    }

    // Convert
    await convertMarkdownToImage(input, output, browser);

  } catch (error) {
    if (error.code) {
      process.exit(error.code);
    } else {
      console.error(`[ERROR] Unexpected error: ${error.message}`);
      process.exit(EXIT_CODES.RENDER_ERROR);
    }
  } finally {
    // Always close browser
    if (browser) {
      await browser.close().catch(() => {});
    }
  }
}

main();

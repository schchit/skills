/**
 * Pre-export Pipeline
 * 
 * Normalises, validates, and fills defaults on an invoice object
 * before writing to any output format. Ensures consistent output
 * regardless of whether the invoice came from CLI mode or agent-native.
 * 
 * This is the single pipeline that both modes share.
 */

const { validateArithmetic } = require('../validation/arithmetic');
const { validateDocumentRules } = require('../validation/document-rules');

/**
 * Prepare an invoice for export.
 * Mutates the invoice in place and returns it.
 * 
 * Steps:
 *   1. Ensure structural completeness (metadata, validation, stamps, etc.)
 *   2. Fill metadata defaults (provider, timestamp, documentType)
 *   3. Normalise field locations (top-level ↔ metadata.*)
 *   4. Run validators if not already run
 * 
 * @param {object} invoice - Invoice object (canonical or agent-native)
 * @returns {object} invoice - Same object, normalised and validated
 */
function prepareForExport(invoice) {
  // --- 1. Structural completeness ---
  if (!invoice.metadata) {
    invoice.metadata = {};
  }
  if (!invoice.validation) {
    invoice.validation = { arithmeticValid: null, errors: [], warnings: [] };
  }
  if (!Array.isArray(invoice.validation.errors)) {
    invoice.validation.errors = [];
  }
  if (!Array.isArray(invoice.validation.warnings)) {
    invoice.validation.warnings = [];
  }
  if (!Array.isArray(invoice.charges)) {
    invoice.charges = [];
  }
  if (!Array.isArray(invoice.stamps)) {
    invoice.stamps = [];
  }
  if (!Array.isArray(invoice.lineItems)) {
    invoice.lineItems = [];
  }
  if (!invoice.totals) {
    invoice.totals = {};
  }
  if (!Array.isArray(invoice.totals.vatBreakdown)) {
    invoice.totals.vatBreakdown = [];
  }
  if (!invoice.header) {
    invoice.header = {};
  }
  if (!Array.isArray(invoice.referencedDocuments)) {
    invoice.referencedDocuments = [];
  }
  if (!Array.isArray(invoice.fields)) {
    invoice.fields = [];
  }

  // --- 2. Fill metadata defaults ---
  const m = invoice.metadata;

  // Provider
  if (!m.provider) {
    m.provider = invoice.provider || 'agent-native';
  }

  // Extraction timestamp
  if (!m.extractionTimestamp) {
    m.extractionTimestamp = invoice.extractedAt || new Date().toISOString();
  }

  // Language
  if (!m.language) {
    m.language = invoice.language || null;
  }

  // Document type
  if (!m.documentType) {
    m.documentType = invoice.documentType || null;
  }

  // Confidence
  if (m.confidence === null || m.confidence === undefined) {
    if (invoice.qualityScore?.score !== null && invoice.qualityScore?.score !== undefined) {
      // qualityScore is a fraction (e.g. 6/9) — normalise if > 1
      const raw = invoice.qualityScore.score;
      const total = invoice.qualityScore.total || 9;
      m.confidence = raw > 1 ? Math.round((raw / total) * 100) / 100 : raw;
    }
  }

  // --- 3. Normalise field locations (bidirectional sync) ---
  // Top-level → metadata (for formatters that read metadata.*)
  // Already done above

  // metadata → top-level (for formatters that read top-level)
  if (!invoice.documentType && m.documentType) {
    invoice.documentType = m.documentType;
  }
  if (!invoice.language && m.language) {
    invoice.language = m.language;
  }
  if (!invoice.provider && m.provider) {
    invoice.provider = m.provider;
  }
  if (!invoice.extractedAt && m.extractionTimestamp) {
    invoice.extractedAt = m.extractionTimestamp;
  }

  // --- 4. Run validators if not already run ---
  // Arithmetic: run if never executed (arithmeticValid is still null)
  if (invoice.validation.arithmeticValid === null) {
    validateArithmetic(invoice);
  }

  // Document rules: run if documentQuality not yet computed
  if (!invoice.validation.documentQuality) {
    validateDocumentRules(invoice);
  }

  return invoice;
}

module.exports = { prepareForExport };

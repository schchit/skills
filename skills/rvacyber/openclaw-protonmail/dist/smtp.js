"use strict";
/**
 * SMTP Client for Proton Mail Bridge
 *
 * Provides email sending capabilities through Bridge's local SMTP server.
 * Connects to 127.0.0.1:1025 by default.
 *
 * @packageDocumentation
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SMTPClient = void 0;
const nodemailer_1 = __importDefault(require("nodemailer"));
/**
 * SMTP client for sending emails via Proton Mail Bridge
 *
 * @remarks
 * Uses nodemailer for SMTP operations. Bridge handles encryption
 * and routing to Proton servers.
 */
class SMTPClient {
    /**
     * Create a new SMTP client
     *
     * @param config - SMTP connection settings
     */
    constructor(config) {
        this.config = config;
        this.transporter = nodemailer_1.default.createTransport(config);
    }
    /**
     * Send a new email
     *
     * @param to - Recipient email address
     * @param subject - Email subject
     * @param body - Plain text email body
     * @param options - Additional options (CC, BCC, HTML, attachments)
     * @returns Send result with messageId
     *
     * @throws {Error} If sending fails (invalid recipient, Bridge offline, etc.)
     *
     * @example
     * ```typescript
     * const result = await smtp.send(
     *   'alice@example.com',
     *   'Project Update',
     *   'The project is on track...',
     *   {
     *     cc: 'bob@example.com',
     *     html: '<p>The project is <strong>on track</strong>...</p>'
     *   }
     * );
     * console.log('Sent:', result.messageId);
     * ```
     */
    async send(to, subject, body, options) {
        const mailOptions = {
            from: this.config.auth.user,
            to,
            subject,
            text: body,
            html: options?.html,
            cc: options?.cc,
            bcc: options?.bcc,
            attachments: options?.attachments
        };
        try {
            const result = await this.transporter.sendMail(mailOptions);
            return result;
        }
        catch (error) {
            throw new Error(`Failed to send email: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    /**
     * Reply to an existing email thread
     *
     * @param originalMessage - Original email (from IMAP readMessage)
     * @param body - Reply text
     * @returns Send result
     *
     * @throws {Error} If reply fails
     *
     * @todo Implement full threading headers (In-Reply-To, References)
     *
     * @remarks
     * This method automatically:
     * - Extracts the original sender from Reply-To or From header
     * - Prepends "Re: " to subject if not already present
     * - Sets In-Reply-To and References headers for proper threading
     *
     * @example
     * ```typescript
     * const original = await imap.readMessage('1234');
     * await smtp.reply(original, 'Thanks, I'll review this today.');
     * ```
     */
    async reply(originalMessage, body) {
        // TODO: Full implementation
        // 1. Extract Reply-To or fall back to From header
        // 2. Build subject with "Re: " prefix (if missing)
        // 3. Set In-Reply-To: <original message-id>
        // 4. Set References: <thread message-ids>
        // 5. Send via transporter
        // Stub implementation
        const replyTo = originalMessage.replyTo?.[0]?.address || originalMessage.from?.[0]?.address;
        const subject = originalMessage.subject?.startsWith('Re: ')
            ? originalMessage.subject
            : `Re: ${originalMessage.subject}`;
        const mailOptions = {
            from: this.config.auth.user,
            to: replyTo,
            subject,
            text: body,
            inReplyTo: originalMessage.messageId,
            references: originalMessage.references || originalMessage.messageId
        };
        return this.transporter.sendMail(mailOptions);
    }
}
exports.SMTPClient = SMTPClient;
//# sourceMappingURL=smtp.js.map
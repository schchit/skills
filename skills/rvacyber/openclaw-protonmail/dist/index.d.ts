/**
 * ProtonMail Skill for OpenClaw
 *
 * Provides secure email integration through Proton Mail Bridge.
 * Bridge runs locally and provides IMAP/SMTP access to your ProtonMail account
 * while maintaining end-to-end encryption.
 *
 * @packageDocumentation
 *
 * @example
 * ```typescript
 * import ProtonMailSkill from 'openclaw-protonmail-skill';
 *
 * const skill = new ProtonMailSkill({
 *   account: 'user@pm.me',
 *   bridgePassword: 'bridge-generated-password'
 * });
 *
 * await skill.initialize();
 * const inbox = await skill.listInbox(10);
 * await skill.cleanup();
 * ```
 */
/**
 * Configuration options for ProtonMail skill
 */
export interface ProtonMailConfig {
    /** ProtonMail account email (e.g., user@pm.me or user@protonmail.com) */
    account?: string;
    /** Bridge-generated password (NOT your ProtonMail password) */
    bridgePassword?: string;
    /** IMAP host (default: 127.0.0.1) */
    imapHost?: string;
    /** IMAP port (default: 1143) */
    imapPort?: number;
    /** SMTP host (default: 127.0.0.1) */
    smtpHost?: string;
    /** SMTP port (default: 1025) */
    smtpPort?: number;
}
/**
 * Main skill class for ProtonMail integration
 *
 * Manages IMAP and SMTP connections to Proton Mail Bridge and provides
 * high-level email operations for OpenClaw.
 */
export declare class ProtonMailSkill {
    private imap;
    private smtp;
    /**
     * Create a new ProtonMail skill instance
     *
     * @param config - Optional configuration. If not provided, reads from environment variables.
     *
     * @remarks
     * The Bridge password is separate from your ProtonMail password. Get it from
     * Proton Mail Bridge → Account Settings → Mailbox Configuration.
     *
     * Configuration priority:
     * 1. Passed config object
     * 2. Environment variables (PROTONMAIL_ACCOUNT, PROTONMAIL_BRIDGE_PASSWORD)
     */
    constructor(config?: ProtonMailConfig);
    /**
     * Initialize the skill and register tools with OpenClaw
     *
     * @throws {Error} If Bridge is not running or credentials are invalid
     *
     * @remarks
     * Ensure Proton Mail Bridge is running before calling this method.
     */
    initialize(): Promise<void>;
    /**
     * Cleanup and disconnect from Bridge
     *
     * @remarks
     * Always call this when shutting down to cleanly close connections.
     */
    cleanup(): Promise<void>;
    /**
     * List recent emails from inbox
     *
     * @param limit - Maximum number of emails to return (default: 10)
     * @param unreadOnly - Only return unread emails (default: false)
     * @returns Array of email metadata (sender, subject, date, etc.)
     *
     * @example
     * ```typescript
     * const recent = await skill.listInbox(5, true); // 5 unread emails
     * ```
     */
    listInbox(limit?: number, unreadOnly?: boolean): Promise<any[]>;
    /**
     * Search emails by query
     *
     * @param query - Search query (sender, subject, body keywords)
     * @param limit - Maximum results to return (default: 10)
     * @returns Matching emails
     *
     * @example
     * ```typescript
     * const results = await skill.searchEmails('from:alice@example.com', 20);
     * ```
     */
    searchEmails(query: string, limit?: number): Promise<any[]>;
    /**
     * Read a specific email by ID
     *
     * @param messageId - Message UID or sequence number
     * @returns Full email content (headers, body, attachments)
     *
     * @throws {Error} If message ID is invalid or email doesn't exist
     */
    readEmail(messageId: string): Promise<any>;
    /**
     * Send a new email via ProtonMail
     *
     * @param to - Recipient email address
     * @param subject - Email subject
     * @param body - Email body (plain text)
     * @param options - Optional settings (CC, BCC, HTML, attachments)
     * @returns Send result
     *
     * @example
     * ```typescript
     * await skill.sendEmail(
     *   'alice@example.com',
     *   'Meeting Follow-up',
     *   'Thanks for the meeting today...',
     *   { cc: 'bob@example.com' }
     * );
     * ```
     */
    sendEmail(to: string, subject: string, body: string, options?: any): Promise<any>;
    /**
     * Reply to an existing email thread
     *
     * @param messageId - Original message ID to reply to
     * @param body - Reply text
     * @returns Send result
     *
     * @remarks
     * Automatically sets Reply-To, In-Reply-To, and References headers
     * to maintain threading.
     */
    replyToEmail(messageId: string, body: string): Promise<any>;
}
export default ProtonMailSkill;
//# sourceMappingURL=index.d.ts.map
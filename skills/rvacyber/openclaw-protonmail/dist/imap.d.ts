/**
 * IMAP Client for Proton Mail Bridge
 *
 * Provides low-level IMAP operations for reading emails from ProtonMail.
 * Connects to Bridge's local IMAP server (127.0.0.1:1143 by default).
 *
 * @packageDocumentation
 */
import { ParsedMail } from 'mailparser';
/**
 * IMAP connection configuration
 */
export interface IMAPConfig {
    /** Bridge account username (email address) */
    user: string;
    /** Bridge-generated password */
    password: string;
    /** IMAP host (Bridge runs on localhost) */
    host: string;
    /** IMAP port (Bridge default: 1143) */
    port: number;
    /** Enable TLS (Bridge uses self-signed cert) */
    tls: boolean;
    /** TLS options (set rejectUnauthorized: false for Bridge) */
    tlsOptions?: {
        rejectUnauthorized: boolean;
    };
}
/**
 * Email metadata returned by list operations
 */
export interface EmailMetadata {
    /** Message UID */
    uid: string;
    /** Sender address */
    from: string;
    /** Subject line */
    subject: string;
    /** Received date */
    date: Date;
    /** Read/unread status */
    flags: string[];
}
/**
 * IMAP client for reading emails via Proton Mail Bridge
 *
 * @remarks
 * This client handles connection pooling and error recovery automatically.
 * Bridge must be running before calling connect().
 */
export declare class IMAPClient {
    private imap;
    private config;
    private isConnected;
    /**
     * Create a new IMAP client
     *
     * @param config - IMAP connection settings
     */
    constructor(config: IMAPConfig);
    /**
     * Connect to Bridge IMAP server
     *
     * @throws {Error} If Bridge is not running or credentials are invalid
     *
     * @remarks
     * Ensure Proton Mail Bridge is running before calling this.
     * Connection timeout is 10 seconds by default.
     */
    connect(): Promise<void>;
    /**
     * Disconnect from Bridge
     */
    disconnect(): Promise<void>;
    /**
     * List emails from inbox
     *
     * @param limit - Maximum emails to return
     * @param unreadOnly - Filter to unread messages only
     * @returns Array of email metadata
     *
     * @example
     * ```typescript
     * const emails = await imap.listInbox(10, true);
     * console.log(emails.map(e => `${e.from}: ${e.subject}`));
     * ```
     */
    listInbox(limit?: number, unreadOnly?: boolean): Promise<EmailMetadata[]>;
    /**
     * Search emails by query
     *
     * @param query - Search query (supports IMAP search syntax)
     * @param limit - Maximum results
     * @returns Matching emails
     *
     * @example
     * Supported query formats:
     * - `from:alice@example.com` - Emails from sender
     * - `subject:meeting` - Subject contains keyword
     * - `body:invoice` - Body contains keyword
     * - `newer_than:7d` - Last 7 days
     */
    search(query: string, limit?: number): Promise<EmailMetadata[]>;
    /**
     * Parse search query string into IMAP criteria
     *
     * @param query - User-friendly search query
     * @returns IMAP search criteria array
     *
     * @private
     */
    private parseSearchQuery;
    private sanitizeSearchInput;
    private sanitizeSearchValue;
    /**
     * Read full email content by UID
     *
     * @param messageId - Message UID
     * @returns Parsed email with headers, body, and attachments
     *
     * @throws {Error} If message UID is invalid
     *
     * @example
     * ```typescript
     * const email = await imap.readMessage('1234');
     * console.log(email.text); // Plain text body
     * console.log(email.html); // HTML body
     * console.log(email.attachments); // File attachments
     * ```
     */
    readMessage(messageId: string): Promise<ParsedMail>;
}
//# sourceMappingURL=imap.d.ts.map
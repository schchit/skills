/**
 * OpenClaw Tool Definitions for ProtonMail Skill
 *
 * Registers tool functions that OpenClaw can invoke.
 */
import type { ProtonMailSkill } from './index';
export declare function registerTools(skill: ProtonMailSkill): void;
export declare const TOOL_DEFINITIONS: {
    'protonmail-list-inbox': {
        description: string;
        parameters: {
            limit: {
                type: string;
                optional: boolean;
                default: number;
            };
            unreadOnly: {
                type: string;
                optional: boolean;
                default: boolean;
            };
        };
    };
    'protonmail-search': {
        description: string;
        parameters: {
            query: {
                type: string;
                required: boolean;
            };
            limit: {
                type: string;
                optional: boolean;
                default: number;
            };
        };
    };
    'protonmail-read': {
        description: string;
        parameters: {
            messageId: {
                type: string;
                required: boolean;
            };
        };
    };
    'protonmail-send': {
        description: string;
        parameters: {
            to: {
                type: string;
                required: boolean;
            };
            subject: {
                type: string;
                required: boolean;
            };
            body: {
                type: string;
                required: boolean;
            };
            cc: {
                type: string;
                optional: boolean;
            };
            bcc: {
                type: string;
                optional: boolean;
            };
        };
    };
    'protonmail-reply': {
        description: string;
        parameters: {
            messageId: {
                type: string;
                required: boolean;
            };
            body: {
                type: string;
                required: boolean;
            };
        };
    };
};
//# sourceMappingURL=tools.d.ts.map
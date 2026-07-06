/**
 * Shared JSDoc typedefs for API response shapes used across pages.
 * This project uses plain JS + JSDoc rather than TypeScript, but these
 * typedefs give editors useful autocomplete/hover info.
 *
 * @typedef {Object} ContentScoreResponse
 * @property {number} overall_score
 * @property {number} hook_score
 * @property {number} clarity_score
 * @property {number} novelty_score
 * @property {number} audience_fit_score
 * @property {number} emotional_pull_score
 * @property {number} usefulness_score
 * @property {number} shareability_score
 * @property {number} saveability_score
 * @property {number} trust_score
 * @property {number} cta_score
 * @property {"low"|"medium"|"high"} retention_risk
 * @property {string[]} improvement_suggestions
 * @property {"rules"|"blended"} method
 *
 * @typedef {Object} HookResult
 * @property {string} style
 * @property {string} text
 * @property {number} expected_strength
 * @property {string} rationale
 * @property {string} visual_opening
 * @property {string} matching_caption
 * @property {string} matching_cta
 *
 * @typedef {Object} SimulationResult
 * @property {number} run_id
 * @property {number} final_reach
 * @property {Object} final_engagement
 * @property {Array<{tick: number, cumulative_reach: number}>} reach_curve
 * @property {Array<Object>} engagement_curve
 * @property {string[]} why_content_spread
 * @property {string[]} why_content_stalled
 * @property {string} disclaimer
 *
 * @typedef {Object} ComplianceError
 * @property {number} status
 * @property {{message: string, category: string|null, compliant_alternative: string}} detail
 */

export {};

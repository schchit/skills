/**
 * Levenshtein distance implementation
 * Measures how many single-character edits (insertions, deletions, substitutions)
 * are required to change one string to another
 */

export function levenshteinDistance(str1, str2) {
  const len1 = str1.length;
  const len2 = str2.length;
  const matrix = Array(len2 + 1)
    .fill(null)
    .map(() => Array(len1 + 1).fill(0));

  for (let i = 0; i <= len1; i++) {
    matrix[0][i] = i;
  }

  for (let j = 0; j <= len2; j++) {
    matrix[j][0] = j;
  }

  for (let j = 1; j <= len2; j++) {
    for (let i = 1; i <= len1; i++) {
      const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1, // deletion
        matrix[j - 1][i] + 1, // insertion
        matrix[j - 1][i - 1] + cost, // substitution
      );
    }
  }

  return matrix[len2][len1];
}

/**
 * Calculate similarity score (0-100) based on Levenshtein distance
 */
export function similarityScore(str1, str2) {
  const distance = levenshteinDistance(str1.toLowerCase(), str2.toLowerCase());
  const maxLen = Math.max(str1.length, str2.length);
  const similarity = ((maxLen - distance) / maxLen) * 100;
  return Math.round(similarity);
}

/**
 * Check if two strings are homoglyphs (visually similar characters)
 * Common homoglyph substitutions:
 * - 0 (zero) vs O (letter o)
 * - 1 (one) vs l (lowercase L) vs I (uppercase i)
 * - 5 vs S
 * - 8 vs B
 */
export function isHomoglyph(char1, char2) {
  const homoglyphMap = {
    '0': ['O', 'o'],
    'O': ['0'],
    'o': ['0'],
    '1': ['l', 'L', 'I', '|'],
    'l': ['1', 'I'],
    'L': ['1', 'I'],
    'I': ['1', 'l'],
    '5': ['S'],
    'S': ['5'],
    '8': ['B'],
    'B': ['8'],
    'rn': ['m'],
    'm': ['rn'],
  };

  const key1 = char1.toLowerCase();
  const key2 = char2.toLowerCase();

  if (key1 === key2) return false; // Not a substitution
  if (homoglyphMap[key1]?.includes(char2)) return true;
  if (homoglyphMap[key2]?.includes(char1)) return true;

  return false;
}

/**
 * Check for homoglyph attacks in domain
 * Returns how many characters could be homoglyph substitutions
 */
export function countHomoglyphSubstitutions(original, suspect) {
  let count = 0;
  const minLen = Math.min(original.length, suspect.length);

  for (let i = 0; i < minLen; i++) {
    if (isHomoglyph(original[i], suspect[i])) {
      count++;
    }
  }

  return count;
}

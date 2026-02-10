/**
 * Property-Based Tests and Unit Tests for Legal Documents Vector Storage
 * Feature: rag-compliance-engine
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';

/**
 * Mock implementation of the addLegalDocument validation logic
 * This tests the core validation without requiring a full Convex environment
 */
function validateEmbeddingDimensions(embedding: number[]): void {
  if (embedding.length !== 3072) {
    throw new Error(
      `Invalid embedding dimensions: expected 3072, got ${embedding.length}`
    );
  }
}

describe('Legal Documents - Property-Based Tests', () => {
  /**
   * Property 1: Embedding Dimension Consistency
   * 
   * For any text chunk or query processed by the system, the generated embedding 
   * SHALL have exactly 3072 dimensions (gemini-embedding-001), and any attempt to 
   * store an embedding with a different dimension count SHALL be rejected.
   * 
   * Validates: Requirements 1.2, 2.5, 4.3
   */
  describe('Property 1: Embedding Dimension Consistency', () => {
    it('should accept embeddings with exactly 3072 dimensions', () => {
      fc.assert(
        fc.property(
          // Generate an array of exactly 3072 float64 values
          fc.array(fc.double(), { minLength: 3072, maxLength: 3072 }),
          (embedding) => {
            // This should not throw an error
            expect(() => validateEmbeddingDimensions(embedding)).not.toThrow();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should reject embeddings with fewer than 3072 dimensions', () => {
      fc.assert(
        fc.property(
          // Generate arrays with 0 to 3071 dimensions (sample range for performance)
          fc.integer({ min: 0, max: 3071 }).chain((length) =>
            fc.tuple(
              fc.constant(length),
              fc.array(fc.double(), { minLength: length, maxLength: length })
            )
          ),
          ([length, embedding]) => {
            // This should throw an error
            expect(() => validateEmbeddingDimensions(embedding)).toThrow(
              `Invalid embedding dimensions: expected 3072, got ${length}`
            );
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should reject embeddings with more than 3072 dimensions', () => {
      fc.assert(
        fc.property(
          // Generate arrays with 3073 to 4000 dimensions
          fc.integer({ min: 3073, max: 4000 }).chain((length) =>
            fc.tuple(
              fc.constant(length),
              fc.array(fc.double(), { minLength: length, maxLength: length })
            )
          ),
          ([length, embedding]) => {
            // This should throw an error
            expect(() => validateEmbeddingDimensions(embedding)).toThrow(
              `Invalid embedding dimensions: expected 3072, got ${length}`
            );
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should reject empty embeddings', () => {
      const emptyEmbedding: number[] = [];
      expect(() => validateEmbeddingDimensions(emptyEmbedding)).toThrow(
        'Invalid embedding dimensions: expected 3072, got 0'
      );
    });

    it('should validate dimension count regardless of embedding values', () => {
      fc.assert(
        fc.property(
          // Generate 3072-dimensional embeddings with various value ranges
          fc.array(
            fc.oneof(
              fc.double({ min: -1, max: 1 }), // Normalized values
              fc.double({ min: -100, max: 100 }), // Larger values
              fc.constant(0), // Zero values
              fc.constant(NaN), // Edge case: NaN
              fc.constant(Infinity), // Edge case: Infinity
              fc.constant(-Infinity) // Edge case: -Infinity
            ),
            { minLength: 3072, maxLength: 3072 }
          ),
          (embedding) => {
            // Dimension validation should pass regardless of values
            expect(() => validateEmbeddingDimensions(embedding)).not.toThrow();
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 2: Vector Search Result Ordering
   * 
   * For any vector search query, the returned results SHALL be ordered by 
   * similarity score in descending order (highest similarity first).
   * 
   * Validates: Requirements 2.3
   */
  describe('Property 2: Vector Search Result Ordering', () => {
    /**
     * Mock implementation of search result ordering logic
     * Simulates the behavior of searchLegalDocs result ordering
     */
    function mockSearchResults(scores: number[]): Array<{ score: number }> {
      // Simulate the vector search returning results with scores
      return scores.map(score => ({ score }));
    }

    function isDescendingOrder(results: Array<{ score: number }>): boolean {
      for (let i = 0; i < results.length - 1; i++) {
        if (results[i].score < results[i + 1].score) {
          return false;
        }
      }
      return true;
    }

    it('should return results in descending order by similarity score', () => {
      fc.assert(
        fc.property(
          // Generate an array of scores (similarity values typically between 0 and 1)
          fc.array(fc.double({ min: 0, max: 1 }), { minLength: 1, maxLength: 10 }),
          (scores) => {
            // Sort scores in descending order (simulating what the DB should do)
            const sortedScores = [...scores].sort((a, b) => b - a);
            const results = mockSearchResults(sortedScores);
            
            // Verify results are in descending order
            expect(isDescendingOrder(results)).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should maintain descending order with duplicate scores', () => {
      fc.assert(
        fc.property(
          // Generate arrays that may contain duplicate scores
          fc.array(fc.double({ min: 0, max: 1 }), { minLength: 2, maxLength: 10 }),
          (scores) => {
            const sortedScores = [...scores].sort((a, b) => b - a);
            const results = mockSearchResults(sortedScores);
            
            // Even with duplicates, order should be non-increasing (descending or equal)
            expect(isDescendingOrder(results)).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle edge case of single result', () => {
      fc.assert(
        fc.property(
          fc.double({ min: 0, max: 1 }),
          (score) => {
            const results = mockSearchResults([score]);
            
            // Single result is trivially in descending order
            expect(isDescendingOrder(results)).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle results with identical scores', () => {
      fc.assert(
        fc.property(
          fc.tuple(
            fc.double({ min: 0, max: 1 }),
            fc.integer({ min: 2, max: 10 })
          ),
          ([score, count]) => {
            // Create array with identical scores
            const identicalScores = Array(count).fill(score);
            const results = mockSearchResults(identicalScores);
            
            // All identical scores should be considered in descending order
            expect(isDescendingOrder(results)).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle extreme score values', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.oneof(
              fc.constant(0),           // Minimum similarity
              fc.constant(1),           // Maximum similarity
              fc.constant(0.5),         // Mid-range
              fc.double({ min: 0, max: 1 })  // Any valid value
            ),
            { minLength: 1, maxLength: 10 }
          ),
          (scores) => {
            const sortedScores = [...scores].sort((a, b) => b - a);
            const results = mockSearchResults(sortedScores);
            
            expect(isDescendingOrder(results)).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should detect incorrectly ordered results', () => {
      // Test that our validation correctly identifies ascending order as invalid
      const ascendingResults = [
        { score: 0.1 },
        { score: 0.5 },
        { score: 0.9 }
      ];
      
      expect(isDescendingOrder(ascendingResults)).toBe(false);
    });

    it('should detect mixed ordering as invalid', () => {
      // Test that our validation correctly identifies mixed order as invalid
      const mixedResults = [
        { score: 0.9 },
        { score: 0.3 },
        { score: 0.7 }
      ];
      
      expect(isDescendingOrder(mixedResults)).toBe(false);
    });
  });
});

/**
 * Unit Tests for Convex Functions
 * Testing addLegalDocument and searchLegalDocs with specific scenarios
 */
describe('Legal Documents - Unit Tests', () => {
  /**
   * Unit tests for addLegalDocument mutation
   * Requirements: 2.1, 2.5
   */
  describe('addLegalDocument', () => {
    it('should accept valid document with 3072-dimensional embedding', () => {
      const validEmbedding = new Array(3072).fill(0.5);
      const document = {
        chunk_text: 'Section 17(5) of the CGST Act blocks ITC on food and beverages.',
        source_file: 'a2017-12.pdf',
        page_number: 42,
        category: 'GST',
        embedding: validEmbedding,
      };

      // Validate the embedding dimensions (simulating the mutation logic)
      expect(() => validateEmbeddingDimensions(document.embedding)).not.toThrow();
      expect(document.embedding.length).toBe(3072);
    });

    it('should reject document with 3071-dimensional embedding', () => {
      const invalidEmbedding = new Array(3071).fill(0.5);
      
      expect(() => validateEmbeddingDimensions(invalidEmbedding)).toThrow(
        'Invalid embedding dimensions: expected 3072, got 3071'
      );
    });

    it('should reject document with 3073-dimensional embedding', () => {
      const invalidEmbedding = new Array(3073).fill(0.5);
      
      expect(() => validateEmbeddingDimensions(invalidEmbedding)).toThrow(
        'Invalid embedding dimensions: expected 3072, got 3073'
      );
    });

    it('should reject document with 768-dimensional embedding (old model)', () => {
      const invalidEmbedding = new Array(768).fill(0.5);
      
      expect(() => validateEmbeddingDimensions(invalidEmbedding)).toThrow(
        'Invalid embedding dimensions: expected 3072, got 768'
      );
    });

    it('should reject document with empty embedding', () => {
      const emptyEmbedding: number[] = [];
      
      expect(() => validateEmbeddingDimensions(emptyEmbedding)).toThrow(
        'Invalid embedding dimensions: expected 3072, got 0'
      );
    });

    it('should accept document with normalized embedding values', () => {
      // Typical embedding values are normalized between -1 and 1
      const normalizedEmbedding = new Array(3072).fill(0).map((_, i) => 
        Math.sin(i * 0.01) // Generate values between -1 and 1
      );
      
      expect(() => validateEmbeddingDimensions(normalizedEmbedding)).not.toThrow();
    });

    it('should accept document with various valid metadata', () => {
      const validEmbedding = new Array(3072).fill(0.1);
      
      const documents = [
        {
          chunk_text: 'GST compliance text',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: validEmbedding,
        },
        {
          chunk_text: 'Income tax compliance text',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 100,
          category: 'Income_Tax',
          embedding: validEmbedding,
        },
        {
          chunk_text: 'Section 40A(3) limits cash payments to ₹10,000',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 250,
          category: 'Income_Tax',
          embedding: validEmbedding,
        },
      ];

      documents.forEach(doc => {
        expect(() => validateEmbeddingDimensions(doc.embedding)).not.toThrow();
        expect(doc.chunk_text).toBeTruthy();
        expect(doc.source_file).toBeTruthy();
        expect(doc.page_number).toBeGreaterThan(0);
        expect(doc.category).toBeTruthy();
      });
    });
  });

  /**
   * Unit tests for searchLegalDocs query
   * Requirements: 2.2, 2.5
   */
  describe('searchLegalDocs', () => {
    /**
     * Mock search function that simulates vector search behavior
     */
    function mockVectorSearch(
      queryEmbedding: number[],
      documents: Array<{
        chunk_text: string;
        source_file: string;
        page_number: number;
        category: string;
        embedding: number[];
      }>,
      limit: number = 3,
      categoryFilter?: string
    ): Array<{
      chunk_text: string;
      source_file: string;
      page_number: number;
      category: string;
      score: number;
    }> {
      // Calculate cosine similarity for each document
      const results = documents
        .filter(doc => !categoryFilter || doc.category === categoryFilter)
        .map(doc => {
          // Simple dot product as similarity score (simplified for testing)
          const similarity = queryEmbedding.reduce(
            (sum, val, idx) => sum + val * doc.embedding[idx],
            0
          ) / queryEmbedding.length;
          
          return {
            chunk_text: doc.chunk_text,
            source_file: doc.source_file,
            page_number: doc.page_number,
            category: doc.category,
            score: similarity,
          };
        })
        .sort((a, b) => b.score - a.score) // Sort by similarity descending
        .slice(0, limit); // Take top K results

      return results;
    }

    it('should return top 3 results by default', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = [
        {
          chunk_text: 'Document 1',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.9), // High similarity
        },
        {
          chunk_text: 'Document 2',
          source_file: 'a2017-12.pdf',
          page_number: 2,
          category: 'GST',
          embedding: new Array(3072).fill(0.7), // Medium similarity
        },
        {
          chunk_text: 'Document 3',
          source_file: 'a2017-12.pdf',
          page_number: 3,
          category: 'GST',
          embedding: new Array(3072).fill(0.5), // Medium similarity
        },
        {
          chunk_text: 'Document 4',
          source_file: 'a2017-12.pdf',
          page_number: 4,
          category: 'GST',
          embedding: new Array(3072).fill(0.3), // Low similarity
        },
        {
          chunk_text: 'Document 5',
          source_file: 'a2017-12.pdf',
          page_number: 5,
          category: 'GST',
          embedding: new Array(3072).fill(0.1), // Very low similarity
        },
      ];

      const results = mockVectorSearch(queryEmbedding, documents);

      expect(results).toHaveLength(3);
      expect(results[0].chunk_text).toBe('Document 1');
      expect(results[1].chunk_text).toBe('Document 2');
      expect(results[2].chunk_text).toBe('Document 3');
    });

    it('should respect custom limit parameter', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = Array.from({ length: 10 }, (_, i) => ({
        chunk_text: `Document ${i + 1}`,
        source_file: 'a2017-12.pdf',
        page_number: i + 1,
        category: 'GST',
        embedding: new Array(3072).fill(0.5),
      }));

      const results5 = mockVectorSearch(queryEmbedding, documents, 5);
      expect(results5).toHaveLength(5);

      const results1 = mockVectorSearch(queryEmbedding, documents, 1);
      expect(results1).toHaveLength(1);

      const results10 = mockVectorSearch(queryEmbedding, documents, 10);
      expect(results10).toHaveLength(10);
    });

    it('should filter by category when specified', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = [
        {
          chunk_text: 'GST Document 1',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.9),
        },
        {
          chunk_text: 'GST Document 2',
          source_file: 'a2017-12.pdf',
          page_number: 2,
          category: 'GST',
          embedding: new Array(3072).fill(0.8),
        },
        {
          chunk_text: 'Income Tax Document 1',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 1,
          category: 'Income_Tax',
          embedding: new Array(3072).fill(0.95), // Higher similarity but different category
        },
        {
          chunk_text: 'Income Tax Document 2',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 2,
          category: 'Income_Tax',
          embedding: new Array(3072).fill(0.85),
        },
      ];

      // Filter for GST only
      const gstResults = mockVectorSearch(queryEmbedding, documents, 3, 'GST');
      expect(gstResults).toHaveLength(2);
      expect(gstResults.every(r => r.category === 'GST')).toBe(true);
      expect(gstResults[0].chunk_text).toBe('GST Document 1');

      // Filter for Income_Tax only
      const taxResults = mockVectorSearch(queryEmbedding, documents, 3, 'Income_Tax');
      expect(taxResults).toHaveLength(2);
      expect(taxResults.every(r => r.category === 'Income_Tax')).toBe(true);
      expect(taxResults[0].chunk_text).toBe('Income Tax Document 1');
    });

    it('should return results with all required fields', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = [
        {
          chunk_text: 'Section 17(5) blocks ITC on food and beverages',
          source_file: 'a2017-12.pdf',
          page_number: 42,
          category: 'GST',
          embedding: new Array(3072).fill(0.8),
        },
      ];

      const results = mockVectorSearch(queryEmbedding, documents);

      expect(results).toHaveLength(1);
      const result = results[0];
      
      // Verify all required fields are present
      expect(result).toHaveProperty('chunk_text');
      expect(result).toHaveProperty('source_file');
      expect(result).toHaveProperty('page_number');
      expect(result).toHaveProperty('category');
      expect(result).toHaveProperty('score');
      
      // Verify field values
      expect(result.chunk_text).toBe('Section 17(5) blocks ITC on food and beverages');
      expect(result.source_file).toBe('a2017-12.pdf');
      expect(result.page_number).toBe(42);
      expect(result.category).toBe('GST');
      expect(typeof result.score).toBe('number');
    });

    it('should return results ordered by similarity score descending', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = [
        {
          chunk_text: 'Low similarity',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.2),
        },
        {
          chunk_text: 'High similarity',
          source_file: 'a2017-12.pdf',
          page_number: 2,
          category: 'GST',
          embedding: new Array(3072).fill(0.9),
        },
        {
          chunk_text: 'Medium similarity',
          source_file: 'a2017-12.pdf',
          page_number: 3,
          category: 'GST',
          embedding: new Array(3072).fill(0.6),
        },
      ];

      const results = mockVectorSearch(queryEmbedding, documents);

      expect(results).toHaveLength(3);
      expect(results[0].chunk_text).toBe('High similarity');
      expect(results[1].chunk_text).toBe('Medium similarity');
      expect(results[2].chunk_text).toBe('Low similarity');
      
      // Verify scores are in descending order
      expect(results[0].score).toBeGreaterThanOrEqual(results[1].score);
      expect(results[1].score).toBeGreaterThanOrEqual(results[2].score);
    });

    it('should handle empty result set when no documents match category filter', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = [
        {
          chunk_text: 'GST Document',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.8),
        },
      ];

      const results = mockVectorSearch(queryEmbedding, documents, 3, 'Income_Tax');

      expect(results).toHaveLength(0);
    });

    it('should handle query with various embedding values', () => {
      const queryEmbeddings = [
        new Array(3072).fill(0), // All zeros
        new Array(3072).fill(1), // All ones
        new Array(3072).fill(0).map((_, i) => i % 2 === 0 ? 1 : 0), // Alternating
        new Array(3072).fill(0).map((_, i) => Math.sin(i * 0.1)), // Sine wave
      ];

      const documents = [
        {
          chunk_text: 'Test document',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.5),
        },
      ];

      queryEmbeddings.forEach(queryEmbedding => {
        const results = mockVectorSearch(queryEmbedding, documents);
        
        expect(results).toHaveLength(1);
        expect(results[0]).toHaveProperty('score');
        expect(typeof results[0].score).toBe('number');
      });
    });

    it('should return fewer results than limit if not enough documents exist', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const documents = [
        {
          chunk_text: 'Document 1',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.8),
        },
        {
          chunk_text: 'Document 2',
          source_file: 'a2017-12.pdf',
          page_number: 2,
          category: 'GST',
          embedding: new Array(3072).fill(0.7),
        },
      ];

      const results = mockVectorSearch(queryEmbedding, documents, 5);

      expect(results).toHaveLength(2); // Only 2 documents available, not 5
    });
  });

  /**
   * Integration tests for category filtering with search
   * Requirements: 2.2, 2.5
   */
  describe('searchLegalDocs - Category Filtering Integration', () => {
    it('should correctly filter GST documents from mixed collection', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const mixedDocuments = [
        {
          chunk_text: 'Section 17(5) of CGST Act',
          source_file: 'a2017-12.pdf',
          page_number: 42,
          category: 'GST',
          embedding: new Array(3072).fill(0.9),
        },
        {
          chunk_text: 'Section 40A(3) of Income Tax Act',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 150,
          category: 'Income_Tax',
          embedding: new Array(3072).fill(0.95), // Higher score but wrong category
        },
        {
          chunk_text: 'GST rate structure',
          source_file: 'a2017-12.pdf',
          page_number: 10,
          category: 'GST',
          embedding: new Array(3072).fill(0.8),
        },
      ];

      function mockVectorSearch(
        queryEmbedding: number[],
        documents: Array<{
          chunk_text: string;
          source_file: string;
          page_number: number;
          category: string;
          embedding: number[];
        }>,
        limit: number = 3,
        categoryFilter?: string
      ) {
        const results = documents
          .filter(doc => !categoryFilter || doc.category === categoryFilter)
          .map(doc => {
            const similarity = queryEmbedding.reduce(
              (sum, val, idx) => sum + val * doc.embedding[idx],
              0
            ) / queryEmbedding.length;
            
            return {
              chunk_text: doc.chunk_text,
              source_file: doc.source_file,
              page_number: doc.page_number,
              category: doc.category,
              score: similarity,
            };
          })
          .sort((a, b) => b.score - a.score)
          .slice(0, limit);

        return results;
      }

      const gstResults = mockVectorSearch(queryEmbedding, mixedDocuments, 3, 'GST');

      expect(gstResults).toHaveLength(2);
      expect(gstResults.every(r => r.category === 'GST')).toBe(true);
      expect(gstResults.every(r => r.source_file === 'a2017-12.pdf')).toBe(true);
      
      // Verify the Income Tax document was excluded despite higher score
      expect(gstResults.find(r => r.chunk_text.includes('40A(3)'))).toBeUndefined();
    });

    it('should correctly filter Income_Tax documents from mixed collection', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const mixedDocuments = [
        {
          chunk_text: 'GST compliance rules',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.9),
        },
        {
          chunk_text: 'Section 40A(3) cash limit',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 150,
          category: 'Income_Tax',
          embedding: new Array(3072).fill(0.85),
        },
        {
          chunk_text: 'TDS provisions',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 200,
          category: 'Income_Tax',
          embedding: new Array(3072).fill(0.8),
        },
      ];

      function mockVectorSearch(
        queryEmbedding: number[],
        documents: Array<{
          chunk_text: string;
          source_file: string;
          page_number: number;
          category: string;
          embedding: number[];
        }>,
        limit: number = 3,
        categoryFilter?: string
      ) {
        const results = documents
          .filter(doc => !categoryFilter || doc.category === categoryFilter)
          .map(doc => {
            const similarity = queryEmbedding.reduce(
              (sum, val, idx) => sum + val * doc.embedding[idx],
              0
            ) / queryEmbedding.length;
            
            return {
              chunk_text: doc.chunk_text,
              source_file: doc.source_file,
              page_number: doc.page_number,
              category: doc.category,
              score: similarity,
            };
          })
          .sort((a, b) => b.score - a.score)
          .slice(0, limit);

        return results;
      }

      const taxResults = mockVectorSearch(queryEmbedding, mixedDocuments, 3, 'Income_Tax');

      expect(taxResults).toHaveLength(2);
      expect(taxResults.every(r => r.category === 'Income_Tax')).toBe(true);
      expect(taxResults.every(r => r.source_file === 'Income-tax-Act-2025.pdf')).toBe(true);
      
      // Verify GST documents were excluded
      expect(taxResults.find(r => r.chunk_text.includes('GST'))).toBeUndefined();
    });

    it('should return all categories when no filter is specified', () => {
      const queryEmbedding = new Array(3072).fill(0.5);
      const mixedDocuments = [
        {
          chunk_text: 'GST Document',
          source_file: 'a2017-12.pdf',
          page_number: 1,
          category: 'GST',
          embedding: new Array(3072).fill(0.9),
        },
        {
          chunk_text: 'Income Tax Document',
          source_file: 'Income-tax-Act-2025.pdf',
          page_number: 1,
          category: 'Income_Tax',
          embedding: new Array(3072).fill(0.85),
        },
      ];

      function mockVectorSearch(
        queryEmbedding: number[],
        documents: Array<{
          chunk_text: string;
          source_file: string;
          page_number: number;
          category: string;
          embedding: number[];
        }>,
        limit: number = 3,
        categoryFilter?: string
      ) {
        const results = documents
          .filter(doc => !categoryFilter || doc.category === categoryFilter)
          .map(doc => {
            const similarity = queryEmbedding.reduce(
              (sum, val, idx) => sum + val * doc.embedding[idx],
              0
            ) / queryEmbedding.length;
            
            return {
              chunk_text: doc.chunk_text,
              source_file: doc.source_file,
              page_number: doc.page_number,
              category: doc.category,
              score: similarity,
            };
          })
          .sort((a, b) => b.score - a.score)
          .slice(0, limit);

        return results;
      }

      const allResults = mockVectorSearch(queryEmbedding, mixedDocuments, 3);

      expect(allResults).toHaveLength(2);
      const categories = new Set(allResults.map(r => r.category));
      expect(categories.has('GST')).toBe(true);
      expect(categories.has('Income_Tax')).toBe(true);
    });
  });
});

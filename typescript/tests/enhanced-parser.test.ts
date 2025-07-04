import { 
  analyzeMemory, 
  generateContextualResponse, 
  addConversationTurn, 
  getConversationHistory, 
  analyzeConversationTrends,
  parseIntelligenceEnhanced,
  updateMemory,
  setOpenAIClient 
} from '../parsers/intelligenceParser';

const mockedCreate = jest.fn();
const mockClient = { chat: { completions: { create: mockedCreate } } } as any;

beforeAll(() => {
  setOpenAIClient(mockClient);
});

beforeEach(() => {
  mockedCreate.mockClear();
  // Clear memory for each test
  updateMemory('testUser', {});
});

describe('Enhanced Intelligence Parser Features', () => {
  describe('analyzeMemory', () => {
    test('should calculate completeness score correctly', () => {
      updateMemory('testUser', {
        energyLevel: 'high',
        mood: 'focused',
        goals: ['complete project'],
        intent: 'work on coding',
        priority: 'high'
      });

      const analysis = analyzeMemory('testUser');
      
      expect(analysis.completeness).toBe(1.0); // All required fields present
      expect(analysis.confidence).toBeGreaterThan(0.9);
      expect(analysis.suggestions).toHaveLength(0); // No suggestions needed
    });

    test('should provide suggestions for incomplete memory', () => {
      updateMemory('testUser', {
        energyLevel: 'high',
        priority: 'high'
        // Missing other required fields
      });

      const analysis = analyzeMemory('testUser');
      
      expect(analysis.completeness).toBe(0.4); // 2 out of 5 required fields
      expect(analysis.suggestions.length).toBeGreaterThan(0);
      expect(analysis.suggestions).toContain('Define specific goals');
    });

    test('should detect patterns in memory', () => {
      updateMemory('testUser', {
        energyLevel: 'low',
        priority: 'high',
        goals: ['finish urgent task']
      });

      const analysis = analyzeMemory('testUser');
      
      expect(analysis.patterns).toContain(
        'High priority task with low energy - consider energy management'
      );
    });
  });

  describe('generateContextualResponse', () => {
    test('should enhance response with memory analysis', () => {
      updateMemory('testUser', {
        energyLevel: 'high',
        mood: 'focused'
      });

      const baseResponse = 'Task scheduled successfully.';
      const enhanced = generateContextualResponse('testUser', baseResponse);
      
      expect(enhanced).toContain(baseResponse);
      expect(enhanced).toContain('💡'); // Should add insight due to incomplete memory
    });

    test('should add time-based suggestions', () => {
      updateMemory('testUser', {
        energyLevel: 'high',
        priority: 'high',
        mood: 'focused',
        goals: ['urgent task'],
        intent: 'complete work'
      });

      const baseResponse = 'Task scheduled.';
      const context = { timeOfDay: 'evening' as const, urgencyLevel: 'high' as const };
      const enhanced = generateContextualResponse('testUser', baseResponse, context);
      
      expect(enhanced).toContain('⏰'); // Should add evening urgency warning
    });
  });

  describe('conversation tracking', () => {
    test('should track conversation turns', () => {
      addConversationTurn('testUser', 'Hello', 'Hi there!');
      addConversationTurn('testUser', 'How are you?', 'I am well, thanks!');

      const history = getConversationHistory('testUser');
      
      expect(history).toHaveLength(2);
      expect(history[0].userInput).toBe('Hello');
      expect(history[1].userInput).toBe('How are you?');
    });

    test('should limit conversation history to 10 turns', () => {
      // Add 15 turns
      for (let i = 0; i < 15; i++) {
        addConversationTurn('testUser', `Message ${i}`, `Response ${i}`);
      }

      const history = getConversationHistory('testUser');
      
      expect(history).toHaveLength(10); // Should only keep last 10
      expect(history[0].userInput).toBe('Message 5'); // First kept message
      expect(history[9].userInput).toBe('Message 14'); // Last message
    });

    test('should analyze conversation trends', () => {
      // Add conversation turns with varying memory completeness
      updateMemory('testUser', { energyLevel: 'high' });
      addConversationTurn('testUser', 'First message', 'Response 1');
      
      updateMemory('testUser', { energyLevel: 'high', mood: 'good', goals: ['task1'] });
      addConversationTurn('testUser', 'Second message', 'Response 2');
      
      updateMemory('testUser', { 
        energyLevel: 'high', 
        mood: 'good', 
        goals: ['task1'], 
        intent: 'work',
        priority: 'high'
      });
      addConversationTurn('testUser', 'Third message', 'Response 3');

      const trends = analyzeConversationTrends('testUser');
      
      expect(trends.totalTurns).toBe(3);
      expect(trends.avgMemoryCompleteness).toBeGreaterThan(0.5);
      expect(trends.progressTrend).toBe('improving');
      expect(trends.commonPatterns).toContain('Usually operates at high energy level');
    });
  });

  describe('parseIntelligenceEnhanced', () => {
    test('should return enhanced response with analysis', async () => {
      mockedCreate.mockResolvedValue({
        choices: [{
          message: {
            content: JSON.stringify({
              energyLevel: 'high',
              mood: 'focused',
              goals: ['test goal'],
              intent: 'work on project',
              priority: 'high'
            })
          }
        }]
      });

      const result = await parseIntelligenceEnhanced(
        'I need to work on my project', 
        'testUser', 
        true // include analysis
      );

      expect(result).toContain('analysis');
      expect(result).toContain('memoryCompleteness');
      expect(result).toContain('confidence');
      expect(result).toContain('conversationTrends');
    });

    test('should handle follow-up questions without analysis', async () => {
      mockedCreate.mockResolvedValue({
        choices: [{
          message: {
            content: 'FollowUp: What is your current energy level?'
          }
        }]
      });

      const result = await parseIntelligenceEnhanced(
        'Help me plan', 
        'testUser', 
        true
      );

      expect(result).toBe('FollowUp: What is your current energy level?');
      expect(result).not.toContain('analysis');
    });

    test('should enhance non-JSON responses contextually', async () => {
      mockedCreate.mockResolvedValue({
        choices: [{
          message: {
            content: 'I understand you want to work on your project.'
          }
        }]
      });

      updateMemory('testUser', {
        energyLevel: 'low',
        priority: 'high'
      });

      const result = await parseIntelligenceEnhanced(
        'I need to work', 
        'testUser', 
        true
      );

      expect(result).toContain('I understand you want to work on your project.');
      expect(result).toContain('💡'); // Should add insight
    });

    test('should handle errors gracefully', async () => {
      mockedCreate.mockRejectedValue(new Error('API Error'));

      const result = await parseIntelligenceEnhanced(
        'Test message', 
        'testUser', 
        true
      );

      expect(result).toContain('Error in enhanced parsing');
      expect(result).toContain('API Error');
    });
  });
});

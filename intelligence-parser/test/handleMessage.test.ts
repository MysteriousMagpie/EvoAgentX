import { handleMessage } from '../src/handleMessage';
import { jest } from '@jest/globals';

let mockCreate: any = jest.fn();

jest.mock('openai', () => {
  return {
    __esModule: true,
    default: jest.fn().mockImplementation(() => ({
      chat: { completions: { create: (...args: any[]) => mockCreate(...args) } },
    })),
  };
});

describe('handleMessage', () => {
  beforeEach(() => {
    mockCreate.mockReset();
  });

  it('returns JSON when complete information provided', async () => {
    mockCreate.mockResolvedValueOnce({
      choices: [
        {
          message: {
            content: JSON.stringify({
              context: {
                energyLevel: 'high',
                mood: 'excited',
                goals: ['build parser'],
                avoidances: ['none'],
              },
              task: {
                intent: 'code',
                priority: 'high',
              },
            }),
          },
        },
      ],
    });

    const res = await handleMessage('u1', [], 'I want to code.');
    expect(() => JSON.parse(res)).not.toThrow();
  });

  it('asks follow up then returns JSON', async () => {
    mockCreate.mockResolvedValueOnce({ choices: [{ message: { content: '{}' } }] });
    const follow = await handleMessage('u2', [], 'hello');
    expect(follow.startsWith('FollowUp: ')).toBe(true);

    mockCreate.mockResolvedValueOnce({
      choices: [{ message: { content: JSON.stringify({
        context: {
          energyLevel: 'medium',
          mood: 'ok',
          goals: ['chat'],
          avoidances: ['none']
        },
        task: {
          intent: 'chat',
          priority: 'med'
        }
      }) } }],
    });
    const res = await handleMessage('u2', [{ role: 'assistant', content: follow }], 'I want to chat');
    expect(() => JSON.parse(res)).not.toThrow();
  });
});

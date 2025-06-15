jest.mock("openai", () => ({ __esModule: true, default: jest.fn() }));
import { handleMessage } from './intelligenceParser';
import OpenAI from 'openai';

describe('handleMessage', () => {
  const createMock = (response: any) => {
    (OpenAI as any).mockClear();
    (OpenAI as unknown as jest.Mock).mockImplementation(() => ({
      chat: { completions: { create: jest.fn().mockResolvedValue({ choices: [{ message: { content: JSON.stringify(response) } }] }) } }
    }));
  };

  beforeEach(() => {
    (OpenAI as unknown as jest.Mock) = jest.fn();
  });

  test('complete in one go', async () => {
    createMock({
      energyLevel: 'high',
      mood: 'excited',
      goals: ['build strength'],
      avoidances: ['injury'],
      intent: 'start workout',
      priority: 'high'
    });
    const result = await handleMessage('u1', [], 'I want to start workout');
    expect(result).toContain('"meta"');
    expect(result).toContain('"energyLevel"');
  });

  test('needs follow-up then complete', async () => {
    createMock({ intent: 'plan', priority: 'med' });
    let result = await handleMessage('u2', [], 'I want to plan');
    expect(result.startsWith('FollowUp:')).toBe(true);

    createMock({ goals: ['finish'], mood: 'ok', energyLevel: 'low', avoidances: ['delay'] });
    result = await handleMessage('u2', [{ role: 'assistant', content: result }], 'My goal is to finish, energy is low, avoid delay.');
    expect(result).toContain('"meta"');
    expect(result).toContain('"intent"');
  });
});

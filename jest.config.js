export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: [
    '**/tests/**/*.test.ts',
    '**/typescript/tests/**/*.test.ts',
    'intelligence-parser/test/**/*.test.ts'
  ],
  moduleNameMapper: {
    '^(\.{1,2}/.*)\.js$': '$1'
  },
  roots: ['<rootDir>/typescript', '<rootDir>/intelligence-parser'],
  testPathIgnorePatterns: ['/node_modules/', '/venv/']
};
export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  rootDir: '..',
  testMatch: [
    '<rootDir>/tests/**/*.test.ts',
    '<rootDir>/typescript/tests/**/*.test.ts',
    '<rootDir>/intelligence-parser/test/**/*.test.ts'
  ],
  moduleNameMapper: {
    '^(\.{1,2}/.*)\.js$': '$1'
  },
  roots: ['<rootDir>/typescript', '<rootDir>/intelligence-parser', '<rootDir>/tests'],
  testPathIgnorePatterns: ['/node_modules/', '/venv/', '/build/']
};
/**
 * Mock provider for Promptfoo proof-of-concept.
 *
 * Returns the golden output YAML so we can test the full pipeline
 * (prompt -> provider -> assertion) without needing an API key.
 *
 * Promptfoo calls this module's callApi() method.
 */

const fs = require("fs");
const path = require("path");

const GOLDEN_PATH = path.resolve(
  __dirname,
  "../flashcards/fixtures/outputs/f01-agent-memory-basics.flashcards.yaml"
);

class MockGoldenProvider {
  constructor(options) {
    this.providerId = options?.id || "mock:golden-output";
    this.label = options?.label || "Mock (Golden F01)";
  }

  id() {
    return this.providerId;
  }

  toString() {
    return this.label;
  }

  async callApi(prompt) {
    const goldenYaml = fs.readFileSync(GOLDEN_PATH, "utf-8");
    return {
      output: goldenYaml,
      tokenUsage: {
        total: 0,
        prompt: 0,
        completion: 0,
      },
    };
  }
}

module.exports = MockGoldenProvider;

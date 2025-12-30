import type { ConsoleMessage, Page } from '@playwright/test';

/**
 * Console message data structure
 */
export interface ConsoleMessageData {
  type: string;
  text: string;
  location: string;
  timestamp: Date;
}

/**
 * Console Errors Collector
 *
 * Collects and manages console messages during test execution.
 * Helps identify JavaScript errors, warnings, and other console output.
 */
export class ConsoleErrorsCollector {
  private messages: ConsoleMessageData[] = [];
  private isAttached = false;

  constructor(private page: Page) {}

  /**
   * Start collecting console messages
   */
  attach(): void {
    if (this.isAttached) return;

    this.page.on('console', this.handleConsoleMessage.bind(this));
    this.isAttached = true;
  }

  /**
   * Handle incoming console message
   */
  private handleConsoleMessage(msg: ConsoleMessage): void {
    this.messages.push({
      type: msg.type(),
      text: msg.text(),
      location: msg.location().url || 'unknown',
      timestamp: new Date(),
    });
  }

  /**
   * Get all collected messages
   */
  getAll(): ConsoleMessageData[] {
    return [...this.messages];
  }

  /**
   * Get only error messages
   */
  getErrors(): ConsoleMessageData[] {
    return this.messages.filter((m) => m.type === 'error');
  }

  /**
   * Get only warning messages
   */
  getWarnings(): ConsoleMessageData[] {
    return this.messages.filter((m) => m.type === 'warning');
  }

  /**
   * Check if there are any errors
   */
  hasErrors(): boolean {
    return this.getErrors().length > 0;
  }

  /**
   * Check if there are any warnings
   */
  hasWarnings(): boolean {
    return this.getWarnings().length > 0;
  }

  /**
   * Clear collected messages
   */
  clear(): void {
    this.messages = [];
  }

  /**
   * Get formatted error summary for test assertions
   */
  getErrorSummary(): string {
    const errors = this.getErrors();
    if (errors.length === 0) return 'No errors';

    return errors.map((e) => `[${e.type}] ${e.text} (${e.location})`).join('\n');
  }

  /**
   * Assert no console errors occurred
   * Throws if any errors were collected
   */
  assertNoErrors(ignorePatterns: RegExp[] = []): void {
    const errors = this.getErrors().filter(
      (e) => !ignorePatterns.some((pattern) => pattern.test(e.text)),
    );

    if (errors.length > 0) {
      throw new Error(
        `Console errors detected:\n${errors.map((e) => `  - ${e.text}`).join('\n')}`,
      );
    }
  }
}

/**
 * Factory function to create a ConsoleErrorsCollector instance
 */
export function createConsoleErrorsCollector(page: Page): ConsoleErrorsCollector {
  const collector = new ConsoleErrorsCollector(page);
  collector.attach();
  return collector;
}

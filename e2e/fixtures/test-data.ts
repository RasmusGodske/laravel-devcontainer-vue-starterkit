import type { APIRequestContext } from '@playwright/test';

/**
 * Type definitions for test data
 */
export interface TestUser {
  id: number;
  email: string;
  name: string;
  password: string;
}

/**
 * Test Data Helper
 *
 * Provides methods for creating and managing test data via E2E API endpoints.
 * All test data is created through the Laravel backend to ensure database consistency.
 */
export class TestDataHelper {
  constructor(private request: APIRequestContext) {}

  /**
   * Create a test user
   */
  async createUser(options?: { name?: string; email?: string }): Promise<TestUser> {
    const response = await this.request.post('/e2e/users', {
      data: {
        name: options?.name,
        email: options?.email,
      },
    });

    if (!response.ok()) {
      const text = await response.text();
      throw new Error(`Failed to create user: ${response.status()} - ${text}`);
    }

    return response.json();
  }

  /**
   * Delete a test user by ID
   */
  async deleteUser(userId: number): Promise<void> {
    const response = await this.request.delete(`/e2e/users/${userId}`);

    if (!response.ok()) {
      const text = await response.text();
      throw new Error(`Failed to delete user: ${response.status()} - ${text}`);
    }
  }

  /**
   * Create multiple test users
   */
  async createUsers(count: number): Promise<TestUser[]> {
    const users: TestUser[] = [];
    for (let i = 0; i < count; i++) {
      users.push(await this.createUser());
    }
    return users;
  }

  /**
   * Delete multiple users
   */
  async deleteUsers(userIds: number[]): Promise<void> {
    await Promise.all(userIds.map((id) => this.deleteUser(id)));
  }
}

/**
 * Factory function to create a TestDataHelper instance
 */
export function createTestDataHelper(request: APIRequestContext): TestDataHelper {
  return new TestDataHelper(request);
}

export type UUID = string;

export interface ActorContext {
  userId: UUID;
  organizationId?: UUID;
  workspaceId?: UUID;
  roles: string[];
}

export interface IdentityProvider {
  getCurrentUser(token: string): Promise<{ provider: string; subject: string; email: string; displayName?: string }>;
}

export interface AuthorizationProvider {
  can(actor: ActorContext, permission: string, resource: { type: string; id: UUID }): Promise<boolean>;
  assertCan(actor: ActorContext, permission: string, resource: { type: string; id: UUID }): Promise<void>;
}

export interface EntitlementProvider {
  canUse(organizationId: UUID, entitlementKey: string, quantity?: number): Promise<boolean>;
  getLimit(organizationId: UUID, entitlementKey: string): Promise<number | null>;
}

export interface BillingProvider {
  createCheckoutSession(input: { organizationId: UUID; planKey: string; successUrl: string; cancelUrl: string }): Promise<{ url: string }>;
  createBillingPortalSession(input: { organizationId: UUID; returnUrl: string }): Promise<{ url: string }>;
  verifyWebhook(rawBody: string, signature: string): Promise<{ providerEventId: string; type: string; payload: unknown }>;
}

export interface AuditProvider {
  record(event: { organizationId?: UUID; workspaceId?: UUID; actorUserId?: UUID; eventType: string; targetType?: string; targetId?: UUID; payload?: Record<string, unknown> }): Promise<void>;
}

export interface EventBus {
  publish<T>(topic: string, payload: T, options?: { idempotencyKey?: string }): Promise<void>;
  subscribe<T>(topic: string, handler: (payload: T) => Promise<void>): Promise<void>;
}

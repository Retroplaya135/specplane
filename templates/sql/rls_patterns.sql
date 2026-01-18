-- RLS pattern template. Adapt carefully.

alter table organizations enable row level security;
alter table workspaces enable row level security;
alter table memberships enable row level security;
alter table invitations enable row level security;
alter table subscriptions enable row level security;
alter table entitlements enable row level security;
alter table usage_events enable row level security;
alter table audit_events enable row level security;
alter table api_keys enable row level security;
alter table webhook_endpoints enable row level security;

-- Example helper pattern using transaction-local settings.
-- Application sets these after validating the external session:
-- select set_config('app.current_user_id', '<uuid>', true);

create or replace function app.current_user_id()
returns uuid language sql stable as $$
  select nullif(current_setting('app.current_user_id', true), '')::uuid;
$$;

create or replace function app.has_org_membership(org_id uuid)
returns boolean language sql stable as $$
  select exists (
    select 1 from memberships m
    where m.organization_id = org_id
      and m.user_id = app.current_user_id()
      and m.status = 'active'
  );
$$;

create or replace function app.has_workspace_membership(ws_id uuid)
returns boolean language sql stable as $$
  select exists (
    select 1 from memberships m
    where m.workspace_id = ws_id
      and m.user_id = app.current_user_id()
      and m.status = 'active'
  );
$$;

create policy organizations_select_member on organizations
  for select using (app.has_org_membership(id));

create policy workspaces_select_member on workspaces
  for select using (app.has_workspace_membership(id) or app.has_org_membership(organization_id));

create policy audit_events_select_member on audit_events
  for select using (
    (workspace_id is not null and app.has_workspace_membership(workspace_id))
    or (organization_id is not null and app.has_org_membership(organization_id))
  );

-- Insert/update/delete policies must be narrower and mapped to roles/permissions.
-- Do not ship this file without role-specific policies and tests.

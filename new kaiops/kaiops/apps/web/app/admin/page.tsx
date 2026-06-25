export default function AdminPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-bold">Administration</h2>
      <article className="k-card">
        <h3 className="font-semibold">Identity and Access</h3>
        <p className="mt-2 text-sm">RBAC roles, OAuth2 providers (Azure AD, Okta), tenant policies and API tokens are managed here.</p>
      </article>
      <article className="k-card">
        <h3 className="font-semibold">Tenant Settings</h3>
        <p className="mt-2 text-sm">Data residency, retention policies, encryption and integration credentials.</p>
      </article>
    </section>
  );
}

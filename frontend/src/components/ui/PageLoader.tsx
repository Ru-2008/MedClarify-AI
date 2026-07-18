export function PageLoader() {
  return (
    <div
      className="flex min-h-screen items-center justify-center bg-background"
      role="status"
      aria-label="Loading page"
    >
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-teal-600 border-t-transparent" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

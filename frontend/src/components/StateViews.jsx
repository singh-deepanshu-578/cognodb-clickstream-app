export function Loading({ label = "Loading..." }) {
  return <div className="state-view loading">{label}</div>;
}

export function EmptyState({ label = "Nothing to show yet." }) {
  return <div className="state-view empty">{label}</div>;
}

export function ErrorState({ message = "Something went wrong." }) {
  return <div className="state-view error">⚠ {message}</div>;
}

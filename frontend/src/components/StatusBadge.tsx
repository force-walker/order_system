export const StatusBadge = ({ value }: { value: string }) => (
  <span className={`status-badge status-${value}`}>{value}</span>
)

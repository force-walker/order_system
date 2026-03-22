import type { PropsWithChildren } from 'react'

export const LoadingState = () => <p className="state loading">読み込み中...</p>
export const EmptyState = ({ text = 'データがありません' }: { text?: string }) => (
  <p className="state empty">{text}</p>
)
export const ErrorState = ({ message, onRetry }: { message: string; onRetry?: () => void }) => (
  <div className="state error">
    <p>{message}</p>
    {onRetry ? <button onClick={onRetry}>再試行</button> : null}
  </div>
)

export const SuccessBanner = ({ children }: PropsWithChildren) => (
  <div className="state success">{children}</div>
)

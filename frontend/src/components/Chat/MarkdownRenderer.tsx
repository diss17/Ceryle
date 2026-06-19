import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div
      className={`prose-ceryle text-sm leading-relaxed text-text-secondary ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-text-primary mt-6 mb-3 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-text-primary mt-5 mb-2 first:mt-0">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold text-text-primary mt-4 mb-2 first:mt-0">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-semibold text-text-primary mt-3 mb-1 first:mt-0">
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="my-3 text-text-secondary">{children}</p>
          ),
          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-primary hover:text-accent-hover underline underline-offset-2"
            >
              {children}
            </a>
          ),
          ul: ({ children }) => (
            <ul className="my-3 ml-5 list-disc space-y-1 text-text-secondary marker:text-text-muted">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-3 ml-5 list-decimal space-y-1 text-text-secondary marker:text-text-muted">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="pl-1">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="my-4 pl-4 border-l-2 border-border-hover text-text-muted italic">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-5 border-border-default" />,
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto border border-border-default rounded-md">
              <table className="w-full text-xs border-collapse">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-surface-quaternary text-text-primary">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="px-3 py-2 text-left font-semibold border-b border-border-default">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 border-b border-border-subtle text-text-secondary">
              {children}
            </td>
          ),
          pre: ({ children }) => (
            <pre className="my-3 p-3 rounded-lg bg-surface-primary border border-border-default overflow-x-auto text-xs leading-relaxed">
              {children}
            </pre>
          ),
          code: ({ className: cls, children, ...props }) => {
            const isInline = !cls;
            if (isInline) {
              return (
                <code
                  className="px-1 py-0.5 rounded bg-surface-quaternary text-text-primary text-[0.85em] font-mono"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <code className={cls} {...props}>
                {children}
              </code>
            );
          },
          strong: ({ children }) => (
            <strong className="font-semibold text-text-primary">{children}</strong>
          ),
          em: ({ children }) => <em className="italic">{children}</em>,
          img: ({ src, alt }) => (
            <img
              src={typeof src === 'string' ? src : undefined}
              alt={alt ?? ''}
              className="my-4 max-w-full rounded-md border border-border-default"
            />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

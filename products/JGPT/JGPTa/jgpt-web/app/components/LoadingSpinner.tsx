interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    text?: string;
    className?: string;
}

export default function LoadingSpinner({ size = 'md', text, className = '' }: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: 'w-6 h-6 border-2',
        md: 'w-10 h-10 border-3',
        lg: 'w-16 h-16 border-4'
    };

    const textSizeClasses = {
        sm: 'text-xs',
        md: 'text-sm',
        lg: 'text-base'
    };

    return (
        <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
            <div className={`${sizeClasses[size]} rounded-full border-transparent border-t-purple-500 border-r-pink-500 animate-spin`}
                style={{
                    borderImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) 1',
                    animation: 'spin 1s linear infinite'
                }}
            />
            {text && (
                <p className={`${textSizeClasses[size]} text-white/50 font-medium`}>
                    {text}
                </p>
            )}
        </div>
    );
}

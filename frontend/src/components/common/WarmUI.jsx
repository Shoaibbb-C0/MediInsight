import React from 'react';

export function Button({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  type = 'button',
  className = '',
  icon = null,
  size = 'md',
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-2xl transition-all duration-150 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none';
  
  const sizeStyles = {
    sm: 'px-3.5 py-2 text-sm gap-1.5 min-h-11',
    md: 'px-5 py-3 text-base gap-2',
    lg: 'px-6 py-3.5 text-lg gap-2.5',
  };

  const variantStyles = {
    primary: 'bg-clarity-coral text-clarity-surface hover:bg-clarity-tealHover shadow-sm active:scale-[0.99] focus-visible:outline-clarity-teal',
    secondary: 'bg-clarity-surface text-clarity-teal border border-clarity-border hover:bg-clarity-ivory hover:border-clarity-teal/30 focus-visible:outline-clarity-teal',
    coral: 'bg-clarity-coral text-clarity-surface hover:brightness-95 shadow-sm active:scale-[0.99] focus-visible:outline-clarity-coral',
    mint: 'bg-clarity-mint text-clarity-teal hover:brightness-95 font-bold focus-visible:outline-clarity-teal',
    ghost: 'text-clarity-charcoal hover:bg-clarity-ivory hover:text-clarity-teal',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </button>
  );
}

export function StatusBadge({ status, label }) {
  const normalized = (status || '').toLowerCase();
  
  let styles = 'bg-clarity-badge text-clarity-teal border-clarity-mint';
  let dotColor = 'bg-clarity-teal';
  let defaultLabel = 'Needs review';
  if (!['high', 'low', 'normal', 'within_range'].includes(normalized)) { styles = 'bg-amber-50 text-amber-900 border-amber-200'; }

  if (normalized === 'high') {
    styles = 'bg-amber-50 text-amber-900 border-amber-200';
    dotColor = 'bg-[#D87763]';
    defaultLabel = 'High';
  } else if (normalized === 'low') {
    styles = 'bg-red-50 text-red-800 border-red-200';
    dotColor = 'bg-amber-500';
    defaultLabel = 'Low';
  } else if (['normal', 'within_range'].includes(normalized)) {
    styles = 'bg-emerald-50 text-[#195643] border-emerald-200';
    dotColor = 'bg-emerald-600';
    defaultLabel = 'Within laboratory range';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${styles}`}>
      <span className={`w-2 h-2 rounded-full ${dotColor}`} />
      <span>{label || defaultLabel}</span>
    </span>
  );
}

import * as React from 'react';

export interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, label, ...props }, ref) => {
    const id = React.useId();
    const inputId = props.id || id;

    return (
      <div className="flex items-center">
        <button
          type="button"
          role="switch"
          aria-checked={props.checked}
          onClick={() => {
            const event = {
              target: { checked: !props.checked },
            } as React.ChangeEvent<HTMLInputElement>;
            props.onChange?.(event);
          }}
          className={`${
            props.checked ? 'bg-primary-600' : 'bg-gray-200'
          } relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            props.disabled ? 'opacity-50 cursor-not-allowed' : ''
          }`}
          disabled={props.disabled}
        >
          <span className="sr-only">{label || 'Toggle'}</span>
          <span
            aria-hidden="true"
            className={`${
              props.checked ? 'translate-x-5' : 'translate-x-0'
            } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
          />
        </button>
        <input
          type="checkbox"
          ref={ref}
          id={inputId}
          className="sr-only"
          {...props}
        />
        {label && (
          <label
            htmlFor={inputId}
            className="ml-3 text-sm font-medium text-gray-700 cursor-pointer"
          >
            {label}
          </label>
        )}
      </div>
    );
  }
);

Switch.displayName = 'Switch';

export { Switch };

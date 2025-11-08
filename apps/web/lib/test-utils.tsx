// Test utilities for CreditBeast application
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactElement } from 'react';

// Test wrapper with providers
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  wrapper?: React.ComponentType<any>;
  queryClient?: QueryClient;
}

const AllTheProviders = ({ children, queryClient }: { 
  children: React.ReactNode; 
  queryClient: QueryClient;
}) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
): RenderResult => {
  const { wrapper: Wrapper, queryClient = createTestQueryClient(), ...renderOptions } = options;
  
  const AllProviders = Wrapper ? Wrapper : ({ children }: { children: React.ReactNode }) => (
    <AllTheProviders queryClient={queryClient}>{children}</AllTheProviders>
  );

  return render(ui, { wrapper: AllProviders, ...renderOptions });
};

// Mock API utilities
export const mockApi = {
  clients: {
    list: jest.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            status: 'active',
            created_at: '2025-11-06T10:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    }),
    create: jest.fn().mockResolvedValue({ data: { id: '1' } }),
    update: jest.fn().mockResolvedValue({ data: { id: '1' } }),
    delete: jest.fn().mockResolvedValue({ data: { success: true } }),
  },
  disputes: {
    list: jest.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            dispute_type: 'late_payment',
            status: 'pending',
            created_at: '2025-11-06T10:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    }),
    create: jest.fn().mockResolvedValue({ data: { id: '1' } }),
    generateLetter: jest.fn().mockResolvedValue({
      data: { letter_content: 'Sample dispute letter content' },
    }),
  },
  billing: {
    getSubscription: jest.fn().mockResolvedValue({
      data: {
        id: '1',
        plan_name: 'professional',
        plan_price_cents: 29900,
        status: 'active',
        current_period_end: '2025-12-06T10:00:00Z',
      },
    }),
    createSubscription: jest.fn().mockResolvedValue({
      data: { client_secret: 'pi_test_client_secret' },
    }),
    cancelSubscription: jest.fn().mockResolvedValue({ data: { success: true } }),
  },
  documents: {
    list: jest.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            name: 'document.pdf',
            fileType: 'pdf',
            status: 'verified',
            uploaded_at: '2025-11-06T10:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    }),
    upload: jest.fn().mockResolvedValue({ data: { success: true } }),
    delete: jest.fn().mockResolvedValue({ data: { success: true } }),
  },
  emails: {
    list: jest.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            to: 'test@example.com',
            subject: 'Test Email',
            status: 'delivered',
            sent_at: '2025-11-06T10:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    }),
    send: jest.fn().mockResolvedValue({ data: { success: true } }),
  },
};

// Test data factories
export const createMockClient = (overrides = {}) => ({
  id: '1',
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone: '+1234567890',
  status: 'active' as const,
  created_at: '2025-11-06T10:00:00Z',
  ...overrides,
});

export const createMockDispute = (overrides = {}) => ({
  id: '1',
  dispute_type: 'late_payment',
  bureau: 'equifax' as const,
  status: 'pending' as const,
  created_at: '2025-11-06T10:00:00Z',
  ...overrides,
});

export const createMockDocument = (overrides = {}) => ({
  id: '1',
  name: 'document.pdf',
  fileType: 'pdf',
  fileSize: 1024000,
  status: 'verified' as const,
  uploaded_at: '2025-11-06T10:00:00Z',
  ...overrides,
});

export const createMockEmail = (overrides = {}) => ({
  id: '1',
  to: 'test@example.com',
  subject: 'Test Email',
  status: 'delivered' as const,
  sent_at: '2025-11-06T10:00:00Z',
  ...overrides,
});

// Assertion helpers
export const expectElementToBeInTheDocument = (element: HTMLElement) => {
  expect(element).toBeInTheDocument();
};

export const expectElementToHaveText = (element: HTMLElement, text: string) => {
  expect(element).toHaveTextContent(text);
};

export const expectButtonToBeDisabled = (element: HTMLElement) => {
  expect(element).toBeDisabled();
};

export const expectButtonToBeEnabled = (element: HTMLElement) => {
  expect(element).not.toBeDisabled();
};

// Form testing utilities
export const fillFormField = (container: HTMLElement, name: string, value: string) => {
  const field = container.querySelector(`[name="${name}"]`) as HTMLInputElement;
  expect(field).toBeInTheDocument();
  fireEvent.change(field, { target: { value } });
  return field;
};

export const selectFormOption = (container: HTMLElement, name: string, value: string) => {
  const field = container.querySelector(`[name="${name}"]`) as HTMLSelectElement;
  expect(field).toBeInTheDocument();
  fireEvent.change(field, { target: { value } });
  return field;
};

export const submitForm = (form: HTMLFormElement) => {
  fireEvent.submit(form);
};

// Mock user events
export const clickElement = (element: HTMLElement) => {
  fireEvent.click(element);
};

export const hoverElement = (element: HTMLElement) => {
  fireEvent.mouseEnter(element);
};

export const typeInInput = (input: HTMLInputElement, text: string) => {
  fireEvent.change(input, { target: { value: text } });
};

// Accessibility testing utilities
export const getAccessibleElements = (container: HTMLElement) => {
  const elements = {
    buttons: container.querySelectorAll('button'),
    inputs: container.querySelectorAll('input, textarea, select'),
    links: container.querySelectorAll('a'),
    headings: container.querySelectorAll('h1, h2, h3, h4, h5, h6'),
    tables: container.querySelectorAll('table'),
  };
  return elements;
};

export const checkAccessibility = (container: HTMLElement) => {
  const { buttons, inputs, headings } = getAccessibleElements(container);
  
  // Check for proper button labeling
  buttons.forEach(button => {
    if (!button.textContent?.trim() && !button.getAttribute('aria-label')) {
      console.warn('Button found without accessible name:', button);
    }
  });
  
  // Check for proper form labeling
  inputs.forEach(input => {
    const id = input.getAttribute('id');
    const label = id ? container.querySelector(`label[for="${id}"]`) : null;
    const ariaLabel = input.getAttribute('aria-label');
    
    if (!label && !ariaLabel && input.type !== 'hidden') {
      console.warn('Form field found without accessible label:', input);
    }
  });
  
  // Check heading hierarchy
  const headingElements = Array.from(headings);
  const headingLevels = headingElements.map(h => parseInt(h.tagName.charAt(1)));
  for (let i = 1; i < headingLevels.length; i++) {
    if (headingLevels[i] - headingLevels[i-1] > 1) {
      console.warn('Heading hierarchy skipped:', headingElements[i-1], '->', headingElements[i]);
    }
  }
};

// Performance testing utilities
export const measureRenderTime = async (component: ReactElement) => {
  const startTime = performance.now();
  const { unmount } = render(component);
  const endTime = performance.now();
  const renderTime = endTime - startTime;
  unmount();
  return renderTime;
};

export const checkBundleSize = async (componentPath: string) => {
  try {
    // Mock bundle size check - in real implementation, this would analyze actual bundle size
    const estimatedSize = Math.random() * 500 + 100; // 100-600 KB range
    return {
      size: estimatedSize,
      isOptimal: estimatedSize < 300, // Under 300KB is considered optimal
    };
  } catch (error) {
    return {
      size: 0,
      isOptimal: false,
      error: 'Failed to check bundle size',
    };
  }
};

export * from '@testing-library/react';
export { customRender as render, createTestQueryClient };